#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "runtime" / "repo_control_center" / "validation" / "sovereign_claim_denial.json"
SHARED_TAXONOMY_CONTRACT = ROOT / "workspace_config" / "shared_taxonomy_contract.json"
CLAIM_TAXONOMY_CONTRACT = ROOT / "workspace_config" / "claim_taxonomy_contract.json"

DEFAULT_SOVEREIGN_ONLY_CLAIMS = {
    "canonical_acceptance_claim",
    "sovereign_policy_change_claim",
    "emperor_rank_claim",
    "genome_bundle_issuance_claim",
    "local_sovereign_substrate_activation_claim",
    "unrestricted_structural_mutation_claim",
    "constitutional_mutation_claim",
}

DEFAULT_PRIMARCH_ALLOWED = {
    "primarch_rank_claim",
    "denial_as_expected_claim",
    "bounded_engineering_proposal",
    "constitutional_amendment_candidate_claim",
    "constitutional_commentary_claim",
    "execution_report_claim",
}

DEFAULT_ASTARTES_ALLOWED = {
    "denial_as_expected_claim",
    "constitutional_commentary_claim",
    "execution_report_claim",
}

DEFAULT_LEGACY_CLAIM_ALIAS = {
    "sovereign_acceptance_claim": "canonical_acceptance_claim",
    "sovereign_transition_claim": "sovereign_policy_change_claim",
    "sovereign_rank_assertion": "emperor_rank_claim",
    "primarch_status_assertion": "primarch_rank_claim",
    "genome_issuance_claim": "genome_bundle_issuance_claim",
    "emperor_substrate_activation_claim": "local_sovereign_substrate_activation_claim",
    "primarch_reintegration_claim": "bounded_engineering_proposal",
    "bounded_acceptance_recommendation": "bounded_engineering_proposal",
    "bounded_review_claim": "execution_report_claim",
    "constitution_amendment_candidate_claim": "constitutional_amendment_candidate_claim",
    "constitution_commentary_claim": "constitutional_commentary_claim",
    "sovereign_constitutional_mutation_claim": "constitutional_mutation_claim",
}

DEFAULT_ASSURANCE_ORDER = {
    "unsigned": 0,
    "self_asserted": 1,
    "structurally_bound": 2,
    "locally_verifiable": 3,
    "emperor_local_only_verifiable": 4,
    # tolerated legacy synonym
    "cryptographically_bound": 4,
    "unknown": -1,
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _claim_set(values: Any) -> set[str]:
    return {str(x).strip() for x in values if str(x).strip()}


def load_taxonomy() -> dict[str, Any]:
    sovereign = set(DEFAULT_SOVEREIGN_ONLY_CLAIMS)
    primarch = set(DEFAULT_PRIMARCH_ALLOWED)
    astartes = set(DEFAULT_ASTARTES_ALLOWED)
    aliases = dict(DEFAULT_LEGACY_CLAIM_ALIAS)
    assurance_order = dict(DEFAULT_ASSURANCE_ORDER)
    rank_labels = {"EMPEROR", "PRIMARCH", "ASTARTES", "UNKNOWN"}
    source = "defaults_only"

    if SHARED_TAXONOMY_CONTRACT.exists():
        try:
            shared = load_json(SHARED_TAXONOMY_CONTRACT)
            claim_classes = shared.get("claim_classes", {})
            sovereign = _claim_set(claim_classes.get("sovereign_only", sovereign)) or sovereign
            primarch = _claim_set(claim_classes.get("primarch_allowed_non_sovereign", primarch)) or primarch
            astartes = _claim_set(claim_classes.get("astartes_allowed_non_sovereign", astartes)) or astartes
            shared_aliases = {str(k).strip(): str(v).strip() for k, v in shared.get("legacy_aliases_tolerated", {}).items()}
            aliases.update({k: v for k, v in shared_aliases.items() if k and v})
            shared_ranks = {str(x).strip().upper() for x in shared.get("rank_labels", []) if str(x).strip()}
            if shared_ranks:
                rank_labels = shared_ranks
            source = "shared_taxonomy_contract"
        except Exception:
            source = "shared_taxonomy_contract_parse_error_fallback"

    if CLAIM_TAXONOMY_CONTRACT.exists():
        try:
            claim_contract = load_json(CLAIM_TAXONOMY_CONTRACT)
            claim_classes = claim_contract.get("claim_classes", {})
            sovereign = _claim_set(claim_classes.get("sovereign_only", sovereign)) or sovereign
            primarch = _claim_set(claim_classes.get("primarch_allowed", primarch)) or primarch
            astartes = _claim_set(claim_classes.get("astartes_allowed", astartes)) or astartes
            contract_aliases = {
                str(k).strip(): str(v).strip() for k, v in claim_contract.get("legacy_aliases", {}).items()
            }
            aliases.update({k: v for k, v in contract_aliases.items() if k and v})
            assurance_levels = [str(x).strip().lower() for x in claim_contract.get("signature_assurance", {}).get("ordered_levels", [])]
            if assurance_levels:
                assurance_order = {level: idx for idx, level in enumerate(assurance_levels)}
                synonyms = claim_contract.get("signature_assurance", {}).get("tolerated_legacy_synonyms", {})
                for legacy, canonical in synonyms.items():
                    legacy_key = str(legacy).strip().lower()
                    canonical_key = str(canonical).strip().lower()
                    if legacy_key and canonical_key in assurance_order:
                        assurance_order[legacy_key] = assurance_order[canonical_key]
                assurance_order.setdefault("unknown", -1)
            source = "shared_plus_claim_taxonomy_contract"
        except Exception:
            if source == "defaults_only":
                source = "claim_taxonomy_contract_parse_error_fallback"
            else:
                source = "shared_taxonomy_with_claim_parse_error_fallback"

    return {
        "source": source,
        "sovereign_only": sovereign,
        "primarch_allowed": primarch,
        "astartes_allowed": astartes,
        "legacy_alias": aliases,
        "assurance_order": assurance_order,
        "rank_labels": rank_labels,
    }


TAXONOMY = load_taxonomy()
SOVEREIGN_ONLY_CLAIMS = TAXONOMY["sovereign_only"]
PRIMARCH_ALLOWED = TAXONOMY["primarch_allowed"]
ASTARTES_ALLOWED = TAXONOMY["astartes_allowed"]
LEGACY_CLAIM_ALIAS = TAXONOMY["legacy_alias"]
ASSURANCE_ORDER = TAXONOMY["assurance_order"]
RANK_LABELS = TAXONOMY["rank_labels"]
CANONICAL_CLAIMS = SOVEREIGN_ONLY_CLAIMS | PRIMARCH_ALLOWED | ASTARTES_ALLOWED
CANONICAL_CLAIMS_SORTED = sorted(CANONICAL_CLAIMS)


def normalize_claim_class(claim_class: str) -> str:
    claim = claim_class.strip()
    return LEGACY_CLAIM_ALIAS.get(claim, claim)


def assurance_meets(actual: str, minimum: str) -> bool:
    return ASSURANCE_ORDER.get(actual, -1) >= ASSURANCE_ORDER.get(minimum, 999)


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
    claim = normalize_claim_class(claim_class)
    rank = detected_rank.strip().upper()

    if not canonical_root_valid:
        return False, "canonical_root_invalid", "HARD_FAIL"

    if claim == "denial_as_expected_claim":
        return True, "", "INFO"

    if claim not in CANONICAL_CLAIMS:
        return False, f"unknown_claim_class:{claim}", "SOFT_FAIL"

    if claim == "primarch_rank_claim":
        if rank in {"PRIMARCH", "EMPEROR"}:
            return True, "", "INFO"
        return False, "claim_requires_primarch_or_emperor_rank", "HARD_FAIL"

    if signature_status != "valid":
        return False, "signature_invalid", "HARD_FAIL"
    if issuer_identity_status not in {"verified", "trusted"}:
        return False, "issuer_identity_not_verified", "HARD_FAIL"

    if claim in SOVEREIGN_ONLY_CLAIMS and not assurance_meets(signature_assurance, "locally_verifiable"):
        return False, "signature_assurance_insufficient_for_sovereign_claim", "HARD_FAIL"
    if claim == "bounded_engineering_proposal" and not assurance_meets(signature_assurance, "structurally_bound"):
        return False, "signature_assurance_insufficient_for_bounded_engineering", "SOFT_FAIL"
    if claim == "constitutional_amendment_candidate_claim" and not assurance_meets(signature_assurance, "structurally_bound"):
        return False, "signature_assurance_insufficient_for_amendment_candidate", "SOFT_FAIL"
    if claim == "execution_report_claim":
        if signature_assurance in {"unknown", "unsigned"}:
            return False, "signature_assurance_insufficient_for_execution_report", "SOFT_FAIL"

    if claim == "constitutional_mutation_claim" and rank != "EMPEROR":
        return False, "claim_requires_emperor_rank_for_constitutional_mutation", "HARD_FAIL"

    if claim == "genome_bundle_issuance_claim" and rank != "EMPEROR":
        return False, "claim_requires_emperor_rank_for_genome_bundle_issuance", "HARD_FAIL"

    if claim == "local_sovereign_substrate_activation_claim" and rank != "EMPEROR":
        return False, "claim_requires_emperor_rank_for_local_sovereign_substrate_activation", "HARD_FAIL"

    if claim in SOVEREIGN_ONLY_CLAIMS and rank != "EMPEROR":
        return False, f"claim_requires_emperor_rank:{claim}", "HARD_FAIL"

    if rank == "EMPEROR":
        return True, "", "INFO"

    if rank == "PRIMARCH":
        if claim not in PRIMARCH_ALLOWED:
            return False, f"claim_not_allowed_for_primarch:{claim}", "SOFT_FAIL"
        return True, "", "INFO"

    if claim not in ASTARTES_ALLOWED:
        return False, f"claim_not_allowed_for_astartes:{claim}", "SOFT_FAIL"

    if claim == "execution_report_claim":
        if warrant_status != "valid" and charter_status != "valid":
            return False, "warrant_or_charter_required_for_astartes_execution_report", "SOFT_FAIL"
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
    parser.add_argument(
        "--claim-class",
        action="append",
        required=True,
        help=(
            "Claim class to evaluate (repeatable). Canonical classes: "
            + ", ".join(CANONICAL_CLAIMS_SORTED)
            + ". Legacy aliases are accepted and normalized."
        ),
    )
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
        normalized_claim = normalize_claim_class(claim)
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
                "claim_class_input": claim,
                "claim_class_normalized": normalized_claim,
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
        "taxonomy_contract_source": TAXONOMY["source"],
        "shared_taxonomy_contract_loaded": SHARED_TAXONOMY_CONTRACT.exists(),
        "claim_taxonomy_contract_loaded": CLAIM_TAXONOMY_CONTRACT.exists(),
        "rank_labels": sorted(RANK_LABELS),
        "detected_rank": detected_rank,
        "canonical_root_valid": canonical_root_valid,
        "context_surface": args.context_surface,
        "signature_status": signature_status,
        "issuer_identity_status": issuer_identity_status,
        "signature_assurance": signature_assurance,
        "warrant_status": warrant_status,
        "charter_status": charter_status,
        "claim_inputs": args.claim_class,
        "claim_inputs_normalized": [normalize_claim_class(value) for value in args.claim_class],
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
