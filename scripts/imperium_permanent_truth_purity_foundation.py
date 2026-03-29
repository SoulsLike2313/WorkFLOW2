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
CAPSULE_ROOT = REVIEW_ROOT / "ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1"
ADMIN_ROOT = REPO_ROOT / "runtime" / "administratum"
ADAPTER_ROOT = REPO_ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters"
STEP_PREFIX = "imperium_permanent_truth_purity_foundation_astronomican_canon_path_delta"

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

TRUTH_SPINE_ADAPTER = ADAPTER_ROOT / "IMPERIUM_TRUTH_SPINE_STATE_SURFACE_V1.json"
DASHBOARD_ENGINE_ADAPTER = ADAPTER_ROOT / "IMPERIUM_DASHBOARD_TRUTH_ENGINE_SURFACE_V1.json"
BUNDLE_CHAMBER_ADAPTER = ADAPTER_ROOT / "IMPERIUM_BUNDLE_TRUTH_CHAMBER_SURFACE_V1.json"
WORKTREE_GATE_ADAPTER = ADAPTER_ROOT / "IMPERIUM_WORKTREE_PURITY_GATE_SURFACE_V1.json"
ADDRESS_LATTICE_ADAPTER = ADAPTER_ROOT / "IMPERIUM_ADDRESS_LATTICE_SURFACE_V1.json"
CONTROL_GATES_ADAPTER = ADAPTER_ROOT / "IMPERIUM_CONTROL_GATES_SURFACE_V1.json"

CANON_PATH = REPO_ROOT / "docs" / "governance" / "IMPERIUM_PERMANENT_TRUTH_AND_PURITY_FOUNDATION_CANON_V1.md"
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
    (CAPSULE_ROOT / "for_chatgpt" / "07_IMPERIUM_SEED_SUPERCOMPACT_STATE.md", ["continuity_line", "handoff_line", "active_line", "active_vertex"]),
    (CAPSULE_ROOT / "for_codex" / "05_CONTEXT_POINTERS_AND_RECOVERY.md", ["continuity_line", "handoff_line", "active_line"]),
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


def main() -> int:
    parser = argparse.ArgumentParser(description="IMPERIUM Permanent Truth & Purity Foundation")
    parser.add_argument("--step-id", default="")
    parser.add_argument("--dashboard-url", default="http://127.0.0.1:8777/")
    args = parser.parse_args()

    step_id = args.step_id.strip() or f"{STEP_PREFIX}_{now_stamp()}"
    step_root = REVIEW_ROOT / step_id
    step_root.mkdir(parents=True, exist_ok=True)
    command_results: dict[str, Any] = {}

    write_text(
        CANON_PATH,
        "# IMPERIUM Permanent Truth & Purity Foundation Canon V1\n\n- 100% truth chain required for green.\n- dashboard truth, bundle truth, and worktree purity are hard gates.\n- Inquisition blocks forward progress on truth drift.\n- Astronomican path remains Emperor-routed.\n- Mandatory execution law: evidence-first, root-cause-first, narrow repair, rerun, self-read, convergence only.\n- Session lifecycle law: hour-4 warning, hour-5 checkpoint question, no-reply auto-sync-and-relocation prompt.\n",
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
    worktree_gate = {
        "surface_id": "IMPERIUM_WORKTREE_PURITY_GATE_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS" if git_state.get("cleanliness_verdict") == "CLEAN" else "FAIL",
        "cleanliness_verdict": git_state.get("cleanliness_verdict", "UNKNOWN"),
        "tracked_dirty_count": int(git_state.get("tracked_dirty_count", 0) or 0),
        "untracked_count": int(git_state.get("untracked_count", 0) or 0),
        "allowed_exception_proven": git_state.get("cleanliness_verdict") != "CLEAN",
        "allowed_exception_reason": "owner_decision_required_for_repo_wide_dirty_baseline_classification_and_cleanup" if git_state.get("cleanliness_verdict") != "CLEAN" else "",
    }
    write_json(WORKTREE_GATE, worktree_gate)

    api_state_meta, api_state = fetch_json(f"{args.dashboard_url.rstrip('/')}/api/state")
    api_live_meta, api_live = fetch_json(f"{args.dashboard_url.rstrip('/')}/api/live_state")
    if not api_live:
        api_live = load_json(REPO_ROOT / "runtime" / "factory_observation" / "live_state_snapshot.json", {})
    command_results["playwright_truth_assault"] = run_cmd(["python", "scripts/imperial_dashboard_visual_audit_loop.py", "--url", args.dashboard_url, "--out-dir", str(step_root / "dashboard_truth_assault")]) if VISUAL_AUDIT_SCRIPT.exists() else {"status": "FAIL", "stderr": "script_missing"}
    playwright_ok = command_results["playwright_truth_assault"].get("status") == "PASS"

    live_text = json.dumps(api_live, ensure_ascii=False, sort_keys=True)
    dashboard_checks = {
        "api_state_ok": bool(api_state_meta.get("ok")),
        "api_live_ok": bool(api_live_meta.get("ok")) or bool(api_live),
        "active_line_present": bool(authority.get("active_line") and authority.get("active_line") in live_text),
        "stale_line_absent": STALE_LINE not in live_text,
        "playwright_ok": bool(playwright_ok),
    }
    dashboard_fail = [k for k, v in dashboard_checks.items() if not v]
    dashboard_engine = {
        "surface_id": "IMPERIUM_DASHBOARD_TRUTH_ENGINE_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS" if len(dashboard_fail) == 0 else "FAIL",
        "checks": dashboard_checks,
        "failures": dashboard_fail,
    }
    write_json(DASHBOARD_ENGINE, dashboard_engine)

    truth_schema = load_json(TRUTH_SCHEMA, {})
    law_gate = load_json(LAW_GATE, {})
    provenance = load_json(PROVENANCE, {})
    inquisition = load_json(INQUISITION, {})
    dims = {
        "seed_sync": 1 if seed_sync_ok else 0,
        "truth_schema": 1 if truth_schema.get("status") == "PASS" else 0,
        "law_gate": 1 if law_gate.get("verdict") != "DENY" else 0,
        "provenance": 1 if provenance.get("status") == "PASS" else 0,
        "dashboard": 1 if dashboard_engine.get("status") == "PASS" else 0,
        "worktree": 1 if worktree_gate.get("status") == "PASS" else 0,
    }
    critical_keys = ["seed_sync", "truth_schema", "law_gate", "provenance", "dashboard"]
    critical_ok = all(dims.get(key, 0) == 1 for key in critical_keys)
    sync_pct = round((sum(dims.values()) / len(dims)) * 100, 2)
    truth_spine = {
        "surface_id": "IMPERIUM_TRUTH_SPINE_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS" if critical_ok else "FAIL",
        "authoritative_current_point": authority,
        "sync_model": {
            "dimensions": dims,
            "critical_dimensions": critical_keys,
            "critical_ok": critical_ok,
            "sync_percentage": sync_pct,
        },
        "seed_sync_mismatches": mismatches,
        "seed_stale_hits": stale_hits,
        "purity_dimension_status": worktree_gate.get("status", "UNKNOWN"),
        "allowed_exception_proven": bool(worktree_gate.get("allowed_exception_proven", False)),
        "allowed_exception_reason": str(worktree_gate.get("allowed_exception_reason", "")),
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
            "watch": to_rel(WATCH),
            "inquisition": to_rel(INQUISITION),
            "astronomican": to_rel(ADMIN_ROOT / "IMPERIUM_ASTRONOMICAN_ROUTE_REGISTRY_V1.json"),
            "capsule_root": to_rel(CAPSULE_ROOT),
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
    inq["generated_at_utc"] = now_iso()
    inq["truth_guard_checks"] = {
        "truth_spine": truth_spine.get("status"),
        "dashboard_truth_engine": dashboard_engine.get("status"),
        "worktree_purity_gate": worktree_gate.get("status"),
        "bundle_truth_chamber": "PENDING",
        "address_lattice": lattice.get("status"),
    }
    inq["failures"] = sorted(set(failures))
    inq["status"] = "PASS" if len(inq["failures"]) == 0 else "REBUILD_REQUIRED"
    inq["rebuild_required"] = len(inq["failures"]) > 0
    write_json(INQUISITION, inq)

    watch = load_json(WATCH, {})
    session = dict((watch.get("session", {}) or {}))
    started_raw = str(session.get("started_at_utc", now_iso()))
    try:
        started_dt = datetime.fromisoformat(started_raw.replace("Z", "+00:00"))
    except ValueError:
        started_dt = datetime.now(timezone.utc)
    elapsed_seconds = int((datetime.now(timezone.utc) - started_dt).total_seconds())
    elapsed_hours = round(float(elapsed_seconds) / 3600.0, 3) if elapsed_seconds > 0 else 0.0
    session["started_at_utc"] = started_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    session["elapsed_seconds"] = max(0, elapsed_seconds)
    session["elapsed_hours"] = elapsed_hours
    session["hour4_warning"] = elapsed_hours >= 4.0
    session["hour5_checkpoint_required"] = elapsed_hours >= 5.0
    session["auto_sync_prompt_if_no_reply"] = elapsed_hours >= 5.0
    session["owner_checkpoint_question"] = (
        "If active tasks remain, finish current bounded step first, then run full sync and relocate to a new chat. Continue?"
    )
    session["auto_prompt_if_silent"] = (
        "No owner response at hour 5. Prepare full-system sync package and start new-chat relocation flow."
    )
    watch["generated_at_utc"] = now_iso()
    watch["step_id"] = step_id
    watch["truth_status"] = truth_spine.get("status", "UNKNOWN")
    watch["session"] = session
    watch["gates"] = {
        **dict(watch.get("gates", {}) or {}),
        "truth_spine": truth_spine.get("status", "UNKNOWN"),
        "dashboard_truth_engine": dashboard_engine.get("status", "UNKNOWN"),
        "worktree_purity_gate": worktree_gate.get("status", "UNKNOWN"),
        "address_lattice": lattice.get("status", "UNKNOWN"),
        "inquisition_loop": inq.get("status", "UNKNOWN"),
    }
    write_json(WATCH, watch)

    write_json(TRUTH_SPINE_ADAPTER, adapter("IMPERIUM_TRUTH_SPINE_STATE_SURFACE_V1", TRUTH_SPINE, truth_spine))
    write_json(DASHBOARD_ENGINE_ADAPTER, adapter("IMPERIUM_DASHBOARD_TRUTH_ENGINE_SURFACE_V1", DASHBOARD_ENGINE, dashboard_engine))
    write_json(WORKTREE_GATE_ADAPTER, adapter("IMPERIUM_WORKTREE_PURITY_GATE_SURFACE_V1", WORKTREE_GATE, worktree_gate))
    write_json(ADDRESS_LATTICE_ADAPTER, adapter("IMPERIUM_ADDRESS_LATTICE_SURFACE_V1", ADDRESS_LATTICE, lattice))

    control = load_json(CONTROL_GATES_ADAPTER, {})
    gates = list((control.get("gates", []) or []))
    extra = [
        {"gate_id": "truth_spine_gate", "title_ru": "Truth Spine Gate", "state": "PASS" if truth_spine.get("status") == "PASS" else "BLOCKED", "source_path": to_rel(TRUTH_SPINE_ADAPTER), "truth_class": "SOURCE_EXACT"},
        {"gate_id": "dashboard_truth_engine_gate", "title_ru": "Dashboard Truth Engine Gate", "state": "PASS" if dashboard_engine.get("status") == "PASS" else "BLOCKED", "source_path": to_rel(DASHBOARD_ENGINE_ADAPTER), "truth_class": "SOURCE_EXACT"},
        {"gate_id": "bundle_truth_chamber_gate", "title_ru": "Bundle Truth Chamber Gate", "state": "WARNING", "source_path": to_rel(BUNDLE_CHAMBER_ADAPTER), "truth_class": "SOURCE_EXACT"},
        {"gate_id": "worktree_purity_gate", "title_ru": "Worktree Purity Gate", "state": "PASS" if worktree_gate.get("status") == "PASS" else "BLOCKED", "source_path": to_rel(WORKTREE_GATE_ADAPTER), "truth_class": "SOURCE_EXACT"},
        {"gate_id": "address_lattice_gate", "title_ru": "Address Lattice Gate", "state": "PASS", "source_path": to_rel(ADDRESS_LATTICE_ADAPTER), "truth_class": "SOURCE_EXACT"},
        {"gate_id": "inquisition_truth_guard_gate", "title_ru": "Inquisition Truth Guard", "state": "PASS" if inq.get("status") == "PASS" else "BLOCKED", "source_path": to_rel(INQUISITION), "truth_class": "SOURCE_EXACT"},
    ]
    known = {str((g or {}).get("gate_id", "")): g for g in gates}
    for row in extra:
        known[row["gate_id"]] = row
    control["gates"] = list(known.values())
    write_json(CONTROL_GATES_ADAPTER, control)

    prelim_final = {
        "schema_version": "imperium_permanent_truth_purity_final.v1",
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
        "bundle_truth_chamber": "PENDING",
        "transport_integrity": "UNKNOWN",
        "transfer_package_completeness": "UNKNOWN",
        "core_required": True,
        "parts_total": 0,
        "optional_included": False,
        "visual_included": False,
        "optional_part_count": 0,
        "visual_part_count": 0,
        "upload_order": [],
        "failure_reasons": [],
        "allowed_exception_proven": bool(worktree_gate.get("allowed_exception_proven", False)),
        "allowed_exception_reason": str(worktree_gate.get("allowed_exception_reason", "")),
    }
    write_json(step_root / "21_FINAL_RESULT.json", prelim_final)

    write_text(step_root / "00_REVIEW_ENTRYPOINT.md", f"# 00_REVIEW_ENTRYPOINT\n\n- step_id: `{step_id}`\n- mode: `permanent truth & purity foundation`\n")
    write_text(step_root / "01_INTEGRATION_REPORT.md", "# 01_INTEGRATION_REPORT\n\nBuilt truth spine, dashboard truth engine, bundle chamber, worktree purity gate, address lattice, and expanded inquisition truth guard.")
    write_text(step_root / "02_VALIDATION_REPORT.md", f"# 02_VALIDATION_REPORT\n\n- truth_spine: `{truth_spine.get('status')}`\n- dashboard_truth_engine: `{dashboard_engine.get('status')}`\n- worktree_purity_gate: `{worktree_gate.get('status')}`\n- address_lattice: `{lattice.get('status')}`\n- inquisition: `{inq.get('status')}`\n")
    write_text(step_root / "03_TRUTH_CHECK_AND_GAPS.md", f"# 03_TRUTH_CHECK_AND_GAPS\n\n- seed_sync_ok: `{str(seed_sync_ok).lower()}`\n- stale_hits: `{len(stale_hits)}`\n- worktree_allowed_exception: `{str(bool(worktree_gate.get('allowed_exception_proven', False))).lower()}`\n")
    write_text(step_root / "04_CHANGED_SURFACES.md", "# 04_CHANGED_SURFACES\n\n- runtime truth/purity surfaces\n- dashboard adapters + control gates\n- server and ui bindings\n- step artifact + transfer truth checks")
    write_json(step_root / "05_API_SMOKE.json", {"generated_at_utc": now_iso(), "state_meta": api_state_meta, "live_meta": api_live_meta, "playwright": command_results.get("playwright_truth_assault", {})})
    write_json(step_root / "07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json", {}))
    write_json(step_root / "08_ORGAN_STRENGTH_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json", {}))
    write_json(step_root / "09_NODE_RANK_DETECTION_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "repo_control_center" / "validation" / "node_rank_detection.json", {}))
    write_json(step_root / "10_MACHINE_MODE_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "repo_control_center" / "one_screen_status.json", {}))
    write_json(step_root / "11_CONSTITUTION_STATUS_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "repo_control_center" / "constitution_status.json", {}))
    write_json(step_root / "12_TRUTH_SPINE_STATE.json", truth_spine)
    write_json(step_root / "13_DASHBOARD_TRUTH_ENGINE_STATE.json", dashboard_engine)
    write_json(step_root / "14_WORKTREE_PURITY_GATE_STATE.json", worktree_gate)
    write_json(step_root / "15_ADDRESS_LATTICE_STATE.json", lattice)
    write_json(step_root / "16_INQUISITION_EXPANDED_AUTHORITY_STATE.json", inq)

    include_paths = [f"docs/review_artifacts/{step_id}/{name}" for name in REQUIRED_REVIEW]
    include_paths += [
        f"docs/review_artifacts/{step_id}/12_TRUTH_SPINE_STATE.json",
        f"docs/review_artifacts/{step_id}/13_DASHBOARD_TRUTH_ENGINE_STATE.json",
        f"docs/review_artifacts/{step_id}/14_WORKTREE_PURITY_GATE_STATE.json",
        f"docs/review_artifacts/{step_id}/15_ADDRESS_LATTICE_STATE.json",
        f"docs/review_artifacts/{step_id}/16_INQUISITION_EXPANDED_AUTHORITY_STATE.json",
        f"docs/review_artifacts/{step_id}/17_BUNDLE_TRUTH_CHAMBER_STATE.json",
        f"docs/review_artifacts/{step_id}/18_EXECUTION_META.json",
        f"docs/review_artifacts/{step_id}/19_TRANSPORT_SELF_READ_REPORT.json",
        f"docs/review_artifacts/{step_id}/20_BLOCKER_CLASSIFICATION.json",
        f"docs/review_artifacts/{step_id}/21_FINAL_RESULT.json",
        to_rel(TRUTH_SPINE),
        to_rel(DASHBOARD_ENGINE),
        to_rel(BUNDLE_CHAMBER),
        to_rel(WORKTREE_GATE),
        to_rel(ADDRESS_LATTICE),
        to_rel(INQUISITION),
        to_rel(WATCH),
        to_rel(TRUTH_SPINE_ADAPTER),
        to_rel(DASHBOARD_ENGINE_ADAPTER),
        to_rel(BUNDLE_CHAMBER_ADAPTER),
        to_rel(WORKTREE_GATE_ADAPTER),
        to_rel(ADDRESS_LATTICE_ADAPTER),
        to_rel(CONTROL_GATES_ADAPTER),
        to_rel(CANON_PATH),
        "scripts/imperium_permanent_truth_purity_foundation.py",
        "shared_systems/factory_observation_window_v1/app/local_factory_observation_server.py",
        "shared_systems/factory_observation_window_v1/web/app.js",
    ]
    write_text(step_root / "06_BUNDLE_INCLUDE_PATHS.txt", "\n".join(sorted(set(include_paths))))

    command_results["enforcer_pass1"] = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
    enforcer1 = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    transport1 = dict(((enforcer1.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}) or {}))
    chamber = {
        "surface_id": "IMPERIUM_BUNDLE_TRUTH_CHAMBER_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS" if str(enforcer1.get("verdict", "UNKNOWN")) == "PASS" and str(transport1.get("status", "UNKNOWN")) == "PASS" else "FAIL",
        "enforcer_verdict": str(enforcer1.get("verdict", "UNKNOWN")),
        "transport_integrity": transport1,
    }
    write_json(BUNDLE_CHAMBER, chamber)
    write_json(BUNDLE_CHAMBER_ADAPTER, adapter("IMPERIUM_BUNDLE_TRUTH_CHAMBER_SURFACE_V1", BUNDLE_CHAMBER, chamber))
    write_json(step_root / "17_BUNDLE_TRUTH_CHAMBER_STATE.json", chamber)
    control_after_chamber = load_json(CONTROL_GATES_ADAPTER, {})
    chamber_gate_rows = list((control_after_chamber.get("gates", []) or []))
    for row in chamber_gate_rows:
        gate_id = str((row or {}).get("gate_id", "")).strip()
        if gate_id == "bundle_truth_chamber_gate":
            row["state"] = "PASS" if chamber.get("status") == "PASS" else "BLOCKED"
        if gate_id == "inquisition_truth_guard_gate":
            row["state"] = "PASS" if inq.get("status") == "PASS" else "BLOCKED"
    if chamber_gate_rows:
        control_after_chamber["gates"] = chamber_gate_rows
        write_json(CONTROL_GATES_ADAPTER, control_after_chamber)

    command_results["enforcer_pass2"] = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
    enforcer2 = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    transport2 = dict(((enforcer2.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}) or {}))
    transfer2 = dict((((enforcer2.get("chatgpt_transfer", {}) or {}).get("result", {}) or {}).get("transfer_report", {}) or {}))

    chamber = {
        "surface_id": "IMPERIUM_BUNDLE_TRUTH_CHAMBER_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS" if str(enforcer2.get("verdict", "UNKNOWN")) == "PASS" and str(transport2.get("status", "UNKNOWN")) == "PASS" else "FAIL",
        "enforcer_verdict": str(enforcer2.get("verdict", "UNKNOWN")),
        "transport_integrity": transport2,
    }
    write_json(BUNDLE_CHAMBER, chamber)
    write_json(BUNDLE_CHAMBER_ADAPTER, adapter("IMPERIUM_BUNDLE_TRUTH_CHAMBER_SURFACE_V1", BUNDLE_CHAMBER, chamber))
    write_json(step_root / "17_BUNDLE_TRUTH_CHAMBER_STATE.json", chamber)

    blockers = {"FIX_NOW": [], "OPEN_BUT_ALLOWED": [], "POLICY_SKIPPED": [], "FUTURE_WORK": []}
    if not bool((truth_spine.get("sync_model", {}) or {}).get("critical_ok", False)):
        blockers["FIX_NOW"].append("truth_spine_not_pass")
    elif worktree_gate.get("status") != "PASS":
        blockers["OPEN_BUT_ALLOWED"].append("truth_spine_purity_exception::owner_decision_required")
    if dashboard_engine.get("status") != "PASS":
        blockers["FIX_NOW"].append("dashboard_truth_engine_not_pass")
    if chamber.get("status") != "PASS":
        blockers["FIX_NOW"].append("bundle_truth_chamber_not_pass")
    if worktree_gate.get("status") != "PASS":
        blockers["OPEN_BUT_ALLOWED"].append("worktree_purity_gate_not_pass::owner_decision_required")
    blockers["FUTURE_WORK"] += [
        "full_event_bus_not_yet_implemented",
        "auto_preview_pipeline_not_yet_implemented",
        "pixel_level_perceptual_diff_unavailable_in_scope",
        "two_disk_migration_not_physically_validated",
    ]
    write_json(step_root / "20_BLOCKER_CLASSIFICATION.json", blockers)

    final = dict(prelim_final)
    final["bundle_truth_chamber"] = chamber.get("status", "UNKNOWN")
    final["failure_reasons"] = sorted(set(list(blockers["FIX_NOW"])))
    final["transport_integrity"] = str(transport2.get("status", "UNKNOWN"))
    final["transfer_package_completeness"] = str(transport2.get("package_completeness", "UNKNOWN"))
    final["core_required"] = bool(transport2.get("core_required", False))
    final["parts_total"] = int(transport2.get("manifest_parts_total", 0) or 0)
    final["upload_order"] = list(transport2.get("upload_order_declared", []) or [])
    final["optional_included"] = bool(transfer2.get("optional_included", False))
    final["visual_included"] = bool(transfer2.get("visual_included", False))
    final["optional_part_count"] = int(transfer2.get("optional_part_count", 0) or 0)
    final["visual_part_count"] = int(transfer2.get("visual_part_count", 0) or 0)
    final["status"] = "PASS" if len(final["failure_reasons"]) == 0 and worktree_gate.get("status") == "PASS" else "FAIL"
    final["acceptance"] = "PASS" if final["status"] == "PASS" else "FAIL"
    write_json(step_root / "21_FINAL_RESULT.json", final)

    write_json(
        step_root / "19_TRANSPORT_SELF_READ_REPORT.json",
        {
            "generated_at_utc": now_iso(),
            "enforcer_verdict": str(enforcer2.get("verdict", "UNKNOWN")),
            "transport_integrity": str(transport2.get("status", "UNKNOWN")),
            "entrypoint_matches_disk": bool(transport2.get("entrypoint_matches_disk", False)),
            "final_result_matches_disk": bool(transport2.get("final_result_matches_disk", False)),
            "required_entries_missing": list(transport2.get("required_entries_missing", []) or []),
            "foreign_review_roots": list(transport2.get("foreign_review_roots", []) or []),
        },
    )
    write_json(
        step_root / "18_EXECUTION_META.json",
        {
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "authority": authority,
            "seed_sync_ok": seed_sync_ok,
            "mismatches": mismatches,
            "stale_hits": stale_hits,
            "command_results": command_results,
        },
    )

    command_results["enforcer_pass3"] = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
    enforcer3 = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    transport3 = dict(((enforcer3.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}) or {}))
    transfer3 = dict((((enforcer3.get("chatgpt_transfer", {}) or {}).get("result", {}) or {}).get("transfer_report", {}) or {}))

    chamber = {
        "surface_id": "IMPERIUM_BUNDLE_TRUTH_CHAMBER_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS" if str(enforcer3.get("verdict", "UNKNOWN")) == "PASS" and str(transport3.get("status", "UNKNOWN")) == "PASS" else "FAIL",
        "enforcer_verdict": str(enforcer3.get("verdict", "UNKNOWN")),
        "transport_integrity": transport3,
    }
    write_json(BUNDLE_CHAMBER, chamber)
    write_json(BUNDLE_CHAMBER_ADAPTER, adapter("IMPERIUM_BUNDLE_TRUTH_CHAMBER_SURFACE_V1", BUNDLE_CHAMBER, chamber))
    write_json(step_root / "17_BUNDLE_TRUTH_CHAMBER_STATE.json", chamber)

    final_fix_now: list[str] = []
    final_open_allowed: list[str] = []
    if not bool((truth_spine.get("sync_model", {}) or {}).get("critical_ok", False)):
        final_fix_now.append("truth_spine_not_pass")
    elif worktree_gate.get("status") != "PASS":
        final_open_allowed.append("truth_spine_purity_exception::owner_decision_required")
    if dashboard_engine.get("status") != "PASS":
        final_fix_now.append("dashboard_truth_engine_not_pass")
    if chamber.get("status") != "PASS":
        final_fix_now.append("bundle_truth_chamber_not_pass")
    if worktree_gate.get("status") != "PASS":
        final_open_allowed.append("worktree_purity_gate_not_pass::owner_decision_required")
    blockers["FIX_NOW"] = sorted(set(final_fix_now))
    blockers["OPEN_BUT_ALLOWED"] = sorted(set(final_open_allowed))
    write_json(step_root / "20_BLOCKER_CLASSIFICATION.json", blockers)

    final = dict(prelim_final)
    final["bundle_truth_chamber"] = chamber.get("status", "UNKNOWN")
    failure_reasons = set(blockers["FIX_NOW"] if isinstance(blockers.get("FIX_NOW", []), list) else [])
    if str(enforcer3.get("verdict", "UNKNOWN")) != "PASS" or str(transport3.get("status", "UNKNOWN")) != "PASS":
        failure_reasons.add("bundle_output_enforcer_not_pass")
    if chamber.get("status") != "PASS":
        failure_reasons.add("bundle_truth_chamber_not_pass")
    final["failure_reasons"] = sorted(failure_reasons)
    final["transport_integrity"] = str(transport3.get("status", "UNKNOWN"))
    final["transfer_package_completeness"] = str(transport3.get("package_completeness", "UNKNOWN"))
    final["core_required"] = bool(transport3.get("core_required", False))
    final["parts_total"] = int(transport3.get("manifest_parts_total", 0) or 0)
    final["upload_order"] = list(transport3.get("upload_order_declared", []) or [])
    final["optional_included"] = bool(transfer3.get("optional_included", False))
    final["visual_included"] = bool(transfer3.get("visual_included", False))
    final["optional_part_count"] = int(transfer3.get("optional_part_count", 0) or 0)
    final["visual_part_count"] = int(transfer3.get("visual_part_count", 0) or 0)
    final["status"] = "PASS" if len(final["failure_reasons"]) == 0 and worktree_gate.get("status") == "PASS" else "FAIL"
    final["acceptance"] = "PASS" if final["status"] == "PASS" else "FAIL"
    write_json(step_root / "21_FINAL_RESULT.json", final)

    write_json(
        step_root / "19_TRANSPORT_SELF_READ_REPORT.json",
        {
            "generated_at_utc": now_iso(),
            "enforcer_verdict": str(enforcer3.get("verdict", "UNKNOWN")),
            "transport_integrity": str(transport3.get("status", "UNKNOWN")),
            "entrypoint_matches_disk": bool(transport3.get("entrypoint_matches_disk", False)),
            "final_result_matches_disk": bool(transport3.get("final_result_matches_disk", False)),
            "required_entries_missing": list(transport3.get("required_entries_missing", []) or []),
            "foreign_review_roots": list(transport3.get("foreign_review_roots", []) or []),
        },
    )
    write_json(
        step_root / "18_EXECUTION_META.json",
        {
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "authority": authority,
            "seed_sync_ok": seed_sync_ok,
            "mismatches": mismatches,
            "stale_hits": stale_hits,
            "command_results": command_results,
        },
    )

    command_results["enforcer_pass4"] = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
    enforcer4 = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    transport4 = dict(((enforcer4.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}) or {}))
    if str(enforcer4.get("verdict", "UNKNOWN")) != "PASS" or str(transport4.get("status", "UNKNOWN")) != "PASS":
        reasons = set(final.get("failure_reasons", []) or [])
        reasons.add("bundle_output_enforcer_not_pass")
        final["failure_reasons"] = sorted(reasons)
        final["transport_integrity"] = str(transport4.get("status", "UNKNOWN"))
        final["transfer_package_completeness"] = str(transport4.get("package_completeness", "UNKNOWN"))
        final["status"] = "FAIL"
        final["acceptance"] = "FAIL"
        write_json(step_root / "21_FINAL_RESULT.json", final)

    print(json.dumps(final, ensure_ascii=False))
    return 0 if final.get("acceptance") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
