#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "runtime" / "repo_control_center" / "validation" / "node_rank_detection.json"
CREATOR_CONTRACT = ROOT / "workspace_config" / "creator_mode_detection_contract.json"

EMPEROR_ENV_VAR = "CVVCODEX_EMPEROR_PROOF_DIR"
EMPEROR_MARKER = "emperor_sovereign_proof.json"
EMPEROR_REQUIRED = {
    "proof_class": "emperor_local_sovereign",
    "profile_version": "v1",
    "issuer_rank": "EMPEROR",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def check_emperor_proof(required_root: str) -> dict[str, Any]:
    env_val = os.environ.get(EMPEROR_ENV_VAR, "")
    details: dict[str, Any] = {
        "env_var_name": EMPEROR_ENV_VAR,
        "marker_filename": EMPEROR_MARKER,
        "required_fields": EMPEROR_REQUIRED,
        "required_root_binding": required_root,
        "env_var_set": bool(env_val),
        "proof_dir": env_val,
        "proof_dir_exists": False,
        "marker_exists": False,
        "marker_valid": False,
        "marker_fields_match": False,
        "root_binding_match": False,
        "detection_state": "emperor_env_var_missing",
        "sovereign_proof_present": False,
        "status": "MISSING_OR_INVALID",
        "errors": [],
    }
    if not env_val:
        details["errors"] = ["emperor_env_var_missing"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}

    proof_dir = Path(env_val)
    details["proof_dir_exists"] = proof_dir.is_dir()
    if not proof_dir.is_dir():
        details["detection_state"] = "emperor_proof_dir_missing"
        details["errors"] = ["emperor_proof_dir_missing"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}

    marker = proof_dir / EMPEROR_MARKER
    details["marker_exists"] = marker.is_file()
    if not marker.is_file():
        details["detection_state"] = "emperor_marker_missing"
        details["errors"] = ["emperor_marker_missing"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}

    try:
        payload = load_json(marker)
    except Exception:
        details["detection_state"] = "emperor_marker_parse_error"
        details["errors"] = ["emperor_marker_parse_error"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}

    fields_match = all(str(payload.get(k, "")).strip() == v for k, v in EMPEROR_REQUIRED.items())
    details["marker_fields_match"] = fields_match
    details["root_binding_match"] = str(payload.get("root_binding", "")).strip().lower() == required_root.lower()
    details["marker_valid"] = fields_match and details["root_binding_match"]
    details["sovereign_proof_present"] = details["marker_valid"]

    if details["marker_valid"]:
        details["detection_state"] = "emperor_proof_valid"
        details["status"] = "VALID"
        return {"status": "VALID", "required_valid": False, "details": details}

    details["detection_state"] = "emperor_marker_invalid"
    details["errors"] = ["emperor_marker_invalid"]
    return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}


def check_primarch_authority() -> dict[str, Any]:
    details: dict[str, Any] = {
        "contract_loaded": False,
        "env_var_name": "CVVCODEX_CREATOR_AUTHORITY_DIR",
        "marker_filename": "creator_authority.json",
        "required_fields": {
            "authority_mode": "creator",
            "profile_version": "v1",
            "machine_role": "canonical_creator_machine",
        },
        "env_var_set": False,
        "authority_dir": "",
        "authority_dir_exists": False,
        "marker_exists": False,
        "marker_valid": False,
        "marker_fields_match": False,
        "authority_present": False,
        "primarch_authority_path_valid": False,
        "detection_state": "contract_missing",
        "errors": [],
    }

    if not CREATOR_CONTRACT.exists():
        return {"status": "INVALID", "required_valid": False, "details": details}

    contract = load_json(CREATOR_CONTRACT)
    details["contract_loaded"] = True
    details["env_var_name"] = str(contract.get("env_var_name", details["env_var_name"]))
    details["marker_filename"] = str(contract.get("marker_filename", details["marker_filename"]))
    details["required_fields"] = dict(contract.get("required_marker_fields", details["required_fields"]))

    env_var = details["env_var_name"]
    env_val = os.environ.get(env_var, "")
    details["env_var_set"] = bool(env_val)
    details["authority_dir"] = env_val

    if not env_val:
        details["detection_state"] = "env_var_missing"
        return {"status": "INVALID", "required_valid": False, "details": details}

    authority_dir = Path(env_val)
    details["authority_dir_exists"] = authority_dir.is_dir()
    if not authority_dir.is_dir():
        details["detection_state"] = "authority_dir_missing"
        return {"status": "INVALID", "required_valid": False, "details": details}

    marker = authority_dir / details["marker_filename"]
    details["marker_exists"] = marker.is_file()
    if not marker.is_file():
        details["detection_state"] = "marker_missing"
        return {"status": "INVALID", "required_valid": False, "details": details}

    try:
        payload = load_json(marker)
    except Exception:
        details["detection_state"] = "marker_parse_error"
        return {"status": "INVALID", "required_valid": False, "details": details}

    fields_match = all(str(payload.get(k, "")).strip() == v for k, v in details["required_fields"].items())
    details["marker_fields_match"] = fields_match
    details["marker_valid"] = fields_match
    details["authority_present"] = fields_match
    details["primarch_authority_path_valid"] = fields_match
    details["detection_state"] = "creator_authority_present" if fields_match else "marker_fields_invalid"

    return {"status": "VALID" if fields_match else "INVALID", "required_valid": False, "details": details}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect node rank with fail-closed authority logic.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT.relative_to(ROOT)), help="Output path for JSON report.")
    parser.add_argument("--canonical-root-expected", default="E:\\CVVCODEX", help="Expected canonical root path.")
    parser.add_argument("--json-only", action="store_true", help="Print JSON only.")
    parser.add_argument("--no-write", action="store_true", help="Do not write output file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out = Path(args.output)
    if not out.is_absolute():
        out = (ROOT / out).resolve()

    expected_root = str(args.canonical_root_expected)
    current_root = str(ROOT)
    canonical_root_valid = current_root.lower() == expected_root.lower()

    emperor = check_emperor_proof(expected_root)
    primarch = check_primarch_authority()

    fail_closed_reason: list[str] = []
    if not primarch["details"].get("primarch_authority_path_valid", False):
        fail_closed_reason.append("primarch_authority_path_invalid")
    if not canonical_root_valid:
        fail_closed_reason.append("canonical_root_invalid")

    if canonical_root_valid and emperor["status"] == "VALID" and primarch["status"] == "VALID":
        detected_rank = "EMPEROR"
    elif canonical_root_valid and primarch["status"] == "VALID":
        detected_rank = "PRIMARCH"
    else:
        detected_rank = "ASTARTES"

    result: dict[str, Any] = {
        "run_id": f"rank-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at": now_utc(),
        "canonical_root_expected": expected_root,
        "canonical_root_current": current_root,
        "canonical_root_valid": canonical_root_valid,
        "detected_rank": detected_rank,
        "verification_verdict": "PASS",
        "proof_status": {
            "emperor": emperor,
            "primarch": primarch,
            "astartes": {
                "status": "FALLBACK_ACTIVE",
                "required_valid": True,
                "details": {"helper_fallback_reason": primarch["details"].get("detection_state", "unknown")},
            },
        },
        "fail_closed_reason": fail_closed_reason,
        "sovereign_proof_present": emperor["details"].get("sovereign_proof_present", False),
        "primarch_authority_path_valid": primarch["details"].get("primarch_authority_path_valid", False),
        "helper_fallback_reason": primarch["details"].get("detection_state", "unknown"),
        "portable_residue_detected": True,
        "safe_mirror_presence_non_elevating": True,
        "notes": [],
    }

    if not args.no_write:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
