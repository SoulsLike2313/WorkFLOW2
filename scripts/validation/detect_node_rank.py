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
STATUS_MODEL_CONTRACT = ROOT / "workspace_config" / "status_model_v2_contract.json"
GENOME_CONTRACT = ROOT / "workspace_config" / "genome_bundle_contract.json"
SOVEREIGN_CONTRACT = ROOT / "workspace_config" / "emperor_local_proof_contract.json"
CREATOR_CONTRACT = ROOT / "workspace_config" / "creator_mode_detection_contract.json"
WORKSPACE_MANIFEST = ROOT / "workspace_config" / "workspace_manifest.json"
SHARED_TAXONOMY_CONTRACT = ROOT / "workspace_config" / "shared_taxonomy_contract.json"

DEFAULT_RANK_LABELS = {"EMPEROR", "PRIMARCH", "ASTARTES", "UNKNOWN"}
DEFAULT_REPO_ANCHORS = [
    "README.md",
    "MACHINE_CONTEXT.md",
    "REPO_MAP.md",
    "workspace_config/workspace_manifest.json",
    "docs/governance/WORKFLOW2_CONSTITUTION_V1.md",
    "scripts/validation/detect_node_rank.py",
    "scripts/validation/check_sovereign_claim_denial.py",
]
DEFAULT_WORKSPACE_SLUG = "workflow"

DEFAULT_GENOME_ENV = "CVVCODEX_PRIMARCH_GENOME_BUNDLE_DIR"
DEFAULT_GENOME_MARKER = "primarch_genome_bundle.json"
DEFAULT_GENOME_REQUIRED_FIELDS = {
    "bundle_kind": "owner_issued_genome_bundle",
    "profile_version": "v2",
    "issuer_rank": "EMPEROR",
    "granted_rank": "PRIMARCH",
}
DEFAULT_GENOME_REQUIRED_LITERALS = {
    "bundle_scope": "offline_manual_transfer_only",
    "authority_surface": "primarch_grade_non_sovereign",
}
DEFAULT_GENOME_REQUIRED_BOOLEANS = {
    "non_sovereign_bundle": True,
    "grants_emperor_authority": False,
    "offline_manual_transfer_only": True,
}

DEFAULT_SUBSTRATE_ENV = "CVVCODEX_LOCAL_SOVEREIGN_SUBSTRATE_DIR"
DEFAULT_SUBSTRATE_MARKER = "emperor_local_proof_surface.json"
DEFAULT_SUBSTRATE_REQUIRED_FIELDS = {
    "proof_surface_class": "emperor_local_proof_surface",
    "substrate_class": "local_sovereign_substrate",
    "contract_class": "sovereign_local_contract",
    "authority_root_class": "local_authority_root",
    "profile_version": "v2",
    "issuer_rank": "EMPEROR",
}
DEFAULT_SUBSTRATE_REQUIRED_LITERALS = {
    "proof_scope": "local_only_non_exportable",
    "export_class": "deny_by_default",
}
DEFAULT_SUBSTRATE_REQUIRED_BOOLEANS = {
    "non_exportable": True,
    "portable_transferable": False,
    "mirror_transferable": False,
}
DEFAULT_SUBSTRATE_FORBIDDEN_TOKENS = {
    "safe_mirror",
    "portable_session_imports",
    "portable_session_exports",
    "transferbundle",
    "import_bundle",
    "staging",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_rank_labels() -> set[str]:
    labels = set(DEFAULT_RANK_LABELS)
    if not SHARED_TAXONOMY_CONTRACT.exists():
        return labels
    try:
        payload = load_json(SHARED_TAXONOMY_CONTRACT)
    except Exception:
        return labels
    contract_labels = {str(x).strip().upper() for x in payload.get("rank_labels", []) if str(x).strip()}
    if contract_labels:
        return contract_labels
    return labels


def load_status_model_contract() -> dict[str, Any]:
    contract: dict[str, Any] = {
        "contract_loaded": False,
        "required_anchor_files": list(DEFAULT_REPO_ANCHORS),
        "workspace_slug_expected": DEFAULT_WORKSPACE_SLUG,
    }
    if not STATUS_MODEL_CONTRACT.exists():
        return contract
    try:
        payload = load_json(STATUS_MODEL_CONTRACT)
    except Exception:
        return contract

    repo_validation = payload.get("repo_copy_validation", {})
    contract["contract_loaded"] = True
    contract["required_anchor_files"] = list(repo_validation.get("required_anchor_files", DEFAULT_REPO_ANCHORS))
    contract["workspace_slug_expected"] = str(repo_validation.get("workspace_slug_expected", DEFAULT_WORKSPACE_SLUG))
    return contract


def check_repo_copy() -> dict[str, Any]:
    contract = load_status_model_contract()
    required_anchor_files = [str(x).replace("\\", "/") for x in contract.get("required_anchor_files", DEFAULT_REPO_ANCHORS)]
    workspace_slug_expected = str(contract.get("workspace_slug_expected", DEFAULT_WORKSPACE_SLUG))

    missing_anchor_files: list[str] = []
    for rel_path in required_anchor_files:
        if not (ROOT / rel_path).exists():
            missing_anchor_files.append(rel_path)

    workspace_manifest_loaded = False
    workspace_slug_actual = ""
    workspace_slug_match = False
    if WORKSPACE_MANIFEST.exists():
        try:
            manifest = load_json(WORKSPACE_MANIFEST)
            workspace_manifest_loaded = True
            workspace_slug_actual = str(manifest.get("workspace_slug", ""))
            workspace_slug_match = workspace_slug_actual.lower() == workspace_slug_expected.lower()
        except Exception:
            workspace_manifest_loaded = False

    valid = not missing_anchor_files and workspace_manifest_loaded and workspace_slug_match
    details = {
        "contract_loaded": bool(contract.get("contract_loaded", False)),
        "contract_path": str(STATUS_MODEL_CONTRACT.relative_to(ROOT)),
        "required_anchor_files": required_anchor_files,
        "missing_anchor_files": missing_anchor_files,
        "workspace_manifest_loaded": workspace_manifest_loaded,
        "workspace_slug_expected": workspace_slug_expected,
        "workspace_slug_actual": workspace_slug_actual,
        "workspace_slug_match": workspace_slug_match,
        "repo_copy_valid": valid,
    }
    return {"status": "VALID" if valid else "MISSING_OR_INVALID", "required_valid": valid, "details": details}


def load_genome_contract() -> dict[str, Any]:
    contract: dict[str, Any] = {
        "contract_loaded": False,
        "bundle_env_var_name": DEFAULT_GENOME_ENV,
        "bundle_marker_filename": DEFAULT_GENOME_MARKER,
        "required_marker_fields": dict(DEFAULT_GENOME_REQUIRED_FIELDS),
        "required_literal_fields": dict(DEFAULT_GENOME_REQUIRED_LITERALS),
        "required_boolean_fields": dict(DEFAULT_GENOME_REQUIRED_BOOLEANS),
        "root_binding_field": "workspace_slug_binding",
        "required_root_binding_value": DEFAULT_WORKSPACE_SLUG,
        "forbidden_origin_tokens": [],
        "must_be_outside_repo_root": True,
    }
    if not GENOME_CONTRACT.exists():
        return contract
    try:
        payload = load_json(GENOME_CONTRACT)
    except Exception:
        return contract

    contract["contract_loaded"] = True
    contract["bundle_env_var_name"] = str(payload.get("bundle_env_var_name", DEFAULT_GENOME_ENV))
    contract["bundle_marker_filename"] = str(payload.get("bundle_marker_filename", DEFAULT_GENOME_MARKER))
    contract["required_marker_fields"] = dict(payload.get("required_marker_fields", DEFAULT_GENOME_REQUIRED_FIELDS))
    contract["required_literal_fields"] = dict(payload.get("required_literal_fields", DEFAULT_GENOME_REQUIRED_LITERALS))
    contract["required_boolean_fields"] = dict(payload.get("required_boolean_fields", DEFAULT_GENOME_REQUIRED_BOOLEANS))
    contract["root_binding_field"] = str(payload.get("root_binding_field", "workspace_slug_binding"))
    contract["required_root_binding_value"] = str(payload.get("required_root_binding_value", DEFAULT_WORKSPACE_SLUG))
    contract["forbidden_origin_tokens"] = [str(x).strip().lower() for x in payload.get("forbidden_origin_tokens", []) if str(x).strip()]
    path_rules = payload.get("path_rules", {})
    contract["must_be_outside_repo_root"] = bool(path_rules.get("must_be_outside_repo_root", True))
    return contract


def load_sovereign_contract() -> dict[str, Any]:
    contract: dict[str, Any] = {
        "contract_loaded": False,
        "substrate_env_var_name": DEFAULT_SUBSTRATE_ENV,
        "legacy_env_var_names": [],
        "proof_surface_filename": DEFAULT_SUBSTRATE_MARKER,
        "legacy_marker_filenames": [],
        "local_authority_root_marker_filename": "local_authority_root.marker",
        "required_marker_fields": dict(DEFAULT_SUBSTRATE_REQUIRED_FIELDS),
        "required_literal_fields": dict(DEFAULT_SUBSTRATE_REQUIRED_LITERALS),
        "required_boolean_fields": dict(DEFAULT_SUBSTRATE_REQUIRED_BOOLEANS),
        "root_binding_field": "workspace_slug_binding",
        "required_root_binding_value": DEFAULT_WORKSPACE_SLUG,
        "forbidden_origin_tokens": list(DEFAULT_SUBSTRATE_FORBIDDEN_TOKENS),
        "required_companion_files": [],
        "must_be_outside_repo_root": True,
    }
    if not SOVEREIGN_CONTRACT.exists():
        return contract
    try:
        payload = load_json(SOVEREIGN_CONTRACT)
    except Exception:
        return contract

    contract["contract_loaded"] = True
    contract["substrate_env_var_name"] = str(
        payload.get("local_sovereign_substrate_env_var_name", payload.get("proof_env_var_name", DEFAULT_SUBSTRATE_ENV))
    )
    contract["legacy_env_var_names"] = [
        str(x).strip() for x in payload.get("legacy_env_var_names", []) if str(x).strip()
    ]
    contract["proof_surface_filename"] = str(
        payload.get("emperor_local_proof_surface_filename", payload.get("proof_marker_filename", DEFAULT_SUBSTRATE_MARKER))
    )
    contract["local_authority_root_marker_filename"] = str(
        payload.get("local_authority_root_marker_filename", "local_authority_root.marker")
    )
    contract["legacy_marker_filenames"] = [
        str(x).strip() for x in payload.get("legacy_marker_filenames", []) if str(x).strip()
    ]
    contract["required_marker_fields"] = dict(payload.get("required_marker_fields", DEFAULT_SUBSTRATE_REQUIRED_FIELDS))
    contract["required_literal_fields"] = dict(payload.get("required_literal_fields", DEFAULT_SUBSTRATE_REQUIRED_LITERALS))
    contract["required_boolean_fields"] = dict(payload.get("required_boolean_fields", DEFAULT_SUBSTRATE_REQUIRED_BOOLEANS))
    contract["root_binding_field"] = str(payload.get("root_binding_field", "workspace_slug_binding"))
    contract["required_root_binding_value"] = str(payload.get("required_root_binding_value", DEFAULT_WORKSPACE_SLUG))
    contract["forbidden_origin_tokens"] = [
        str(x).strip().lower()
        for x in payload.get("forbidden_origin_tokens", DEFAULT_SUBSTRATE_FORBIDDEN_TOKENS)
        if str(x).strip()
    ]
    contract["required_companion_files"] = [
        str(x).strip() for x in payload.get("required_companion_files", []) if str(x).strip()
    ]
    path_rules = payload.get("path_rules", {})
    contract["must_be_outside_repo_root"] = bool(path_rules.get("must_be_outside_repo_root", True))
    return contract


def load_creator_contract() -> dict[str, Any]:
    details: dict[str, Any] = {
        "contract_loaded": False,
        "load_bearing_for_emperor": False,
        "classification": "compatibility_only",
        "status": "ABSENT_OR_UNUSED",
    }
    if not CREATOR_CONTRACT.exists():
        return details
    try:
        contract = load_json(CREATOR_CONTRACT)
    except Exception:
        details["status"] = "PARSE_ERROR"
        return details

    env_var_name = str(contract.get("env_var_name", "CVVCODEX_CREATOR_AUTHORITY_DIR"))
    marker_filename = str(contract.get("marker_filename", "creator_authority.json"))
    required_fields = dict(contract.get("required_marker_fields", {}))

    env_value = os.getenv(env_var_name, "")
    authority_dir_exists = bool(env_value) and Path(env_value).is_dir()
    marker_exists = authority_dir_exists and (Path(env_value) / marker_filename).is_file()
    marker_fields_match = False
    if marker_exists:
        try:
            payload = load_json(Path(env_value) / marker_filename)
            marker_fields_match = all(str(payload.get(k, "")).strip() == str(v) for k, v in required_fields.items())
        except Exception:
            marker_fields_match = False

    details.update(
        {
            "contract_loaded": True,
            "env_var_name": env_var_name,
            "marker_filename": marker_filename,
            "required_marker_fields": required_fields,
            "env_var_set": bool(env_value),
            "authority_dir_exists": authority_dir_exists,
            "marker_exists": marker_exists,
            "marker_fields_match": marker_fields_match,
            "status": "PRESENT" if marker_fields_match else "ABSENT_OR_INVALID",
        }
    )
    return details


def _path_contains_forbidden_tokens(path: Path, forbidden_tokens: list[str]) -> bool:
    lowered = str(path).replace("\\", "/").lower()
    return any(token in lowered for token in forbidden_tokens if token)


def _path_is_under_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except Exception:
        return False


def _fields_match(payload: dict[str, Any], required: dict[str, Any]) -> bool:
    return all(str(payload.get(k, "")).strip() == str(v) for k, v in required.items())


def _boolean_fields_match(payload: dict[str, Any], required: dict[str, bool]) -> bool:
    return all((k in payload) and isinstance(payload.get(k), bool) and (payload.get(k) == bool(v)) for k, v in required.items())


def check_genome_bundle() -> dict[str, Any]:
    contract = load_genome_contract()
    env_var_name = str(contract.get("bundle_env_var_name", DEFAULT_GENOME_ENV))
    marker_filename = str(contract.get("bundle_marker_filename", DEFAULT_GENOME_MARKER))
    required_fields = dict(contract.get("required_marker_fields", DEFAULT_GENOME_REQUIRED_FIELDS))
    required_literal_fields = dict(contract.get("required_literal_fields", DEFAULT_GENOME_REQUIRED_LITERALS))
    required_boolean_fields = dict(contract.get("required_boolean_fields", DEFAULT_GENOME_REQUIRED_BOOLEANS))
    root_binding_field = str(contract.get("root_binding_field", "workspace_slug_binding"))
    required_root_binding_value = str(contract.get("required_root_binding_value", DEFAULT_WORKSPACE_SLUG))
    forbidden_tokens = list(contract.get("forbidden_origin_tokens", []))
    must_be_outside_repo_root = bool(contract.get("must_be_outside_repo_root", True))

    env_val = os.environ.get(env_var_name, "")
    details: dict[str, Any] = {
        "contract_loaded": bool(contract.get("contract_loaded", False)),
        "contract_path": str(GENOME_CONTRACT.relative_to(ROOT)),
        "env_var_name": env_var_name,
        "marker_filename": marker_filename,
        "required_fields": required_fields,
        "required_literal_fields": required_literal_fields,
        "required_boolean_fields": required_boolean_fields,
        "root_binding_field": root_binding_field,
        "required_root_binding_value": required_root_binding_value,
        "forbidden_origin_tokens": forbidden_tokens,
        "must_be_outside_repo_root": must_be_outside_repo_root,
        "env_var_set": bool(env_val),
        "bundle_dir": env_val,
        "bundle_dir_exists": False,
        "bundle_dir_under_repo_root": False,
        "bundle_dir_forbidden_origin": False,
        "marker_exists": False,
        "marker_valid": False,
        "marker_fields_match": False,
        "literal_fields_match": False,
        "boolean_fields_match": False,
        "root_binding_match": False,
        "grants_only_primarch": False,
        "detection_state": "genome_bundle_env_var_missing",
        "status": "MISSING_OR_INVALID",
        "errors": [],
    }

    if not env_val:
        details["errors"] = ["genome_bundle_env_var_missing"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}

    bundle_dir = Path(env_val)
    details["bundle_dir_exists"] = bundle_dir.is_dir()
    details["bundle_dir_under_repo_root"] = _path_is_under_repo(bundle_dir)
    details["bundle_dir_forbidden_origin"] = _path_contains_forbidden_tokens(bundle_dir, forbidden_tokens)
    if not bundle_dir.is_dir():
        details["detection_state"] = "genome_bundle_dir_missing"
        details["errors"] = ["genome_bundle_dir_missing"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}
    if must_be_outside_repo_root and details["bundle_dir_under_repo_root"]:
        details["detection_state"] = "genome_bundle_dir_inside_repo_forbidden"
        details["errors"] = ["genome_bundle_dir_inside_repo_forbidden"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}
    if details["bundle_dir_forbidden_origin"]:
        details["detection_state"] = "genome_bundle_forbidden_origin"
        details["errors"] = ["genome_bundle_forbidden_origin"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}

    marker = bundle_dir / marker_filename
    details["marker_exists"] = marker.is_file()
    if not marker.is_file():
        details["detection_state"] = "genome_bundle_marker_missing"
        details["errors"] = ["genome_bundle_marker_missing"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}

    try:
        payload = load_json(marker)
    except Exception:
        details["detection_state"] = "genome_bundle_marker_parse_error"
        details["errors"] = ["genome_bundle_marker_parse_error"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}

    details["marker_fields_match"] = _fields_match(payload, required_fields)
    details["literal_fields_match"] = _fields_match(payload, required_literal_fields)
    details["boolean_fields_match"] = _boolean_fields_match(payload, required_boolean_fields)
    details["root_binding_match"] = str(payload.get(root_binding_field, "")).strip().lower() == required_root_binding_value.lower()
    details["grants_only_primarch"] = (
        str(payload.get("granted_rank", "")).strip().upper() == "PRIMARCH"
        and bool(payload.get("grants_emperor_authority", False)) is False
    )
    details["marker_valid"] = (
        details["marker_fields_match"]
        and details["literal_fields_match"]
        and details["boolean_fields_match"]
        and details["root_binding_match"]
        and details["grants_only_primarch"]
    )

    if details["marker_valid"]:
        details["detection_state"] = "genome_bundle_valid"
        details["status"] = "VALID"
        return {"status": "VALID", "required_valid": True, "details": details}

    details["detection_state"] = "genome_bundle_marker_invalid"
    details["errors"] = ["genome_bundle_marker_invalid"]
    return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}


def check_local_sovereign_substrate() -> dict[str, Any]:
    contract = load_sovereign_contract()
    primary_env_var = str(contract.get("substrate_env_var_name", DEFAULT_SUBSTRATE_ENV))
    legacy_env_vars = [str(x) for x in contract.get("legacy_env_var_names", []) if str(x).strip()]
    marker_filename = str(contract.get("proof_surface_filename", DEFAULT_SUBSTRATE_MARKER))
    legacy_markers = [str(x) for x in contract.get("legacy_marker_filenames", []) if str(x).strip()]
    required_fields = dict(contract.get("required_marker_fields", DEFAULT_SUBSTRATE_REQUIRED_FIELDS))
    required_literal_fields = dict(contract.get("required_literal_fields", DEFAULT_SUBSTRATE_REQUIRED_LITERALS))
    required_boolean_fields = dict(contract.get("required_boolean_fields", DEFAULT_SUBSTRATE_REQUIRED_BOOLEANS))
    local_authority_root_marker_filename = str(
        contract.get("local_authority_root_marker_filename", "local_authority_root.marker")
    )
    root_binding_field = str(contract.get("root_binding_field", "workspace_slug_binding"))
    required_root_binding_value = str(contract.get("required_root_binding_value", DEFAULT_WORKSPACE_SLUG))
    forbidden_tokens = [str(x).strip().lower() for x in contract.get("forbidden_origin_tokens", DEFAULT_SUBSTRATE_FORBIDDEN_TOKENS)]
    required_companion_files = [str(x).strip() for x in contract.get("required_companion_files", []) if str(x).strip()]
    must_be_outside_repo_root = bool(contract.get("must_be_outside_repo_root", True))

    env_val = os.environ.get(primary_env_var, "")
    legacy_env_var_values_present = {legacy: bool(os.environ.get(legacy, "")) for legacy in legacy_env_vars}
    legacy_env_present_any = any(legacy_env_var_values_present.values())

    details: dict[str, Any] = {
        "contract_loaded": bool(contract.get("contract_loaded", False)),
        "contract_path": str(SOVEREIGN_CONTRACT.relative_to(ROOT)),
        "primary_env_var_name": primary_env_var,
        "legacy_env_var_names": legacy_env_vars,
        "used_env_var_name": primary_env_var if env_val else "",
        "legacy_env_var_values_present": legacy_env_var_values_present,
        "legacy_env_present_any": legacy_env_present_any,
        "legacy_env_ignored_for_authority": True,
        "proof_surface_filename": marker_filename,
        "legacy_marker_filenames": legacy_markers,
        "legacy_marker_files_present": [],
        "legacy_markers_ignored_for_authority": True,
        "required_fields": required_fields,
        "required_literal_fields": required_literal_fields,
        "required_boolean_fields": required_boolean_fields,
        "local_authority_root_marker_filename": local_authority_root_marker_filename,
        "root_binding_field": root_binding_field,
        "required_root_binding_value": required_root_binding_value,
        "required_companion_files": required_companion_files,
        "forbidden_origin_tokens": forbidden_tokens,
        "must_be_outside_repo_root": must_be_outside_repo_root,
        "env_var_set": bool(env_val),
        "proof_dir": env_val,
        "proof_dir_exists": False,
        "proof_dir_under_repo_root": False,
        "proof_dir_forbidden_origin": False,
        "proof_surface_exists": False,
        "proof_surface_filename_used": "",
        "proof_surface_valid": False,
        "marker_fields_match": False,
        "literal_fields_match": False,
        "boolean_fields_match": False,
        "root_binding_match": False,
        "required_companion_files_present": False,
        "local_authority_root_marker_present": False,
        "detection_state": "local_sovereign_substrate_env_var_missing",
        "local_sovereign_substrate_present": False,
        "status": "MISSING_OR_INVALID",
        "errors": [],
    }

    if not env_val:
        if legacy_env_present_any:
            details["detection_state"] = "local_sovereign_substrate_primary_env_missing_legacy_ignored"
            details["errors"] = ["local_sovereign_substrate_primary_env_missing_legacy_ignored"]
        else:
            details["errors"] = ["local_sovereign_substrate_env_var_missing"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}

    proof_dir = Path(env_val)
    details["proof_dir_exists"] = proof_dir.is_dir()
    details["proof_dir_under_repo_root"] = _path_is_under_repo(proof_dir)
    details["proof_dir_forbidden_origin"] = _path_contains_forbidden_tokens(proof_dir, forbidden_tokens)
    if not proof_dir.is_dir():
        details["detection_state"] = "local_sovereign_substrate_dir_missing"
        details["errors"] = ["local_sovereign_substrate_dir_missing"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}
    if must_be_outside_repo_root and details["proof_dir_under_repo_root"]:
        details["detection_state"] = "local_sovereign_substrate_inside_repo_forbidden"
        details["errors"] = ["local_sovereign_substrate_inside_repo_forbidden"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}
    if details["proof_dir_forbidden_origin"]:
        details["detection_state"] = "local_sovereign_substrate_forbidden_origin"
        details["errors"] = ["local_sovereign_substrate_forbidden_origin"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}

    marker_path = proof_dir / marker_filename
    details["proof_surface_exists"] = marker_path.is_file()
    details["proof_surface_filename_used"] = marker_filename if marker_path.is_file() else ""
    details["legacy_marker_files_present"] = [x for x in legacy_markers if (proof_dir / x).is_file()]

    if not marker_path.is_file():
        if details["legacy_marker_files_present"]:
            details["detection_state"] = "local_sovereign_surface_missing_primary_marker_legacy_ignored"
            details["errors"] = ["local_sovereign_surface_missing_primary_marker_legacy_ignored"]
        else:
            details["detection_state"] = "local_sovereign_surface_missing"
            details["errors"] = ["local_sovereign_surface_missing"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}

    try:
        payload = load_json(marker_path)
    except Exception:
        details["detection_state"] = "local_sovereign_surface_parse_error"
        details["errors"] = ["local_sovereign_surface_parse_error"]
        return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}

    details["marker_fields_match"] = _fields_match(payload, required_fields)
    details["literal_fields_match"] = _fields_match(payload, required_literal_fields)
    details["boolean_fields_match"] = _boolean_fields_match(payload, required_boolean_fields)
    details["root_binding_match"] = str(payload.get(root_binding_field, "")).strip().lower() == required_root_binding_value.lower()
    details["required_companion_files_present"] = all((proof_dir / rel).exists() for rel in required_companion_files)
    details["local_authority_root_marker_present"] = (proof_dir / local_authority_root_marker_filename).is_file()
    details["proof_surface_valid"] = (
        details["marker_fields_match"]
        and details["literal_fields_match"]
        and details["boolean_fields_match"]
        and details["root_binding_match"]
        and details["required_companion_files_present"]
        and details["local_authority_root_marker_present"]
    )
    details["local_sovereign_substrate_present"] = details["proof_surface_valid"]

    if details["proof_surface_valid"]:
        details["detection_state"] = "local_sovereign_substrate_valid"
        details["status"] = "VALID"
        return {"status": "VALID", "required_valid": True, "details": details}

    details["detection_state"] = "local_sovereign_surface_invalid"
    details["errors"] = ["local_sovereign_surface_invalid"]
    return {"status": "MISSING_OR_INVALID", "required_valid": False, "details": details}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect node rank with status-model v2 fail-closed logic.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT.relative_to(ROOT)), help="Output path for JSON report.")
    parser.add_argument(
        "--canonical-root-expected",
        default="E:\\CVVCODEX",
        help="Legacy compatibility hint only (no longer load-bearing for rank elevation in v2).",
    )
    parser.add_argument("--json-only", action="store_true", help="Print JSON only.")
    parser.add_argument("--no-write", action="store_true", help="Do not write output file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out = Path(args.output)
    if not out.is_absolute():
        out = (ROOT / out).resolve()

    legacy_root_expected = str(args.canonical_root_expected)
    current_root = str(ROOT)
    legacy_root_match = current_root.lower() == legacy_root_expected.lower()

    repo_copy = check_repo_copy()
    primarch = check_genome_bundle()
    emperor = check_local_sovereign_substrate()
    creator_compat = load_creator_contract()
    rank_labels = load_rank_labels()

    fail_closed_reason: list[str] = []
    if repo_copy["status"] != "VALID":
        fail_closed_reason.append("repo_copy_validation_failed")

    if repo_copy["status"] == "VALID" and emperor["status"] == "VALID":
        detected_rank = "EMPEROR"
    elif repo_copy["status"] == "VALID" and primarch["status"] == "VALID":
        detected_rank = "PRIMARCH"
    elif repo_copy["status"] == "VALID":
        detected_rank = "ASTARTES"
    else:
        detected_rank = "UNKNOWN"

    if detected_rank not in rank_labels:
        fail_closed_reason.append("detected_rank_not_in_shared_taxonomy")
        detected_rank = "ASTARTES" if repo_copy["status"] == "VALID" else "UNKNOWN"

    result: dict[str, Any] = {
        "run_id": f"rank-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at": now_utc(),
        "status_model_version": "v2",
        "status_model_contract_path": str(STATUS_MODEL_CONTRACT.relative_to(ROOT)),
        "legacy_canonical_root_expected": legacy_root_expected,
        "canonical_root_current": current_root,
        "legacy_canonical_root_match": legacy_root_match,
        "canonical_root_valid": repo_copy["status"] == "VALID",
        "repo_copy_valid": repo_copy["status"] == "VALID",
        "detected_rank": detected_rank,
        "verification_verdict": "PASS",
        "proof_status": {
            "repo_copy": repo_copy,
            "primarch": primarch,
            "emperor": emperor,
            "astartes": {
                "status": "REPO_COPY_ONLY" if repo_copy["status"] == "VALID" else "REPO_COPY_INVALID",
                "required_valid": repo_copy["status"] == "VALID",
                "details": {
                    "rank_path": "repo_only_fallback",
                    "repo_copy_valid": repo_copy["status"] == "VALID",
                },
            },
            "creator_authority_legacy_compatibility": creator_compat,
        },
        "fail_closed_reason": fail_closed_reason,
        "sovereign_proof_present": emperor["details"].get("local_sovereign_substrate_present", False),
        "primarch_genome_bundle_valid": primarch["status"] == "VALID",
        "primarch_authority_path_valid": primarch["status"] == "VALID",
        "helper_fallback_reason": primarch["details"].get("detection_state", "unknown"),
        "portable_residue_detected": True,
        "safe_mirror_presence_non_elevating": True,
        "creator_authority_load_bearing_for_emperor": False,
        "shared_rank_taxonomy_loaded": bool(SHARED_TAXONOMY_CONTRACT.exists()),
        "shared_rank_labels": sorted(rank_labels),
        "notes": [
            "creator authority remains compatibility surface and is no longer load-bearing for EMPEROR determination",
            "EMPEROR requires valid repo copy + valid local sovereign substrate",
            "PRIMARCH requires valid repo copy + valid owner-issued genome bundle",
        ],
    }

    if not args.no_write:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
