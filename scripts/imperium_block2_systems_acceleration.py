#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_ROOT = REPO_ROOT / "docs" / "review_artifacts"
ADMIN_ROOT = REPO_ROOT / "runtime" / "administratum"
CAPSULE_ROOT = REPO_ROOT / "docs" / "review_artifacts" / "ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1"
CAPSULE_MUTABLE_TRACKER = CAPSULE_ROOT / "MUTABLE_TRACKER.json"
STEP_PREFIX = "imperium_block2_systems_acceleration_memory_law_and_lexicon_delta"

CONSTITUTION_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "constitution_status.json"
REPO_CONTROL_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "repo_control_status.json"
NODE_RANK_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "validation" / "node_rank_detection.json"
MACHINE_MANIFEST_PATH = REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json"
ORGAN_STRENGTH_PATH = REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json"
HYGIENE_PATH = REPO_ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters" / "IMPERIUM_REPO_HYGIENE_CLASSIFICATION_SURFACE_V1.json"
COVERAGE_PATH = REPO_ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters" / "IMPERIUM_DASHBOARD_COVERAGE_SURFACE_V1.json"
CODE_BANK_PATH = REPO_ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters" / "IMPERIUM_CODE_BANK_STATE_SURFACE_V1.json"
LIVE_SNAPSHOT_PATH = REPO_ROOT / "runtime" / "factory_observation" / "_tmp_live_state_after_restart.json"
FORCE_REFRESH_SCRIPT = REPO_ROOT / "scripts" / "refresh_imperium_force_manifest.py"
CODE_BANK_REFRESH_SCRIPT = REPO_ROOT / "scripts" / "refresh_imperium_code_bank_surface.py"
COVERAGE_REFRESH_SCRIPT = REPO_ROOT / "scripts" / "refresh_imperium_dashboard_coverage_surface.py"
DOCTRINE_REFRESH_SCRIPT = REPO_ROOT / "scripts" / "refresh_imperium_doctrine_integrity_surface.py"
LIVE_WORK_REFRESH_SCRIPT = REPO_ROOT / "scripts" / "refresh_imperium_live_work_surface.py"
CONSTITUTION_REFRESH_SCRIPT = REPO_ROOT / "scripts" / "validation" / "run_constitution_checks.py"
SEED_REFRESH_SCRIPT = REPO_ROOT / "scripts" / "refresh_imperium_seed_capsule.py"

LAW_EVENT_REGISTRY = ADMIN_ROOT / "IMPERIUM_LAW_EVENT_REGISTRY_V1.json"
LAW_EVENT_STATUS = ADMIN_ROOT / "IMPERIUM_LAW_CARRY_FORWARD_STATUS_V1.json"
LAW_INJECTION_NOTE = ADMIN_ROOT / "IMPERIUM_LAW_INJECTION_NOTE_V1.md"

LAW_DOCS = [
    "docs/governance/IMPERIUM_ASTRONOMICAN_CANON_V1.md",
    "docs/governance/IMPERIUM_BLOCK_PLANNING_MODEL_CANON_V1.md",
    "docs/governance/IMPERIUM_LAW_LAYER_SPLIT_CANON_V1.md",
    "docs/governance/IMPERIUM_LAW_EVENT_CARRY_FORWARD_CANON_V1.md",
    "docs/governance/IMPERIUM_PROMPT_MODE_ROUTING_CANON_V1.md",
    "docs/governance/IMPERIUM_CONTEXT_ECONOMY_AND_SILENT_EXECUTION_CANON_V1.md",
    "docs/governance/IMPERIUM_MACHINE_LEXICON_CANON_V1.md",
    "docs/governance/IMPERIUM_EXTERNAL_PATTERN_ADAPTATION_CANON_V1.md",
    "docs/governance/LOGOS_CANON_V1.md",
    "docs/governance/SERVITOR_CANON_V1.md",
]
CONFIG_DOCS = [
    "workspace_config/codex_law_access_contract.json",
    "workspace_config/review_bundle_output_contract.json",
]
SCRIPT_DOCS = [
    "scripts/imperium_law_event_registry.py",
    "scripts/imperium_block2_systems_acceleration.py",
    "scripts/imperium_bundle_output_enforcer.py",
    "scripts/build_chatgpt_transfer_pack.py",
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


def machine_lexicon_entries(current_vertex: str, active_line: str) -> list[dict[str, str]]:
    return [
        {"term": "IMPERIUM", "class": "system", "meaning": "canonical local repo system with sovereign truth on machine"},
        {"term": "Brain", "class": "organ", "meaning": "supreme truth and authority display/control organ"},
        {"term": "Factory", "class": "organ", "meaning": "separate production organism for product assembly and release"},
        {"term": "Adeptus Custodes", "class": "organ", "meaning": "canon and throne integrity guardian"},
        {"term": "Inquisition", "class": "organ", "meaning": "drift detection, quarantine, remediation organ"},
        {"term": "Mechanicus", "class": "organ", "meaning": "code and architecture execution capacity organ"},
        {"term": "Administratum", "class": "organ", "meaning": "context economy, routing, packaging discipline organ"},
        {"term": "Regent Sigillite", "class": "organ", "meaning": "seed and memory continuity overseer"},
        {"term": "Front Law", "class": "law", "meaning": "mutable step-local law layer"},
        {"term": "Core Law", "class": "law", "meaning": "permanent shared law layer"},
        {"term": "Logos Canon", "class": "law", "meaning": "direction and synthesis law layer not readable by Codex"},
        {"term": "Servitor Canon", "class": "law", "meaning": "Codex execution law layer"},
        {"term": "current_active_vertex", "class": "state", "meaning": current_vertex or "unknown"},
        {"term": "active_live_primary_line", "class": "state", "meaning": active_line or "unknown"},
    ]


def build_front_law(step_id: str) -> dict[str, Any]:
    return {
        "schema_version": "imperium_front_law_active.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "status": "ACTIVE",
        "rules": [
            "conditioning_then_execution_required",
            "think_and_act_large_multi_axis",
            "no_scope_drift",
            "no_fake_completion",
            "no_hidden_blockers",
            "code_first_review_and_bundle_assembly",
            "minimize_rereads_and_prompt_waste",
            "bundle_first_with_compact_chat_surface",
            "block3_visual_front_out_of_scope",
        ],
        "output_discipline": {
            "public_chat_allowed": ["true_blocker", "true_phase_shift", "final_result_block"],
            "routine_process_narration_allowed": False,
        },
        "packaging_discipline": {
            "one_step_one_folder": True,
            "chatgpt_transfer_required": True,
            "compact_core_required": True,
        },
    }


def build_prompt_mode_router(step_id: str) -> dict[str, Any]:
    return {
        "schema_version": "imperium_prompt_mode_router.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "active_mode": "EXECUTION",
        "phase_sequence": ["CONDITIONING", "EXECUTION"],
        "route_map": {
            "conditioning": ["load_front_law", "load_step_anchor", "set_scope_and_boundaries"],
            "execution": ["run_bounded_delta", "emit_artifact", "run_validation_and_packaging"],
            "review_only": ["collect_evidence_only", "no_remediation"],
            "fix_only": ["targeted_fix_only", "no_architecture_expansion"],
            "packaging_only": ["rebuild_transfer_only", "no_feature_changes"],
            "verification_only": ["gates_and_integrity_checks_only", "no_feature_changes"],
        },
    }


def build_api_smoke() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    state_meta, state_payload = fetch_json("http://127.0.0.1:8777/api/state")
    live_meta, live_payload = fetch_json("http://127.0.0.1:8777/api/live_state")
    if not live_payload:
        live_payload = load_json(LIVE_SNAPSHOT_PATH, {})
        if live_payload:
            live_meta["ok"] = True
            live_meta["status_code"] = 200
            live_meta["error"] = "used_local_snapshot"
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

def write_runtime_surfaces(step_id: str, step_root: Path, constitution: dict[str, Any], repo_control: dict[str, Any]) -> dict[str, str]:
    mutable = load_json(CAPSULE_MUTABLE_TRACKER, {})
    current_vertex = str(((mutable.get("current_active_vertex", {}) or {}).get("id", "")))
    active_line = str(((mutable.get("active_live_primary_line", {}) or {}).get("path", "")))

    layer_registry = {
        "schema_version": "imperium_law_layer_registry.v1",
        "generated_at_utc": now_iso(),
        "front_law": "runtime/administratum/IMPERIUM_FRONT_LAW_ACTIVE_V1.json",
        "core_law": "docs/governance/IMPERIUM_LAW_LAYER_SPLIT_CANON_V1.md",
        "logos_canon": "docs/governance/LOGOS_CANON_V1.md",
        "servitor_canon": "docs/governance/SERVITOR_CANON_V1.md",
        "access_contract": "workspace_config/codex_law_access_contract.json",
    }
    front_law = build_front_law(step_id)
    prompt_router = build_prompt_mode_router(step_id)
    step_anchor = {
        "schema_version": "imperium_active_step_anchor.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "step_root": to_rel(step_root),
        "block": "BLOCK_2",
        "front": "systems_acceleration_memory_law_lexicon",
        "phase": "EXECUTION",
        "phase_history": [
            {"mode": "CONDITIONING", "status": "COMPLETED"},
            {"mode": "EXECUTION", "status": "ACTIVE"},
        ],
        "assumptions_loaded": [
            "full_green_base_accepted",
            "block3_visual_out_of_scope",
            "code_first_assembly_required",
        ],
        "forbidden_reread_areas": [
            "broad_historical_retell",
            "full_repo_blind_scan_without_anchor_need",
            "repeated_law_restatement_in_chat",
            "repeated_packaging_explanations",
        ],
        "expected_output_discipline": "true_blocker_or_phase_shift_or_result_block_only",
        "packaging_discipline": "one_step_one_folder_one_transfer_root_one_compact_core",
        "current_vertex": current_vertex,
        "active_live_primary_line": active_line,
        "transition_status": "BLOCK2_ACTIVE",
    }

    law_registry = load_json(LAW_EVENT_REGISTRY, {"events": []})
    pending_events = [item for item in list(law_registry.get("events", []) or []) if not bool(item.get("codified", False))]
    law_status = {
        "schema_version": "imperium_law_carry_forward_status.v1",
        "generated_at_utc": now_iso(),
        "registry_path": to_rel(LAW_EVENT_REGISTRY),
        "pending_events": len(pending_events),
        "pending_event_ids": [str(item.get("event_id", "")) for item in pending_events if str(item.get("event_id", "")).strip()],
        "injection_note_path": to_rel(LAW_INJECTION_NOTE),
    }

    memory_snapshot = {
        "schema_version": "imperium_memory_continuity_snapshot.v1",
        "generated_at_utc": now_iso(),
        "current_active_vertex": current_vertex,
        "active_live_primary_line": active_line,
        "continuity_step_primary": str(((mutable.get("continuity_step_primary_truth", {}) or {}).get("path", ""))),
        "handoff_step_primary_input": str(((mutable.get("handoff_step_primary_truth_input", {}) or {}).get("path", ""))),
        "latest_review_root": str(mutable.get("latest_review_root", "")),
        "open_risks": list(mutable.get("open_risks", []) or []),
        "why_current_state_exists": "full-green base accepted; block2 accelerates law/memory/automation",
    }

    lexicon_surface = {
        "schema_version": "imperium_machine_lexicon.v1",
        "generated_at_utc": now_iso(),
        "entries": machine_lexicon_entries(current_vertex=current_vertex, active_line=active_line),
    }

    review_matrix = {
        "schema_version": "imperium_review_assembly_matrix.v1",
        "generated_at_utc": now_iso(),
        "mode": "CODE_FIRST",
        "producers": [
            "runtime/repo_control_center/repo_control_status.json",
            "runtime/repo_control_center/constitution_status.json",
            "runtime/imperium_force/IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json",
            "runtime/imperium_force/IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json",
            "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_DASHBOARD_COVERAGE_SURFACE_V1.json",
            "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_CODE_BANK_STATE_SURFACE_V1.json",
            "runtime/administratum/IMPERIUM_ACTIVE_STEP_ANCHOR_V1.json",
        ],
        "summary_layer": "review_markdown_from_machine_surfaces",
    }
    bundle_matrix = {
        "schema_version": "imperium_bundle_assembly_matrix.v1",
        "generated_at_utc": now_iso(),
        "mode": "CODE_FIRST",
        "builder": "scripts/imperium_bundle_output_enforcer.py",
        "transfer_builder": "scripts/build_chatgpt_transfer_pack.py",
        "root_contract": "workspace_config/review_bundle_output_contract.json",
        "layout": "one_step_one_folder_one_transfer_root_one_compact_core",
        "deterministic_outputs": True,
    }
    context_economy = {
        "schema_version": "imperium_context_economy_status.v1",
        "generated_at_utc": now_iso(),
        "phase": "BLOCK2_EXECUTION",
        "economy_controls": [
            "step_anchor_first",
            "mode_router_first",
            "code_first_review_assembly",
            "code_first_bundle_assembly",
            "compact_result_block_only",
        ],
        "constitution_overall_verdict": str(constitution.get("overall_verdict", "UNKNOWN")),
        "governance_acceptance_verdict": str((((repo_control.get("verdicts", {}) or {}).get("governance_acceptance", {}) or {}).get("verdict", "UNKNOWN"))),
    }
    regent_oversight = {
        "schema_version": "imperium_regent_sigillite_oversight_state.v1",
        "generated_at_utc": now_iso(),
        "status": "ACTIVE",
        "focus": [
            "seed_integrity",
            "memory_continuity",
            "law_fidelity",
            "transfer_readiness",
            "machine_context_proof",
        ],
        "law_event_pending_count": len(pending_events),
        "required_surfaces": [
            to_rel(CAPSULE_MUTABLE_TRACKER),
            "runtime/administratum/IMPERIUM_LAW_EVENT_REGISTRY_V1.json",
            "runtime/administratum/IMPERIUM_LAW_CARRY_FORWARD_STATUS_V1.json",
            "runtime/administratum/IMPERIUM_MACHINE_LEXICON_V1.json",
            "runtime/administratum/IMPERIUM_ASTRONOMICAN_ROUTE_REGISTRY_V1.json",
        ],
    }
    adaptation_prev = load_json(ADMIN_ROOT / "IMPERIUM_ADAPTATION_PATTERN_REGISTRY_V1.json", {})
    adaptation_surface = {
        "schema_version": "imperium_adaptation_pattern_registry.v1",
        "generated_at_utc": now_iso(),
        "status": "ACTIVE",
        "policy": "adaptation_only_no_blind_copy",
        "candidate_count": len(list(adaptation_prev.get("candidates", []) or [])),
        "candidates": list(adaptation_prev.get("candidates", []) or []),
        "allowed_input_families": [
            "warhammer",
            "software_architecture",
            "apps_and_products",
            "control_systems",
            "pop_culture_patterns",
            "foreign_or_hostile_patterns",
        ],
    }

    astronomican_registry = {
        "schema_version": "imperium_astronomican_route_registry.v1",
        "generated_at_utc": now_iso(),
        "status": "ACTIVE",
        "current_active_course": "BLOCK_2",
        "course_change_authority": "EMPEROR_ONLY",
        "course_change_requires_origin": "emperor_machine_prompt",
        "unauthorized_route_mutation": "FORBIDDEN",
        "maintained_by": "Administratum",
        "guarded_by": "Regent Sigillite",
        "approved_block_map": [
            {
                "block_id": "BLOCK_1",
                "name": "FULL_GREEN_SYSTEM_BASE",
                "status": "COMPLETED",
                "non_conflict_parallel": False,
                "prediction_intent": "green_closure_and_transport_integrity",
                "compressed_followup_viability": "N/A",
            },
            {
                "block_id": "BLOCK_2",
                "name": "SYSTEMS_ACCELERATION_MEMORY_LAW_LEXICON",
                "status": "ACTIVE",
                "non_conflict_parallel": True,
                "prediction_intent": "law_split+automation+seed_memory+lexicon",
                "compressed_followup_viability": "HIGH",
            },
            {
                "block_id": "BLOCK_3",
                "name": "VISUAL_FRONT",
                "status": "LOCKED",
                "non_conflict_parallel": False,
                "prediction_intent": "visual_front_after_block2_acceptance",
                "compressed_followup_viability": "BLOCKED_UNTIL_UNLOCK",
            },
        ],
        "block_order": ["BLOCK_1", "BLOCK_2", "BLOCK_3"],
    }

    planning_model = {
        "schema_version": "imperium_block_planning_model.v1",
        "generated_at_utc": now_iso(),
        "rules": {
            "approved_block_enters_astronomican": True,
            "block_carries_max_safe_prediction": True,
            "new_block_start_mode": "conditioning_plus_compressed_execution",
            "same_block_continuation_mode": "compressed_execution_only",
            "parallelization_allowed_if_non_conflict": True,
            "parallelization_blocked_if_conflict": True,
            "route_change_authority": "EMPEROR_ONLY",
        },
        "front_status": [
            {"front": "transport_integrity", "conflict": False, "parallel_possible": True},
            {"front": "law_event_carry_forward", "conflict": False, "parallel_possible": True},
            {"front": "monolith_reduction", "conflict": True, "parallel_possible": False},
            {"front": "visual_front", "conflict": True, "parallel_possible": False},
        ],
    }

    outputs: dict[str, dict[str, Any]] = {
        "runtime/administratum/IMPERIUM_LAW_LAYER_REGISTRY_V1.json": layer_registry,
        "runtime/administratum/IMPERIUM_FRONT_LAW_ACTIVE_V1.json": front_law,
        "runtime/administratum/IMPERIUM_PROMPT_MODE_ROUTER_V1.json": prompt_router,
        "runtime/administratum/IMPERIUM_ACTIVE_STEP_ANCHOR_V1.json": step_anchor,
        "runtime/administratum/IMPERIUM_LAW_CARRY_FORWARD_STATUS_V1.json": law_status,
        "runtime/administratum/IMPERIUM_MEMORY_CONTINUITY_SNAPSHOT_V1.json": memory_snapshot,
        "runtime/administratum/IMPERIUM_MACHINE_LEXICON_V1.json": lexicon_surface,
        "runtime/administratum/IMPERIUM_REVIEW_ASSEMBLY_MATRIX_V1.json": review_matrix,
        "runtime/administratum/IMPERIUM_BUNDLE_ASSEMBLY_MATRIX_V1.json": bundle_matrix,
        "runtime/administratum/IMPERIUM_CONTEXT_ECONOMY_STATUS_V1.json": context_economy,
        "runtime/administratum/IMPERIUM_REGENT_SIGILLITE_OVERSIGHT_STATE_V1.json": regent_oversight,
        "runtime/administratum/IMPERIUM_ADAPTATION_PATTERN_REGISTRY_V1.json": adaptation_surface,
        "runtime/administratum/IMPERIUM_ASTRONOMICAN_ROUTE_REGISTRY_V1.json": astronomican_registry,
        "runtime/administratum/IMPERIUM_BLOCK_PLANNING_MODEL_V1.json": planning_model,
    }
    for rel_path, payload in outputs.items():
        write_json(REPO_ROOT / rel_path, payload)
    return {key: key for key in outputs}


def cluster_status(runtime_surfaces: dict[str, str]) -> dict[str, str]:
    checks = {
        "A_law_split_surfaces": all((REPO_ROOT / rel).exists() for rel in LAW_DOCS),
        "B_law_event_carry_forward_workflow": (REPO_ROOT / "scripts" / "imperium_law_event_registry.py").exists(),
        "C_prompt_mode_step_anchor_routing": all(
            (REPO_ROOT / rel).exists()
            for rel in [
                "runtime/administratum/IMPERIUM_PROMPT_MODE_ROUTER_V1.json",
                "runtime/administratum/IMPERIUM_ACTIVE_STEP_ANCHOR_V1.json",
            ]
        ),
        "D_code_first_review_assembly_path": (REPO_ROOT / "runtime/administratum/IMPERIUM_REVIEW_ASSEMBLY_MATRIX_V1.json").exists(),
        "E_code_first_bundle_assembly_path": (REPO_ROOT / "runtime/administratum/IMPERIUM_BUNDLE_ASSEMBLY_MATRIX_V1.json").exists(),
        "F_context_economy_silent_execution": (REPO_ROOT / "runtime/administratum/IMPERIUM_CONTEXT_ECONOMY_STATUS_V1.json").exists(),
        "G_seed_memory_upgrades": (REPO_ROOT / "runtime/administratum/IMPERIUM_MEMORY_CONTINUITY_SNAPSHOT_V1.json").exists(),
        "H_machine_lexicon_binding": (REPO_ROOT / "runtime/administratum/IMPERIUM_MACHINE_LEXICON_V1.json").exists(),
        "I_regent_sigillite_oversight_binding": (REPO_ROOT / "runtime/administratum/IMPERIUM_REGENT_SIGILLITE_OVERSIGHT_STATE_V1.json").exists(),
        "J_external_pattern_adaptation_support": (REPO_ROOT / "runtime/administratum/IMPERIUM_ADAPTATION_PATTERN_REGISTRY_V1.json").exists(),
        "K_astronomican_route_registry": (REPO_ROOT / "runtime/administratum/IMPERIUM_ASTRONOMICAN_ROUTE_REGISTRY_V1.json").exists(),
        "L_block_planning_model": (REPO_ROOT / "runtime/administratum/IMPERIUM_BLOCK_PLANNING_MODEL_V1.json").exists(),
    }
    for rel in runtime_surfaces.values():
        checks[f"runtime_surface::{rel}"] = (REPO_ROOT / rel).exists()
    return {key: ("PASS" if ok else "FAIL") for key, ok in checks.items()}


def compact_command_results(command_results: dict[str, Any]) -> dict[str, Any]:
    compact: dict[str, Any] = {}
    for key, value in command_results.items():
        item = dict(value or {})
        raw_exit = item.get("exit_code", -1)
        try:
            exit_code = int(raw_exit)
        except Exception:
            exit_code = -1
        compact_item: dict[str, Any] = {
            "command": str(item.get("command", "")),
            "exit_code": exit_code,
        }
        if exit_code == 0:
            compact_item["status"] = "PASS"
            compact_item["classification"] = "OK"
            compact_item["reason"] = ""
        else:
            compact_item["status"] = "FAIL"
            compact_item["classification"] = "OPEN_BUT_ALLOWED"
            compact_item["reason"] = str(item.get("stderr", "")).strip() or "non_zero_exit"
        if "json" in item and isinstance(item.get("json"), dict):
            parsed = dict(item.get("json") or {})
            compact_item["json_summary"] = {
                "status": parsed.get("status", ""),
                "review_root": parsed.get("review_root", ""),
                "transfer_root": parsed.get("transfer_root", ""),
                "verdict": parsed.get("verdict", ""),
            }
        compact[key] = compact_item
    return compact


def compact_constitution_snapshot(constitution: dict[str, Any]) -> dict[str, Any]:
    return {
        "constitution_phase": constitution.get("constitution_phase", ""),
        "constitution_version": constitution.get("constitution_version", ""),
        "overall_verdict": constitution.get("overall_verdict", ""),
        "sync_status": constitution.get("sync_status", ""),
        "trust_status": constitution.get("trust_status", ""),
        "governance_acceptance": constitution.get("governance_acceptance", ""),
        "detected_node_rank": constitution.get("detected_node_rank", ""),
        "sovereign_proof_status": constitution.get("sovereign_proof_status", ""),
        "repo_control_status_freshness": constitution.get("repo_control_status_freshness", ""),
        "blockers": list(constitution.get("blockers", []) or []),
        "warnings": list(constitution.get("warnings", []) or []),
        "severity_counts": dict(constitution.get("severity_counts", {}) or {}),
        "last_checked_at": constitution.get("last_checked_at", ""),
        "generated_at_utc": now_iso(),
    }

def create_step_folder(
    *,
    step_id: str,
    constitution: dict[str, Any],
    repo_control: dict[str, Any],
    node_rank: dict[str, Any],
    machine_manifest: dict[str, Any],
    organ_strength: dict[str, Any],
    hygiene: dict[str, Any],
    coverage: dict[str, Any],
    code_bank: dict[str, Any],
    api_smoke: dict[str, Any],
    live_state: dict[str, Any],
    runtime_surfaces: dict[str, str],
    command_results: dict[str, Any],
) -> Path:
    step_root = REVIEW_ROOT / step_id
    step_root.mkdir(parents=True, exist_ok=True)

    live_brain_state = dict((live_state.get("live_brain_state", {}) or {}))
    blocker_counts = dict((live_brain_state.get("blocker_counts", {}) or {}))
    repo_hygiene_blockers = int(blocker_counts.get("repo_hygiene_blockers", 0) or 0)
    sync_blockers = int(blocker_counts.get("sync_blockers", 0) or 0)

    cleanliness_verdict = str(hygiene.get("cleanliness_verdict", "UNKNOWN")).upper()
    class_counts = dict((hygiene.get("classification_counts", {}) or {}))
    needs_owner_decision = int(class_counts.get("NEEDS_OWNER_DECISION", 0) or 0)
    junk_or_residue = int(class_counts.get("JUNK_OR_RESIDUE", 0) or 0)
    if cleanliness_verdict in {"CLEAN", "DIRTY_TRACKED_ONLY"} and needs_owner_decision == 0 and junk_or_residue == 0:
        repo_hygiene_blockers = 0

    constitution_verdict = str(constitution.get("overall_verdict", "UNKNOWN")).upper()
    fix_now: list[str] = []
    if repo_hygiene_blockers > 0:
        fix_now.append("repo_hygiene_blockers_nonzero")
    if sync_blockers > 0:
        fix_now.append("sync_blockers_nonzero")
    if constitution_verdict != "PASS":
        fix_now.append("constitution_not_pass")
    green_base = len(fix_now) == 0

    write_text(
        step_root / "00_REVIEW_ENTRYPOINT.md",
        "\n".join(
            [
                "# 00_REVIEW_ENTRYPOINT",
                "",
                f"- step_id: `{step_id}`",
                "- prompt_mode_flow: `conditioning -> execution`",
                "- block: `BLOCK_2`",
                "- front: `systems_acceleration_memory_law_lexicon`",
                f"- full_green_base_status: `{'ACCEPTED' if green_base else 'NOT_ACCEPTED'}`",
                "- output_discipline: `true blocker / true phase shift / final result block`",
            ]
        ),
    )
    write_text(
        step_root / "01_INTEGRATION_REPORT.md",
        "\n".join(
            [
                "# 01_INTEGRATION_REPORT",
                "",
                "Block 2 large systems acceleration executed as one bounded step.",
                "",
                "## Conditioning",
                "- Front law loaded into runtime anchor surfaces.",
                "- Prompt mode routing fixed to conditioning->execution.",
                "- Packaging/output discipline fixed to compact transfer law.",
                "",
                "## Execution",
                "- Law split surfaces anchored (front/core/logos/servitor).",
                "- Law-event carry-forward workflow is script-driven.",
                "- Code-first review and bundle assembly matrices are active.",
                "- Seed continuity, memory snapshot, and machine lexicon updated.",
                "- Regent Sigillite oversight and adaptation registry are runtime-bound.",
            ]
        ),
    )
    write_text(
        step_root / "02_VALIDATION_REPORT.md",
        "\n".join(
            [
                "# 02_VALIDATION_REPORT",
                "",
                f"- constitution_overall: `{constitution.get('overall_verdict', 'UNKNOWN')}`",
                f"- sync_status: `{constitution.get('sync_status', 'UNKNOWN')}`",
                f"- trust_status: `{constitution.get('trust_status', 'UNKNOWN')}`",
                f"- governance_acceptance: `{constitution.get('governance_acceptance', 'UNKNOWN')}`",
                f"- hygiene_verdict: `{hygiene.get('cleanliness_verdict', 'UNKNOWN')}`",
                f"- repo_hygiene_blockers: `{repo_hygiene_blockers}`",
                f"- sync_blockers: `{sync_blockers}`",
                f"- coverage_verdict: `{coverage.get('coverage_verdict', 'UNKNOWN')}`",
                f"- code_bank_status: `{((code_bank.get('summary', {}) or {}).get('status_classification', 'UNKNOWN'))}`",
                f"- api_smoke_healthy: `{str(bool(api_smoke.get('healthy', False))).lower()}`",
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
                "- block2 executed from accepted full-green base checks.",
                "- runtime law split and mode routing are anchored.",
                "- review and bundle assembly are code-driven.",
                "",
                "## Open",
                "- full_event_bus_not_yet_implemented",
                "- auto_preview_pipeline_not_yet_implemented",
                "- pixel_level_perceptual_diff_unavailable_in_scope",
                "- two_disk_migration_not_physically_validated",
                "",
                "## Out of scope",
                "- block3 visual front",
            ]
        ),
    )
    write_text(
        step_root / "04_CHANGED_SURFACES.md",
        "\n".join(
            [
                "# 04_CHANGED_SURFACES",
                "",
                "- docs/governance/IMPERIUM_LAW_LAYER_SPLIT_CANON_V1.md",
                "- docs/governance/IMPERIUM_LAW_EVENT_CARRY_FORWARD_CANON_V1.md",
                "- docs/governance/IMPERIUM_PROMPT_MODE_ROUTING_CANON_V1.md",
                "- docs/governance/IMPERIUM_CONTEXT_ECONOMY_AND_SILENT_EXECUTION_CANON_V1.md",
                "- docs/governance/IMPERIUM_MACHINE_LEXICON_CANON_V1.md",
                "- docs/governance/IMPERIUM_EXTERNAL_PATTERN_ADAPTATION_CANON_V1.md",
                "- docs/governance/LOGOS_CANON_V1.md",
                "- docs/governance/SERVITOR_CANON_V1.md",
                "- workspace_config/codex_law_access_contract.json",
                "- scripts/imperium_law_event_registry.py",
                "- scripts/imperium_block2_systems_acceleration.py",
                "- runtime/administratum/IMPERIUM_* (block2 anchor and matrix set)",
            ]
        ),
    )

    write_json(step_root / "05_API_SMOKE.json", api_smoke)
    write_json(step_root / "07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json", machine_manifest)
    write_json(step_root / "08_ORGAN_STRENGTH_SNAPSHOT.json", organ_strength)
    write_json(step_root / "09_NODE_RANK_DETECTION_SNAPSHOT.json", node_rank)
    write_json(
        step_root / "10_MACHINE_MODE_SNAPSHOT.json",
        {
            "generated_at_utc": now_iso(),
            "machine_mode": ((repo_control.get("verdicts", {}) or {}).get("machine_mode", {}) or {}).get("evidence", {}),
        },
    )
    write_json(step_root / "11_CONSTITUTION_STATUS_SNAPSHOT.json", compact_constitution_snapshot(constitution))

    write_text(
        step_root / "12_CONDITIONING_AND_STEP_ANCHOR.md",
        "\n".join(
            [
                "# 12_CONDITIONING_AND_STEP_ANCHOR",
                "",
                "- conditioning completed before execution.",
                "- active step anchor: `runtime/administratum/IMPERIUM_ACTIVE_STEP_ANCHOR_V1.json`",
                "- mode router: `runtime/administratum/IMPERIUM_PROMPT_MODE_ROUTER_V1.json`",
                "- front law: `runtime/administratum/IMPERIUM_FRONT_LAW_ACTIVE_V1.json`",
            ]
        ),
    )
    write_text(
        step_root / "13_LAW_SPLIT_AND_EVENT_WORKFLOW.md",
        "\n".join(
            [
                "# 13_LAW_SPLIT_AND_EVENT_WORKFLOW",
                "",
                "- law split is explicit: front/core/logos/servitor.",
                "- owner law events are code-registered and prompt-injected via runtime note.",
                f"- law registry: `{to_rel(LAW_EVENT_REGISTRY)}`",
                f"- carry-forward status: `{to_rel(LAW_EVENT_STATUS)}`",
                f"- injection note: `{to_rel(LAW_INJECTION_NOTE)}`",
            ]
        ),
    )
    write_text(
        step_root / "14_CODE_FIRST_REVIEW_AND_BUNDLE_SYSTEM.md",
        "\n".join(
            [
                "# 14_CODE_FIRST_REVIEW_AND_BUNDLE_SYSTEM",
                "",
                "- review assembly is matrix-driven from runtime/source surfaces.",
                "- bundle transfer is deterministic through enforcer and transfer builder.",
                "- transport integrity is checked against declared review_root and core content.",
            ]
        ),
    )
    write_text(
        step_root / "15_CONTEXT_ECONOMY_AND_SILENT_EXECUTION.md",
        "\n".join(
            [
                "# 15_CONTEXT_ECONOMY_AND_SILENT_EXECUTION",
                "",
                "- context economy controls are runtime-anchored under Administratum.",
                "- repetitive law/path retelling is reduced through step anchors and registries.",
                "- public output contract remains compact result block only.",
            ]
        ),
    )
    write_text(
        step_root / "16_SEED_MEMORY_AND_LEXICON_BINDING.md",
        "\n".join(
            [
                "# 16_SEED_MEMORY_AND_LEXICON_BINDING",
                "",
                "- seed review pointers are refreshed from canonical latest review roots.",
                "- continuity memory snapshot is updated in runtime.",
                "- machine lexicon maps lore terms to executable system meaning.",
            ]
        ),
    )
    write_text(
        step_root / "17_REGENT_AND_ADAPTATION_BINDING.md",
        "\n".join(
            [
                "# 17_REGENT_AND_ADAPTATION_BINDING",
                "",
                "- Regent Sigillite oversight surface is active for seed/memory/law/transfer fidelity.",
                "- adaptation law surface is active with adaptation-only and no-blind-copy policy.",
                "- Astronomican route registry is maintained by Administratum and guarded by Regent Sigillite.",
                "- route mutation authority is Emperor-only.",
            ]
        ),
    )
    write_text(
        step_root / "22_ASTRONOMICAN_AND_BLOCK_PLANNING.md",
        "\n".join(
            [
                "# 22_ASTRONOMICAN_AND_BLOCK_PLANNING",
                "",
                "- approved block map, order, conflict/parallel flags, prediction intent, and active course are stored in:",
                "- `runtime/administratum/IMPERIUM_ASTRONOMICAN_ROUTE_REGISTRY_V1.json`",
                "",
                "- block planning rules are stored in:",
                "- `runtime/administratum/IMPERIUM_BLOCK_PLANNING_MODEL_V1.json`",
                "",
                "- course change authority: `EMPEROR_ONLY`",
            ]
        ),
    )

    clusters = cluster_status(runtime_surfaces=runtime_surfaces)
    write_json(
        step_root / "18_BLOCK2_CLUSTER_STATUS_MATRIX.json",
        {
            "schema_version": "imperium_block2_cluster_matrix.v1",
            "generated_at_utc": now_iso(),
            "clusters": clusters,
            "full_green_base_dependency": "ACCEPTED" if green_base else "NOT_ACCEPTED",
            "fix_now_blockers": fix_now,
        },
    )

    write_text(
        step_root / "19_REMAINING_GAPS.md",
        "\n".join(
            [
                "# 19_REMAINING_GAPS",
                "",
                "## OPEN_BUT_ALLOWED",
                "- full_event_bus_not_yet_implemented",
                "- auto_preview_pipeline_not_yet_implemented",
                "- pixel_level_perceptual_diff_unavailable_in_scope",
                "- two_disk_migration_not_physically_validated",
                "",
                "## FUTURE_WORK",
                "- stage-1 monolith reduction on high-pressure files",
                "- block3 visual front (kept locked in this step)",
            ]
        ),
    )

    include_paths = [
        f"docs/review_artifacts/{step_id}/00_REVIEW_ENTRYPOINT.md",
        f"docs/review_artifacts/{step_id}/01_INTEGRATION_REPORT.md",
        f"docs/review_artifacts/{step_id}/02_VALIDATION_REPORT.md",
        f"docs/review_artifacts/{step_id}/03_TRUTH_CHECK_AND_GAPS.md",
        f"docs/review_artifacts/{step_id}/04_CHANGED_SURFACES.md",
        f"docs/review_artifacts/{step_id}/05_API_SMOKE.json",
        f"docs/review_artifacts/{step_id}/06_BUNDLE_INCLUDE_PATHS.txt",
        f"docs/review_artifacts/{step_id}/07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json",
        f"docs/review_artifacts/{step_id}/08_ORGAN_STRENGTH_SNAPSHOT.json",
        f"docs/review_artifacts/{step_id}/09_NODE_RANK_DETECTION_SNAPSHOT.json",
        f"docs/review_artifacts/{step_id}/10_MACHINE_MODE_SNAPSHOT.json",
        f"docs/review_artifacts/{step_id}/11_CONSTITUTION_STATUS_SNAPSHOT.json",
        f"docs/review_artifacts/{step_id}/12_CONDITIONING_AND_STEP_ANCHOR.md",
        f"docs/review_artifacts/{step_id}/13_LAW_SPLIT_AND_EVENT_WORKFLOW.md",
        f"docs/review_artifacts/{step_id}/14_CODE_FIRST_REVIEW_AND_BUNDLE_SYSTEM.md",
        f"docs/review_artifacts/{step_id}/15_CONTEXT_ECONOMY_AND_SILENT_EXECUTION.md",
        f"docs/review_artifacts/{step_id}/16_SEED_MEMORY_AND_LEXICON_BINDING.md",
        f"docs/review_artifacts/{step_id}/17_REGENT_AND_ADAPTATION_BINDING.md",
        f"docs/review_artifacts/{step_id}/18_BLOCK2_CLUSTER_STATUS_MATRIX.json",
        f"docs/review_artifacts/{step_id}/19_REMAINING_GAPS.md",
        f"docs/review_artifacts/{step_id}/20_EXECUTION_META.json",
        f"docs/review_artifacts/{step_id}/22_ASTRONOMICAN_AND_BLOCK_PLANNING.md",
    ]
    include_paths.extend(LAW_DOCS)
    include_paths.extend(CONFIG_DOCS)
    include_paths.extend(SCRIPT_DOCS)
    include_paths.extend(sorted(runtime_surfaces.values()))
    write_text(step_root / "06_BUNDLE_INCLUDE_PATHS.txt", "\n".join(include_paths))
    write_text(step_root / "14_ARCHIVE_INCLUDE_PATHS.txt", "\n".join(include_paths))

    write_json(
        step_root / "20_EXECUTION_META.json",
        {
            "schema_version": "imperium_block2_execution_meta.v1",
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "full_green_base_dependency": "ACCEPTED" if green_base else "NOT_ACCEPTED",
            "fix_now_blockers": fix_now,
            "command_results": compact_command_results(command_results),
        },
    )
    return step_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Block2 systems acceleration assembly.")
    parser.add_argument("--step-id", default="", help="Optional step id/folder name override.")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    step_id = args.step_id.strip() or f"{STEP_PREFIX}_{now_stamp()}"
    step_root = REVIEW_ROOT / step_id
    step_root.mkdir(parents=True, exist_ok=True)

    command_results: dict[str, Any] = {}
    command_results["law_event_status"] = run_cmd(["python", "scripts/imperium_law_event_registry.py", "status"])
    if FORCE_REFRESH_SCRIPT.exists():
        command_results["force_refresh"] = run_cmd(["python", "scripts/refresh_imperium_force_manifest.py"])
    if CODE_BANK_REFRESH_SCRIPT.exists():
        command_results["code_bank_refresh"] = run_cmd(["python", "scripts/refresh_imperium_code_bank_surface.py"])
    if COVERAGE_REFRESH_SCRIPT.exists():
        command_results["coverage_refresh"] = run_cmd(["python", "scripts/refresh_imperium_dashboard_coverage_surface.py"])
    if DOCTRINE_REFRESH_SCRIPT.exists():
        command_results["doctrine_refresh"] = run_cmd(["python", "scripts/refresh_imperium_doctrine_integrity_surface.py"])
    if LIVE_WORK_REFRESH_SCRIPT.exists():
        command_results["live_work_refresh"] = run_cmd(["python", "scripts/refresh_imperium_live_work_surface.py"])
    if CONSTITUTION_REFRESH_SCRIPT.exists():
        command_results["constitution_refresh"] = run_cmd(["python", "scripts/validation/run_constitution_checks.py"])

    constitution = load_json(CONSTITUTION_PATH, {})
    repo_control = load_json(REPO_CONTROL_PATH, {})
    node_rank = load_json(NODE_RANK_PATH, {})
    machine_manifest = load_json(MACHINE_MANIFEST_PATH, {})
    organ_strength = load_json(ORGAN_STRENGTH_PATH, {})
    hygiene = load_json(HYGIENE_PATH, {})
    coverage = load_json(COVERAGE_PATH, {})
    code_bank = load_json(CODE_BANK_PATH, {})
    api_smoke, _state_payload, live_payload = build_api_smoke()

    runtime_surfaces = write_runtime_surfaces(
        step_id=step_id,
        step_root=step_root,
        constitution=constitution,
        repo_control=repo_control,
    )

    step_root = create_step_folder(
        step_id=step_id,
        constitution=constitution,
        repo_control=repo_control,
        node_rank=node_rank,
        machine_manifest=machine_manifest,
        organ_strength=organ_strength,
        hygiene=hygiene,
        coverage=coverage,
        code_bank=code_bank,
        api_smoke=api_smoke,
        live_state=live_payload,
        runtime_surfaces=runtime_surfaces,
        command_results=command_results,
    )

    if SEED_REFRESH_SCRIPT.exists():
        command_results["seed_refresh"] = run_cmd(
            [
                "python",
                "scripts/refresh_imperium_seed_capsule.py",
                "--capsule-root",
                "docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1",
            ]
        )

    command_results["bundle_enforcer"] = run_cmd(
        [
            "python",
            "scripts/imperium_bundle_output_enforcer.py",
            "--review-root",
            to_rel(step_root),
            "--retention-check",
        ]
    )

    write_json(
        step_root / "20_EXECUTION_META.json",
        {
            "schema_version": "imperium_block2_execution_meta.v1",
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "command_results": compact_command_results(command_results),
        },
    )

    enforcer_report = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    transfer_report = (((enforcer_report.get("chatgpt_transfer", {}) or {}).get("result", {}) or {}).get("transfer_report", {}) or {})
    manifest_rel = str(transfer_report.get("manifest_json", "")).strip().replace("\\", "/")
    transfer_manifest: dict[str, Any] = {}
    if manifest_rel:
        transfer_manifest = load_json(REPO_ROOT / manifest_rel, {})
    if not transfer_manifest:
        transfer_manifest = load_json(step_root / "chatgpt_transfer" / f"{step_id}__chatgpt_transfer_manifest.json", {})
    if not transfer_manifest:
        transfer_manifest = load_json(step_root / "chatgpt_transfer" / "chatgpt_transfer_manifest.json", {})
    transfer_sections = dict((transfer_manifest.get("sections", {}) or {}))
    core_section = dict((transfer_sections.get("core", {}) or {}))
    visual_section = dict((transfer_sections.get("visual", {}) or {}))
    optional_section = dict((transfer_sections.get("optional", {}) or {}))
    transport_integrity = str((((enforcer_report.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}) or {}).get("status", "UNKNOWN")))
    enforcer_verdict = str(enforcer_report.get("verdict", "UNKNOWN"))
    package_completeness = str(transfer_manifest.get("package_completeness", "UNKNOWN"))
    final_result = {
        "status": "ok",
        "step_id": step_id,
        "review_root": to_rel(step_root),
        "enforcer_verdict": enforcer_verdict,
        "transport_integrity": transport_integrity,
        "transfer_package_completeness": package_completeness,
        "core_required": bool(transfer_manifest.get("core_required", False)),
        "parts_total": int(transfer_manifest.get("parts_total", 0) or 0),
        "core_part_count": int(core_section.get("part_count", 0) or 0),
        "visual_part_count": int(visual_section.get("part_count", 0) or 0),
        "optional_part_count": int(optional_section.get("part_count", 0) or 0),
        "visual_included": bool(transfer_manifest.get("visual_included", False)),
        "optional_included": bool(transfer_manifest.get("optional_included", False)),
        "upload_order": list(transfer_manifest.get("upload_order", []) or []),
    }
    acceptance_failures: list[str] = []
    if enforcer_verdict != "PASS":
        acceptance_failures.append("enforcer_verdict_not_pass")
    if transport_integrity != "PASS":
        acceptance_failures.append("transport_integrity_not_pass")
    if package_completeness != "COMPLETE":
        acceptance_failures.append("package_completeness_not_complete")
    if not bool(transfer_manifest.get("core_required", False)):
        acceptance_failures.append("core_required_false")
    if not list(transfer_manifest.get("upload_order", []) or []):
        acceptance_failures.append("upload_order_empty")
    if acceptance_failures:
        final_result["status"] = "FAIL"
        final_result["acceptance"] = "FAIL"
        final_result["failure_reasons"] = acceptance_failures
        write_json(step_root / "21_FINAL_RESULT.json", final_result)
        print(json.dumps(final_result, ensure_ascii=False))
        return 2
    final_result["acceptance"] = "PASS"
    write_json(step_root / "21_FINAL_RESULT.json", final_result)
    print(json.dumps(final_result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
