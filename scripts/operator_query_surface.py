#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
ONE_SCREEN_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "one_screen_status.json"
POLICY_DIGEST_PATH = REPO_ROOT / "docs" / "governance" / "POLICY_DIGEST.md"
CAPABILITIES_PATH = REPO_ROOT / "docs" / "governance" / "MACHINE_CAPABILITIES_SUMMARY.md"
NEXT_STEP_PATH = REPO_ROOT / "docs" / "NEXT_CANONICAL_STEP.md"


@dataclass(frozen=True)
class RouteRule:
    request_class: str
    tokens: tuple[str, ...]


ROUTING_PRECEDENCE: tuple[RouteRule, ...] = (
    RouteRule(
        "blocker_query",
        (
            "blocker",
            "blocked",
            "why fail",
            "why warning",
            "что блокирует",
            "блокирует",
            "почему verdict",
            "escalation requirement",
            "эскалац",
        ),
    ),
    RouteRule(
        "authority_query",
        (
            "creator authority",
            "creator-level",
            "authority",
            "авторитет",
            "права",
            "creator-level acceptance",
            "canonical completion",
            "creator acceptance",
        ),
    ),
    RouteRule(
        "admission_query",
        ("admission", "admissible", "gate open", "gate closed", "допуск", "admission gate"),
    ),
    RouteRule(
        "policy_reference_query",
        (
            "какой policy",
            "policy basis",
            "based on policy",
            "source rule",
            "основание",
            " policy ",
            "какой документ",
            "какой файл policy",
        ),
    ),
    RouteRule(
        "governance_query",
        ("governance acceptance", "governance gate", "governance", "compliant", "governance compliant"),
    ),
    RouteRule(
        "workspace_health_query",
        ("workspace health", "repo health", "system health", "sync health", "здоров", "состояние системы", "trust status"),
    ),
    RouteRule(
        "mode_query",
        ("machine mode", "в каком ты режиме", "какой режим", "режим", "mode"),
    ),
    RouteRule(
        "next_step_query",
        ("next canonical step", "next step", "canonical step", "что дальше", "следующий шаг", "что делать дальше"),
    ),
    RouteRule(
        "capability_query",
        ("what can", "capabilit", "умеешь", "allowed", "forbidden", "можешь", "запрещено", "forbidden actions"),
    ),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def route_request(raw_query: str) -> str:
    text = f" {' '.join(raw_query.strip().lower().split())} "
    for rule in ROUTING_PRECEDENCE:
        if any(token in text for token in rule.tokens):
            return rule.request_class
    return "workspace_health_query"


def short_text(path: Path, default: str = "not-available") -> str:
    if not path.exists():
        return default
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8-sig").splitlines() if ln.strip()]
    return lines[0][:160] if lines else default


def build_response(request_class: str, one_screen: dict[str, Any]) -> dict[str, Any]:
    resolved_scope = {
        "mode_query": "machine_mode_identity",
        "authority_query": "creator_authority_contract",
        "workspace_health_query": "workspace_control_health",
        "governance_query": "governance_chain_state",
        "admission_query": "admission_gate_state",
        "capability_query": "capability_and_authority_surface",
        "blocker_query": "active_blockers",
        "next_step_query": "canonical_next_step",
        "policy_reference_query": "policy_basis_reference",
    }.get(request_class, "workspace_control_health")

    current_state = {
        "machine_mode": one_screen.get("machine_mode"),
        "workspace_health": one_screen.get("workspace_health"),
        "sync_verdict": one_screen.get("sync_verdict"),
        "trust_verdict": one_screen.get("trust_verdict"),
        "governance_verdict": one_screen.get("governance_verdict"),
        "governance_acceptance_verdict": one_screen.get("governance_acceptance_verdict"),
        "admission_verdict": one_screen.get("admission_verdict"),
    }

    authority = {
        "authority_present": one_screen.get("authority_present"),
        "authority_status": one_screen.get("authority_status"),
        "authority_path": one_screen.get("authority_path", ""),
        "creator_level_acceptance_allowed": bool(
            one_screen.get("machine_mode") == "creator"
            and one_screen.get("authority_present")
            and one_screen.get("governance_acceptance_verdict") == "PASS"
            and one_screen.get("admission_verdict") == "ADMISSIBLE"
        ),
    }

    class_verdict = {
        "mode_query": one_screen.get("machine_mode_verdict"),
        "authority_query": "PASS" if one_screen.get("authority_present") else "BLOCKED",
        "workspace_health_query": one_screen.get("workspace_health"),
        "governance_query": one_screen.get("governance_verdict"),
        "admission_query": one_screen.get("admission_verdict"),
        "capability_query": "PASS" if one_screen.get("machine_mode_verdict") in {"PASS", "WARNING"} else "BLOCKED",
        "blocker_query": "NONE" if one_screen.get("blocking_reason_category") == "NONE" else "BLOCKED",
        "next_step_query": "PASS",
        "policy_reference_query": "PASS" if POLICY_DIGEST_PATH.exists() else "WARNING",
    }.get(request_class, one_screen.get("trust_verdict"))

    blocking_factors = {
        "category": one_screen.get("blocking_reason_category"),
        "detail": one_screen.get("blocking_reason_detail"),
        "critical_contradictions": one_screen.get("critical_contradictions", 0),
        "major_contradictions": one_screen.get("major_contradictions", 0),
    }

    response: dict[str, Any] = {
        "response_contract_version": "operator_response_contract.v1.0.0",
        "request_class": request_class,
        "resolved_scope": resolved_scope,
        "current_state": current_state,
        "authority": authority,
        "verdict": class_verdict,
        "blocking_factors": blocking_factors,
        "next_step": one_screen.get("next_canonical_step"),
        "evidence_source": [
            "runtime/repo_control_center/one_screen_status.json",
            "runtime/repo_control_center/repo_control_status.json",
        ],
        "confidence_or_stability": "stable_schema_contract",
        "notes": [],
    }

    if request_class == "capability_query":
        response["capability_scope"] = {
            "source": "docs/governance/MACHINE_CAPABILITIES_SUMMARY.md",
            "summary": short_text(CAPABILITIES_PATH),
        }
    if request_class == "policy_reference_query":
        response["policy_basis"] = {
            "source": "docs/governance/POLICY_DIGEST.md",
            "summary": short_text(POLICY_DIGEST_PATH),
        }
    if request_class == "next_step_query":
        response["notes"].append(f"next_step_source={NEXT_STEP_PATH.as_posix()}")
    if request_class in {"authority_query", "admission_query", "blocker_query"}:
        response["escalation_requirement"] = bool(one_screen.get("operator_action_required"))
    return response


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Operator query command surface over governance baseline.")
    parser.add_argument("--query", required=True, help="Raw operator query text.")
    parser.add_argument("--json-only", action="store_true", help="Print only response payload.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not ONE_SCREEN_PATH.exists():
        raise SystemExit("missing runtime one-screen status; run repo_control_center first")
    one_screen = load_json(ONE_SCREEN_PATH)
    request_class = route_request(args.query)
    response = build_response(request_class, one_screen)
    envelope = {
        "run_at": utc_now(),
        "query": args.query,
        "response": response,
    }
    print(json.dumps(envelope if not args.json_only else response, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
