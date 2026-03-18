#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "runtime" / "repo_control_center" / "validation" / "sovereign_claim_denial.json"

SOVEREIGN_ONLY_CLAIMS = {
    "sovereign_acceptance_claim",
    "sovereign_transition_claim",
    "sovereign_rank_assertion",
}

PRIMARCH_ALLOWED = {
    "denial_as_expected_claim",
    "primarch_reintegration_claim",
    "bounded_acceptance_recommendation",
}

ASTARTES_ALLOWED = {
    "denial_as_expected_claim",
    "bounded_review_claim",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def evaluate_claim(
    claim_class: str,
    detected_rank: str,
    canonical_root_valid: bool,
    signature_status: str,
    issuer_identity_status: str,
    signature_assurance: str,
    warrant_status: str,
    charter_status: str,
) -> tuple[bool, str, str]:
    claim = claim_class.strip()
    rank = detected_rank.strip().upper()

    if not canonical_root_valid:
        return False, "canonical_root_invalid", "HARD_FAIL"
    if signature_status != "valid":
        return False, "signature_invalid", "HARD_FAIL"
    if issuer_identity_status not in {"verified", "trusted"}:
        return False, "issuer_identity_not_verified", "HARD_FAIL"
    if signature_assurance not in {"structurally_bound", "cryptographically_bound"}:
        return False, "signature_assurance_insufficient", "SOFT_FAIL"

    if claim in SOVEREIGN_ONLY_CLAIMS and rank != "EMPEROR":
        return False, f"claim_requires_emperor_rank:{claim}", "HARD_FAIL"

    if rank == "EMPEROR":
        if claim == "sovereign_transition_claim" and warrant_status not in {"valid", "not_required"}:
            return False, "warrant_invalid_for_transition", "HARD_FAIL"
        if claim == "sovereign_transition_claim" and charter_status not in {"valid", "not_required"}:
            return False, "charter_invalid_for_transition", "HARD_FAIL"
        return True, "", "INFO"

    if rank == "PRIMARCH":
        if claim not in PRIMARCH_ALLOWED:
            return False, f"claim_not_allowed_for_primarch:{claim}", "SOFT_FAIL"
        if warrant_status not in {"valid", "not_required"}:
            return False, "warrant_invalid_for_primarch_claim", "SOFT_FAIL"
        return True, "", "INFO"

    if claim not in ASTARTES_ALLOWED:
        return False, f"claim_not_allowed_for_astartes:{claim}", "SOFT_FAIL"
    if warrant_status not in {"valid", "not_required"}:
        return False, "warrant_invalid_for_astartes_claim", "SOFT_FAIL"
    return True, "", "INFO"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate sovereign claim denial/allow result from rank and assurance inputs.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT.relative_to(ROOT)), help="Output path for JSON report.")
    parser.add_argument("--json-only", action="store_true", help="Print JSON only.")
    parser.add_argument("--no-write", action="store_true", help="Do not write output file.")
    parser.add_argument("--detected-rank", required=True, help="Detected node rank (EMPEROR|PRIMARCH|ASTARTES).")
    parser.add_argument("--canonical-root-valid", default="true", help="Whether canonical root context is valid.")
    parser.add_argument("--context-surface", default="local_runtime", help="Execution context surface.")
    parser.add_argument("--signature-status", default="valid", help="Signature status.")
    parser.add_argument("--issuer-identity-status", default="verified", help="Issuer identity status.")
    parser.add_argument("--signature-assurance", default="structurally_bound", help="Signature assurance level.")
    parser.add_argument("--warrant-status", default="not_required", help="Warrant status.")
    parser.add_argument("--charter-status", default="not_required", help="Charter status.")
    parser.add_argument("--claim-class", action="append", required=True, help="Claim class to evaluate (repeatable).")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out = Path(args.output)
    if not out.is_absolute():
        out = (ROOT / out).resolve()

    detected_rank = args.detected_rank.strip().upper()
    canonical_root_valid = parse_bool(args.canonical_root_valid)
    signature_status = args.signature_status.strip().lower()
    issuer_identity_status = args.issuer_identity_status.strip().lower()
    signature_assurance = args.signature_assurance.strip().lower()
    warrant_status = args.warrant_status.strip().lower()
    charter_status = args.charter_status.strip().lower()

    claim_results: list[dict[str, Any]] = []
    any_denied = False
    top_severity = "INFO"
    top_reason = ""

    severity_order = {"INFO": 0, "SOFT_FAIL": 1, "HARD_FAIL": 2}

    for claim in args.claim_class:
        allowed, reason, severity = evaluate_claim(
            claim_class=claim,
            detected_rank=detected_rank,
            canonical_root_valid=canonical_root_valid,
            signature_status=signature_status,
            issuer_identity_status=issuer_identity_status,
            signature_assurance=signature_assurance,
            warrant_status=warrant_status,
            charter_status=charter_status,
        )
        denied = not allowed
        if denied:
            any_denied = True
        if severity_order[severity] > severity_order[top_severity]:
            top_severity = severity
            top_reason = reason
        elif not top_reason and reason:
            top_reason = reason

        claim_results.append(
            {
                "claim_class": claim,
                "allowed": allowed,
                "denied": denied,
                "claim_severity": severity,
                "denial_reason": reason,
            }
        )

    overall_verdict = "DENY" if any_denied else "ALLOW"
    result: dict[str, Any] = {
        "run_id": f"claim-denial-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at": now_utc(),
        "detected_rank": detected_rank,
        "canonical_root_valid": canonical_root_valid,
        "context_surface": args.context_surface,
        "signature_status": signature_status,
        "issuer_identity_status": issuer_identity_status,
        "signature_assurance": signature_assurance,
        "warrant_status": warrant_status,
        "charter_status": charter_status,
        "claim_inputs": args.claim_class,
        "claim_results": claim_results,
        "claim_allowed": not any_denied,
        "claim_denied": any_denied,
        "denial_reason": top_reason if any_denied else "",
        "claim_severity": top_severity if any_denied else "INFO",
        "overall_verdict": overall_verdict,
        "notes": [],
    }

    if not args.no_write:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if any_denied and top_severity == "HARD_FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
