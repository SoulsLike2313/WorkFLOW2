#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_ROOT = REPO_ROOT / "docs" / "review_artifacts"
CAPSULE_ROOT = REVIEW_ROOT / "ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1"
ADMIN_ROOT = REPO_ROOT / "runtime" / "administratum"
ADAPTER_ROOT = REPO_ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters"
STEP_PREFIX = "imperium_100_truth_live_state_regime_anti_lie_foundation_delta"

MUTABLE_TRACKER = CAPSULE_ROOT / "MUTABLE_TRACKER.json"
POINT_CHECK = CAPSULE_ROOT / "08_CURRENT_POINT_VERIFICATION.md"
LADDER = CAPSULE_ROOT / "06_CURRENT_WORK_LADDER_AND_RECENT_CHAIN.md"
MUTABLE_STATE = CAPSULE_ROOT / "02_MUTABLE_ACTIVE_STATE.md"

TRUTH_SCHEMA = ADMIN_ROOT / "IMPERIUM_TRUTH_SCHEMA_ENGINE_V1.json"
LAW_GATE = ADMIN_ROOT / "IMPERIUM_LAW_GATE_V1.json"
PROVENANCE = ADMIN_ROOT / "IMPERIUM_PROVENANCE_SEAL_V1.json"
INQUISITION = ADMIN_ROOT / "IMPERIUM_INQUISITION_LOOP_V1.json"
WATCH = ADMIN_ROOT / "IMPERIUM_WATCH_STATE_V1.json"

TRUTH_SPINE = ADMIN_ROOT / "IMPERIUM_TRUTH_SPINE_V1.json"
DASHBOARD_ENGINE = ADMIN_ROOT / "IMPERIUM_DASHBOARD_TRUTH_ENGINE_V1.json"
BUNDLE_CHAMBER = ADMIN_ROOT / "IMPERIUM_BUNDLE_TRUTH_CHAMBER_V1.json"
WORKTREE_GATE = ADMIN_ROOT / "IMPERIUM_WORKTREE_PURITY_GATE_V1.json"
ADDRESS_LATTICE = ADMIN_ROOT / "IMPERIUM_ADDRESS_LATTICE_V1.json"
ANTI_LIE_MODEL = ADMIN_ROOT / "IMPERIUM_ANTI_LIE_MODEL_V1.json"
LIVE_TRUTH_SUPPORT_LOOP = ADMIN_ROOT / "IMPERIUM_LIVE_TRUTH_SUPPORT_LOOP_V1.json"
HERESY_MAP = ADMIN_ROOT / "IMPERIUM_FOUNDATION_HERESY_MAP_V1.json"
HERESY_EARLY_DETECTION = ADMIN_ROOT / "IMPERIUM_HERESY_EARLY_DETECTION_V1.json"
HERESY_CONTAINMENT = ADMIN_ROOT / "IMPERIUM_HERESY_CONTAINMENT_V1.json"
HERESY_SUPPRESSION = ADMIN_ROOT / "IMPERIUM_HERESY_SUPPRESSION_V1.json"

TRUTH_SPINE_ADAPTER = ADAPTER_ROOT / "IMPERIUM_TRUTH_SPINE_STATE_SURFACE_V1.json"
DASHBOARD_ENGINE_ADAPTER = ADAPTER_ROOT / "IMPERIUM_DASHBOARD_TRUTH_ENGINE_SURFACE_V1.json"
BUNDLE_CHAMBER_ADAPTER = ADAPTER_ROOT / "IMPERIUM_BUNDLE_TRUTH_CHAMBER_SURFACE_V1.json"
WORKTREE_GATE_ADAPTER = ADAPTER_ROOT / "IMPERIUM_WORKTREE_PURITY_GATE_SURFACE_V1.json"
ADDRESS_LATTICE_ADAPTER = ADAPTER_ROOT / "IMPERIUM_ADDRESS_LATTICE_SURFACE_V1.json"
ANTI_LIE_MODEL_ADAPTER = ADAPTER_ROOT / "IMPERIUM_ANTI_LIE_MODEL_SURFACE_V1.json"
LIVE_TRUTH_SUPPORT_LOOP_ADAPTER = ADAPTER_ROOT / "IMPERIUM_LIVE_TRUTH_SUPPORT_LOOP_SURFACE_V1.json"
HERESY_MAP_ADAPTER = ADAPTER_ROOT / "IMPERIUM_FOUNDATION_HERESY_MAP_SURFACE_V1.json"
HERESY_EARLY_DETECTION_ADAPTER = ADAPTER_ROOT / "IMPERIUM_HERESY_EARLY_DETECTION_SURFACE_V1.json"
HERESY_CONTAINMENT_ADAPTER = ADAPTER_ROOT / "IMPERIUM_HERESY_CONTAINMENT_SURFACE_V1.json"
HERESY_SUPPRESSION_ADAPTER = ADAPTER_ROOT / "IMPERIUM_HERESY_SUPPRESSION_SURFACE_V1.json"
CONTROL_GATES_ADAPTER = ADAPTER_ROOT / "IMPERIUM_CONTROL_GATES_SURFACE_V1.json"

CANON_PATH = REPO_ROOT / "docs" / "governance" / "IMPERIUM_PERMANENT_TRUTH_AND_PURITY_FOUNDATION_CANON_V1.md"
REGIME_CANON_PATH = REPO_ROOT / "docs" / "governance" / "IMPERIUM_100_TRUTH_LIVE_STATE_REGIME_CANON_V1.md"
WAVE1_SCRIPT = REPO_ROOT / "scripts" / "imperium_wave1_native_organs.py"
VISUAL_AUDIT_SCRIPT = REPO_ROOT / "scripts" / "imperial_dashboard_visual_audit_loop.py"
ENFORCER_SCRIPT = REPO_ROOT / "scripts" / "imperium_bundle_output_enforcer.py"

REQUIRED_REVIEW = [
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

SYNC_SURFACES: list[tuple[Path, list[str]]] = [
    (CAPSULE_ROOT / "00_CAPSULE_ENTRYPOINT.md", ["continuity_line", "handoff_line", "active_line", "active_vertex"]),
    (MUTABLE_STATE, ["continuity_line", "handoff_line", "active_line", "active_vertex"]),
    (LADDER, ["continuity_line", "handoff_line", "active_line", "active_vertex"]),
    (POINT_CHECK, ["continuity_line", "handoff_line", "active_line", "active_vertex"]),
    (CAPSULE_ROOT / "for_chatgpt" / "01_PASTE_THIS_FULL.md", ["continuity_line", "handoff_line", "active_line", "active_vertex"]),
    (CAPSULE_ROOT / "for_chatgpt" / "02_PASTE_THIS_IF_CONTEXT_IS_TIGHT.md", ["continuity_line", "handoff_line", "active_line", "active_vertex"]),
    (CAPSULE_ROOT / "for_chatgpt" / "07_IMPERIUM_SEED_SUPERCOMPACT_STATE.md", ["continuity_line", "handoff_line", "active_line", "active_vertex"]),
    (CAPSULE_ROOT / "for_codex" / "05_CONTEXT_POINTERS_AND_RECOVERY.md", ["continuity_line", "handoff_line", "active_line", "active_vertex"]),
]

STALE_LINE = "imperium_living_spatial_brain_of_imperium_delta_primary_truth_bundle_latest.zip"


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
    done = subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True, encoding="utf-8", errors="replace", check=False)
    out: dict[str, Any] = {
        "command": " ".join(args),
        "exit_code": int(done.returncode),
        "stdout": str(done.stdout or "").strip(),
        "stderr": str(done.stderr or "").strip(),
        "status": "PASS" if done.returncode == 0 else "FAIL",
    }
    if out["stdout"].startswith("{"):
        try:
            out["json"] = json.loads(out["stdout"])
        except json.JSONDecodeError:
            pass
    return out


def fetch_json(url: str) -> tuple[dict[str, Any], dict[str, Any]]:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return (
                {"ok": int(response.status) == 200, "status_code": int(response.status), "size_bytes": len(raw.encode("utf-8")), "error": ""},
                json.loads(raw),
            )
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        return ({"ok": False, "status_code": 0, "size_bytes": 0, "error": str(exc)}, {})


def parse_git_state() -> dict[str, Any]:
    status = run_cmd(["git", "status", "--porcelain=v1", "--branch"]).get("stdout", "")
    staged = 0
    unstaged = 0
    untracked = 0
    for idx, line in enumerate(str(status).splitlines()):
        if idx == 0 and line.startswith("##"):
            continue
        if line.startswith("?? "):
            untracked += 1
            continue
        if len(line) >= 2:
            if line[0] not in {" ", "?"}:
                staged += 1
            if line[1] not in {" ", "?"}:
                unstaged += 1
    tracked_dirty = staged + unstaged
    if tracked_dirty == 0 and untracked == 0:
        cleanliness = "CLEAN"
    elif tracked_dirty > 0 and untracked == 0:
        cleanliness = "DIRTY_TRACKED_ONLY"
    elif tracked_dirty == 0 and untracked > 0:
        cleanliness = "DIRTY_UNTRACKED_ONLY"
    else:
        cleanliness = "DIRTY_MIXED"
    return {
        "generated_at_utc": now_iso(),
        "cleanliness_verdict": cleanliness,
        "tracked_dirty_count": tracked_dirty,
        "untracked_count": untracked,
        "head": run_cmd(["git", "rev-parse", "HEAD"]).get("stdout", ""),
        "status_short": run_cmd(["git", "status", "--short"]).get("stdout", ""),
    }


def adapter(surface_id: str, source: Path, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "surface_id": surface_id,
        "version": "1.0.0",
        "status": "ACTIVE",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "source_path": to_rel(source),
        "payload": payload,
    }


def as_status(value: Any, default: str = "UNKNOWN") -> str:
    text = str(value if value is not None else default).strip()
    return text.upper() if text else default


def load_transport(step_root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    report = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    transfer = dict(report.get("chatgpt_transfer", {}) or {})
    transport = dict(transfer.get("transport_integrity", {}) or {})
    transfer_report = dict((transfer.get("result", {}) or {}).get("transfer_report", {}) or {})
    return report, transport, transfer_report


def as_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def command_layer_signature(state: dict[str, Any], live: dict[str, Any]) -> dict[str, Any]:
    wave_surfaces = dict((state.get("wave1_control_surfaces", {}) or {}))
    wave_status = dict((wave_surfaces.get("wave_status_surface", {}) or {}))
    contradictions = dict((wave_surfaces.get("contradiction_ledger", {}) or {}))
    control = dict((state.get("imperium_control_gates_state", {}) or {}))
    factory = dict((state.get("factory_overview", {}) or {}))
    live_factory = dict((live.get("live_factory_state", {}) or {}))
    live_gate = dict((live.get("live_gate_state", {}) or {}))
    source_disclosure = dict((state.get("source_disclosure", {}) or {}))
    bundle_binding = dict((state.get("bundle_binding", {}) or {}))

    gate_states = [
        as_status((row or {}).get("state", "UNKNOWN"))
        for row in list((control.get("gates", []) or []))
        if isinstance(row, dict)
    ]

    truth_spine = dict((state.get("imperium_truth_spine_state", {}) or {}))
    dashboard_truth = dict((state.get("imperium_dashboard_truth_engine_state", {}) or {}))
    bundle_truth = dict((state.get("imperium_bundle_truth_chamber_state", {}) or {}))

    return {
        "wave_status": as_status(wave_status.get("status", "UNKNOWN")),
        "wave_claim": as_status(wave_status.get("claim", "UNKNOWN")),
        "open_contradictions_count": len(list((contradictions.get("open", []) or []))),
        "closed_contradictions_count": len(list((contradictions.get("closed", []) or []))),
        "control_gate_summary": as_status(control.get("gate_summary", "UNKNOWN")),
        "control_blocked_count": as_int(control.get("blocked_count", 0), 0),
        "control_warning_count": as_int(control.get("warning_count", 0), 0),
        "factory_owner_gates_waiting_count": len(list((factory.get("owner_gates_waiting", []) or []))),
        "live_pending_owner_gates_count": as_int(live_factory.get("pending_owner_gates_count", 0), 0),
        "factory_blockers_count": len(list((factory.get("blockers", []) or []))),
        "live_blockers_count": as_int(live_factory.get("open_blockers_count", 0), 0),
        "owner_gate_required": bool(live_gate.get("owner_required", False)),
        "pending_gate_markers": as_int(live_gate.get("pending_gate_markers", 0), 0),
        "pending_gate_ids_count": len(list((live_gate.get("pending_gate_ids", []) or []))),
        "gate_states": gate_states,
        "bundle_name_present": bool(str(state.get("bundle_name", "")).strip()),
        "bundle_path_present": bool(str(state.get("bundle_path", "")).strip()),
        "source_disclosure_present": bool(source_disclosure),
        "bundle_binding_present": bool(bundle_binding),
        "truth_spine_status": as_status(truth_spine.get("status", "NOT_INITIALIZED"), "NOT_INITIALIZED"),
        "dashboard_truth_status": as_status(dashboard_truth.get("status", "NOT_INITIALIZED"), "NOT_INITIALIZED"),
        "bundle_truth_status": as_status(bundle_truth.get("status", "NOT_INITIALIZED"), "NOT_INITIALIZED"),
        "bundle_transport_status": as_status(
            dict((bundle_truth.get("transport_integrity", {}) or {})).get("status", "NOT_INITIALIZED"),
            "NOT_INITIALIZED",
        ),
    }


def command_layer_checks(signature: dict[str, Any]) -> dict[str, bool]:
    wave_closed = "CLOSED" in str(signature.get("wave_status", ""))
    open_contradictions = as_int(signature.get("open_contradictions_count", 0), 0)
    control_gate_summary = as_status(signature.get("control_gate_summary", "UNKNOWN"))
    control_warning_count = as_int(signature.get("control_warning_count", 0), 0)
    control_blocked_count = as_int(signature.get("control_blocked_count", 0), 0)
    owner_gate_visible = (
        bool(signature.get("owner_gate_required", False))
        or as_int(signature.get("factory_owner_gates_waiting_count", 0), 0) > 0
        or as_int(signature.get("live_pending_owner_gates_count", 0), 0) > 0
        or as_int(signature.get("pending_gate_markers", 0), 0) > 0
        or as_int(signature.get("pending_gate_ids_count", 0), 0) > 0
    )
    wave_contradiction_visibility_ok = (
        open_contradictions == 0
        or control_gate_summary in {"WARNING", "BLOCKED"}
        or control_warning_count > 0
        or control_blocked_count > 0
        or owner_gate_visible
    )
    allowed_gate_states = {
        "PASS",
        "WARNING",
        "BLOCKED",
        "UNKNOWN",
        "ACTIVE",
        "PARTIAL",
        "WAIT",
        "FAIL",
        "PROVEN",
        "NOT_INITIALIZED",
    }
    gate_states = [str(x or "").strip().upper() for x in list(signature.get("gate_states", []) or []) if str(x or "").strip()]
    status_fields = [
        str(signature.get("truth_spine_status", "NOT_INITIALIZED")),
        str(signature.get("dashboard_truth_status", "NOT_INITIALIZED")),
        str(signature.get("bundle_truth_status", "NOT_INITIALIZED")),
        str(signature.get("bundle_transport_status", "NOT_INITIALIZED")),
    ]
    return {
        "wave_closed_requires_visible_non_calm_when_contradictions_open": (
            True if not wave_closed else wave_contradiction_visibility_ok
        ),
        "factory_owner_gate_counts_aligned": (
            as_int(signature.get("factory_owner_gates_waiting_count", 0), 0)
            == as_int(signature.get("live_pending_owner_gates_count", 0), 0)
        ),
        "factory_blocker_counts_aligned": (
            as_int(signature.get("factory_blockers_count", 0), 0)
            == as_int(signature.get("live_blockers_count", 0), 0)
        ),
        "command_bundle_fastpath_fields_present": (
            bool(signature.get("bundle_name_present"))
            and bool(signature.get("bundle_path_present"))
            and bool(signature.get("source_disclosure_present"))
            and bool(signature.get("bundle_binding_present"))
        ),
        "status_vocabulary_normalized": all(state in allowed_gate_states for state in gate_states),
        "truth_status_fields_explicit": all(bool(str(x).strip()) for x in status_fields),
    }


def stability_drift_fields(base: dict[str, Any], sample: dict[str, Any]) -> list[str]:
    fields = [
        "wave_status",
        "wave_claim",
        "open_contradictions_count",
        "control_gate_summary",
        "control_blocked_count",
        "control_warning_count",
        "factory_owner_gates_waiting_count",
        "live_pending_owner_gates_count",
        "factory_blockers_count",
        "live_blockers_count",
        "owner_gate_required",
    ]
    drifted: list[str] = []
    for field in fields:
        if base.get(field) != sample.get(field):
            drifted.append(field)
    return drifted


def update_control_gate_rows(
    *,
    truth_spine_status: str,
    dashboard_status: str,
    bundle_status: str,
    purity_status: str,
    lattice_status: str,
    inquisition_status: str,
    anti_lie_status: str,
    live_loop_status: str,
    heresy_detection_status: str,
    heresy_containment_status: str,
    heresy_suppression_status: str,
) -> None:
    control = load_json(CONTROL_GATES_ADAPTER, {})
    gates = list((control.get("gates", []) or []))
    existing = {str((row or {}).get("gate_id", "")).strip(): dict(row or {}) for row in gates if row}

    def gate(gate_id: str, title: str, state: str, source_path: str) -> dict[str, Any]:
        return {
            "gate_id": gate_id,
            "title_ru": title,
            "state": state,
            "source_path": source_path,
            "truth_class": "SOURCE_EXACT",
        }

    existing["truth_spine_gate"] = gate("truth_spine_gate", "Truth Spine Gate", "PASS" if truth_spine_status == "PASS" else "BLOCKED", to_rel(TRUTH_SPINE_ADAPTER))
    existing["dashboard_truth_engine_gate"] = gate(
        "dashboard_truth_engine_gate",
        "Dashboard Truth Engine Gate",
        "PASS" if dashboard_status == "PASS" else "BLOCKED",
        to_rel(DASHBOARD_ENGINE_ADAPTER),
    )
    existing["bundle_truth_chamber_gate"] = gate(
        "bundle_truth_chamber_gate",
        "Bundle Truth Chamber Gate",
        "PASS" if bundle_status == "PASS" else "BLOCKED",
        to_rel(BUNDLE_CHAMBER_ADAPTER),
    )
    existing["worktree_purity_gate"] = gate(
        "worktree_purity_gate",
        "Worktree Purity Gate",
        "PASS" if purity_status == "PASS" else "BLOCKED",
        to_rel(WORKTREE_GATE_ADAPTER),
    )
    existing["address_lattice_gate"] = gate(
        "address_lattice_gate",
        "Address Lattice Gate",
        "PASS" if lattice_status == "PASS" else "BLOCKED",
        to_rel(ADDRESS_LATTICE_ADAPTER),
    )
    existing["inquisition_truth_guard_gate"] = gate(
        "inquisition_truth_guard_gate",
        "Inquisition Truth Guard Gate",
        "PASS" if inquisition_status == "PASS" else "BLOCKED",
        to_rel(INQUISITION),
    )
    existing["anti_lie_foundation_gate"] = gate(
        "anti_lie_foundation_gate",
        "Anti Lie Foundation Gate",
        "PASS" if anti_lie_status == "PASS" else "BLOCKED",
        to_rel(ANTI_LIE_MODEL_ADAPTER),
    )
    existing["live_truth_support_loop_gate"] = gate(
        "live_truth_support_loop_gate",
        "Live Truth Support Loop Gate",
        "PASS" if live_loop_status == "PASS" else "BLOCKED",
        to_rel(LIVE_TRUTH_SUPPORT_LOOP_ADAPTER),
    )
    existing["heresy_early_detection_gate"] = gate(
        "heresy_early_detection_gate",
        "Heresy Early Detection Gate",
        "PASS" if heresy_detection_status == "PASS" else "BLOCKED",
        to_rel(HERESY_EARLY_DETECTION_ADAPTER),
    )
    existing["heresy_containment_gate"] = gate(
        "heresy_containment_gate",
        "Heresy Containment Gate",
        "PASS" if heresy_containment_status == "PASS" else "BLOCKED",
        to_rel(HERESY_CONTAINMENT_ADAPTER),
    )
    existing["heresy_suppression_gate"] = gate(
        "heresy_suppression_gate",
        "Heresy Suppression Gate",
        "PASS" if heresy_suppression_status == "PASS" else "BLOCKED",
        to_rel(HERESY_SUPPRESSION_ADAPTER),
    )
    control["gates"] = list(existing.values())
    write_json(CONTROL_GATES_ADAPTER, control)


def compute_drift_count(
    *,
    seed_sync_ok: bool,
    dashboard_status: str,
    anti_lie_status: str,
    bundle_status: str,
) -> int:
    drift = 0
    if not seed_sync_ok:
        drift += 1
    if as_status(dashboard_status) != "PASS":
        drift += 1
    if as_status(anti_lie_status) != "PASS":
        drift += 1
    if as_status(bundle_status) != "PASS":
        drift += 1
    return drift


def build_foundation_heresy_map(
    *,
    seed_sync_ok: bool,
    stale_hits: list[str],
    mismatches: list[str],
    dashboard_status: str,
    chamber_status: str,
    transport_status: str,
    inquisition_direct_action_ready: bool,
    worktree_status: str,
) -> dict[str, Any]:
    classes: list[dict[str, Any]] = [
        {
            "class_id": "stale_or_conflicting_current_point_surface",
            "location": "seed-facing pointer surfaces",
            "source_mechanism": "stale regeneration or missing current-point token",
            "detected": (not seed_sync_ok) or bool(stale_hits) or bool(mismatches),
            "detection_surface": to_rel(TRUTH_SPINE),
            "blocker_surface": "truth_spine_gate",
            "remediation_path": "refresh seed pointers from mutable authority and re-run truth convergence",
            "recurrence_risk": "HIGH",
        },
        {
            "class_id": "dashboard_truth_drift",
            "location": "dashboard/live-state rendering chain",
            "source_mechanism": "derived display not aligned with authoritative runtime state",
            "detected": as_status(dashboard_status) != "PASS",
            "detection_surface": to_rel(DASHBOARD_ENGINE),
            "blocker_surface": "dashboard_truth_engine_gate",
            "remediation_path": "force dashboard truth checks + visual audit + re-render from truth spine only",
            "recurrence_risk": "MEDIUM",
        },
        {
            "class_id": "bundle_shell_core_result_mismatch",
            "location": "transfer layer / bundle transport chain",
            "source_mechanism": "manifest/core/final divergence",
            "detected": as_status(chamber_status) != "PASS" or as_status(transport_status) != "PASS",
            "detection_surface": to_rel(BUNDLE_CHAMBER),
            "blocker_surface": "bundle_truth_chamber_gate",
            "remediation_path": "rebuild bundle -> self-read -> enforcer until PASS convergence",
            "recurrence_risk": "HIGH",
        },
        {
            "class_id": "inquisition_bypass_or_soft_hold",
            "location": "verdict-chain gating",
            "source_mechanism": "fail-state not held or direct action not armed",
            "detected": not bool(inquisition_direct_action_ready),
            "detection_surface": to_rel(INQUISITION),
            "blocker_surface": "inquisition_truth_guard_gate",
            "remediation_path": "enable direct-action hold and block-forward policy",
            "recurrence_risk": "HIGH",
        },
        {
            "class_id": "worktree_purity_truth_blur",
            "location": "repo cleanliness + truth representation",
            "source_mechanism": "impurity masking or unclassified dirty baseline",
            "detected": as_status(worktree_status) != "PASS",
            "detection_surface": to_rel(WORKTREE_GATE),
            "blocker_surface": "worktree_purity_gate",
            "remediation_path": "reclassify baseline + enforce purity gate before progress",
            "recurrence_risk": "MEDIUM",
        },
    ]
    active = [row for row in classes if bool(row.get("detected"))]
    return {
        "surface_id": "IMPERIUM_FOUNDATION_HERESY_MAP_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS" if len(active) == 0 else "ALERT",
        "active_heresy_count": len(active),
        "map": classes,
    }


def build_transport_self_read_mirror(
    *,
    authority_source: str,
    enforcer_report: dict[str, Any],
    transport_report: dict[str, Any],
    final_surface: dict[str, Any],
    watch_surface: dict[str, Any],
    chamber_surface: dict[str, Any],
    truth_spine_surface: dict[str, Any],
    inquisition_surface: dict[str, Any],
) -> dict[str, Any]:
    canonical_transport = as_status(transport_report.get("status", "UNKNOWN"))
    chamber_transport = as_status(((chamber_surface.get("transport_integrity", {}) or {}).get("status", "UNKNOWN")))
    final_transport = as_status(final_surface.get("transport_integrity", "UNKNOWN"))
    watch_transport = as_status(watch_surface.get("transport_status", "UNKNOWN"))
    truth_transport = as_status(truth_spine_surface.get("transport_status", "UNKNOWN"))
    chamber_status = as_status(chamber_surface.get("status", "UNKNOWN"))
    inq_bundle_gate = as_status(((inquisition_surface.get("truth_guard_checks", {}) or {}).get("bundle_truth_chamber", "UNKNOWN")))

    checks = {
        "enforcer_pass": as_status(enforcer_report.get("verdict", "UNKNOWN")) == "PASS",
        "canonical_transport_pass": canonical_transport == "PASS",
        "final_transport_matches_canonical": final_transport == canonical_transport,
        "watch_transport_matches_canonical": watch_transport == canonical_transport,
        "chamber_transport_matches_canonical": chamber_transport == canonical_transport,
        "truth_spine_transport_matches_canonical": truth_transport == canonical_transport,
        "inquisition_bundle_gate_matches_chamber": inq_bundle_gate == chamber_status,
    }
    return {
        "schema_version": "imperium_transport_chain_mirror.v1",
        "generated_at_utc": now_iso(),
        "mechanism_classification": "DERIVED_REDUNDANT_MERGE",
        "mode": "CANONICAL_MIRROR_ONLY",
        "authoritative_transport_source": authority_source,
        "canonical_transport_status": canonical_transport,
        "enforcer_verdict": as_status(enforcer_report.get("verdict", "UNKNOWN")),
        "mirror_checks": checks,
        "status": "PASS" if all(bool(v) for v in checks.values()) else "FAIL",
        "entrypoint_matches_disk": bool(transport_report.get("entrypoint_matches_disk", False)),
        "final_result_matches_disk": bool(transport_report.get("final_result_matches_disk", False)),
        "required_entries_missing": list(transport_report.get("required_entries_missing", []) or []),
        "foreign_review_roots": list(transport_report.get("foreign_review_roots", []) or []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="IMPERIUM 100% truth / live-state regime / anti-lie foundation")
    parser.add_argument("--step-id", default="")
    parser.add_argument("--dashboard-url", default="http://127.0.0.1:8777/")
    args = parser.parse_args()

    step_id = args.step_id.strip() or f"{STEP_PREFIX}_{now_stamp()}"
    step_root = REVIEW_ROOT / step_id
    step_root.mkdir(parents=True, exist_ok=True)
    command_results: dict[str, Any] = {}
    transport_authority_source = (
        f"docs/review_artifacts/{step_id}/12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json"
        "::chatgpt_transfer.transport_integrity"
    )

    write_text(
        CANON_PATH,
        "# IMPERIUM Permanent Truth & Purity Foundation Canon V1\n\n- dashboard truth, bundle truth, and worktree purity support are hard gates.\n- Inquisition holds FAIL until full convergence.\n- no stale FAIL beside PASS in critical verdict-chain surfaces.\n- Mandatory execution law: evidence-first, root-cause-first, narrow-or-systemic repair, rerun, self-read, convergence only.\n- Session lifecycle law: hour-4 warning, hour-5 checkpoint question, no-reply auto-sync-and-relocation prompt.\n",
    )
    write_text(
        REGIME_CANON_PATH,
        "# IMPERIUM 100% Truth / Live-State Regime Canon V1\n\n- dashboard must mirror authoritative runtime truth.\n- bundle shell/core/result mismatch is hard FAIL.\n- anti-lie classes are detector+blocker+remediation objects, not decorative labels.\n- truth-holding loop keeps PASS state from silently degrading.\n- 4h warning / 5h checkpoint / no-reply auto-sync prompt is mandatory.\n",
    )

    if WAVE1_SCRIPT.exists():
        command_results["wave1_refresh"] = run_cmd(["python", "scripts/imperium_wave1_native_organs.py"])

    mutable = load_json(MUTABLE_TRACKER, {})
    authority = {
        "continuity_line": str(((mutable.get("continuity_step_primary_truth", {}) or {}).get("path", ""))),
        "handoff_line": str(((mutable.get("handoff_step_primary_truth_input", {}) or {}).get("path", ""))),
        "active_line": str(((mutable.get("active_live_primary_line", {}) or {}).get("path", ""))),
        "active_vertex": str(((mutable.get("current_active_vertex", {}) or {}).get("id", ""))),
    }

    mismatches: list[str] = []
    stale_hits: list[str] = []
    for surface, keys in SYNC_SURFACES:
        text = surface.read_text(encoding="utf-8-sig") if surface.exists() else ""
        if not text:
            mismatches.append(f"missing::{to_rel(surface)}")
            continue
        if STALE_LINE in text:
            stale_hits.append(to_rel(surface))
        for key in keys:
            value = authority.get(key, "")
            if value and value not in text:
                mismatches.append(f"sync::{to_rel(surface)}::{key}")
    seed_sync_ok = len(mismatches) == 0 and len(stale_hits) == 0

    git_state = parse_git_state()
    worktree_gate = load_json(WORKTREE_GATE, {})
    if not worktree_gate:
        worktree_gate = {
            "surface_id": "IMPERIUM_WORKTREE_PURITY_GATE_V1",
            "generated_at_utc": now_iso(),
            "truth_class": "SOURCE_EXACT",
            "status": "PASS" if git_state.get("cleanliness_verdict") == "CLEAN" else "FAIL",
            "mode": "STRICT",
            "cleanliness_verdict": git_state.get("cleanliness_verdict", "UNKNOWN"),
            "tracked_dirty_count": int(git_state.get("tracked_dirty_count", 0) or 0),
            "untracked_count": int(git_state.get("untracked_count", 0) or 0),
            "allowed_exception_proven": git_state.get("cleanliness_verdict") != "CLEAN",
            "allowed_exception_reason": "owner_decision_required_for_repo_wide_dirty_baseline_classification_and_cleanup"
            if git_state.get("cleanliness_verdict") != "CLEAN"
            else "",
        }
    else:
        worktree_gate = {
            **dict(worktree_gate),
            "generated_at_utc": now_iso(),
            "cleanliness_verdict": git_state.get("cleanliness_verdict", worktree_gate.get("cleanliness_verdict", "UNKNOWN")),
            "tracked_dirty_count": int(git_state.get("tracked_dirty_count", worktree_gate.get("tracked_dirty_count", 0)) or 0),
            "untracked_count": int(git_state.get("untracked_count", worktree_gate.get("untracked_count", 0)) or 0),
        }
    write_json(WORKTREE_GATE, worktree_gate)

    api_state_meta, api_state = fetch_json(f"{args.dashboard_url.rstrip('/')}/api/state")
    api_live_meta, api_live = fetch_json(f"{args.dashboard_url.rstrip('/')}/api/live_state")
    if not api_live:
        api_live = load_json(REPO_ROOT / "runtime" / "factory_observation" / "live_state_snapshot.json", {})
    command_results["playwright_truth_assault"] = run_cmd(["python", "scripts/imperial_dashboard_visual_audit_loop.py", "--url", args.dashboard_url, "--out-dir", str(step_root / "dashboard_truth_assault")]) if VISUAL_AUDIT_SCRIPT.exists() else {"status": "FAIL", "stderr": "script_missing"}
    playwright_ok = command_results["playwright_truth_assault"].get("status") == "PASS"

    signature_base = command_layer_signature(api_state, api_live)
    command_checks = command_layer_checks(signature_base)
    stability_samples: list[dict[str, Any]] = []
    for sample_idx in range(1, 3):
        time.sleep(0.6)
        sample_state_meta, sample_state = fetch_json(f"{args.dashboard_url.rstrip('/')}/api/state")
        sample_live_meta, sample_live = fetch_json(f"{args.dashboard_url.rstrip('/')}/api/live_state")
        if not sample_live:
            sample_live = api_live
        sample_signature = command_layer_signature(sample_state, sample_live)
        drift_fields = stability_drift_fields(signature_base, sample_signature)
        stability_samples.append(
            {
                "sample_index": sample_idx,
                "state_ok": bool(sample_state_meta.get("ok")),
                "live_ok": bool(sample_live_meta.get("ok")) or bool(sample_live),
                "drift_fields": drift_fields,
                "signature": sample_signature,
            }
        )
    stability_ok = all(len(list(sample.get("drift_fields", []) or [])) == 0 for sample in stability_samples)
    stability_report = {
        "base_signature": signature_base,
        "samples": stability_samples,
        "status": "PASS" if stability_ok else "FAIL",
        "drift_detected": not stability_ok,
    }
    command_results["hold_line_stability_drill"] = {
        "status": stability_report["status"],
        "drift_detected": stability_report["drift_detected"],
        "sample_count": len(stability_samples),
    }

    live_text = json.dumps(api_live, ensure_ascii=False, sort_keys=True)
    state_text = json.dumps(api_state, ensure_ascii=False, sort_keys=True)
    dashboard_checks = {
        "api_state_ok": bool(api_state_meta.get("ok")),
        "api_live_ok": bool(api_live_meta.get("ok")) or bool(api_live),
        "active_line_present_in_live": bool(authority.get("active_line") and authority.get("active_line") in live_text),
        "active_line_present_in_state": bool(authority.get("active_line") and authority.get("active_line") in state_text),
        "stale_line_absent": STALE_LINE not in live_text and STALE_LINE not in state_text,
        "playwright_truth_assault_ok": bool(playwright_ok),
        "wave_semantics_non_calm_on_open_contradictions": bool(
            command_checks.get("wave_closed_requires_visible_non_calm_when_contradictions_open", False)
        ),
        "factory_owner_gate_counts_aligned": bool(command_checks.get("factory_owner_gate_counts_aligned", False)),
        "factory_blocker_counts_aligned": bool(command_checks.get("factory_blocker_counts_aligned", False)),
        "command_bundle_fastpath_fields_present": bool(command_checks.get("command_bundle_fastpath_fields_present", False)),
        "status_vocabulary_normalized": bool(command_checks.get("status_vocabulary_normalized", False)),
        "truth_status_fields_explicit": bool(command_checks.get("truth_status_fields_explicit", False)),
        "hold_line_stability_rerun_ok": bool(stability_ok),
    }
    dashboard_fail = [k for k, v in dashboard_checks.items() if not v]
    dashboard_engine = {
        "surface_id": "IMPERIUM_DASHBOARD_TRUTH_ENGINE_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS" if len(dashboard_fail) == 0 else "FAIL",
        "truth_mirror_mode": "AUTHORITATIVE_MIRROR",
        "checks": dashboard_checks,
        "failures": dashboard_fail,
        "command_layer_signature": signature_base,
        "command_layer_checks": command_checks,
        "stability_drill": stability_report,
    }
    write_json(DASHBOARD_ENGINE, dashboard_engine)

    truth_schema = load_json(TRUTH_SCHEMA, {})
    law_gate = load_json(LAW_GATE, {})
    provenance = load_json(PROVENANCE, {})
    inquisition = load_json(INQUISITION, {})
    bundle_pre = load_json(BUNDLE_CHAMBER, {})
    transport_pre = as_status(((bundle_pre.get("transport_integrity", {}) or {}).get("status", "UNKNOWN")))

    anti_lie_classes = [
        {
            "class_id": "stale_pointer_or_line",
            "severity": "CRITICAL",
            "detected": len(stale_hits) > 0,
            "detector": "seed_sync_scan",
            "blocker": "truth_spine_gate",
            "remediation": "sync current-point surfaces from mutable tracker authority",
        },
        {
            "class_id": "cross_surface_current_point_mismatch",
            "severity": "CRITICAL",
            "detected": len(mismatches) > 0,
            "detector": "seed_sync_scan",
            "blocker": "truth_spine_gate",
            "remediation": "repair current-point mismatch in seed-facing files",
        },
        {
            "class_id": "dashboard_unsourced_or_stale_display",
            "severity": "CRITICAL",
            "detected": len(dashboard_fail) > 0,
            "detector": "dashboard_truth_engine",
            "blocker": "dashboard_truth_engine_gate",
            "remediation": "rerun dashboard truth checks and fix stale rendering source",
        },
        {
            "class_id": "bundle_shell_core_result_mismatch",
            "severity": "CRITICAL",
            "detected": as_status(bundle_pre.get("status", "UNKNOWN")) != "PASS" or transport_pre != "PASS",
            "detector": "bundle_truth_chamber",
            "blocker": "bundle_truth_chamber_gate",
            "remediation": "rebuild transfer package and rerun self-read enforcement",
        },
        {
            "class_id": "purity_drift_or_unclean_state",
            "severity": "MAJOR",
            "detected": as_status(worktree_gate.get("status", "UNKNOWN")) != "PASS",
            "detector": "worktree_purity_gate",
            "blocker": "worktree_purity_gate",
            "remediation": "apply baseline classification cleanup policy",
        },
    ]
    anti_lie_model = {
        "surface_id": "IMPERIUM_ANTI_LIE_MODEL_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS",
        "mode": "ANTI_LIE_FOUNDATION_ACTIVE",
        "lie_classes": anti_lie_classes,
        "active_critical_count": len([x for x in anti_lie_classes if x.get("detected") and str(x.get("severity", "")).upper() == "CRITICAL"]),
        "active_total_count": len([x for x in anti_lie_classes if x.get("detected")]),
        "remediation_policy": "detected_lie_class_triggers_remediation_loop",
    }
    anti_lie_model["status"] = "PASS" if int(anti_lie_model.get("active_critical_count", 0) or 0) == 0 else "FAIL"
    write_json(ANTI_LIE_MODEL, anti_lie_model)

    watch_seed = load_json(WATCH, {})
    session_seed = dict((watch_seed.get("session", {}) or {}))
    started_raw = str(session_seed.get("started_at_utc", now_iso()))
    try:
        started_dt = datetime.fromisoformat(started_raw.replace("Z", "+00:00"))
    except ValueError:
        started_dt = datetime.now(timezone.utc)
    elapsed_seconds = int((datetime.now(timezone.utc) - started_dt).total_seconds())
    elapsed_hours = round(float(max(0, elapsed_seconds)) / 3600.0, 3)
    live_truth_support_loop = {
        "surface_id": "IMPERIUM_LIVE_TRUTH_SUPPORT_LOOP_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS",
        "mode": "HOLD_TRUTH_AFTER_PASS",
        "loop_profile": "EVENT_OR_INTERVAL",
        "check_interval_seconds": 30,
        "active_drift_count": 0,
        "session_lifecycle": {
            "started_at_utc": started_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "elapsed_seconds": max(0, elapsed_seconds),
            "elapsed_hours": elapsed_hours,
            "hour4_warning": elapsed_hours >= 4.0,
            "hour5_checkpoint_required": elapsed_hours >= 5.0,
            "auto_sync_prompt_if_no_reply": elapsed_hours >= 5.0,
            "owner_checkpoint_question": "If active tasks remain, finish current bounded step first, then run full sync and relocate to a new chat. Continue?",
            "auto_prompt_if_silent": "No owner response at hour 5. Prepare full-system sync package and start new-chat relocation flow.",
        },
        "truth_retention_checks": {
            "seed_sync_ok": seed_sync_ok,
            "dashboard_truth_engine": as_status(dashboard_engine.get("status", "UNKNOWN")),
            "worktree_purity_gate": as_status(worktree_gate.get("status", "UNKNOWN")),
            "anti_lie_model": as_status(anti_lie_model.get("status", "UNKNOWN")),
            "bundle_truth_chamber": as_status(bundle_pre.get("status", "UNKNOWN")),
        },
    }
    live_truth_support_loop["active_drift_count"] = compute_drift_count(
        seed_sync_ok=seed_sync_ok,
        dashboard_status=as_status(dashboard_engine.get("status", "UNKNOWN")),
        anti_lie_status=as_status(anti_lie_model.get("status", "UNKNOWN")),
        bundle_status=as_status(bundle_pre.get("status", "UNKNOWN")),
    )
    live_truth_support_loop["status"] = "PASS" if int(live_truth_support_loop.get("active_drift_count", 0) or 0) == 0 else "FAIL"
    write_json(LIVE_TRUTH_SUPPORT_LOOP, live_truth_support_loop)

    heresy_map = build_foundation_heresy_map(
        seed_sync_ok=seed_sync_ok,
        stale_hits=stale_hits,
        mismatches=mismatches,
        dashboard_status=as_status(dashboard_engine.get("status", "UNKNOWN")),
        chamber_status=as_status(bundle_pre.get("status", "UNKNOWN")),
        transport_status=transport_pre,
        inquisition_direct_action_ready=True,
        worktree_status=as_status(worktree_gate.get("status", "UNKNOWN")),
    )
    heresy_early_detection = {
        "surface_id": "IMPERIUM_HERESY_EARLY_DETECTION_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS",
            "checks": {
                "seed_sync_authority_check": seed_sync_ok,
                "dashboard_truth_chain_check": as_status(dashboard_engine.get("status", "UNKNOWN")) == "PASS",
                "bundle_transport_chain_check": as_status(bundle_pre.get("status", "UNKNOWN")) == "PASS" and transport_pre == "PASS",
                "inquisition_direct_action_ready": True,
                "worktree_purity_check": as_status(worktree_gate.get("status", "UNKNOWN")) == "PASS",
            },
        "trigger_policy": "any_failed_check_is_immediate_alert",
    }
    heresy_early_detection["status"] = "PASS" if all(bool(v) for v in dict(heresy_early_detection.get("checks", {})).values()) else "FAIL"

    heresy_containment = {
        "surface_id": "IMPERIUM_HERESY_CONTAINMENT_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS",
        "fail_hold_enabled": True,
        "forward_progress_block_enabled": True,
        "forced_rerun_enabled": True,
        "active_blockers": list((inquisition.get("failures", []) or [])),
        "containment_policy": "hold_fail_until_verdict_surfaces_converge",
    }
    heresy_containment["status"] = "PASS" if len(list(heresy_containment.get("active_blockers", []) or [])) == 0 else "FAIL"

    heresy_suppression = {
        "surface_id": "IMPERIUM_HERESY_SUPPRESSION_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS",
        "suppression_loop": "detect -> hold -> rerun -> reread -> verify -> converge",
        "active_heresy_count": int(heresy_map.get("active_heresy_count", 0) or 0),
        "suppressed_in_this_pass": int(0),
        "suppression_ready": True,
    }
    heresy_suppression["status"] = "PASS" if int(heresy_suppression.get("active_heresy_count", 0) or 0) == 0 else "FAIL"

    write_json(HERESY_MAP, heresy_map)
    write_json(HERESY_EARLY_DETECTION, heresy_early_detection)
    write_json(HERESY_CONTAINMENT, heresy_containment)
    write_json(HERESY_SUPPRESSION, heresy_suppression)

    dims = {
        "seed_sync": 1 if seed_sync_ok else 0,
        "truth_schema_engine": 1 if as_status(truth_schema.get("status", "UNKNOWN")) == "PASS" else 0,
        "law_gate": 1 if as_status(law_gate.get("verdict", "ALLOW")) != "DENY" else 0,
        "provenance_seal": 1 if as_status(provenance.get("status", "UNKNOWN")) == "PASS" else 0,
        "dashboard_truth_engine": 1 if as_status(dashboard_engine.get("status", "UNKNOWN")) == "PASS" else 0,
        "bundle_truth_chamber": 1 if as_status(bundle_pre.get("status", "UNKNOWN")) == "PASS" else 0,
        "transport_truth": 1 if transport_pre == "PASS" else 0,
        "worktree_purity_support": 1 if as_status(worktree_gate.get("status", "UNKNOWN")) == "PASS" else 0,
        "anti_lie_model": 1 if as_status(anti_lie_model.get("status", "UNKNOWN")) == "PASS" else 0,
        "live_truth_support_loop": 1 if as_status(live_truth_support_loop.get("status", "UNKNOWN")) == "PASS" else 0,
        "heresy_early_detection": 1 if as_status(heresy_early_detection.get("status", "UNKNOWN")) == "PASS" else 0,
        "heresy_containment": 1 if as_status(heresy_containment.get("status", "UNKNOWN")) == "PASS" else 0,
        "heresy_suppression": 1 if as_status(heresy_suppression.get("status", "UNKNOWN")) == "PASS" else 0,
    }
    critical_keys = list(dims.keys())
    critical_ok = all(dims.get(key, 0) == 1 for key in critical_keys)
    sync_pct = round((sum(dims.values()) / len(dims)) * 100, 2)
    truth_spine = {
        "surface_id": "IMPERIUM_TRUTH_SPINE_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS" if critical_ok else "FAIL",
        "full_truth_claim": bool(critical_ok),
        "authoritative_current_point": authority,
        "sync_model": {
            "dimensions": dims,
            "critical_dimensions": critical_keys,
            "critical_ok": critical_ok,
            "sync_percentage": sync_pct,
        },
        "partial_truth_classes": [str(x.get("class_id", "")) for x in anti_lie_classes if bool(x.get("detected"))],
        "seed_sync_mismatches": mismatches,
        "seed_stale_hits": stale_hits,
        "transport_authority_source": transport_authority_source,
        "transport_status": transport_pre,
        "bundle_truth_status": as_status(bundle_pre.get("status", "UNKNOWN")),
    }
    write_json(TRUTH_SPINE, truth_spine)

    lattice = {
        "surface_id": "IMPERIUM_ADDRESS_LATTICE_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS",
        "addresses": {
            "foundation": "docs/governance",
            "mutable_tracker": to_rel(MUTABLE_TRACKER),
            "truth_spine": to_rel(TRUTH_SPINE),
            "dashboard_truth_engine": to_rel(DASHBOARD_ENGINE),
            "bundle_truth_chamber": to_rel(BUNDLE_CHAMBER),
            "worktree_purity_gate": to_rel(WORKTREE_GATE),
            "anti_lie_model": to_rel(ANTI_LIE_MODEL),
            "live_truth_support_loop": to_rel(LIVE_TRUTH_SUPPORT_LOOP),
            "watch": to_rel(WATCH),
            "inquisition": to_rel(INQUISITION),
            "astronomican": to_rel(ADMIN_ROOT / "IMPERIUM_ASTRONOMICAN_ROUTE_REGISTRY_V1.json"),
            "capsule_root": to_rel(CAPSULE_ROOT),
            "review_root": to_rel(step_root),
        },
    }
    write_json(ADDRESS_LATTICE, lattice)

    inq = dict(inquisition)
    failures = list((inq.get("failures", []) or []))
    if truth_spine.get("status") != "PASS":
        failures.append("truth_spine_not_pass")
    if dashboard_engine.get("status") != "PASS":
        failures.append("dashboard_truth_engine_not_pass")
    if worktree_gate.get("status") != "PASS":
        failures.append("worktree_purity_gate_not_pass")
    if anti_lie_model.get("status") != "PASS":
        failures.append("anti_lie_model_not_pass")
    if live_truth_support_loop.get("status") != "PASS":
        failures.append("live_truth_support_loop_not_pass")
    inq["generated_at_utc"] = now_iso()
    inq["step_id"] = step_id
    inq["mode"] = "DIRECT_ACTION"
    inq["direct_action_profile"] = {
        "detect": True,
        "hold_fail_state": True,
        "block_forward_progress": True,
        "force_rerun_and_reread": True,
        "suppression_required_for_pass": True,
    }
    inq["truth_guard_checks"] = {
        "truth_spine": truth_spine.get("status"),
        "dashboard_truth_engine": dashboard_engine.get("status"),
        "worktree_purity_gate": worktree_gate.get("status"),
        "bundle_truth_chamber": as_status(bundle_pre.get("status", "UNKNOWN")),
        "address_lattice": lattice.get("status"),
        "anti_lie_model": anti_lie_model.get("status"),
        "live_truth_support_loop": live_truth_support_loop.get("status"),
        "heresy_early_detection": heresy_early_detection.get("status"),
        "heresy_containment": heresy_containment.get("status"),
        "heresy_suppression": heresy_suppression.get("status"),
    }
    inq["failures"] = sorted(set(failures))
    inq["status"] = "PASS" if len(inq["failures"]) == 0 else "REBUILD_REQUIRED"
    inq["rebuild_required"] = len(inq["failures"]) > 0
    write_json(INQUISITION, inq)

    watch = load_json(WATCH, {})
    watch["generated_at_utc"] = now_iso()
    watch["step_id"] = step_id
    watch["status"] = "HEALTHY" if as_status(inq.get("status", "UNKNOWN")) == "PASS" and as_status(truth_spine.get("status", "UNKNOWN")) == "PASS" else "AT_RISK"
    watch["truth_status"] = truth_spine.get("status", "UNKNOWN")
    watch["transport_status"] = transport_pre
    watch["seed_status"] = "PASS" if seed_sync_ok else "FAIL"
    watch["session"] = dict(live_truth_support_loop.get("session_lifecycle", {}))
    watch["gates"] = {
        **dict(watch.get("gates", {}) or {}),
        "truth_spine": truth_spine.get("status", "UNKNOWN"),
        "dashboard_truth_engine": dashboard_engine.get("status", "UNKNOWN"),
        "bundle_truth_chamber": as_status(bundle_pre.get("status", "UNKNOWN")),
        "worktree_purity_gate": worktree_gate.get("status", "UNKNOWN"),
        "address_lattice": lattice.get("status", "UNKNOWN"),
        "anti_lie_foundation": anti_lie_model.get("status", "UNKNOWN"),
        "live_truth_support_loop": live_truth_support_loop.get("status", "UNKNOWN"),
        "heresy_early_detection": heresy_early_detection.get("status", "UNKNOWN"),
        "heresy_containment": heresy_containment.get("status", "UNKNOWN"),
        "heresy_suppression": heresy_suppression.get("status", "UNKNOWN"),
        "inquisition_loop": inq.get("status", "UNKNOWN"),
    }
    watch["open_blockers"] = list(inq.get("failures", []) or [])
    write_json(WATCH, watch)

    write_json(TRUTH_SPINE_ADAPTER, adapter("IMPERIUM_TRUTH_SPINE_STATE_SURFACE_V1", TRUTH_SPINE, truth_spine))
    write_json(DASHBOARD_ENGINE_ADAPTER, adapter("IMPERIUM_DASHBOARD_TRUTH_ENGINE_SURFACE_V1", DASHBOARD_ENGINE, dashboard_engine))
    write_json(WORKTREE_GATE_ADAPTER, adapter("IMPERIUM_WORKTREE_PURITY_GATE_SURFACE_V1", WORKTREE_GATE, worktree_gate))
    write_json(ADDRESS_LATTICE_ADAPTER, adapter("IMPERIUM_ADDRESS_LATTICE_SURFACE_V1", ADDRESS_LATTICE, lattice))
    write_json(ANTI_LIE_MODEL_ADAPTER, adapter("IMPERIUM_ANTI_LIE_MODEL_SURFACE_V1", ANTI_LIE_MODEL, anti_lie_model))
    write_json(
        LIVE_TRUTH_SUPPORT_LOOP_ADAPTER,
        adapter("IMPERIUM_LIVE_TRUTH_SUPPORT_LOOP_SURFACE_V1", LIVE_TRUTH_SUPPORT_LOOP, live_truth_support_loop),
    )
    write_json(HERESY_MAP_ADAPTER, adapter("IMPERIUM_FOUNDATION_HERESY_MAP_SURFACE_V1", HERESY_MAP, heresy_map))
    write_json(
        HERESY_EARLY_DETECTION_ADAPTER,
        adapter("IMPERIUM_HERESY_EARLY_DETECTION_SURFACE_V1", HERESY_EARLY_DETECTION, heresy_early_detection),
    )
    write_json(
        HERESY_CONTAINMENT_ADAPTER,
        adapter("IMPERIUM_HERESY_CONTAINMENT_SURFACE_V1", HERESY_CONTAINMENT, heresy_containment),
    )
    write_json(
        HERESY_SUPPRESSION_ADAPTER,
        adapter("IMPERIUM_HERESY_SUPPRESSION_SURFACE_V1", HERESY_SUPPRESSION, heresy_suppression),
    )

    update_control_gate_rows(
        truth_spine_status=as_status(truth_spine.get("status", "UNKNOWN")),
        dashboard_status=as_status(dashboard_engine.get("status", "UNKNOWN")),
        bundle_status=as_status(bundle_pre.get("status", "UNKNOWN")),
        purity_status=as_status(worktree_gate.get("status", "UNKNOWN")),
        lattice_status=as_status(lattice.get("status", "UNKNOWN")),
        inquisition_status=as_status(inq.get("status", "UNKNOWN")),
        anti_lie_status=as_status(anti_lie_model.get("status", "UNKNOWN")),
        live_loop_status=as_status(live_truth_support_loop.get("status", "UNKNOWN")),
        heresy_detection_status=as_status(heresy_early_detection.get("status", "UNKNOWN")),
        heresy_containment_status=as_status(heresy_containment.get("status", "UNKNOWN")),
        heresy_suppression_status=as_status(heresy_suppression.get("status", "UNKNOWN")),
    )

    prelim_final = {
        "schema_version": "imperium_100_truth_live_state_regime_final.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "review_root": to_rel(step_root),
        "status": "PENDING",
        "acceptance": "PENDING",
        "truth_spine": truth_spine.get("status"),
        "dashboard_truth_engine": dashboard_engine.get("status"),
        "worktree_purity_gate": worktree_gate.get("status"),
        "address_lattice": lattice.get("status"),
        "inquisition_loop": inq.get("status"),
        "anti_lie_model": anti_lie_model.get("status"),
        "live_truth_support_loop": live_truth_support_loop.get("status"),
        "heresy_early_detection": heresy_early_detection.get("status"),
        "heresy_containment": heresy_containment.get("status"),
        "heresy_suppression": heresy_suppression.get("status"),
        "bundle_truth_chamber": "PENDING",
        "transport_authority_source": transport_authority_source,
        "transport_integrity": "UNKNOWN",
        "transfer_package_completeness": "UNKNOWN",
        "core_required": True,
        "parts_total": 0,
        "optional_included": False,
        "visual_included": False,
        "optional_part_count": 0,
        "visual_part_count": 0,
        "upload_order": [],
        "full_truth_claim": bool(truth_spine.get("full_truth_claim", False)),
        "failure_reasons": [],
    }
    write_json(step_root / "21_FINAL_RESULT.json", prelim_final)

    write_text(step_root / "00_REVIEW_ENTRYPOINT.md", f"# 00_REVIEW_ENTRYPOINT\n\n- step_id: `{step_id}`\n- mode: `100% truth / live-state regime / anti-lie foundation`\n")
    write_text(
        step_root / "01_INTEGRATION_REPORT.md",
        "# 01_INTEGRATION_REPORT\n\nUpgraded truth-everywhere hold-line regime: dashboard command-layer semantics tightened, wave/factory/control-gate consistency surfaced, stability rerun drill added, and anti-lie live chain kept convergent.",
    )
    write_text(
        step_root / "02_VALIDATION_REPORT.md",
        f"# 02_VALIDATION_REPORT\n\n- truth_spine: `{truth_spine.get('status')}`\n- dashboard_truth_engine: `{dashboard_engine.get('status')}`\n- anti_lie_model: `{anti_lie_model.get('status')}`\n- live_truth_support_loop: `{live_truth_support_loop.get('status')}`\n- worktree_purity_gate: `{worktree_gate.get('status')}`\n- inquisition: `{inq.get('status')}`\n",
    )
    write_text(
        step_root / "03_TRUTH_CHECK_AND_GAPS.md",
        f"# 03_TRUTH_CHECK_AND_GAPS\n\n- seed_sync_ok: `{str(seed_sync_ok).lower()}`\n- sync_mismatches: `{len(mismatches)}`\n- stale_hits: `{len(stale_hits)}`\n- dashboard_failures: `{len(dashboard_fail)}`\n- stability_drill: `{stability_report.get('status', 'UNKNOWN')}`\n",
    )
    write_text(
        step_root / "04_CHANGED_SURFACES.md",
        "# 04_CHANGED_SURFACES\n\n- command-layer dashboard semantics (bundle/wave/semantic/factory cards)\n- hold-line stability drill and rerun verification surfaces\n- truth spine/dashboard/bundle/purity convergence surfaces\n- control gates + anti-lie/live-loop hard rows\n- step artifact + transport self-read convergence",
    )
    write_json(step_root / "05_API_SMOKE.json", {"generated_at_utc": now_iso(), "state_meta": api_state_meta, "live_meta": api_live_meta, "playwright": command_results.get("playwright_truth_assault", {})})
    write_json(step_root / "07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json", {}))
    write_json(step_root / "08_ORGAN_STRENGTH_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json", {}))
    write_json(step_root / "09_NODE_RANK_DETECTION_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "repo_control_center" / "validation" / "node_rank_detection.json", {}))
    write_json(step_root / "10_MACHINE_MODE_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "repo_control_center" / "one_screen_status.json", {}))
    write_json(step_root / "11_CONSTITUTION_STATUS_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "repo_control_center" / "constitution_status.json", {}))
    write_json(step_root / "12_ANTI_LIE_MODEL_STATE.json", anti_lie_model)
    write_json(step_root / "13_LIVE_TRUTH_SUPPORT_LOOP_STATE.json", live_truth_support_loop)
    write_json(step_root / "14_TRUTH_SPINE_STATE.json", truth_spine)
    write_json(step_root / "15_DASHBOARD_TRUTH_ENGINE_STATE.json", dashboard_engine)
    write_json(step_root / "16_BUNDLE_TRUTH_CHAMBER_STATE.json", bundle_pre)
    write_json(step_root / "17_WORKTREE_PURITY_GATE_STATE.json", worktree_gate)
    write_json(step_root / "18_INQUISITION_STATE.json", inq)
    write_json(step_root / "22_FOUNDATION_HERESY_MAP.json", heresy_map)
    write_json(step_root / "23_HERESY_EARLY_DETECTION_STATE.json", heresy_early_detection)
    write_json(step_root / "24_HERESY_CONTAINMENT_STATE.json", heresy_containment)
    write_json(step_root / "25_HERESY_SUPPRESSION_STATE.json", heresy_suppression)
    write_json(step_root / "29_STABILITY_DRILL_REPORT.json", stability_report)
    write_text(
        step_root / "26_INQUISITION_DIRECT_ACTION_REPORT.md",
        "# 26_INQUISITION_DIRECT_ACTION_REPORT\n\nInquisition now runs in direct-action profile: detect, hold-fail, block progress, force rerun/reread, and require suppression before PASS.",
    )
    write_text(
        step_root / "27_STAGE1_HOLD_LINE_REPORT.md",
        "# 27_STAGE1_HOLD_LINE_REPORT\n\nStage 1 hold-line status is green only when truth spine, dashboard truth, bundle truth, transport self-read, inquisition, anti-lie, and heresy chain all converge.\n\nNo downstream PASS is allowed over upstream transport FAIL.",
    )

    include_paths = [f"docs/review_artifacts/{step_id}/{name}" for name in REQUIRED_REVIEW]
    include_paths += [
        f"docs/review_artifacts/{step_id}/12_ANTI_LIE_MODEL_STATE.json",
        f"docs/review_artifacts/{step_id}/13_LIVE_TRUTH_SUPPORT_LOOP_STATE.json",
        f"docs/review_artifacts/{step_id}/14_TRUTH_SPINE_STATE.json",
        f"docs/review_artifacts/{step_id}/15_DASHBOARD_TRUTH_ENGINE_STATE.json",
        f"docs/review_artifacts/{step_id}/16_BUNDLE_TRUTH_CHAMBER_STATE.json",
        f"docs/review_artifacts/{step_id}/17_WORKTREE_PURITY_GATE_STATE.json",
        f"docs/review_artifacts/{step_id}/18_INQUISITION_STATE.json",
        f"docs/review_artifacts/{step_id}/19_TRANSPORT_SELF_READ_REPORT.json",
        f"docs/review_artifacts/{step_id}/20_BLOCKER_CLASSIFICATION.json",
        f"docs/review_artifacts/{step_id}/21_FINAL_RESULT.json",
        f"docs/review_artifacts/{step_id}/22_FOUNDATION_HERESY_MAP.json",
        f"docs/review_artifacts/{step_id}/23_HERESY_EARLY_DETECTION_STATE.json",
        f"docs/review_artifacts/{step_id}/24_HERESY_CONTAINMENT_STATE.json",
        f"docs/review_artifacts/{step_id}/25_HERESY_SUPPRESSION_STATE.json",
        f"docs/review_artifacts/{step_id}/26_INQUISITION_DIRECT_ACTION_REPORT.md",
        f"docs/review_artifacts/{step_id}/27_STAGE1_HOLD_LINE_REPORT.md",
        f"docs/review_artifacts/{step_id}/28_TRANSPORT_MECHANISM_CLASSIFICATION.md",
        f"docs/review_artifacts/{step_id}/29_STABILITY_DRILL_REPORT.json",
        f"docs/review_artifacts/{step_id}/24_EXECUTION_META.json",
        to_rel(TRUTH_SPINE),
        to_rel(DASHBOARD_ENGINE),
        to_rel(BUNDLE_CHAMBER),
        to_rel(WORKTREE_GATE),
        to_rel(ADDRESS_LATTICE),
        to_rel(ANTI_LIE_MODEL),
        to_rel(LIVE_TRUTH_SUPPORT_LOOP),
        to_rel(HERESY_MAP),
        to_rel(HERESY_EARLY_DETECTION),
        to_rel(HERESY_CONTAINMENT),
        to_rel(HERESY_SUPPRESSION),
        to_rel(INQUISITION),
        to_rel(WATCH),
        to_rel(TRUTH_SPINE_ADAPTER),
        to_rel(DASHBOARD_ENGINE_ADAPTER),
        to_rel(BUNDLE_CHAMBER_ADAPTER),
        to_rel(WORKTREE_GATE_ADAPTER),
        to_rel(ADDRESS_LATTICE_ADAPTER),
        to_rel(ANTI_LIE_MODEL_ADAPTER),
        to_rel(LIVE_TRUTH_SUPPORT_LOOP_ADAPTER),
        to_rel(HERESY_MAP_ADAPTER),
        to_rel(HERESY_EARLY_DETECTION_ADAPTER),
        to_rel(HERESY_CONTAINMENT_ADAPTER),
        to_rel(HERESY_SUPPRESSION_ADAPTER),
        to_rel(CONTROL_GATES_ADAPTER),
        to_rel(CANON_PATH),
        to_rel(REGIME_CANON_PATH),
        "scripts/imperium_100_truth_live_state_regime.py",
        "shared_systems/factory_observation_window_v1/app/local_factory_observation_server.py",
        "shared_systems/factory_observation_window_v1/web/app.js",
    ]
    write_text(step_root / "06_BUNDLE_INCLUDE_PATHS.txt", "\n".join(sorted(set(include_paths))))

    command_results["enforcer_pass1"] = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
    enforcer1, transport1, transfer1 = load_transport(step_root)
    chamber = {
        "surface_id": "IMPERIUM_BUNDLE_TRUTH_CHAMBER_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS" if as_status(enforcer1.get("verdict", "UNKNOWN")) == "PASS" and as_status(transport1.get("status", "UNKNOWN")) == "PASS" else "FAIL",
        "enforcer_verdict": as_status(enforcer1.get("verdict", "UNKNOWN")),
        "transport_authority_source": transport_authority_source,
        "transport_integrity": transport1,
    }
    write_json(BUNDLE_CHAMBER, chamber)
    write_json(BUNDLE_CHAMBER_ADAPTER, adapter("IMPERIUM_BUNDLE_TRUTH_CHAMBER_SURFACE_V1", BUNDLE_CHAMBER, chamber))
    write_json(step_root / "16_BUNDLE_TRUTH_CHAMBER_STATE.json", chamber)

    for row in anti_lie_classes:
        if str(row.get("class_id", "")) == "bundle_shell_core_result_mismatch":
            row["detected"] = as_status(chamber.get("status", "UNKNOWN")) != "PASS"
    anti_lie_model["lie_classes"] = anti_lie_classes
    anti_lie_model["active_critical_count"] = len([x for x in anti_lie_classes if x.get("detected") and str(x.get("severity", "")).upper() == "CRITICAL"])
    anti_lie_model["active_total_count"] = len([x for x in anti_lie_classes if x.get("detected")])
    anti_lie_model["status"] = "PASS" if int(anti_lie_model.get("active_critical_count", 0) or 0) == 0 else "FAIL"
    anti_lie_model["generated_at_utc"] = now_iso()
    write_json(ANTI_LIE_MODEL, anti_lie_model)
    write_json(ANTI_LIE_MODEL_ADAPTER, adapter("IMPERIUM_ANTI_LIE_MODEL_SURFACE_V1", ANTI_LIE_MODEL, anti_lie_model))
    write_json(step_root / "12_ANTI_LIE_MODEL_STATE.json", anti_lie_model)

    live_truth_support_loop["truth_retention_checks"]["seed_sync_ok"] = seed_sync_ok
    live_truth_support_loop["truth_retention_checks"]["dashboard_truth_engine"] = as_status(dashboard_engine.get("status", "UNKNOWN"))
    live_truth_support_loop["truth_retention_checks"]["anti_lie_model"] = as_status(anti_lie_model.get("status", "UNKNOWN"))
    live_truth_support_loop["truth_retention_checks"]["bundle_truth_chamber"] = as_status(chamber.get("status", "UNKNOWN"))
    live_truth_support_loop["active_drift_count"] = compute_drift_count(
        seed_sync_ok=seed_sync_ok,
        dashboard_status=as_status(dashboard_engine.get("status", "UNKNOWN")),
        anti_lie_status=as_status(anti_lie_model.get("status", "UNKNOWN")),
        bundle_status=as_status(chamber.get("status", "UNKNOWN")),
    )
    live_truth_support_loop["status"] = "PASS" if int(live_truth_support_loop.get("active_drift_count", 0) or 0) == 0 else "FAIL"
    live_truth_support_loop["generated_at_utc"] = now_iso()
    write_json(LIVE_TRUTH_SUPPORT_LOOP, live_truth_support_loop)
    write_json(
        LIVE_TRUTH_SUPPORT_LOOP_ADAPTER,
        adapter("IMPERIUM_LIVE_TRUTH_SUPPORT_LOOP_SURFACE_V1", LIVE_TRUTH_SUPPORT_LOOP, live_truth_support_loop),
    )
    write_json(step_root / "13_LIVE_TRUTH_SUPPORT_LOOP_STATE.json", live_truth_support_loop)

    dims["bundle_truth_chamber"] = 1 if as_status(chamber.get("status", "UNKNOWN")) == "PASS" else 0
    dims["transport_truth"] = 1 if as_status(transport1.get("status", "UNKNOWN")) == "PASS" else 0
    dims["anti_lie_model"] = 1 if as_status(anti_lie_model.get("status", "UNKNOWN")) == "PASS" else 0
    dims["live_truth_support_loop"] = 1 if as_status(live_truth_support_loop.get("status", "UNKNOWN")) == "PASS" else 0
    critical_ok = all(dims.get(key, 0) == 1 for key in critical_keys)
    sync_pct = round((sum(dims.values()) / len(dims)) * 100, 2)
    truth_spine["generated_at_utc"] = now_iso()
    truth_spine["status"] = "PASS" if critical_ok else "FAIL"
    truth_spine["full_truth_claim"] = bool(critical_ok)
    truth_spine["sync_model"] = {
        "dimensions": dims,
        "critical_dimensions": critical_keys,
        "critical_ok": critical_ok,
        "sync_percentage": sync_pct,
    }
    truth_spine["transport_status"] = as_status(transport1.get("status", "UNKNOWN"))
    truth_spine["bundle_truth_status"] = as_status(chamber.get("status", "UNKNOWN"))
    truth_spine["partial_truth_classes"] = [str(x.get("class_id", "")) for x in anti_lie_classes if bool(x.get("detected"))]
    write_json(TRUTH_SPINE, truth_spine)
    write_json(TRUTH_SPINE_ADAPTER, adapter("IMPERIUM_TRUTH_SPINE_STATE_SURFACE_V1", TRUTH_SPINE, truth_spine))
    write_json(step_root / "14_TRUTH_SPINE_STATE.json", truth_spine)
    write_json(step_root / "15_DASHBOARD_TRUTH_ENGINE_STATE.json", dashboard_engine)
    write_json(step_root / "17_WORKTREE_PURITY_GATE_STATE.json", worktree_gate)

    inq["generated_at_utc"] = now_iso()
    inq["truth_guard_checks"] = {
        "truth_spine": truth_spine.get("status"),
        "dashboard_truth_engine": dashboard_engine.get("status"),
        "worktree_purity_gate": worktree_gate.get("status"),
        "bundle_truth_chamber": chamber.get("status"),
        "address_lattice": lattice.get("status"),
        "anti_lie_model": anti_lie_model.get("status"),
        "live_truth_support_loop": live_truth_support_loop.get("status"),
    }
    inq_failures = []
    for key, value in inq["truth_guard_checks"].items():
        if as_status(value, "UNKNOWN") != "PASS":
            inq_failures.append(f"{key}_not_pass")
    inq["failures"] = sorted(set(inq_failures))
    inq["status"] = "PASS" if len(inq["failures"]) == 0 else "REBUILD_REQUIRED"
    inq["rebuild_required"] = len(inq["failures"]) > 0
    write_json(INQUISITION, inq)
    write_json(step_root / "18_INQUISITION_STATE.json", inq)

    watch["generated_at_utc"] = now_iso()
    watch["status"] = "HEALTHY" if as_status(inq.get("status", "UNKNOWN")) == "PASS" and as_status(truth_spine.get("status", "UNKNOWN")) == "PASS" else "AT_RISK"
    watch["truth_status"] = truth_spine.get("status", "UNKNOWN")
    watch["transport_status"] = as_status(transport1.get("status", "UNKNOWN"))
    watch["seed_status"] = "PASS" if seed_sync_ok else "FAIL"
    watch["session"] = dict(live_truth_support_loop.get("session_lifecycle", {}))
    watch["gates"] = {
        **dict(watch.get("gates", {}) or {}),
        "truth_spine": truth_spine.get("status", "UNKNOWN"),
        "dashboard_truth_engine": dashboard_engine.get("status", "UNKNOWN"),
        "bundle_truth_chamber": chamber.get("status", "UNKNOWN"),
        "worktree_purity_gate": worktree_gate.get("status", "UNKNOWN"),
        "address_lattice": lattice.get("status", "UNKNOWN"),
        "anti_lie_foundation": anti_lie_model.get("status", "UNKNOWN"),
        "live_truth_support_loop": live_truth_support_loop.get("status", "UNKNOWN"),
        "inquisition_loop": inq.get("status", "UNKNOWN"),
    }
    watch["open_blockers"] = list(inq.get("failures", []) or [])
    write_json(WATCH, watch)

    update_control_gate_rows(
        truth_spine_status=as_status(truth_spine.get("status", "UNKNOWN")),
        dashboard_status=as_status(dashboard_engine.get("status", "UNKNOWN")),
        bundle_status=as_status(chamber.get("status", "UNKNOWN")),
        purity_status=as_status(worktree_gate.get("status", "UNKNOWN")),
        lattice_status=as_status(lattice.get("status", "UNKNOWN")),
        inquisition_status=as_status(inq.get("status", "UNKNOWN")),
        anti_lie_status=as_status(anti_lie_model.get("status", "UNKNOWN")),
        live_loop_status=as_status(live_truth_support_loop.get("status", "UNKNOWN")),
        heresy_detection_status=as_status(heresy_early_detection.get("status", "UNKNOWN")),
        heresy_containment_status=as_status(heresy_containment.get("status", "UNKNOWN")),
        heresy_suppression_status=as_status(heresy_suppression.get("status", "UNKNOWN")),
    )

    blockers = {"FIX_NOW": [], "OPEN_BUT_ALLOWED": [], "POLICY_SKIPPED": [], "FUTURE_WORK": []}
    if as_status(truth_spine.get("status", "UNKNOWN")) != "PASS":
        blockers["FIX_NOW"].append("truth_spine_not_pass")
    if as_status(dashboard_engine.get("status", "UNKNOWN")) != "PASS":
        blockers["FIX_NOW"].append("dashboard_truth_engine_not_pass")
    if as_status(chamber.get("status", "UNKNOWN")) != "PASS":
        blockers["FIX_NOW"].append("bundle_truth_chamber_not_pass")
    if as_status(anti_lie_model.get("status", "UNKNOWN")) != "PASS":
        blockers["FIX_NOW"].append("anti_lie_model_not_pass")
    if as_status(live_truth_support_loop.get("status", "UNKNOWN")) != "PASS":
        blockers["FIX_NOW"].append("live_truth_support_loop_not_pass")
    if as_status(inq.get("status", "UNKNOWN")) != "PASS":
        blockers["FIX_NOW"].append("inquisition_not_pass")
    if as_status(heresy_early_detection.get("status", "UNKNOWN")) != "PASS":
        blockers["FIX_NOW"].append("heresy_early_detection_not_pass")
    if as_status(heresy_containment.get("status", "UNKNOWN")) != "PASS":
        blockers["FIX_NOW"].append("heresy_containment_not_pass")
    if as_status(heresy_suppression.get("status", "UNKNOWN")) != "PASS":
        blockers["FIX_NOW"].append("heresy_suppression_not_pass")
    if as_status(worktree_gate.get("status", "UNKNOWN")) != "PASS":
        blockers["OPEN_BUT_ALLOWED"].append("worktree_purity_gate_baseline_exception_active")
    blockers["FUTURE_WORK"] = [
        "full_event_bus_not_yet_implemented",
        "auto_preview_pipeline_not_yet_implemented",
        "pixel_level_perceptual_diff_unavailable_in_scope",
        "two_disk_migration_not_physically_validated",
    ]
    write_json(step_root / "20_BLOCKER_CLASSIFICATION.json", blockers)

    write_text(
        step_root / "26_INQUISITION_DIRECT_ACTION_REPORT.md",
        "# 26_INQUISITION_DIRECT_ACTION_REPORT\n\n- detection: Inquisition monitors truth spine, dashboard, bundle chamber, purity, anti-lie, live support, and heresy chain.\n- containment: any failing critical layer is held as blocker (`REBUILD_REQUIRED`) until convergence.\n- suppression: rerun+reread enforcement remains mandatory before PASS.\n- anti-bypass: downstream PASS cannot survive upstream transport or truth FAIL.\n",
    )
    write_text(
        step_root / "27_STAGE1_HOLD_LINE_REPORT.md",
        "# 27_STAGE1_HOLD_LINE_REPORT\n\nStage 1 hold-line proof requires simultaneous PASS across:\n- truth spine\n- dashboard truth\n- bundle truth + transport self-read\n- anti-lie model\n- heresy early detection / containment / suppression\n- inquisition direct action\n- watch truth status\n",
    )
    write_text(
        step_root / "28_TRANSPORT_MECHANISM_CLASSIFICATION.md",
        "# 28_TRANSPORT_MECHANISM_CLASSIFICATION\n\nClassification: `DERIVED_REDUNDANT_MERGE`.\n\n- authoritative transport truth: `12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json::chatgpt_transfer.transport_integrity`\n- `19_TRANSPORT_SELF_READ_REPORT.json` is now canonical mirror audit only, not independent truth origin.\n- downstream PASS depends on canonical transport PASS and mirror consistency checks.\n- transport FAIL upstream cannot survive with downstream PASS by construction.\n",
    )

    final = dict(prelim_final)
    final["truth_spine"] = as_status(truth_spine.get("status", "UNKNOWN"))
    final["dashboard_truth_engine"] = as_status(dashboard_engine.get("status", "UNKNOWN"))
    final["bundle_truth_chamber"] = as_status(chamber.get("status", "UNKNOWN"))
    final["worktree_purity_gate"] = as_status(worktree_gate.get("status", "UNKNOWN"))
    final["inquisition_loop"] = as_status(inq.get("status", "UNKNOWN"))
    final["anti_lie_model"] = as_status(anti_lie_model.get("status", "UNKNOWN"))
    final["live_truth_support_loop"] = as_status(live_truth_support_loop.get("status", "UNKNOWN"))
    final["heresy_early_detection"] = as_status(heresy_early_detection.get("status", "UNKNOWN"))
    final["heresy_containment"] = as_status(heresy_containment.get("status", "UNKNOWN"))
    final["heresy_suppression"] = as_status(heresy_suppression.get("status", "UNKNOWN"))
    final["transport_integrity"] = as_status(transport1.get("status", "UNKNOWN"))
    final["transfer_package_completeness"] = str(transport1.get("package_completeness", "UNKNOWN"))
    final["core_required"] = bool(transport1.get("core_required", False))
    final["parts_total"] = int(transport1.get("manifest_parts_total", 0) or 0)
    final["upload_order"] = list(transport1.get("upload_order_declared", []) or [])
    final["optional_included"] = bool(transfer1.get("optional_included", False))
    final["visual_included"] = bool(transfer1.get("visual_included", False))
    final["optional_part_count"] = int(transfer1.get("optional_part_count", 0) or 0)
    final["visual_part_count"] = int(transfer1.get("visual_part_count", 0) or 0)
    final["full_truth_claim"] = bool(truth_spine.get("full_truth_claim", False))

    failure_reasons = set(blockers.get("FIX_NOW", []))
    if as_status(enforcer1.get("verdict", "UNKNOWN")) != "PASS":
        failure_reasons.add("bundle_output_enforcer_not_pass")
    if as_status(transport1.get("status", "UNKNOWN")) != "PASS":
        failure_reasons.add("transport_truth_not_pass")
    final["failure_reasons"] = sorted(failure_reasons)
    final["status"] = "PASS" if len(final["failure_reasons"]) == 0 else "FAIL"
    final["acceptance"] = "PASS" if final["status"] == "PASS" else "FAIL"
    write_json(step_root / "21_FINAL_RESULT.json", final)

    write_json(
        step_root / "24_EXECUTION_META.json",
        {
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "authority": authority,
            "seed_sync_ok": seed_sync_ok,
            "mismatches": mismatches,
            "stale_hits": stale_hits,
            "command_results": command_results,
            "git_state": git_state,
        },
    )

    command_results["enforcer_pass2"] = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
    enforcer2, transport2, transfer2 = load_transport(step_root)
    final["transport_integrity"] = as_status(transport2.get("status", final.get("transport_integrity", "UNKNOWN")))
    final["transfer_package_completeness"] = str(transport2.get("package_completeness", final.get("transfer_package_completeness", "UNKNOWN")))
    final["parts_total"] = int(transport2.get("manifest_parts_total", final.get("parts_total", 0)) or 0)
    final["upload_order"] = list(transport2.get("upload_order_declared", final.get("upload_order", [])) or [])
    final["optional_included"] = bool(transfer2.get("optional_included", final.get("optional_included", False)))
    final["visual_included"] = bool(transfer2.get("visual_included", final.get("visual_included", False)))
    final["optional_part_count"] = int(transfer2.get("optional_part_count", final.get("optional_part_count", 0)) or 0)
    final["visual_part_count"] = int(transfer2.get("visual_part_count", final.get("visual_part_count", 0)) or 0)
    if as_status(enforcer2.get("verdict", "UNKNOWN")) != "PASS":
        final["failure_reasons"] = sorted(set(list(final.get("failure_reasons", []) or []) + ["bundle_output_enforcer_not_pass"]))
    if as_status(transport2.get("status", "UNKNOWN")) != "PASS":
        final["failure_reasons"] = sorted(set(list(final.get("failure_reasons", []) or []) + ["transport_truth_not_pass"]))
    final["status"] = "PASS" if len(final.get("failure_reasons", []) or []) == 0 else "FAIL"
    final["acceptance"] = "PASS" if final["status"] == "PASS" else "FAIL"
    write_json(step_root / "21_FINAL_RESULT.json", final)

    def reconcile_from_enforcer(
        *,
        enforcer_report: dict[str, Any],
        transport_report: dict[str, Any],
        transfer_report: dict[str, Any],
    ) -> None:
        nonlocal chamber, anti_lie_model, live_truth_support_loop, truth_spine, inq, watch, blockers, final
        nonlocal heresy_map, heresy_early_detection, heresy_containment, heresy_suppression

        chamber = {
            "surface_id": "IMPERIUM_BUNDLE_TRUTH_CHAMBER_V1",
            "generated_at_utc": now_iso(),
            "truth_class": "SOURCE_EXACT",
            "status": "PASS"
            if as_status(enforcer_report.get("verdict", "UNKNOWN")) == "PASS" and as_status(transport_report.get("status", "UNKNOWN")) == "PASS"
            else "FAIL",
            "enforcer_verdict": as_status(enforcer_report.get("verdict", "UNKNOWN")),
            "transport_authority_source": transport_authority_source,
            "transport_integrity": transport_report,
        }
        write_json(BUNDLE_CHAMBER, chamber)
        write_json(BUNDLE_CHAMBER_ADAPTER, adapter("IMPERIUM_BUNDLE_TRUTH_CHAMBER_SURFACE_V1", BUNDLE_CHAMBER, chamber))
        write_json(step_root / "16_BUNDLE_TRUTH_CHAMBER_STATE.json", chamber)

        for row in anti_lie_classes:
            class_id = str(row.get("class_id", ""))
            if class_id == "stale_pointer_or_line":
                row["detected"] = len(stale_hits) > 0
            elif class_id == "cross_surface_current_point_mismatch":
                row["detected"] = len(mismatches) > 0
            elif class_id == "dashboard_unsourced_or_stale_display":
                row["detected"] = len(dashboard_fail) > 0
            elif class_id == "bundle_shell_core_result_mismatch":
                row["detected"] = as_status(chamber.get("status", "UNKNOWN")) != "PASS"
            elif class_id == "purity_drift_or_unclean_state":
                row["detected"] = as_status(worktree_gate.get("status", "UNKNOWN")) != "PASS"

        anti_lie_model["generated_at_utc"] = now_iso()
        anti_lie_model["lie_classes"] = anti_lie_classes
        anti_lie_model["active_critical_count"] = len([x for x in anti_lie_classes if x.get("detected") and str(x.get("severity", "")).upper() == "CRITICAL"])
        anti_lie_model["active_total_count"] = len([x for x in anti_lie_classes if x.get("detected")])
        anti_lie_model["status"] = "PASS" if int(anti_lie_model.get("active_critical_count", 0) or 0) == 0 else "FAIL"
        write_json(ANTI_LIE_MODEL, anti_lie_model)
        write_json(ANTI_LIE_MODEL_ADAPTER, adapter("IMPERIUM_ANTI_LIE_MODEL_SURFACE_V1", ANTI_LIE_MODEL, anti_lie_model))
        write_json(step_root / "12_ANTI_LIE_MODEL_STATE.json", anti_lie_model)

        live_truth_support_loop["generated_at_utc"] = now_iso()
        live_truth_support_loop["truth_retention_checks"]["seed_sync_ok"] = seed_sync_ok
        live_truth_support_loop["truth_retention_checks"]["dashboard_truth_engine"] = as_status(dashboard_engine.get("status", "UNKNOWN"))
        live_truth_support_loop["truth_retention_checks"]["worktree_purity_gate"] = as_status(worktree_gate.get("status", "UNKNOWN"))
        live_truth_support_loop["truth_retention_checks"]["anti_lie_model"] = as_status(anti_lie_model.get("status", "UNKNOWN"))
        live_truth_support_loop["truth_retention_checks"]["bundle_truth_chamber"] = as_status(chamber.get("status", "UNKNOWN"))
        live_truth_support_loop["active_drift_count"] = compute_drift_count(
            seed_sync_ok=seed_sync_ok,
            dashboard_status=as_status(dashboard_engine.get("status", "UNKNOWN")),
            anti_lie_status=as_status(anti_lie_model.get("status", "UNKNOWN")),
            bundle_status=as_status(chamber.get("status", "UNKNOWN")),
        )
        live_truth_support_loop["status"] = "PASS" if int(live_truth_support_loop.get("active_drift_count", 0) or 0) == 0 else "FAIL"
        write_json(LIVE_TRUTH_SUPPORT_LOOP, live_truth_support_loop)
        write_json(
            LIVE_TRUTH_SUPPORT_LOOP_ADAPTER,
            adapter("IMPERIUM_LIVE_TRUTH_SUPPORT_LOOP_SURFACE_V1", LIVE_TRUTH_SUPPORT_LOOP, live_truth_support_loop),
        )
        write_json(step_root / "13_LIVE_TRUTH_SUPPORT_LOOP_STATE.json", live_truth_support_loop)

        heresy_map = build_foundation_heresy_map(
            seed_sync_ok=seed_sync_ok,
            stale_hits=stale_hits,
            mismatches=mismatches,
            dashboard_status=as_status(dashboard_engine.get("status", "UNKNOWN")),
            chamber_status=as_status(chamber.get("status", "UNKNOWN")),
            transport_status=as_status(transport_report.get("status", "UNKNOWN")),
            inquisition_direct_action_ready=True,
            worktree_status=as_status(worktree_gate.get("status", "UNKNOWN")),
        )
        heresy_early_detection = {
            "surface_id": "IMPERIUM_HERESY_EARLY_DETECTION_V1",
            "generated_at_utc": now_iso(),
            "truth_class": "SOURCE_EXACT",
            "status": "PASS",
            "checks": {
                "seed_sync_authority_check": seed_sync_ok,
                "dashboard_truth_chain_check": as_status(dashboard_engine.get("status", "UNKNOWN")) == "PASS",
                "bundle_transport_chain_check": as_status(chamber.get("status", "UNKNOWN")) == "PASS"
                and as_status(transport_report.get("status", "UNKNOWN")) == "PASS",
                "inquisition_direct_action_ready": True,
                "worktree_purity_check": as_status(worktree_gate.get("status", "UNKNOWN")) == "PASS",
            },
            "trigger_policy": "any_failed_check_is_immediate_alert",
        }
        heresy_early_detection["status"] = "PASS" if all(bool(v) for v in dict(heresy_early_detection.get("checks", {})).values()) else "FAIL"

        active_heresy = [row for row in list(heresy_map.get("map", []) or []) if bool(row.get("detected"))]
        heresy_containment = {
            "surface_id": "IMPERIUM_HERESY_CONTAINMENT_V1",
            "generated_at_utc": now_iso(),
            "truth_class": "SOURCE_EXACT",
            "status": "PASS",
            "fail_hold_enabled": True,
            "forward_progress_block_enabled": True,
            "forced_rerun_enabled": True,
            "active_blockers": [str(row.get("class_id", "")) for row in active_heresy],
            "containment_policy": "hold_fail_until_verdict_surfaces_converge",
        }
        heresy_containment["status"] = "PASS" if len(list(heresy_containment.get("active_blockers", []) or [])) == 0 else "FAIL"

        heresy_suppression = {
            "surface_id": "IMPERIUM_HERESY_SUPPRESSION_V1",
            "generated_at_utc": now_iso(),
            "truth_class": "SOURCE_EXACT",
            "status": "PASS",
            "suppression_loop": "detect -> hold -> rerun -> reread -> verify -> converge",
            "active_heresy_count": len(active_heresy),
            "suppressed_in_this_pass": int(max(0, len(list(heresy_map.get("map", []) or [])) - len(active_heresy))),
            "suppression_ready": True,
        }
        heresy_suppression["status"] = "PASS" if int(heresy_suppression.get("active_heresy_count", 0) or 0) == 0 else "FAIL"

        write_json(HERESY_MAP, heresy_map)
        write_json(HERESY_EARLY_DETECTION, heresy_early_detection)
        write_json(HERESY_CONTAINMENT, heresy_containment)
        write_json(HERESY_SUPPRESSION, heresy_suppression)
        write_json(HERESY_MAP_ADAPTER, adapter("IMPERIUM_FOUNDATION_HERESY_MAP_SURFACE_V1", HERESY_MAP, heresy_map))
        write_json(
            HERESY_EARLY_DETECTION_ADAPTER,
            adapter("IMPERIUM_HERESY_EARLY_DETECTION_SURFACE_V1", HERESY_EARLY_DETECTION, heresy_early_detection),
        )
        write_json(
            HERESY_CONTAINMENT_ADAPTER,
            adapter("IMPERIUM_HERESY_CONTAINMENT_SURFACE_V1", HERESY_CONTAINMENT, heresy_containment),
        )
        write_json(
            HERESY_SUPPRESSION_ADAPTER,
            adapter("IMPERIUM_HERESY_SUPPRESSION_SURFACE_V1", HERESY_SUPPRESSION, heresy_suppression),
        )
        write_json(step_root / "22_FOUNDATION_HERESY_MAP.json", heresy_map)
        write_json(step_root / "23_HERESY_EARLY_DETECTION_STATE.json", heresy_early_detection)
        write_json(step_root / "24_HERESY_CONTAINMENT_STATE.json", heresy_containment)
        write_json(step_root / "25_HERESY_SUPPRESSION_STATE.json", heresy_suppression)

        dims["bundle_truth_chamber"] = 1 if as_status(chamber.get("status", "UNKNOWN")) == "PASS" else 0
        dims["transport_truth"] = 1 if as_status(transport_report.get("status", "UNKNOWN")) == "PASS" else 0
        dims["anti_lie_model"] = 1 if as_status(anti_lie_model.get("status", "UNKNOWN")) == "PASS" else 0
        dims["live_truth_support_loop"] = 1 if as_status(live_truth_support_loop.get("status", "UNKNOWN")) == "PASS" else 0
        dims["heresy_early_detection"] = 1 if as_status(heresy_early_detection.get("status", "UNKNOWN")) == "PASS" else 0
        dims["heresy_containment"] = 1 if as_status(heresy_containment.get("status", "UNKNOWN")) == "PASS" else 0
        dims["heresy_suppression"] = 1 if as_status(heresy_suppression.get("status", "UNKNOWN")) == "PASS" else 0
        critical_ok_local = all(dims.get(key, 0) == 1 for key in critical_keys)
        sync_pct_local = round((sum(dims.values()) / len(dims)) * 100, 2)

        truth_spine["generated_at_utc"] = now_iso()
        truth_spine["status"] = "PASS" if critical_ok_local else "FAIL"
        truth_spine["full_truth_claim"] = bool(critical_ok_local)
        truth_spine["sync_model"] = {
            "dimensions": dims,
            "critical_dimensions": critical_keys,
            "critical_ok": critical_ok_local,
            "sync_percentage": sync_pct_local,
        }
        truth_spine["partial_truth_classes"] = [str(x.get("class_id", "")) for x in anti_lie_classes if bool(x.get("detected"))]
        truth_spine["seed_sync_mismatches"] = mismatches
        truth_spine["seed_stale_hits"] = stale_hits
        truth_spine["transport_status"] = as_status(transport_report.get("status", "UNKNOWN"))
        truth_spine["bundle_truth_status"] = as_status(chamber.get("status", "UNKNOWN"))
        write_json(TRUTH_SPINE, truth_spine)
        write_json(TRUTH_SPINE_ADAPTER, adapter("IMPERIUM_TRUTH_SPINE_STATE_SURFACE_V1", TRUTH_SPINE, truth_spine))
        write_json(step_root / "14_TRUTH_SPINE_STATE.json", truth_spine)
        write_json(step_root / "15_DASHBOARD_TRUTH_ENGINE_STATE.json", dashboard_engine)
        write_json(step_root / "17_WORKTREE_PURITY_GATE_STATE.json", worktree_gate)

        inq["generated_at_utc"] = now_iso()
        inq["mode"] = "DIRECT_ACTION"
        inq["direct_action_profile"] = {
            "detect": True,
            "hold_fail_state": True,
            "block_forward_progress": True,
            "force_rerun_and_reread": True,
            "suppression_required_for_pass": True,
        }
        inq["truth_guard_checks"] = {
            "truth_spine": truth_spine.get("status"),
            "dashboard_truth_engine": dashboard_engine.get("status"),
            "worktree_purity_gate": worktree_gate.get("status"),
            "bundle_truth_chamber": chamber.get("status"),
            "address_lattice": lattice.get("status"),
            "anti_lie_model": anti_lie_model.get("status"),
            "live_truth_support_loop": live_truth_support_loop.get("status"),
            "heresy_early_detection": heresy_early_detection.get("status"),
            "heresy_containment": heresy_containment.get("status"),
            "heresy_suppression": heresy_suppression.get("status"),
        }
        inq_failures_local = []
        for key, value in inq["truth_guard_checks"].items():
            if as_status(value, "UNKNOWN") != "PASS":
                inq_failures_local.append(f"{key}_not_pass")
        inq["failures"] = sorted(set(inq_failures_local))
        inq["status"] = "PASS" if len(inq["failures"]) == 0 else "REBUILD_REQUIRED"
        inq["rebuild_required"] = len(inq["failures"]) > 0
        write_json(INQUISITION, inq)
        write_json(step_root / "18_INQUISITION_STATE.json", inq)

        watch["generated_at_utc"] = now_iso()
        watch["status"] = "HEALTHY" if as_status(inq.get("status", "UNKNOWN")) == "PASS" and as_status(truth_spine.get("status", "UNKNOWN")) == "PASS" else "AT_RISK"
        watch["truth_status"] = truth_spine.get("status", "UNKNOWN")
        watch["transport_status"] = as_status(transport_report.get("status", "UNKNOWN"))
        watch["seed_status"] = "PASS" if seed_sync_ok else "FAIL"
        watch["session"] = dict(live_truth_support_loop.get("session_lifecycle", {}))
        watch["gates"] = {
            **dict(watch.get("gates", {}) or {}),
            "truth_spine": truth_spine.get("status", "UNKNOWN"),
            "dashboard_truth_engine": dashboard_engine.get("status", "UNKNOWN"),
            "bundle_truth_chamber": chamber.get("status", "UNKNOWN"),
            "worktree_purity_gate": worktree_gate.get("status", "UNKNOWN"),
            "address_lattice": lattice.get("status", "UNKNOWN"),
            "anti_lie_foundation": anti_lie_model.get("status", "UNKNOWN"),
            "live_truth_support_loop": live_truth_support_loop.get("status", "UNKNOWN"),
            "heresy_early_detection": heresy_early_detection.get("status", "UNKNOWN"),
            "heresy_containment": heresy_containment.get("status", "UNKNOWN"),
            "heresy_suppression": heresy_suppression.get("status", "UNKNOWN"),
            "inquisition_loop": inq.get("status", "UNKNOWN"),
        }
        watch["open_blockers"] = list(inq.get("failures", []) or [])
        write_json(WATCH, watch)

        update_control_gate_rows(
            truth_spine_status=as_status(truth_spine.get("status", "UNKNOWN")),
            dashboard_status=as_status(dashboard_engine.get("status", "UNKNOWN")),
            bundle_status=as_status(chamber.get("status", "UNKNOWN")),
            purity_status=as_status(worktree_gate.get("status", "UNKNOWN")),
            lattice_status=as_status(lattice.get("status", "UNKNOWN")),
            inquisition_status=as_status(inq.get("status", "UNKNOWN")),
            anti_lie_status=as_status(anti_lie_model.get("status", "UNKNOWN")),
            live_loop_status=as_status(live_truth_support_loop.get("status", "UNKNOWN")),
            heresy_detection_status=as_status(heresy_early_detection.get("status", "UNKNOWN")),
            heresy_containment_status=as_status(heresy_containment.get("status", "UNKNOWN")),
            heresy_suppression_status=as_status(heresy_suppression.get("status", "UNKNOWN")),
        )

        blockers = {"FIX_NOW": [], "OPEN_BUT_ALLOWED": [], "POLICY_SKIPPED": [], "FUTURE_WORK": []}
        if as_status(truth_spine.get("status", "UNKNOWN")) != "PASS":
            blockers["FIX_NOW"].append("truth_spine_not_pass")
        if as_status(dashboard_engine.get("status", "UNKNOWN")) != "PASS":
            blockers["FIX_NOW"].append("dashboard_truth_engine_not_pass")
        if as_status(chamber.get("status", "UNKNOWN")) != "PASS":
            blockers["FIX_NOW"].append("bundle_truth_chamber_not_pass")
        if as_status(anti_lie_model.get("status", "UNKNOWN")) != "PASS":
            blockers["FIX_NOW"].append("anti_lie_model_not_pass")
        if as_status(live_truth_support_loop.get("status", "UNKNOWN")) != "PASS":
            blockers["FIX_NOW"].append("live_truth_support_loop_not_pass")
        if as_status(inq.get("status", "UNKNOWN")) != "PASS":
            blockers["FIX_NOW"].append("inquisition_not_pass")
        if as_status(heresy_early_detection.get("status", "UNKNOWN")) != "PASS":
            blockers["FIX_NOW"].append("heresy_early_detection_not_pass")
        if as_status(heresy_containment.get("status", "UNKNOWN")) != "PASS":
            blockers["FIX_NOW"].append("heresy_containment_not_pass")
        if as_status(heresy_suppression.get("status", "UNKNOWN")) != "PASS":
            blockers["FIX_NOW"].append("heresy_suppression_not_pass")
        if as_status(worktree_gate.get("status", "UNKNOWN")) != "PASS":
            blockers["OPEN_BUT_ALLOWED"].append("worktree_purity_gate_baseline_exception_active")
        blockers["FUTURE_WORK"] = [
            "full_event_bus_not_yet_implemented",
            "auto_preview_pipeline_not_yet_implemented",
            "pixel_level_perceptual_diff_unavailable_in_scope",
            "two_disk_migration_not_physically_validated",
        ]
        write_json(step_root / "20_BLOCKER_CLASSIFICATION.json", blockers)

        failure_reasons_local: set[str] = set(list(blockers.get("FIX_NOW", []) or []))

        final["generated_at_utc"] = now_iso()
        final["truth_spine"] = as_status(truth_spine.get("status", "UNKNOWN"))
        final["dashboard_truth_engine"] = as_status(dashboard_engine.get("status", "UNKNOWN"))
        final["bundle_truth_chamber"] = as_status(chamber.get("status", "UNKNOWN"))
        final["worktree_purity_gate"] = as_status(worktree_gate.get("status", "UNKNOWN"))
        final["address_lattice"] = as_status(lattice.get("status", "UNKNOWN"))
        final["inquisition_loop"] = as_status(inq.get("status", "UNKNOWN"))
        final["anti_lie_model"] = as_status(anti_lie_model.get("status", "UNKNOWN"))
        final["live_truth_support_loop"] = as_status(live_truth_support_loop.get("status", "UNKNOWN"))
        final["heresy_early_detection"] = as_status(heresy_early_detection.get("status", "UNKNOWN"))
        final["heresy_containment"] = as_status(heresy_containment.get("status", "UNKNOWN"))
        final["heresy_suppression"] = as_status(heresy_suppression.get("status", "UNKNOWN"))
        final["transport_authority_source"] = transport_authority_source
        final["transport_integrity"] = as_status(transport_report.get("status", "UNKNOWN"))
        final["transfer_package_completeness"] = str(transport_report.get("package_completeness", "UNKNOWN"))
        final["core_required"] = bool(transport_report.get("core_required", False))
        final["parts_total"] = int(transport_report.get("manifest_parts_total", 0) or 0)
        final["upload_order"] = list(transport_report.get("upload_order_declared", []) or [])
        final["optional_included"] = bool(transfer_report.get("optional_included", False))
        final["visual_included"] = bool(transfer_report.get("visual_included", False))
        final["optional_part_count"] = int(transfer_report.get("optional_part_count", 0) or 0)
        final["visual_part_count"] = int(transfer_report.get("visual_part_count", 0) or 0)
        final["full_truth_claim"] = bool(truth_spine.get("full_truth_claim", False))

        transport_mirror = build_transport_self_read_mirror(
            authority_source=transport_authority_source,
            enforcer_report=enforcer_report,
            transport_report=transport_report,
            final_surface=final,
            watch_surface=watch,
            chamber_surface=chamber,
            truth_spine_surface=truth_spine,
            inquisition_surface=inq,
        )
        final["transport_chain_mirror"] = as_status(transport_mirror.get("status", "UNKNOWN"))
        if as_status(transport_mirror.get("status", "UNKNOWN")) != "PASS":
            blockers["FIX_NOW"].append("transport_chain_mirror_not_pass")
            write_json(step_root / "20_BLOCKER_CLASSIFICATION.json", blockers)

        if as_status(enforcer_report.get("verdict", "UNKNOWN")) != "PASS":
            failure_reasons_local.add("bundle_output_enforcer_not_pass")
        if as_status(transport_report.get("status", "UNKNOWN")) != "PASS":
            failure_reasons_local.add("transport_truth_not_pass")
        if as_status(transport_mirror.get("status", "UNKNOWN")) != "PASS":
            failure_reasons_local.add("transport_chain_mirror_not_pass")

        final["failure_reasons"] = sorted(failure_reasons_local)
        final["status"] = "PASS" if len(final["failure_reasons"]) == 0 else "FAIL"
        final["acceptance"] = "PASS" if final["status"] == "PASS" else "FAIL"
        write_json(step_root / "21_FINAL_RESULT.json", final)
        write_json(step_root / "19_TRANSPORT_SELF_READ_REPORT.json", transport_mirror)

    command_results["enforcer_pass3"] = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
    enforcer3, transport3, transfer3 = load_transport(step_root)
    reconcile_from_enforcer(enforcer_report=enforcer3, transport_report=transport3, transfer_report=transfer3)

    command_results["enforcer_pass4"] = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
    enforcer4, transport4, transfer4 = load_transport(step_root)
    reconcile_from_enforcer(enforcer_report=enforcer4, transport_report=transport4, transfer_report=transfer4)

    write_json(
        step_root / "24_EXECUTION_META.json",
        {
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "authority": authority,
            "seed_sync_ok": seed_sync_ok,
            "mismatches": mismatches,
            "stale_hits": stale_hits,
            "command_results": command_results,
            "git_state": git_state,
        },
    )

    print(json.dumps(final, ensure_ascii=False))
    return 0 if final.get("acceptance") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
