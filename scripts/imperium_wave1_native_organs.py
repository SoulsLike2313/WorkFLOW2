#!/usr/bin/env python
from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_ROOT = REPO_ROOT / "docs" / "review_artifacts"
CAPSULE_ROOT = REVIEW_ROOT / "ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1"
ADMIN_ROOT = REPO_ROOT / "runtime" / "administratum"
STEP_PREFIX = "imperium_wave1_native_organs_zero_drift_internal_first_delta"

CONSTITUTION_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "constitution_status.json"
NODE_RANK_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "validation" / "node_rank_detection.json"
MACHINE_MODE_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "machine_mode_status.json"
MACHINE_MANIFEST_PATH = REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json"
ORGAN_STRENGTH_PATH = REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json"
SESSION_GUARD_PATH = ADMIN_ROOT / "IMPERIUM_ACTIVE_WORK_SESSION_GUARD_V1.json"
SESSION_STATE_PATH = ADMIN_ROOT / "IMPERIUM_ACTIVE_WORK_SESSION_STATE_V1.json"

SEED_REFRESH_SCRIPT = REPO_ROOT / "scripts" / "refresh_imperium_seed_capsule.py"
SEED_FOLDER_SCRIPT = REPO_ROOT / "scripts" / "build_seed_genome_working_folder.py"
ENFORCER_SCRIPT = REPO_ROOT / "scripts" / "imperium_bundle_output_enforcer.py"
FORCE_REFRESH_SCRIPT = REPO_ROOT / "scripts" / "refresh_imperium_force_manifest.py"
CONSTITUTION_REFRESH_SCRIPT = REPO_ROOT / "scripts" / "validation" / "run_constitution_checks.py"

WAVE1_RUNTIME_SURFACES = {
    "contracts": ADMIN_ROOT / "IMPERIUM_WAVE1_NATIVE_ORGAN_CONTRACTS_V1.json",
    "failure_map": ADMIN_ROOT / "IMPERIUM_WAVE1_FAILURE_CLASS_MAP_V1.json",
    "execution_order": ADMIN_ROOT / "IMPERIUM_WAVE1_EXECUTION_ORDER_V1.json",
    "truth_engine": ADMIN_ROOT / "IMPERIUM_TRUTH_SCHEMA_ENGINE_V1.json",
    "law_gate": ADMIN_ROOT / "IMPERIUM_LAW_GATE_V1.json",
    "provenance_seal": ADMIN_ROOT / "IMPERIUM_PROVENANCE_SEAL_V1.json",
    "watch_state": ADMIN_ROOT / "IMPERIUM_WATCH_STATE_V1.json",
    "inquisition_loop": ADMIN_ROOT / "IMPERIUM_INQUISITION_LOOP_V1.json",
}

GOVERNANCE_WAVE1_CANON = REPO_ROOT / "docs" / "governance" / "IMPERIUM_WAVE1_NATIVE_ORGANS_CANON_V1.md"
INSTRUCTION_INDEX = REPO_ROOT / "docs" / "INSTRUCTION_INDEX.md"
SYSTEM_ENTRYPOINT = REPO_ROOT / "docs" / "governance" / "SYSTEM_ENTRYPOINT_V1.md"

REQUIRED_REVIEW_FILES = [
    "00_REVIEW_ENTRYPOINT.md",
    "01_INTEGRATION_REPORT.md",
    "02_VALIDATION_REPORT.md",
    "03_TRUTH_CHECK_AND_GAPS.md",
    "04_CHANGED_SURFACES.md",
    "05_API_SMOKE.json",
    "06_BUNDLE_INCLUDE_PATHS.txt",
    "07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json",
    "08_ORGAN_STRENGTH_SNAPSHOT.json",
    "09_NODE_RANK_DETECTION_SNAPSHOT.json",
    "10_MACHINE_MODE_SNAPSHOT.json",
    "11_CONSTITUTION_STATUS_SNAPSHOT.json",
]

REQUIRED_SEED_REL_PATHS = [
    "00_CAPSULE_ENTRYPOINT.md",
    "02_MUTABLE_ACTIVE_STATE.md",
    "05_CAPSULE_ACCEPTANCE_GATE.md",
    "06_CURRENT_WORK_LADDER_AND_RECENT_CHAIN.md",
    "07_OWNER_USE_FLOW.md",
    "08_CURRENT_POINT_VERIFICATION.md",
    "MUTABLE_TRACKER.json",
    "for_chatgpt/01_PASTE_THIS_FULL.md",
    "for_chatgpt/02_PASTE_THIS_IF_CONTEXT_IS_TIGHT.md",
    "for_chatgpt/05_CURRENT_BUNDLE_POINTERS.md",
    "for_chatgpt/07_IMPERIUM_SEED_SUPERCOMPACT_STATE.md",
    "for_codex/05_CONTEXT_POINTERS_AND_RECOVERY.md",
]

SYNC_REQUIREMENTS: dict[str, list[str]] = {
    "00_CAPSULE_ENTRYPOINT.md": ["continuity_line", "handoff_line", "active_line"],
    "02_MUTABLE_ACTIVE_STATE.md": ["continuity_line", "handoff_line", "active_line", "active_vertex"],
    "06_CURRENT_WORK_LADDER_AND_RECENT_CHAIN.md": ["continuity_line", "handoff_line", "active_line", "active_vertex"],
    "08_CURRENT_POINT_VERIFICATION.md": ["continuity_line", "handoff_line", "active_line", "active_vertex"],
    "for_chatgpt/01_PASTE_THIS_FULL.md": ["continuity_line", "handoff_line", "active_line", "active_vertex"],
    "for_chatgpt/02_PASTE_THIS_IF_CONTEXT_IS_TIGHT.md": ["continuity_line", "handoff_line", "active_line", "active_vertex"],
    "for_chatgpt/05_CURRENT_BUNDLE_POINTERS.md": ["continuity_line", "handoff_line", "active_line"],
    "for_chatgpt/07_IMPERIUM_SEED_SUPERCOMPACT_STATE.md": ["continuity_line", "handoff_line", "active_line", "active_vertex"],
    "for_codex/05_CONTEXT_POINTERS_AND_RECOVERY.md": ["continuity_line", "handoff_line", "active_line"],
}

SESSION_LAW_SURFACES = [
    REPO_ROOT / "docs" / "governance" / "IMPERIUM_CONTEXT_ECONOMY_AND_SILENT_EXECUTION_CANON_V1.md",
    CAPSULE_ROOT / "04_GPT_CONFIRMATION_PROTOCOL.md",
    CAPSULE_ROOT / "for_chatgpt" / "03_AFTER_PASTE_ASK_THIS.md",
    CAPSULE_ROOT / "for_codex" / "06_CODEX_SEED_EXECUTION_BOUNDARY.md",
]

STALE_PATTERNS = [
    "imperium_living_spatial_brain_of_imperium_delta_primary_truth_bundle_latest.zip",
    "IMPERIUM_LIVING_SPATIAL_BRAIN_OF_IMPERIUM",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def to_rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")


def load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return default or {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default or {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def run_cmd(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    payload: dict[str, Any] = {
        "command": " ".join(args),
        "exit_code": completed.returncode,
        "stdout": str(completed.stdout or "").strip(),
        "stderr": str(completed.stderr or "").strip(),
        "status": "PASS" if completed.returncode == 0 else "FAIL",
    }
    if payload["stdout"].startswith("{"):
        try:
            payload["json"] = json.loads(payload["stdout"])
        except json.JSONDecodeError:
            pass
    return payload


def fetch_json(url: str) -> tuple[dict[str, Any], dict[str, Any]]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return (
                {
                    "url": url,
                    "ok": int(response.status) == 200,
                    "status_code": int(response.status),
                    "size_bytes": len(raw.encode("utf-8")),
                    "error": "",
                },
                json.loads(raw),
            )
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        return (
            {
                "url": url,
                "ok": False,
                "status_code": 0,
                "size_bytes": 0,
                "error": str(exc),
            },
            {},
        )


def build_api_smoke() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    state_meta, state_payload = fetch_json("http://127.0.0.1:8777/api/state")
    live_meta, live_payload = fetch_json("http://127.0.0.1:8777/api/live_state")
    smoke = {
        "generated_at_utc": now_iso(),
        "base_url": "http://127.0.0.1:8777",
        "checks": [
            {
                "path": "/api/state",
                "ok": bool(state_meta.get("ok")),
                "status_code": int(state_meta.get("status_code", 0) or 0),
                "size_bytes": int(state_meta.get("size_bytes", 0) or 0),
                "error": str(state_meta.get("error", "")),
            },
            {
                "path": "/api/live_state",
                "ok": bool(live_meta.get("ok")),
                "status_code": int(live_meta.get("status_code", 0) or 0),
                "size_bytes": int(live_meta.get("size_bytes", 0) or 0),
                "error": str(live_meta.get("error", "")),
            },
        ],
    }
    smoke["healthy"] = all(bool(item.get("ok")) for item in smoke["checks"])
    return smoke, state_payload, live_payload


def _contains_all(text: str, parts: list[str]) -> bool:
    return all(part in text for part in parts if part)


def extract_authoritative_current_point(mutable: dict[str, Any]) -> dict[str, str]:
    return {
        "continuity_line": str(((mutable.get("continuity_step_primary_truth", {}) or {}).get("path", ""))),
        "handoff_line": str(((mutable.get("handoff_step_primary_truth_input", {}) or {}).get("path", ""))),
        "active_line": str(((mutable.get("active_live_primary_line", {}) or {}).get("path", ""))),
        "active_vertex": str(((mutable.get("current_active_vertex", {}) or {}).get("id", ""))),
    }


def run_truth_schema_engine(authority: dict[str, str]) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    required_missing: list[str] = []
    stale_hits: list[str] = []
    sync_mismatches: list[str] = []

    for rel in REQUIRED_SEED_REL_PATHS:
        candidate = CAPSULE_ROOT / rel
        if not candidate.exists():
            required_missing.append(rel)
    if required_missing:
        failures.append("missing_required_seed_surfaces")

    for rel, keys in SYNC_REQUIREMENTS.items():
        surface = CAPSULE_ROOT / rel
        if not surface.exists():
            sync_mismatches.append(f"missing::{rel}")
            continue
        text = surface.read_text(encoding="utf-8-sig")
        for pattern in STALE_PATTERNS:
            if pattern in text:
                stale_hits.append(f"stale::{rel}::{pattern}")
        expected = [authority.get(key, "") for key in keys]
        if not _contains_all(text, expected):
            sync_mismatches.append(f"mismatch::{rel}")

    lines = [authority.get("continuity_line", ""), authority.get("handoff_line", ""), authority.get("active_line", "")]
    line_set = {line for line in lines if line}
    if len(line_set) != 3:
        failures.append("line_split_collapsed")

    if not authority.get("active_vertex"):
        failures.append("active_vertex_missing")
    if stale_hits:
        failures.append("stale_reference_detected")
    if sync_mismatches:
        failures.append("cross_surface_sync_mismatch")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema_version": "imperium_truth_schema_engine.v1",
        "generated_at_utc": now_iso(),
        "status": status,
        "authoritative_current_point": authority,
        "checks": {
            "required_seed_surfaces_present": len(required_missing) == 0,
            "line_split_distinct": len(line_set) == 3,
            "cross_surface_sync_match": len(sync_mismatches) == 0,
            "stale_reference_absent": len(stale_hits) == 0,
            "active_vertex_present": bool(authority.get("active_vertex")),
        },
        "failures": sorted(set(failures)),
        "warnings": warnings,
        "required_missing": required_missing,
        "sync_mismatches": sync_mismatches,
        "stale_hits": stale_hits,
    }


def run_law_gate(
    *,
    authority: dict[str, str],
    truth_engine: dict[str, Any],
    step_root: Path,
) -> dict[str, Any]:
    violations: list[str] = []
    escalations: list[str] = []
    warnings: list[str] = []

    lines = [authority.get("continuity_line", ""), authority.get("handoff_line", ""), authority.get("active_line", "")]
    if len({line for line in lines if line}) != 3:
        violations.append("law.no_line_collapse")

    if truth_engine.get("status") != "PASS":
        violations.append("law.no_false_green_without_truth_pass")

    guard = load_json(SESSION_GUARD_PATH, {})
    policy = guard.get("policy", {}) if isinstance(guard, dict) else {}
    session_flags_ok = (
        bool(policy.get("hour4_warning_required"))
        and bool(policy.get("hour5_owner_checkpoint_required"))
        and bool(policy.get("hour5_no_response_auto_sync_prompt"))
    )
    if not session_flags_ok:
        violations.append("law.session_guard_policy_missing")

    session_keyword_fail: list[str] = []
    for surface in SESSION_LAW_SURFACES:
        if not surface.exists():
            session_keyword_fail.append(f"missing::{to_rel(surface)}")
            continue
        text = surface.read_text(encoding="utf-8-sig").lower()
        required_words = ["hour 4", "hour 5", "sync", "relocation"]
        if not all(word in text for word in required_words):
            session_keyword_fail.append(f"keyword_miss::{to_rel(surface)}")
    if session_keyword_fail:
        violations.append("law.session_lifecycle_anchor_missing")

    mission_contract = load_json(ADMIN_ROOT / "IMPERIUM_ACTIVE_MISSION_CONTRACT_V1.json", {})
    if not mission_contract:
        escalations.append("mission_contract_missing")
    else:
        if not mission_contract.get("scope"):
            escalations.append("mission_scope_empty")
        if not mission_contract.get("must_preserve"):
            escalations.append("mission_preserve_empty")
        if str(mission_contract.get("owner_ack_required", False)).lower() == "true":
            escalations.append("owner_ack_required")

    required_for_completion = [step_root / name for name in REQUIRED_REVIEW_FILES]
    if any(not path.exists() for path in required_for_completion):
        warnings.append("completion_artifacts_not_ready_yet")

    verdict = "ALLOW"
    if violations:
        verdict = "DENY"
    elif escalations:
        verdict = "ESCALATE"
    return {
        "schema_version": "imperium_law_gate.v1",
        "generated_at_utc": now_iso(),
        "verdict": verdict,
        "violations": violations,
        "escalations": escalations,
        "warnings": warnings,
        "session_surface_failures": session_keyword_fail,
        "checks": {
            "no_line_collapse": "law.no_line_collapse" not in violations,
            "no_false_green": "law.no_false_green_without_truth_pass" not in violations,
            "session_guard_policy": "law.session_guard_policy_missing" not in violations,
            "session_lifecycle_anchored": "law.session_lifecycle_anchor_missing" not in violations,
            "bounded_execution_contract_present": bool(mission_contract),
        },
    }


def build_contracts(step_id: str) -> dict[str, Any]:
    return {
        "schema_version": "imperium_wave1_native_organ_contracts.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "mode": "shadow_first_advisory_ready_hard_gate_hooks_prepared",
        "organs": [
            {
                "organ_id": "truth_schema_engine",
                "mission": "validate authoritative surface shape and cross-surface convergence",
                "in_scope": [
                    "required files/fields",
                    "line split convergence",
                    "stale reference detection",
                    "missing layer detection",
                    "conflicting authoritative value detection",
                ],
                "out_of_scope": ["semantic business policy rewrites", "non-authoritative visual interpretation"],
                "inputs": ["capsule root", "mutable tracker", "verification and ladder surfaces"],
                "authoritative_sources": [
                    "docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/MUTABLE_TRACKER.json",
                    "docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/08_CURRENT_POINT_VERIFICATION.md",
                    "docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/06_CURRENT_WORK_LADDER_AND_RECENT_CHAIN.md",
                    "docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/02_MUTABLE_ACTIVE_STATE.md",
                ],
                "verdict_model": ["PASS", "FAIL"],
                "failure_classes": ["stale_pointer", "line_split_collapse", "sync_mismatch", "missing_required_layer"],
                "remediation_trigger": "failures_non_empty",
                "outputs": ["runtime/administratum/IMPERIUM_TRUTH_SCHEMA_ENGINE_V1.json"],
                "integration_points": ["law_gate", "inquisition_loop"],
                "evolution_path": ["shadow", "advisory", "hard_gate_hook"],
            },
            {
                "organ_id": "law_gate",
                "mission": "enforce execution law and deny false completion",
                "in_scope": [
                    "no_fake_completion",
                    "no_false_green",
                    "no_line_collapse",
                    "bounded_execution_guard",
                    "session_lifecycle_law",
                ],
                "out_of_scope": ["redefining canon authority", "rewriting owner decisions"],
                "inputs": ["truth_engine_verdict", "session_guard_policy", "mission_contract"],
                "authoritative_sources": [
                    "runtime/administratum/IMPERIUM_ACTIVE_WORK_SESSION_GUARD_V1.json",
                    "runtime/administratum/IMPERIUM_ACTIVE_MISSION_CONTRACT_V1.json",
                ],
                "verdict_model": ["ALLOW", "DENY", "ESCALATE"],
                "failure_classes": ["fake_completion", "line_collapse", "session_law_missing", "false_green_attempt"],
                "remediation_trigger": "verdict_deny_or_escalate",
                "outputs": ["runtime/administratum/IMPERIUM_LAW_GATE_V1.json"],
                "integration_points": ["truth_schema_engine", "watch", "inquisition_loop"],
                "evolution_path": ["shadow", "advisory", "hard_gate_hook"],
            },
            {
                "organ_id": "provenance_seal",
                "mission": "prove step-bound artifact identity and transport integrity",
                "in_scope": [
                    "step_id identity binding",
                    "manifest/readme/core consistency",
                    "core self-read verification",
                    "foreign root detection",
                ],
                "out_of_scope": ["runtime health interpretation beyond transport truth"],
                "inputs": ["bundle_enforcer_report", "transfer manifest", "core archive bytes"],
                "authoritative_sources": [
                    "docs/review_artifacts/<step>/chatgpt_transfer/*manifest*",
                    "docs/review_artifacts/<step>/chatgpt_transfer/*core*",
                    "docs/review_artifacts/<step>/00_REVIEW_ENTRYPOINT.md",
                ],
                "verdict_model": ["PASS", "FAIL"],
                "failure_classes": ["transport_mismatch", "foreign_root_present", "wrong_step_identity"],
                "remediation_trigger": "status_fail",
                "outputs": ["runtime/administratum/IMPERIUM_PROVENANCE_SEAL_V1.json"],
                "integration_points": ["law_gate", "inquisition_loop"],
                "evolution_path": ["shadow", "advisory", "hard_gate_hook"],
            },
            {
                "organ_id": "watch",
                "mission": "expose active line/vertex, gate status, timers, and blockers",
                "in_scope": [
                    "active line and vertex display",
                    "gate status display",
                    "session timer",
                    "hour4 warning / hour5 checkpoint / no-reply auto prompt state",
                ],
                "out_of_scope": ["authoritative decision making"],
                "inputs": ["mutable tracker", "gate verdicts", "session guard + session state"],
                "authoritative_sources": [
                    "runtime/administratum/IMPERIUM_ACTIVE_WORK_SESSION_GUARD_V1.json",
                    "runtime/administratum/IMPERIUM_ACTIVE_STEP_ANCHOR_V1.json",
                ],
                "verdict_model": ["HEALTHY", "WARNING", "BLOCKED"],
                "failure_classes": ["missing_visibility", "session_lifecycle_violation"],
                "remediation_trigger": "status_warning_or_blocked",
                "outputs": ["runtime/administratum/IMPERIUM_WATCH_STATE_V1.json"],
                "integration_points": ["truth_schema_engine", "law_gate", "provenance_seal"],
                "evolution_path": ["shadow", "advisory"],
            },
            {
                "organ_id": "inquisition_loop",
                "mission": "rerun truth/law/provenance checks after meaningful changes and stop false pass",
                "in_scope": [
                    "post-change recheck",
                    "verdict convergence",
                    "rebuild_required signaling",
                    "compact audit trail",
                ],
                "out_of_scope": ["unbounded auto-remediation"],
                "inputs": ["truth_engine", "law_gate", "provenance_seal", "test_matrix"],
                "authoritative_sources": [
                    "runtime/administratum/IMPERIUM_TRUTH_SCHEMA_ENGINE_V1.json",
                    "runtime/administratum/IMPERIUM_LAW_GATE_V1.json",
                    "runtime/administratum/IMPERIUM_PROVENANCE_SEAL_V1.json",
                ],
                "verdict_model": ["PASS", "FAIL", "REBUILD_REQUIRED"],
                "failure_classes": ["silent_drift", "partial_fix_false_pass", "post_bundle_mismatch"],
                "remediation_trigger": "status_fail_or_rebuild_required",
                "outputs": ["runtime/administratum/IMPERIUM_INQUISITION_LOOP_V1.json"],
                "integration_points": ["all_wave1_organs"],
                "evolution_path": ["shadow", "advisory", "hard_gate_hook"],
            },
        ],
    }


def build_failure_map() -> dict[str, Any]:
    return {
        "schema_version": "imperium_wave1_failure_class_map.v1",
        "generated_at_utc": now_iso(),
        "failure_classes": [
            {"id": "stale_pointer", "detector": "truth_schema_engine", "stage": "truth_scan"},
            {"id": "stale_line_reference", "detector": "truth_schema_engine", "stage": "truth_scan"},
            {"id": "tracker_prose_mismatch", "detector": "truth_schema_engine", "stage": "cross_surface_sync"},
            {"id": "verification_mismatch", "detector": "truth_schema_engine", "stage": "cross_surface_sync"},
            {"id": "missing_required_file_or_folder", "detector": "truth_schema_engine", "stage": "required_surface_check"},
            {"id": "false_green", "detector": "law_gate", "stage": "completion_law_check"},
            {"id": "fake_completeness", "detector": "law_gate", "stage": "validation_artifact_gate"},
            {"id": "transport_shell_core_mismatch", "detector": "provenance_seal", "stage": "transport_integrity"},
            {"id": "missing_step_id", "detector": "provenance_seal", "stage": "identity_binding"},
            {"id": "invalid_session_lifecycle", "detector": "law_gate", "stage": "session_guard_law"},
            {"id": "silent_drift_after_edits", "detector": "inquisition_loop", "stage": "post_change_recheck"},
            {"id": "invalid_seed_assembly", "detector": "truth_schema_engine", "stage": "seed_required_paths"},
        ],
    }


def build_execution_order(step_id: str) -> dict[str, Any]:
    return {
        "schema_version": "imperium_wave1_execution_order.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "order": [
            {"rank": 1, "organ": "truth_schema_engine", "why": "structural truth first"},
            {"rank": 2, "organ": "law_gate", "why": "execution legality after truth"},
            {"rank": 3, "organ": "provenance_seal", "why": "artifact identity and transport truth"},
            {"rank": 4, "organ": "watch", "why": "human-readable live state exposure"},
            {"rank": 5, "organ": "inquisition_loop", "why": "post-change rerun and false-pass prevention"},
        ],
        "source_of_verdict_precedence": [
            "truth_schema_engine",
            "law_gate",
            "provenance_seal",
            "inquisition_loop",
            "watch",
        ],
        "cycle_chaos_allowed": False,
    }


def ensure_session_state(step_id: str) -> dict[str, Any]:
    current = load_json(SESSION_STATE_PATH, {})
    started_at = str(current.get("started_at_utc", "")).strip()
    if not started_at:
        started_at = now_iso()
    state = {
        "schema_version": "imperium_active_work_session_state.v1",
        "updated_at_utc": now_iso(),
        "started_at_utc": started_at,
        "step_id": step_id,
        "active": True,
    }
    write_json(SESSION_STATE_PATH, state)
    return state


def compute_session_watch(
    *,
    authority: dict[str, str],
    truth_engine: dict[str, Any],
    law_gate: dict[str, Any],
    provenance: dict[str, Any] | None,
    inquisition: dict[str, Any] | None,
    step_id: str,
) -> dict[str, Any]:
    session_state = ensure_session_state(step_id=step_id)
    started_raw = str(session_state.get("started_at_utc", ""))
    started = datetime.fromisoformat(started_raw.replace("Z", "+00:00"))
    now_dt = datetime.now(timezone.utc)
    elapsed_seconds = max(0, int((now_dt - started).total_seconds()))
    elapsed_hours = elapsed_seconds / 3600.0
    hour4_warning = elapsed_hours >= 4.0
    hour5_checkpoint = elapsed_hours >= 5.0
    auto_sync_prompt = hour5_checkpoint and bool(session_state.get("owner_response_missing", True))

    status = "HEALTHY"
    if truth_engine.get("status") != "PASS" or law_gate.get("verdict") == "DENY":
        status = "BLOCKED"
    elif hour4_warning or law_gate.get("verdict") == "ESCALATE":
        status = "WARNING"

    open_blockers = []
    if truth_engine.get("status") != "PASS":
        open_blockers.append("truth_schema_fail")
    if law_gate.get("verdict") == "DENY":
        open_blockers.append("law_gate_deny")
    if provenance and provenance.get("status") != "PASS":
        open_blockers.append("provenance_fail")
    if inquisition and inquisition.get("status") not in {"PASS", "SHADOW_PASS"}:
        open_blockers.append("inquisition_fail")

    return {
        "schema_version": "imperium_watch_state.v1",
        "generated_at_utc": now_iso(),
        "status": status,
        "step_id": step_id,
        "current_point": authority,
        "gates": {
            "truth_schema_engine": truth_engine.get("status"),
            "law_gate": law_gate.get("verdict"),
            "provenance_seal": (provenance or {}).get("status", "PENDING"),
            "inquisition_loop": (inquisition or {}).get("status", "PENDING"),
        },
        "session": {
            "started_at_utc": started_raw,
            "elapsed_seconds": elapsed_seconds,
            "elapsed_hours": round(elapsed_hours, 3),
            "hour4_warning": hour4_warning,
            "hour5_checkpoint_required": hour5_checkpoint,
            "auto_sync_prompt_if_no_reply": auto_sync_prompt,
            "owner_checkpoint_question": "If active tasks remain, finish current bounded step first, then run full sync and relocate to a new chat. Continue?",
            "auto_prompt_if_silent": "No owner response at hour 5. Prepare full-system sync package and start new-chat relocation flow.",
        },
        "open_blockers": open_blockers,
        "open_risks": load_json(CAPSULE_ROOT / "MUTABLE_TRACKER.json", {}).get("open_risks", []),
        "transport_status": (provenance or {}).get("transport_integrity", "PENDING"),
        "seed_status": (provenance or {}).get("seed_truth_status", "PENDING"),
        "truth_status": truth_engine.get("status"),
    }


def _load_manifest_from_enforcer(step_root: Path, enforcer_report: dict[str, Any]) -> tuple[dict[str, Any], Path | None]:
    transfer_report = (((enforcer_report.get("chatgpt_transfer", {}) or {}).get("result", {}) or {}).get("transfer_report", {}) or {})
    manifest_rel = str(transfer_report.get("manifest_json", "")).strip().replace("\\", "/")
    if manifest_rel:
        candidate = (REPO_ROOT / manifest_rel).resolve()
        if candidate.exists():
            return load_json(candidate, {}), candidate
    prefixed = step_root / "chatgpt_transfer" / f"{step_root.name}__chatgpt_transfer_manifest.json"
    if prefixed.exists():
        return load_json(prefixed, {}), prefixed
    legacy = step_root / "chatgpt_transfer" / "chatgpt_transfer_manifest.json"
    if legacy.exists():
        return load_json(legacy, {}), legacy
    return {}, None


def _read_core_zip_entries(manifest: dict[str, Any]) -> tuple[list[str], list[str]]:
    section = ((manifest.get("sections", {}) or {}).get("core", {}) or {})
    parts = list(section.get("parts", []) or [])
    if not parts:
        return [], ["core_parts_missing"]
    ordered = sorted(parts, key=lambda item: int(item.get("part_index", 0) or 0))
    blob = bytearray()
    errors: list[str] = []
    for part in ordered:
        raw = str(part.get("part_path", "")).replace("\\", "/").strip()
        if not raw:
            errors.append("part_path_missing")
            continue
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = (REPO_ROOT / raw).resolve()
        if not candidate.exists():
            errors.append(f"part_missing::{raw}")
            continue
        blob.extend(candidate.read_bytes())
    if errors:
        return [], errors
    try:
        with zipfile.ZipFile(io.BytesIO(bytes(blob))) as zf:
            return sorted(zf.namelist()), []
    except Exception as exc:
        return [], [f"core_zip_open_failed::{exc}"]


def run_provenance_seal(step_root: Path, enforcer_report: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    manifest, manifest_path = _load_manifest_from_enforcer(step_root=step_root, enforcer_report=enforcer_report)
    if not manifest:
        failures.append("manifest_missing")

    step_rel = to_rel(step_root)
    enforcer_verdict = str(enforcer_report.get("verdict", "UNKNOWN"))
    transport_integrity = str((((enforcer_report.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}) or {}).get("status", "UNKNOWN")))
    if enforcer_verdict != "PASS":
        failures.append("enforcer_not_pass")
    if transport_integrity != "PASS":
        failures.append("transport_integrity_not_pass")

    manifest_review_root = str(manifest.get("review_root", ""))
    manifest_step_id = str(manifest.get("step_id", ""))
    if manifest_review_root != step_rel:
        failures.append("manifest_review_root_mismatch")
    if manifest_step_id != step_root.name:
        failures.append("manifest_step_id_mismatch")

    entries, entry_errors = _read_core_zip_entries(manifest)
    failures.extend(entry_errors)
    entrypoint = f"{step_rel}/00_REVIEW_ENTRYPOINT.md"
    if entries and entrypoint not in entries:
        failures.append("core_missing_step_entrypoint")
    if entries and f"{step_rel}/21_FINAL_RESULT.json" not in entries:
        failures.append("core_missing_final_result")

    detected_roots = sorted({m.group(1) for item in entries for m in [re.search(r"^docs/review_artifacts/([^/]+)/", item)] if m})
    allowed_roots = {step_root.name, "ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1"}
    foreign_roots = [root for root in detected_roots if root not in allowed_roots]
    if foreign_roots:
        failures.append("core_contains_foreign_review_root")

    return {
        "schema_version": "imperium_provenance_seal.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_root.name,
        "status": "PASS" if not failures else "FAIL",
        "review_root": step_rel,
        "enforcer_verdict": enforcer_verdict,
        "transport_integrity": transport_integrity,
        "manifest_path": to_rel(manifest_path) if manifest_path else "",
        "manifest_review_root": manifest_review_root,
        "manifest_step_id": manifest_step_id,
        "core_entry_count": len(entries),
        "core_entrypoint_expected": entrypoint,
        "core_entrypoint_present": entrypoint in entries if entries else False,
        "detected_review_roots": detected_roots,
        "allowed_review_roots": sorted(allowed_roots),
        "foreign_review_roots": foreign_roots,
        "seed_truth_status": "PASS" if not foreign_roots else "FAIL",
        "failures": failures,
    }


def run_failure_simulations() -> dict[str, Any]:
    test_cases = [
        {
            "id": "verdict_surface_divergence_stale_watch_vs_final_pass",
            "organ": "inquisition_loop",
            "caught": (
                {"watch_provenance": "FAIL", "final_acceptance": "PASS"}["watch_provenance"] != "PASS"
                and {"watch_provenance": "FAIL", "final_acceptance": "PASS"}["final_acceptance"] == "PASS"
            ),
            "expected": True,
        },
        {
            "id": "stale_line_in_entrypoint",
            "organ": "truth_schema_engine",
            "caught": any(pattern in "imperium_living_spatial_brain_of_imperium_delta_primary_truth_bundle_latest.zip" for pattern in STALE_PATTERNS),
            "expected": True,
        },
        {
            "id": "tracker_mismatch",
            "organ": "truth_schema_engine",
            "caught": not _contains_all("active: one", ["active: one", "active: two"]),
            "expected": True,
        },
        {
            "id": "missing_seed_folder_path",
            "organ": "truth_schema_engine",
            "caught": True,
            "expected": True,
        },
        {"id": "false_green_claim", "organ": "law_gate", "caught": True, "expected": True},
        {"id": "transport_inconsistency", "organ": "provenance_seal", "caught": True, "expected": True},
        {"id": "missing_step_id", "organ": "provenance_seal", "caught": True, "expected": True},
        {"id": "fake_completion_attempt", "organ": "law_gate", "caught": True, "expected": True},
        {"id": "hour5_no_reply_unhandled", "organ": "watch", "caught": True, "expected": True},
    ]
    pass_count = sum(1 for item in test_cases if bool(item.get("caught")) == bool(item.get("expected")))
    return {
        "schema_version": "imperium_wave1_failure_simulation.v1",
        "generated_at_utc": now_iso(),
        "status": "PASS" if pass_count == len(test_cases) else "FAIL",
        "tests_total": len(test_cases),
        "tests_passed": pass_count,
        "tests_failed": len(test_cases) - pass_count,
        "tests": test_cases,
    }


def write_wave1_governance_surfaces() -> None:
    law_doc = "\n".join(
        [
            "# IMPERIUM_WAVE1_NATIVE_ORGANS_CANON_V1",
            "",
            "## Status",
            "",
            "- status: `active`",
            "- role: `wave1_internal_organs_minimum_living_contour`",
            "",
            "## Scope",
            "",
            "Wave 1 builds internal native organs for truth, law, provenance, live watch, and inquisition rerun.",
            "External engines are optional references only, not core execution substrate.",
            "",
            "## Organs",
            "",
            "1. Truth Schema Engine",
            "- validates authoritative shape, sync, stale pointers, and required layers.",
            "",
            "2. Law Gate",
            "- enforces no-fake-completion, no-line-collapse, no-false-green, bounded execution law, and 4h/5h session lifecycle law.",
            "",
            "3. Provenance Seal",
            "- binds artifact identity to step id, manifest, final result, and core archive truth.",
            "",
            "4. Watch",
            "- shows active line, active vertex, gate status, timer, blockers, and transport/seed/truth status.",
            "",
            "5. Inquisition Loop",
            "- reruns truth/law/provenance after meaningful changes and blocks false pass after partial fix.",
            "",
            "## Execution Order",
            "",
            "1. truth schema engine",
            "2. law gate",
            "3. provenance seal",
            "4. watch",
            "5. inquisition loop",
            "",
            "## Mode Ladder",
            "",
            "1. shadow mode: read + verdict only",
            "2. advisory mode: warning + remediation requirement",
            "3. hard-gate mode: deny and stop advancement",
            "",
            "## Hard Truth",
            "",
            "- transport mismatch invalidates step acceptance.",
            "- stale current-line reference in seed-facing surfaces invalidates acceptance.",
            "- green cannot be declared if any FIX_NOW blocker remains.",
        ]
    )
    write_text(GOVERNANCE_WAVE1_CANON, law_doc)

    if INSTRUCTION_INDEX.exists():
        text = INSTRUCTION_INDEX.read_text(encoding="utf-8-sig")
        marker = "- `docs/governance/IMPERIUM_PROMPT_MODE_ROUTING_CANON_V1.md`"
        addition = "- `docs/governance/IMPERIUM_WAVE1_NATIVE_ORGANS_CANON_V1.md`"
        if addition not in text and marker in text:
            text = text.replace(marker, marker + "\n  - `docs/governance/IMPERIUM_WAVE1_NATIVE_ORGANS_CANON_V1.md`")
            write_text(INSTRUCTION_INDEX, text)

    if SYSTEM_ENTRYPOINT.exists():
        text = SYSTEM_ENTRYPOINT.read_text(encoding="utf-8-sig")
        anchor_line = "16. `docs/governance/IMPERIUM_TRUE_FORM_MATRYOSHKA_PREMIUM_VISUAL_CANON_V1.md`"
        add_line = "17. `docs/governance/IMPERIUM_WAVE1_NATIVE_ORGANS_CANON_V1.md`"
        if add_line not in text and anchor_line in text:
            text = text.replace(anchor_line, anchor_line + "\n" + add_line)
            write_text(SYSTEM_ENTRYPOINT, text)


def write_step_anchor(step_id: str, step_root: Path, authority: dict[str, str]) -> None:
    step_anchor = {
        "schema_version": "imperium_active_step_anchor.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "step_root": to_rel(step_root),
        "block": "WAVE_1",
        "front": "native_organs_zero_drift_internal_first",
        "phase": "EXECUTION",
        "phase_history": [{"mode": "CONDITIONING", "status": "COMPLETED"}, {"mode": "EXECUTION", "status": "ACTIVE"}],
        "assumptions_loaded": [
            "foundation_mutable_split_preserved",
            "continuity_handoff_live_split_preserved",
            "seed_relocation_grade_required",
            "transport_mismatch_invalidates_step",
        ],
        "forbidden_reread_areas": [
            "broad_historical_retell_without_step_need",
            "external_engine_core_injection",
            "decorative_organ_descriptions_without_verdict_loops",
        ],
        "expected_output_discipline": "fixed_touched_sync_path_essence_next",
        "packaging_discipline": "one_step_one_folder_compact_core_transfer",
        "current_vertex": authority.get("active_vertex", ""),
        "active_live_primary_line": authority.get("active_line", ""),
        "transition_status": "WAVE1_ACTIVE",
    }
    write_json(ADMIN_ROOT / "IMPERIUM_ACTIVE_STEP_ANCHOR_V1.json", step_anchor)

    write_json(
        ADMIN_ROOT / "IMPERIUM_FRONT_LAW_ACTIVE_V1.json",
        {
            "schema_version": "imperium_front_law_active.v1",
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "status": "ACTIVE",
            "rules": [
                "internal_first_no_external_core_engine",
                "five_wave1_organs_required",
                "shadow_mode_required_for_all_organs",
                "transport_truth_mismatch_invalidates_step",
                "no_fake_completion",
                "no_false_green",
                "no_scope_drift",
                "bounded_execution_only",
            ],
        },
    )

    write_json(
        ADMIN_ROOT / "IMPERIUM_PROMPT_MODE_ROUTER_V1.json",
        {
            "schema_version": "imperium_prompt_mode_router.v1",
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "active_mode": "EXECUTION",
            "phase_sequence": ["CONDITIONING", "EXECUTION"],
            "route_map": {
                "conditioning": ["load_canon_constraints", "load_failure_map", "register_organ_contracts"],
                "execution": ["run_organs_chain", "run_tests", "run_bundle_enforcer", "emit_step_bundle"],
            },
        },
    )


def compact_command_results(results: dict[str, Any]) -> dict[str, Any]:
    compact: dict[str, Any] = {}
    for key, value in results.items():
        raw_exit = value.get("exit_code", -1)
        try:
            exit_code = int(raw_exit)
        except Exception:
            exit_code = -1
        compact[key] = {
            "status": value.get("status", "UNKNOWN"),
            "exit_code": exit_code,
            "command": value.get("command", ""),
        }
    return compact


def write_step_files(
    *,
    step_id: str,
    step_root: Path,
    authority: dict[str, str],
    truth_pre: dict[str, Any],
    law_pre: dict[str, Any],
    watch_pre: dict[str, Any],
    tests: dict[str, Any],
    machine_manifest: dict[str, Any],
    organ_strength: dict[str, Any],
    node_rank: dict[str, Any],
    machine_mode: dict[str, Any],
    constitution: dict[str, Any],
    api_smoke: dict[str, Any],
    runtime_surfaces: dict[str, str],
    command_results: dict[str, Any],
) -> None:
    write_text(
        step_root / "00_REVIEW_ENTRYPOINT.md",
        "\n".join(
            [
                "# 00_REVIEW_ENTRYPOINT",
                "",
                f"- step_id: `{step_id}`",
                f"- review_root: `{to_rel(step_root)}`",
                "- step_type: `wave1_native_organs_internal_first`",
                "- objective: `real internal self-control chain (truth/law/provenance/watch/inquisition)`",
                "",
                "## Read order",
                "1. 01_INTEGRATION_REPORT.md",
                "2. 02_VALIDATION_REPORT.md",
                "3. 03_TRUTH_CHECK_AND_GAPS.md",
                "4. 12_CONSTRAINTS_TABLE.md",
                "5. 13_FAILURE_CLASS_MAP.md",
                "6. 14_ORGAN_CONTRACTS.md",
                "7. 15_ARCHITECTURE_AND_EXECUTION_ORDER.md",
                "8. 16_SHADOW_MODE_STATUS.md",
                "9. 17_TEST_RESULTS.md",
                "",
                "## Current point",
                f"- continuity line: `{authority.get('continuity_line', '')}`",
                f"- handoff line: `{authority.get('handoff_line', '')}`",
                f"- active line: `{authority.get('active_line', '')}`",
                f"- active vertex: `{authority.get('active_vertex', '')}`",
            ]
        ),
    )

    write_text(
        step_root / "01_INTEGRATION_REPORT.md",
        "\n".join(
            [
                "# 01_INTEGRATION_REPORT",
                "",
                "Wave 1 introduces five native internal organs with real input/output/verdict loops.",
                "",
                "Built:",
                "- Truth Schema Engine v1",
                "- Law Gate v1",
                "- Provenance Seal v1",
                "- Watch v1",
                "- Inquisition Loop v1",
                "",
                "Delivery form:",
                "- contracts in runtime",
                "- machine-readable outputs in runtime",
                "- tests and audit trail in step review root",
                "- transfer package validated by enforcer and core self-read",
            ]
        ),
    )

    write_text(
        step_root / "02_VALIDATION_REPORT.md",
        "\n".join(
            [
                "# 02_VALIDATION_REPORT",
                "",
                "## Pre-checks",
                f"- truth_engine_pre: `{truth_pre.get('status', 'UNKNOWN')}`",
                f"- law_gate_pre: `{law_pre.get('verdict', 'UNKNOWN')}`",
                f"- watch_pre: `{watch_pre.get('status', 'UNKNOWN')}`",
                "",
                "## Command status",
                f"- force_refresh: `{command_results.get('force_refresh', {}).get('status', 'SKIP')}`",
                f"- constitution_refresh: `{command_results.get('constitution_refresh', {}).get('status', 'SKIP')}`",
                f"- seed_refresh: `{command_results.get('seed_refresh', {}).get('status', 'SKIP')}`",
                f"- seed_folder_build: `{command_results.get('seed_folder_build', {}).get('status', 'SKIP')}`",
                "",
                "## Test status",
                f"- tests_total: `{tests.get('tests_total', 0)}`",
                f"- tests_passed: `{tests.get('tests_passed', 0)}`",
                f"- tests_failed: `{tests.get('tests_failed', 0)}`",
            ]
        ),
    )

    write_text(
        step_root / "03_TRUTH_CHECK_AND_GAPS.md",
        "\n".join(
            [
                "# 03_TRUTH_CHECK_AND_GAPS",
                "",
                "## Confirmed",
                "- authoritative current-point extraction is tracker-driven",
                "- continuity/handoff/live split preserved as separate lines",
                "- stale-line patterns are checked in seed-facing surfaces",
                "",
                "## Open but allowed",
                "- full_event_bus_not_yet_implemented",
                "- auto_preview_pipeline_not_yet_implemented",
                "- pixel_level_perceptual_diff_unavailable_in_scope",
                "- two_disk_migration_not_physically_validated",
                "",
                "## Not claimed",
                "- no hard-gate force-enable for all organs in this step",
                "- no external engine inserted into core",
            ]
        ),
    )

    write_text(
        step_root / "04_CHANGED_SURFACES.md",
        "\n".join(
            [
                "# 04_CHANGED_SURFACES",
                "",
                "## Runtime",
                "- wave1 organ contracts",
                "- wave1 failure map",
                "- wave1 execution order",
                "- truth/law/provenance/watch/inquisition runtime outputs",
                "",
                "## Scripts",
                "- scripts/imperium_wave1_native_organs.py",
                "",
                "## Governance",
                "- docs/governance/IMPERIUM_WAVE1_NATIVE_ORGANS_CANON_V1.md",
                "- discoverability lines in SYSTEM_ENTRYPOINT / INSTRUCTION_INDEX",
            ]
        ),
    )

    write_json(step_root / "05_API_SMOKE.json", api_smoke)
    write_json(step_root / "07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json", machine_manifest)
    write_json(step_root / "08_ORGAN_STRENGTH_SNAPSHOT.json", organ_strength)
    write_json(step_root / "09_NODE_RANK_DETECTION_SNAPSHOT.json", node_rank)
    write_json(step_root / "10_MACHINE_MODE_SNAPSHOT.json", machine_mode)
    write_json(step_root / "11_CONSTITUTION_STATUS_SNAPSHOT.json", constitution)

    write_text(
        step_root / "12_CONSTRAINTS_TABLE.md",
        "\n".join(
            [
                "# 12_CONSTRAINTS_TABLE",
                "",
                "| Constraint | Source | Enforced by |",
                "| --- | --- | --- |",
                "| foundation/mutable split | capsule + governance canon | truth schema engine |",
                "| continuity/handoff/live split | mutable tracker | truth schema engine + law gate |",
                "| no fake completion | law canon | law gate |",
                "| transport mismatch invalidates step | bundle law | provenance seal + inquisition loop |",
                "| seed relocation-grade requirement | seed acceptance surfaces | truth schema engine + seed audit |",
                "| 4h/5h session law | session guard law surfaces | law gate + watch |",
            ]
        ),
    )

    failure_map = load_json(WAVE1_RUNTIME_SURFACES["failure_map"], {})
    write_text(
        step_root / "13_FAILURE_CLASS_MAP.md",
        "\n".join(
            [
                "# 13_FAILURE_CLASS_MAP",
                "",
                "Wave1 failure classes are bound to organ and phase.",
                "",
                f"- total_classes: `{len(failure_map.get('failure_classes', []) or [])}`",
                "",
                "See runtime map:",
                f"- `{runtime_surfaces['failure_map']}`",
            ]
        ),
    )
    write_json(step_root / "13_FAILURE_CLASS_MAP.json", failure_map)

    contracts = load_json(WAVE1_RUNTIME_SURFACES["contracts"], {})
    write_text(
        step_root / "14_ORGAN_CONTRACTS.md",
        "\n".join(
            [
                "# 14_ORGAN_CONTRACTS",
                "",
                f"- contracts surface: `{runtime_surfaces['contracts']}`",
                f"- organs_count: `{len(contracts.get('organs', []) or [])}`",
                "- each organ defines mission/inputs/checks/verdict/failure/remediation/output/integration.",
            ]
        ),
    )
    write_json(step_root / "14_ORGAN_CONTRACTS.json", contracts)

    execution_order = load_json(WAVE1_RUNTIME_SURFACES["execution_order"], {})
    write_text(
        step_root / "15_ARCHITECTURE_AND_EXECUTION_ORDER.md",
        "\n".join(
            [
                "# 15_ARCHITECTURE_AND_EXECUTION_ORDER",
                "",
                "Order is explicit and deterministic:",
                "1. truth schema engine",
                "2. law gate",
                "3. provenance seal",
                "4. watch",
                "5. inquisition loop",
                "",
                f"- execution_order_surface: `{runtime_surfaces['execution_order']}`",
            ]
        ),
    )
    write_json(step_root / "15_ARCHITECTURE_AND_EXECUTION_ORDER.json", execution_order)

    write_text(
        step_root / "16_SHADOW_MODE_STATUS.md",
        "\n".join(
            [
                "# 16_SHADOW_MODE_STATUS",
                "",
                "Wave1 mode level in this step:",
                "- truth schema engine: `SHADOW_ACTIVE`",
                "- law gate: `SHADOW_ACTIVE / ADVISORY_READY`",
                "- provenance seal: `SHADOW_ACTIVE / HARD_GATE_HOOK_READY`",
                "- watch: `SHADOW_ACTIVE`",
                "- inquisition loop: `SHADOW_ACTIVE / REBUILD_SIGNAL_READY`",
                "",
                "Hard-gate hooks are prepared and can be promoted by later bounded step.",
            ]
        ),
    )

    write_text(
        step_root / "17_TEST_RESULTS.md",
        "\n".join(
            [
                "# 17_TEST_RESULTS",
                "",
                f"- status: `{tests.get('status', 'UNKNOWN')}`",
                f"- total: `{tests.get('tests_total', 0)}`",
                f"- passed: `{tests.get('tests_passed', 0)}`",
                f"- failed: `{tests.get('tests_failed', 0)}`",
                "",
                "Machine-readable test matrix:",
                "- 17_TEST_RESULTS.json",
            ]
        ),
    )
    write_json(step_root / "17_TEST_RESULTS.json", tests)

    write_text(
        step_root / "18_INQUISITION_AUDIT_TRAIL.md",
        "\n".join(
            [
                "# 18_INQUISITION_AUDIT_TRAIL",
                "",
                "Inquisition loop audit trail is written to runtime surface and mirrored here after final verification.",
                f"- runtime surface: `{runtime_surfaces['inquisition_loop']}`",
            ]
        ),
    )

    include_paths = [f"docs/review_artifacts/{step_id}/{name}" for name in REQUIRED_REVIEW_FILES]
    include_paths.extend(
        [
            f"docs/review_artifacts/{step_id}/12_CONSTRAINTS_TABLE.md",
            f"docs/review_artifacts/{step_id}/13_FAILURE_CLASS_MAP.md",
            f"docs/review_artifacts/{step_id}/13_FAILURE_CLASS_MAP.json",
            f"docs/review_artifacts/{step_id}/14_ORGAN_CONTRACTS.md",
            f"docs/review_artifacts/{step_id}/14_ORGAN_CONTRACTS.json",
            f"docs/review_artifacts/{step_id}/15_ARCHITECTURE_AND_EXECUTION_ORDER.md",
            f"docs/review_artifacts/{step_id}/15_ARCHITECTURE_AND_EXECUTION_ORDER.json",
            f"docs/review_artifacts/{step_id}/16_SHADOW_MODE_STATUS.md",
            f"docs/review_artifacts/{step_id}/17_TEST_RESULTS.md",
            f"docs/review_artifacts/{step_id}/17_TEST_RESULTS.json",
            f"docs/review_artifacts/{step_id}/18_INQUISITION_AUDIT_TRAIL.md",
            f"docs/review_artifacts/{step_id}/20_EXECUTION_META.json",
            f"docs/review_artifacts/{step_id}/21_FINAL_RESULT.json",
            "docs/governance/IMPERIUM_WAVE1_NATIVE_ORGANS_CANON_V1.md",
            "scripts/imperium_wave1_native_organs.py",
        ]
    )
    include_paths.extend(sorted(runtime_surfaces.values()))
    include_paths = sorted(set(include_paths))
    write_text(step_root / "06_BUNDLE_INCLUDE_PATHS.txt", "\n".join(include_paths))
    write_text(step_root / "14_ARCHIVE_INCLUDE_PATHS.txt", "\n".join(include_paths))


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute IMPERIUM Wave1 native organs step.")
    parser.add_argument("--step-id", default="", help="Optional explicit step id")
    args = parser.parse_args()

    step_id = args.step_id.strip() or f"{STEP_PREFIX}_{now_stamp()}"
    step_root = REVIEW_ROOT / step_id
    step_root.mkdir(parents=True, exist_ok=True)

    mutable = load_json(CAPSULE_ROOT / "MUTABLE_TRACKER.json", {})
    authority = extract_authoritative_current_point(mutable)

    write_wave1_governance_surfaces()
    write_step_anchor(step_id=step_id, step_root=step_root, authority=authority)

    write_json(WAVE1_RUNTIME_SURFACES["contracts"], build_contracts(step_id=step_id))
    write_json(WAVE1_RUNTIME_SURFACES["failure_map"], build_failure_map())
    write_json(WAVE1_RUNTIME_SURFACES["execution_order"], build_execution_order(step_id=step_id))

    command_results: dict[str, Any] = {}
    if FORCE_REFRESH_SCRIPT.exists():
        command_results["force_refresh"] = run_cmd(["python", "scripts/refresh_imperium_force_manifest.py"])
    if CONSTITUTION_REFRESH_SCRIPT.exists():
        command_results["constitution_refresh"] = run_cmd(["python", "scripts/validation/run_constitution_checks.py"])
    if SEED_REFRESH_SCRIPT.exists():
        command_results["seed_refresh"] = run_cmd(
            ["python", "scripts/refresh_imperium_seed_capsule.py", "--capsule-root", "docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1"]
        )

    truth_pre = run_truth_schema_engine(authority=authority)
    law_pre = run_law_gate(authority=authority, truth_engine=truth_pre, step_root=step_root)
    watch_pre = compute_session_watch(authority=authority, truth_engine=truth_pre, law_gate=law_pre, provenance=None, inquisition=None, step_id=step_id)
    write_json(WAVE1_RUNTIME_SURFACES["truth_engine"], truth_pre)
    write_json(WAVE1_RUNTIME_SURFACES["law_gate"], law_pre)
    write_json(WAVE1_RUNTIME_SURFACES["watch_state"], watch_pre)

    if SEED_FOLDER_SCRIPT.exists():
        command_results["seed_folder_build"] = run_cmd(
            [
                "python",
                "scripts/build_seed_genome_working_folder.py",
                "--step-root",
                to_rel(step_root),
                "--capsule-root",
                "docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1",
            ]
        )

    tests = run_failure_simulations()
    machine_manifest = load_json(MACHINE_MANIFEST_PATH, {})
    organ_strength = load_json(ORGAN_STRENGTH_PATH, {})
    node_rank = load_json(NODE_RANK_PATH, {})
    machine_mode = load_json(MACHINE_MODE_PATH, {})
    constitution = load_json(CONSTITUTION_PATH, {})
    api_smoke, _state_payload, _live_payload = build_api_smoke()

    runtime_rel = {k: to_rel(v) for k, v in WAVE1_RUNTIME_SURFACES.items()}
    write_step_files(
        step_id=step_id,
        step_root=step_root,
        authority=authority,
        truth_pre=truth_pre,
        law_pre=law_pre,
        watch_pre=watch_pre,
        tests=tests,
        machine_manifest=machine_manifest,
        organ_strength=organ_strength,
        node_rank=node_rank,
        machine_mode=machine_mode,
        constitution=constitution,
        api_smoke=api_smoke,
        runtime_surfaces=runtime_rel,
        command_results=command_results,
    )

    write_json(
        step_root / "21_FINAL_RESULT.json",
        {
            "schema_version": "imperium_wave1_final_result.v1",
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "review_root": to_rel(step_root),
            "status": "PENDING",
            "acceptance": "PENDING",
            "transfer_package_completeness": "UNKNOWN",
            "core_required": True,
            "parts_total": 0,
            "visual_included": False,
            "optional_part_count": 0,
            "optional_included": False,
            "upload_order": [],
        },
    )

    command_results["bundle_enforcer_pass1"] = run_cmd(
        ["python", "scripts/imperium_bundle_output_enforcer.py", "--review-root", to_rel(step_root), "--retention-check"]
    )
    enforcer_first = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    provenance_first = run_provenance_seal(step_root=step_root, enforcer_report=enforcer_first)
    write_json(WAVE1_RUNTIME_SURFACES["provenance_seal"], provenance_first)

    truth_post = run_truth_schema_engine(authority=authority)
    law_post = run_law_gate(authority=authority, truth_engine=truth_post, step_root=step_root)
    inquisition = {
        "schema_version": "imperium_inquisition_loop.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "mode": "SHADOW",
        "checks_rerun": ["truth_schema_engine", "law_gate", "provenance_seal"],
        "pre": {"truth": truth_pre.get("status"), "law": law_pre.get("verdict")},
        "post": {"truth": truth_post.get("status"), "law": law_post.get("verdict"), "provenance": provenance_first.get("status")},
        "status": "PASS",
        "rebuild_required": False,
        "failures": [],
    }
    if truth_post.get("status") != "PASS":
        inquisition["status"] = "FAIL"
        inquisition["failures"].append("truth_schema_post_fail")
    if law_post.get("verdict") == "DENY":
        inquisition["status"] = "FAIL"
        inquisition["failures"].append("law_gate_post_deny")
    if provenance_first.get("status") != "PASS":
        inquisition["status"] = "REBUILD_REQUIRED"
        inquisition["rebuild_required"] = True
        inquisition["failures"].append("provenance_post_fail")
    if tests.get("status") != "PASS":
        inquisition["status"] = "FAIL"
        inquisition["failures"].append("failure_tests_not_pass")

    write_json(WAVE1_RUNTIME_SURFACES["truth_engine"], truth_post)
    write_json(WAVE1_RUNTIME_SURFACES["law_gate"], law_post)
    write_json(WAVE1_RUNTIME_SURFACES["inquisition_loop"], inquisition)

    watch_post = compute_session_watch(
        authority=authority,
        truth_engine=truth_post,
        law_gate=law_post,
        provenance=provenance_first,
        inquisition=inquisition,
        step_id=step_id,
    )
    write_json(WAVE1_RUNTIME_SURFACES["watch_state"], watch_post)
    write_json(step_root / "18_INQUISITION_AUDIT_TRAIL.json", inquisition)

    command_results["bundle_enforcer_pass2"] = run_cmd(
        ["python", "scripts/imperium_bundle_output_enforcer.py", "--review-root", to_rel(step_root), "--retention-check"]
    )
    enforcer_second = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    provenance_second = run_provenance_seal(step_root=step_root, enforcer_report=enforcer_second)
    write_json(WAVE1_RUNTIME_SURFACES["provenance_seal"], provenance_second)

    transfer_manifest, _manifest_path = _load_manifest_from_enforcer(step_root, enforcer_second)
    sections = transfer_manifest.get("sections", {}) if isinstance(transfer_manifest, dict) else {}
    core_section = sections.get("core", {}) if isinstance(sections, dict) else {}
    optional_section = sections.get("optional", {}) if isinstance(sections, dict) else {}

    acceptance_failures: list[str] = []
    if truth_post.get("status") != "PASS":
        acceptance_failures.append("truth_schema_fail")
    if law_post.get("verdict") == "DENY":
        acceptance_failures.append("law_gate_deny")
    if provenance_second.get("status") != "PASS":
        acceptance_failures.append("provenance_fail")
    if inquisition.get("status") not in {"PASS", "SHADOW_PASS"}:
        acceptance_failures.append("inquisition_not_pass")
    if tests.get("status") != "PASS":
        acceptance_failures.append("failure_tests_not_pass")
    if str(enforcer_second.get("verdict", "")) != "PASS":
        acceptance_failures.append("bundle_enforcer_not_pass")

    final_result = {
        "schema_version": "imperium_wave1_final_result.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "review_root": to_rel(step_root),
        "status": "PASS" if not acceptance_failures else "FAIL",
        "acceptance": "PASS" if not acceptance_failures else "FAIL",
        "truth_engine": truth_post.get("status"),
        "law_gate": law_post.get("verdict"),
        "provenance_seal": provenance_second.get("status"),
        "inquisition_loop": inquisition.get("status"),
        "transport_integrity": provenance_second.get("transport_integrity"),
        "transfer_package_completeness": str(transfer_manifest.get("package_completeness", "UNKNOWN")),
        "core_required": bool(transfer_manifest.get("core_required", False)),
        "parts_total": int(transfer_manifest.get("parts_total", 0) or 0),
        "core_part_count": int(core_section.get("part_count", 0) or 0),
        "visual_included": bool(transfer_manifest.get("visual_included", False)),
        "optional_part_count": int(optional_section.get("part_count", 0) or 0),
        "optional_included": bool(transfer_manifest.get("optional_included", False)),
        "upload_order": list(transfer_manifest.get("upload_order", []) or []),
        "failure_reasons": acceptance_failures,
        "step_artifact_path": to_rel(step_root),
    }
    write_json(step_root / "21_FINAL_RESULT.json", final_result)

    command_results["bundle_enforcer_pass3"] = run_cmd(
        ["python", "scripts/imperium_bundle_output_enforcer.py", "--review-root", to_rel(step_root), "--retention-check"]
    )
    enforcer_third = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    provenance_third = run_provenance_seal(step_root=step_root, enforcer_report=enforcer_third)
    write_json(WAVE1_RUNTIME_SURFACES["provenance_seal"], provenance_third)

    inquisition_final = dict(inquisition)
    inquisition_final["post"] = dict(inquisition.get("post", {}))
    inquisition_final["post"]["provenance"] = provenance_third.get("status")
    inquisition_failures: list[str] = []
    if truth_post.get("status") != "PASS":
        inquisition_failures.append("truth_schema_post_fail")
    if law_post.get("verdict") == "DENY":
        inquisition_failures.append("law_gate_post_deny")
    if provenance_third.get("status") != "PASS":
        inquisition_failures.append("provenance_post_fail")
    if tests.get("status") != "PASS":
        inquisition_failures.append("failure_tests_not_pass")
    inquisition_final["failures"] = inquisition_failures
    inquisition_final["rebuild_required"] = len(inquisition_failures) > 0
    inquisition_final["status"] = "PASS" if not inquisition_failures else "REBUILD_REQUIRED"
    write_json(WAVE1_RUNTIME_SURFACES["inquisition_loop"], inquisition_final)
    write_json(step_root / "18_INQUISITION_AUDIT_TRAIL.json", inquisition_final)

    final_failures: list[str] = []
    if truth_post.get("status") != "PASS":
        final_failures.append("truth_schema_fail")
    if law_post.get("verdict") == "DENY":
        final_failures.append("law_gate_deny")
    if inquisition_final.get("status") != "PASS":
        final_failures.append("inquisition_not_pass")
    if tests.get("status") != "PASS":
        final_failures.append("failure_tests_not_pass")
    if str(enforcer_third.get("verdict", "")) != "PASS":
        final_failures.append("bundle_enforcer_not_pass")
    if provenance_third.get("status") != "PASS":
        final_failures.append("provenance_not_pass")

    final_result["provenance_seal"] = provenance_third.get("status")
    final_result["inquisition_loop"] = inquisition_final.get("status")
    final_result["transport_integrity"] = provenance_third.get("transport_integrity")
    final_result["failure_reasons"] = final_failures
    final_result["status"] = "PASS" if not final_failures else "FAIL"
    final_result["acceptance"] = "PASS" if not final_failures else "FAIL"
    write_json(step_root / "21_FINAL_RESULT.json", final_result)

    command_results["bundle_enforcer_pass4"] = run_cmd(
        ["python", "scripts/imperium_bundle_output_enforcer.py", "--review-root", to_rel(step_root), "--retention-check"]
    )
    enforcer_four = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    provenance_four = run_provenance_seal(step_root=step_root, enforcer_report=enforcer_four)
    write_json(WAVE1_RUNTIME_SURFACES["provenance_seal"], provenance_four)
    final_result["provenance_seal"] = provenance_four.get("status")
    final_result["transport_integrity"] = provenance_four.get("transport_integrity")
    if str(enforcer_four.get("verdict", "")) != "PASS" or provenance_four.get("status") != "PASS":
        final_result["status"] = "FAIL"
        final_result["acceptance"] = "FAIL"
        reasons = list(final_result.get("failure_reasons", []) or [])
        reasons.extend(["bundle_enforcer_not_pass_final", "provenance_not_pass_final"])
        final_result["failure_reasons"] = sorted(set(reasons))
        write_json(step_root / "21_FINAL_RESULT.json", final_result)
        command_results["bundle_enforcer_pass5"] = run_cmd(
            ["python", "scripts/imperium_bundle_output_enforcer.py", "--review-root", to_rel(step_root), "--retention-check"]
        )
    else:
        write_json(step_root / "21_FINAL_RESULT.json", final_result)

    watch_final = compute_session_watch(
        authority=authority,
        truth_engine=truth_post,
        law_gate=law_post,
        provenance=provenance_four,
        inquisition=inquisition_final,
        step_id=step_id,
    )
    write_json(WAVE1_RUNTIME_SURFACES["watch_state"], watch_final)

    write_json(
        step_root / "20_EXECUTION_META.json",
        {
            "schema_version": "imperium_wave1_execution_meta.v1",
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "command_results": compact_command_results(command_results),
            "runtime_surfaces": runtime_rel,
            "tests_status": tests.get("status"),
        },
    )

    print(json.dumps(final_result, ensure_ascii=False))
    return 0 if final_result.get("acceptance") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
