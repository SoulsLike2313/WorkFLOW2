#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = REPO_ROOT / "runtime" / "repo_control_center"
FEDERATION_CONTRACT_PATH = REPO_ROOT / "workspace_config" / "federation_mode_contract.json"
RANK_DETECT_SCRIPT = REPO_ROOT / "scripts" / "validation" / "detect_node_rank.py"
LEGACY_DETECTION_CONTRACT_PATH = REPO_ROOT / "workspace_config" / "creator_mode_detection_contract.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def safe_read_marker(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def evaluate_legacy_creator_authority(contract: dict[str, Any]) -> dict[str, Any]:
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
        "classification": "legacy_compatibility_non_load_bearing",
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


def load_mode_contract() -> dict[str, Any]:
    if FEDERATION_CONTRACT_PATH.exists():
        return load_json(FEDERATION_CONTRACT_PATH)
    return {
        "schema_version": "2.0.0-fallback",
        "mode_derivation": "rank_model_v2",
        "supported_modes": ["emperor", "helper"],
        "helper_tiers": ["high", "low"],
        "canonical_acceptance_mode": "emperor_only",
        "rank_to_mode_map": {
            "EMPEROR": {"machine_mode": "emperor", "helper_tier": None},
            "PRIMARCH": {"machine_mode": "helper", "helper_tier": "high"},
            "ASTARTES": {"machine_mode": "helper", "helper_tier": "low"},
        },
        "integration_posture_overlay": {
            "authority_effect": "none",
            "allowed_for_modes": ["emperor", "helper"],
            "additional_allowed_operations": [],
            "forbidden_operations": [],
        },
        "emperor_mode": {"allowed_operations": [], "forbidden_operations": []},
        "helper_mode_high": {"allowed_operations": [], "forbidden_operations": []},
        "helper_mode_low": {"allowed_operations": [], "forbidden_operations": []},
    }


def load_legacy_detection_contract() -> dict[str, Any]:
    if LEGACY_DETECTION_CONTRACT_PATH.exists():
        return load_json(LEGACY_DETECTION_CONTRACT_PATH)
    return {
        "env_var_name": "CVVCODEX_CREATOR_AUTHORITY_DIR",
        "marker_filename": "creator_authority.json",
        "required_marker_fields": {
            "authority_mode": "creator",
            "profile_version": "v1",
            "machine_role": "canonical_creator_machine",
        },
    }


def run_rank_detection() -> dict[str, Any]:
    proc = subprocess.run(
        [
            sys.executable,
            str(RANK_DETECT_SCRIPT),
            "--json-only",
            "--no-write",
            "--canonical-root-expected",
            str(REPO_ROOT),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return {
            "ok": False,
            "exit_code": proc.returncode,
            "error": "detect_node_rank_nonzero",
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    try:
        payload = json.loads(proc.stdout)
    except Exception as exc:
        return {
            "ok": False,
            "exit_code": proc.returncode,
            "error": f"detect_node_rank_json_parse_error:{exc}",
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    return {"ok": True, "exit_code": 0, "payload": payload}


def derive_base_mode(
    rank: str, contract: dict[str, Any]
) -> tuple[str, str | None, dict[str, Any], list[str], list[str]]:
    warnings: list[str] = []
    blockers: list[str] = []
    rank_map = contract.get("rank_to_mode_map", {})
    mapped = rank_map.get(rank)
    if not isinstance(mapped, dict):
        blockers.append(f"rank_to_mode_map_missing_for_rank:{rank}")
        return "helper", "low", {"machine_mode": "helper", "helper_tier": "low"}, warnings, blockers

    machine_mode = str(mapped.get("machine_mode", "helper")).strip().lower()
    helper_tier = mapped.get("helper_tier")
    if helper_tier is not None:
        helper_tier = str(helper_tier).strip().lower()

    if machine_mode == "emperor" and rank != "EMPEROR":
        blockers.append("invalid_mode_map_emperor_not_emperor_rank")
    if machine_mode == "creator":
        warnings.append("legacy_creator_mode_alias_detected")
        machine_mode = "emperor"
    if machine_mode == "helper" and rank == "PRIMARCH" and helper_tier != "high":
        blockers.append("invalid_mode_map_primarch_not_high_helper")
    if machine_mode == "helper" and rank == "ASTARTES" and helper_tier != "low":
        blockers.append("invalid_mode_map_astartes_not_low_helper")
    if rank == "EMPEROR" and helper_tier is not None:
        warnings.append("emperor_mapping_contains_helper_tier_ignored")
        helper_tier = None

    return machine_mode, helper_tier, mapped, warnings, blockers


def merge_unique(base: list[str], extra: list[str]) -> list[str]:
    seen = set()
    merged: list[str] = []
    for item in base + extra:
        if item not in seen:
            seen.add(item)
            merged.append(item)
    return merged


def resolve_operations(
    machine_mode: str,
    helper_tier: str | None,
    work_posture: str,
    contract: dict[str, Any],
) -> tuple[list[str], list[str], dict[str, Any]]:
    if machine_mode == "emperor":
        base = contract.get("emperor_mode", contract.get("creator_mode", {}))
    elif machine_mode == "creator":
        base = contract.get("creator_mode", contract.get("emperor_mode", {}))
    elif machine_mode == "helper" and helper_tier == "high":
        base = contract.get("helper_mode_high", contract.get("helper_mode", {}))
    else:
        base = contract.get("helper_mode_low", contract.get("helper_mode", {}))

    allowed = list(base.get("allowed_operations", []))
    forbidden = list(base.get("forbidden_operations", []))

    overlay_info = {
        "work_posture": work_posture,
        "applied": False,
        "authority_effect": "none",
        "additional_allowed_operations": [],
        "forbidden_operations": [],
    }

    if work_posture == "integration":
        overlay = contract.get("integration_posture_overlay", {})
        overlay_allowed_for = [str(x).strip().lower() for x in overlay.get("allowed_for_modes", ["creator", "helper"])]
        if machine_mode in overlay_allowed_for:
            overlay_allowed = list(overlay.get("additional_allowed_operations", []))
            overlay_forbidden = list(overlay.get("forbidden_operations", []))
            allowed = merge_unique(allowed, overlay_allowed)
            forbidden = merge_unique(forbidden, overlay_forbidden)
            overlay_info = {
                "work_posture": work_posture,
                "applied": True,
                "authority_effect": str(overlay.get("authority_effect", "none")),
                "additional_allowed_operations": overlay_allowed,
                "forbidden_operations": overlay_forbidden,
            }

    return allowed, forbidden, overlay_info


def build_mode_payload(intent: str = "auto") -> dict[str, Any]:
    federation_contract = load_mode_contract()
    legacy_contract = load_legacy_detection_contract()
    legacy_authority = evaluate_legacy_creator_authority(legacy_contract)
    rank_result = run_rank_detection()

    warnings: list[str] = []
    blockers: list[str] = []
    if not rank_result["ok"]:
        blockers.append(rank_result["error"])
        detected_rank = "UNKNOWN"
        rank_payload = {}
    else:
        rank_payload = rank_result["payload"]
        detected_rank = str(rank_payload.get("detected_rank", "UNKNOWN")).strip().upper()
        if rank_payload.get("verification_verdict") != "PASS":
            blockers.append("rank_detection_verdict_not_pass")

    machine_mode, helper_tier, raw_mapping, mapping_warnings, mapping_blockers = derive_base_mode(
        detected_rank, federation_contract
    )
    warnings.extend(mapping_warnings)
    blockers.extend(mapping_blockers)

    # Integration is posture-only overlay, never a base authority mode.
    if intent == "integration":
        work_posture = "integration"
    elif intent in {"emperor", "creator", "helper"}:
        work_posture = intent
    else:
        work_posture = "standard"

    if intent in {"emperor", "creator"} and machine_mode != "emperor":
        warnings.append("emperor intent requested but rank-derived mode is helper")
    if intent == "helper" and machine_mode == "emperor":
        warnings.append("helper intent requested on emperor-capable node; authority remains emperor")

    allowed_ops, forbidden_ops, posture_overlay = resolve_operations(
        machine_mode=machine_mode,
        helper_tier=helper_tier,
        work_posture=work_posture,
        contract=federation_contract,
    )

    authority_present = machine_mode == "emperor"
    payload = {
        "run_id": f"mode-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at": utc_now(),
        "intent": intent,  # requested posture intent
        "work_posture": work_posture,  # posture only, non-authority
        "machine_mode": machine_mode,  # base authority mode derived from rank
        "helper_tier": helper_tier,
        "detected_rank": detected_rank,
        "authority_source": "rank_model_v2",
        "authority": {
            "source": "rank_model_v2",
            "authority_present": authority_present,
            "full_system_authority": authority_present,
            "detection_state": f"rank_derived:{detected_rank}",
            "env_var_name": None,
            "marker_filename": None,
        },
        "legacy_creator_authority": legacy_authority,
        "rank_detection": {
            "ok": rank_result.get("ok", False),
            "exit_code": rank_result.get("exit_code", 1),
            "verification_verdict": rank_payload.get("verification_verdict", "BLOCKED") if rank_result.get("ok") else "BLOCKED",
            "detected_rank": detected_rank,
            "run_id": rank_payload.get("run_id") if rank_result.get("ok") else None,
            "emperor_status": rank_payload.get("emperor_status") if rank_result.get("ok") else None,
            "throne_breach": rank_payload.get("throne_breach") if rank_result.get("ok") else None,
            "emperor_status_blocked": rank_payload.get("emperor_status_blocked") if rank_result.get("ok") else None,
            "throne_anchor_path": rank_payload.get("throne_anchor_path") if rank_result.get("ok") else None,
            "proof_summary": {
                "repo_copy_status": rank_payload.get("proof_status", {}).get("repo_copy", {}).get("status"),
                "primarch_status": rank_payload.get("proof_status", {}).get("primarch", {}).get("status"),
                "emperor_status": rank_payload.get("proof_status", {}).get("emperor", {}).get("status"),
                "emperor_detection_state": rank_payload.get("proof_status", {}).get("emperor", {}).get("details", {}).get("detection_state"),
                "throne_anchor_path": rank_payload.get("proof_status", {}).get("emperor", {}).get("details", {}).get("authority_anchor_relative_path"),
            } if rank_result.get("ok") else {},
        },
        "rank_to_mode_derivation": {
            "schema_version": federation_contract.get("schema_version", "unknown"),
            "raw_mapping_for_rank": raw_mapping,
            "decisive_rule": "rank_determines_base_machine_mode",
            "no_legacy_creator_backdoor": True,
        },
        "federation_contract": {
            "schema_version": federation_contract.get("schema_version", "unknown"),
            "mode_derivation": federation_contract.get("mode_derivation", "unknown"),
            "supported_modes": federation_contract.get("supported_modes", []),
            "helper_tiers": federation_contract.get("helper_tiers", []),
            "canonical_acceptance_mode": federation_contract.get("canonical_acceptance_mode", "creator_only"),
        },
        "operations": {
            "allowed": allowed_ops,
            "forbidden": forbidden_ops,
            "posture_overlay": posture_overlay,
        },
        "warnings": warnings,
        "blockers": blockers,
        "emperor_only_operations": [
            "canonical_acceptance",
            "final_completion_claim",
            "governance_protected_layer_edit",
        ],
    }
    payload["creator_only_operations"] = list(payload["emperor_only_operations"])
    return payload


def report_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Machine Mode Report",
        "",
        f"- run_id: `{payload['run_id']}`",
        f"- generated_at: `{payload['generated_at']}`",
        f"- intent: `{payload['intent']}`",
        f"- work_posture: `{payload['work_posture']}`",
        f"- detected_rank: `{payload['detected_rank']}`",
        f"- machine_mode: `{payload['machine_mode']}`",
        f"- helper_tier: `{payload.get('helper_tier')}`",
        f"- authority_source: `{payload.get('authority_source')}`",
        f"- authority_present: `{payload['authority'].get('authority_present')}`",
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
        "## Emperor-Only Operations",
    ]
    for item in payload["emperor_only_operations"]:
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
    parser = argparse.ArgumentParser(description="Detect machine mode derived from rank model v2 (integration as posture overlay).")
    parser.add_argument("--intent", choices=["auto", "emperor", "creator", "helper", "integration"], default="auto")
    parser.add_argument("--json-only", action="store_true", help="Print only JSON payload.")
    parser.add_argument("--no-write", action="store_true", help="Do not write runtime report files.")
    parser.add_argument(
        "--strict-intent",
        action="store_true",
        help="Return non-zero when requested creator/helper intent cannot be satisfied by rank-derived base mode.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_mode_payload(intent=args.intent)
    if not args.no_write:
        write_outputs(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.strict_intent and args.intent in {"emperor", "creator"} and payload["machine_mode"] != "emperor":
        return 1
    if args.strict_intent and args.intent == "helper" and payload["machine_mode"] != "helper":
        return 1
    if args.strict_intent and payload["blockers"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
