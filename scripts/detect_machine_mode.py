#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = REPO_ROOT / "runtime" / "repo_control_center"
DETECTION_CONTRACT_PATH = REPO_ROOT / "workspace_config" / "creator_mode_detection_contract.json"
FEDERATION_CONTRACT_PATH = REPO_ROOT / "workspace_config" / "federation_mode_contract.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def safe_read_marker(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def evaluate_creator_authority(contract: dict[str, Any]) -> dict[str, Any]:
    env_var_name = str(contract.get("env_var_name", "CVVCODEX_CREATOR_AUTHORITY_DIR"))
    marker_filename = str(contract.get("marker_filename", "creator_authority.json"))
    required_fields = contract.get("required_marker_fields", {})

    env_value = os.getenv(env_var_name)
    authority_dir_exists = False
    marker_exists = False
    marker_valid = False
    marker_fields_match = False
    detection_state = "env_var_missing"

    if env_value:
        authority_dir = Path(env_value)
        authority_dir_exists = authority_dir.exists() and authority_dir.is_dir()
        if authority_dir_exists:
            marker_path = authority_dir / marker_filename
            marker_exists = marker_path.exists() and marker_path.is_file()
            if marker_exists:
                marker_data = safe_read_marker(marker_path)
                if marker_data is not None:
                    marker_valid = True
                    marker_fields_match = all(marker_data.get(k) == v for k, v in required_fields.items())
                    detection_state = "creator_authority_present" if marker_fields_match else "marker_invalid"
                else:
                    detection_state = "marker_invalid"
            else:
                detection_state = "marker_missing"
        else:
            detection_state = "authority_dir_missing"

    authority_present = detection_state == "creator_authority_present"
    return {
        "env_var_name": env_var_name,
        "marker_filename": marker_filename,
        "required_marker_fields": required_fields,
        "env_var_set": bool(env_value),
        "authority_dir_exists": authority_dir_exists,
        "marker_exists": marker_exists,
        "marker_valid": marker_valid,
        "marker_fields_match": marker_fields_match,
        "authority_present": authority_present,
        "detection_state": detection_state,
    }


def resolve_mode(*, authority_present: bool, intent: str) -> tuple[str, list[str]]:
    warnings: list[str] = []
    if intent == "helper":
        return "helper", warnings
    if intent == "creator":
        if authority_present:
            return "creator", warnings
        warnings.append("creator intent requested but authority absent; fallback to helper")
        return "helper", warnings
    if intent == "integration":
        if authority_present:
            return "integration", warnings
        warnings.append("integration intent requested but authority absent; fallback to helper")
        return "helper", warnings

    # auto
    if authority_present:
        return "creator", warnings
    return "helper", warnings


def load_mode_contract() -> dict[str, Any]:
    if FEDERATION_CONTRACT_PATH.exists():
        return load_json(FEDERATION_CONTRACT_PATH)
    return {
        "schema_version": "fallback",
        "supported_modes": ["creator", "helper", "integration"],
        "canonical_acceptance_mode": "creator_only",
        "creator_mode": {"allowed_operations": [], "forbidden_operations": []},
        "helper_mode": {"allowed_operations": [], "forbidden_operations": []},
        "integration_mode": {"allowed_operations": [], "forbidden_operations": []},
    }


def build_mode_payload(intent: str = "auto") -> dict[str, Any]:
    detection_contract = load_json(DETECTION_CONTRACT_PATH)
    federation_contract = load_mode_contract()
    authority = evaluate_creator_authority(detection_contract)
    mode, warnings = resolve_mode(authority_present=authority["authority_present"], intent=intent)

    mode_key = f"{mode}_mode"
    mode_contract = federation_contract.get(mode_key, {})
    payload = {
        "run_id": f"mode-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at": utc_now(),
        "intent": intent,
        "machine_mode": mode,
        "authority": authority,
        "federation_contract": {
            "schema_version": federation_contract.get("schema_version", "unknown"),
            "supported_modes": federation_contract.get("supported_modes", []),
            "canonical_acceptance_mode": federation_contract.get("canonical_acceptance_mode", "creator_only"),
        },
        "operations": {
            "allowed": mode_contract.get("allowed_operations", []),
            "forbidden": mode_contract.get("forbidden_operations", []),
        },
        "warnings": warnings,
        "blockers": [],
        "creator_only_operations": [
            "canonical_acceptance",
            "final_completion_claim",
            "governance_protected_layer_edit",
        ],
    }
    return payload


def report_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Machine Mode Report",
        "",
        f"- run_id: `{payload['run_id']}`",
        f"- generated_at: `{payload['generated_at']}`",
        f"- intent: `{payload['intent']}`",
        f"- machine_mode: `{payload['machine_mode']}`",
        f"- authority_present: `{payload['authority']['authority_present']}`",
        f"- detection_state: `{payload['authority']['detection_state']}`",
        "",
        "## Allowed Operations",
    ]
    for item in payload["operations"]["allowed"] or ["none"]:
        lines.append(f"- {item}")
    lines += [
        "",
        "## Forbidden Operations",
    ]
    for item in payload["operations"]["forbidden"] or ["none"]:
        lines.append(f"- {item}")
    lines += [
        "",
        "## Creator-Only Operations",
    ]
    for item in payload["creator_only_operations"]:
        lines.append(f"- {item}")
    if payload["warnings"]:
        lines += ["", "## Warnings"]
        for item in payload["warnings"]:
            lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def write_outputs(payload: dict[str, Any]) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    (RUNTIME_DIR / "machine_mode_status.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (RUNTIME_DIR / "machine_mode_report.md").write_text(report_markdown(payload), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect machine federation mode from creator authority contract.")
    parser.add_argument("--intent", choices=["auto", "creator", "helper", "integration"], default="auto")
    parser.add_argument("--json-only", action="store_true", help="Print only JSON payload.")
    parser.add_argument("--no-write", action="store_true", help="Do not write runtime report files.")
    parser.add_argument("--strict-intent", action="store_true", help="Return non-zero if requested creator/integration intent is not satisfied.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_mode_payload(intent=args.intent)
    if not args.no_write:
        write_outputs(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.strict_intent and args.intent in {"creator", "integration"} and payload["machine_mode"] != args.intent:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

