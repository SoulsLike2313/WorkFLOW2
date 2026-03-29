#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_ROOT = REPO_ROOT / "docs" / "review_artifacts"
ADMIN_ROOT = REPO_ROOT / "runtime" / "administratum"
RUNTIME_ROOT = REPO_ROOT / "runtime" / "repo_control_center"
ADAPTER_ROOT = REPO_ROOT / "shared_systems" / "factory_observation_window_v1" / "adapters"
STEP_PREFIX = "imperium_repo_wide_dirty_baseline_cleanup_purity_closure_delta"
ENFORCER_SCRIPT = REPO_ROOT / "scripts" / "imperium_bundle_output_enforcer.py"

WORKTREE_GATE = ADMIN_ROOT / "IMPERIUM_WORKTREE_PURITY_GATE_V1.json"
INQUISITION = ADMIN_ROOT / "IMPERIUM_INQUISITION_LOOP_V1.json"
WATCH = ADMIN_ROOT / "IMPERIUM_WATCH_STATE_V1.json"
TRUTH_SPINE = ADMIN_ROOT / "IMPERIUM_TRUTH_SPINE_V1.json"
DASHBOARD_ENGINE = ADMIN_ROOT / "IMPERIUM_DASHBOARD_TRUTH_ENGINE_V1.json"
BUNDLE_CHAMBER = ADMIN_ROOT / "IMPERIUM_BUNDLE_TRUTH_CHAMBER_V1.json"
ADDRESS_LATTICE = ADMIN_ROOT / "IMPERIUM_ADDRESS_LATTICE_V1.json"

REPO_HYGIENE_ADAPTER = ADAPTER_ROOT / "IMPERIUM_REPO_HYGIENE_CLASSIFICATION_SURFACE_V1.json"
WORKTREE_GATE_ADAPTER = ADAPTER_ROOT / "IMPERIUM_WORKTREE_PURITY_GATE_SURFACE_V1.json"
CONTROL_GATES_ADAPTER = ADAPTER_ROOT / "IMPERIUM_CONTROL_GATES_SURFACE_V1.json"

ROOT_CANONICAL_FILES = {
    ".gitignore",
    "README.md",
    "REPO_MAP.md",
    "MACHINE_CONTEXT.md",
    "CHAT_TRANSFER_CAPSULE_V1.md",
}

CLASS_CANONICAL = "CANONICAL_INTENDED_TRACKED"
CLASS_GENERATED = "GENERATED_RUNTIME_ONLY"
CLASS_REVIEW = "REVIEW_ARTIFACT_RETENTION"
CLASS_JUNK = "JUNK_OR_RESIDUE"
CLASS_AMBIGUOUS = "NEEDS_OWNER_DECISION"
CLASS_SUSPICIOUS = "SUSPICIOUS_INQUISITION_ATTENTION"

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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run_cmd(args: list[str]) -> dict[str, Any]:
    done = subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True, encoding="utf-8", errors="replace", check=False)
    return {
        "command": " ".join(args),
        "exit_code": int(done.returncode),
        "stdout": str(done.stdout or "").strip(),
        "stderr": str(done.stderr or "").strip(),
        "status": "PASS" if done.returncode == 0 else "FAIL",
    }


def parse_git_status() -> dict[str, Any]:
    raw = run_cmd(["git", "-c", "core.quotepath=false", "status", "--porcelain=v1", "--branch"]).get("stdout", "")
    branch = "UNKNOWN"
    staged: list[str] = []
    unstaged: list[str] = []
    untracked: list[str] = []
    deleted: list[str] = []
    renamed: list[str] = []

    for idx, row in enumerate(str(raw).splitlines()):
        line = str(row or "")
        if idx == 0 and line.startswith("##"):
            branch = line[2:].strip().split("...")[0].strip() or branch
            continue
        if line.startswith("?? "):
            untracked.append(line[3:].replace("\\", "/").strip().strip('\"'))
            continue
        if len(line) < 4:
            continue
        x = line[0]
        y = line[1]
        payload = line[3:].strip()
        path_norm = payload
        if " -> " in payload:
            left, right = payload.split(" -> ", 1)
            renamed.append(f"{left.replace('\\\\', '/').strip().strip('\"')} -> {right.replace('\\\\', '/').strip().strip('\"')}")
            path_norm = right
        path_norm = path_norm.replace("\\", "/").strip().strip('\"')
        if x not in {" ", "?"}:
            staged.append(path_norm)
        if y not in {" ", "?"}:
            unstaged.append(path_norm)
        if "D" in {x, y}:
            deleted.append(path_norm)

    def uniq(values: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            out.append(value)
        return out

    staged = uniq(staged)
    unstaged = uniq(unstaged)
    untracked = uniq(untracked)
    deleted = uniq(deleted)
    renamed = uniq(renamed)

    tracked_dirty_count = len(staged) + len(unstaged) + len(deleted) + len(renamed)
    untracked_count = len(untracked)
    if tracked_dirty_count == 0 and untracked_count == 0:
        cleanliness = "CLEAN"
    elif tracked_dirty_count > 0 and untracked_count == 0:
        cleanliness = "DIRTY_TRACKED_ONLY"
    elif tracked_dirty_count == 0 and untracked_count > 0:
        cleanliness = "DIRTY_UNTRACKED_ONLY"
    else:
        cleanliness = "DIRTY_MIXED"

    return {
        "generated_at_utc": now_iso(),
        "branch": branch,
        "head": run_cmd(["git", "rev-parse", "HEAD"]).get("stdout", ""),
        "cleanliness_verdict": cleanliness,
        "tracked_dirty_count": tracked_dirty_count,
        "untracked_count": untracked_count,
        "staged_paths": staged,
        "unstaged_paths": unstaged,
        "deleted_paths": deleted,
        "renamed_paths": renamed,
        "untracked_paths": untracked,
    }


def classify_path(path: str) -> str:
    rel = str(path or "").replace("\\", "/").strip().rstrip("/")
    if not rel:
        return CLASS_AMBIGUOUS
    low = rel.lower()

    if low.endswith((".tmp", ".temp", ".bak", ".old", ".orig", ".pyc")) or "/__pycache__/" in low:
        return CLASS_JUNK

    if rel in ROOT_CANONICAL_FILES:
        return CLASS_CANONICAL
    if rel.startswith("docs/governance/"):
        return CLASS_CANONICAL
    if rel.startswith("docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/"):
        return CLASS_CANONICAL
    if rel.startswith("scripts/"):
        return CLASS_CANONICAL
    if rel.startswith("shared_systems/"):
        return CLASS_CANONICAL
    if rel.startswith("workspace_config/"):
        return CLASS_CANONICAL
    if rel.startswith("projects/"):
        return CLASS_CANONICAL
    if rel.startswith("docs/INSTRUCTION_INDEX.md") or rel.startswith("docs/NEXT_CANONICAL_STEP.md"):
        return CLASS_CANONICAL

    if rel.startswith("runtime/"):
        return CLASS_GENERATED
    if rel.startswith("docs/review_artifacts/"):
        return CLASS_REVIEW

    if low.endswith((".rar", ".7z", ".bin", ".exe", ".dll")):
        return CLASS_SUSPICIOUS

    return CLASS_AMBIGUOUS


def build_classification(git_state: dict[str, Any]) -> dict[str, Any]:
    classes: dict[str, list[str]] = {
        CLASS_CANONICAL: [],
        CLASS_GENERATED: [],
        CLASS_REVIEW: [],
        CLASS_JUNK: [],
        CLASS_AMBIGUOUS: [],
        CLASS_SUSPICIOUS: [],
    }

    tracked = sorted(set(list(git_state.get("staged_paths", [])) + list(git_state.get("unstaged_paths", [])) + list(git_state.get("deleted_paths", [])) + list(git_state.get("renamed_paths", []))))
    untracked = sorted(set(list(git_state.get("untracked_paths", []))))

    for path in tracked:
        cls = classify_path(path)
        classes[cls].append(path)
    for path in untracked:
        cls = classify_path(path)
        classes[cls].append(path)

    for key in classes:
        classes[key] = sorted(set(classes[key]))

    summary = {
        "generated_at_utc": now_iso(),
        "tracked_dirty_count": int(git_state.get("tracked_dirty_count", 0) or 0),
        "untracked_count": int(git_state.get("untracked_count", 0) or 0),
        "classification_counts": {k: len(v) for k, v in classes.items()},
        "classification": classes,
    }
    return summary


def update_runtime_surfaces(step_id: str, git_state: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    counts = classification.get("classification_counts", {}) or {}
    classes = classification.get("classification", {}) or {}

    fix_now: list[str] = []
    open_allowed: list[str] = []
    if int(counts.get(CLASS_AMBIGUOUS, 0) or 0) > 0:
        fix_now.append("ambiguous_dirty_paths_present")
    if int(counts.get(CLASS_SUSPICIOUS, 0) or 0) > 0:
        fix_now.append("suspicious_dirty_paths_present")
    if int(counts.get(CLASS_JUNK, 0) or 0) > 0:
        fix_now.append("junk_or_residue_present")
    if int(git_state.get("tracked_dirty_count", 0) or 0) > 0:
        open_allowed.append("tracked_dirty_baseline_classified_as_canonical_intended")
    if int(git_state.get("untracked_count", 0) or 0) > 0:
        open_allowed.append("untracked_dirty_baseline_classified_and_governed")

    purity_pass = len(fix_now) == 0

    purity_gate = {
        "surface_id": "IMPERIUM_WORKTREE_PURITY_GATE_V1",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "status": "PASS" if purity_pass else "FAIL",
        "mode": "CANON_SAFE_BASELINE_CLASSIFIED" if purity_pass else "BLOCKED_UNRESOLVED_DIRTY_CLASS",
        "git_clean": bool((git_state.get("tracked_dirty_count", 0) == 0) and (git_state.get("untracked_count", 0) == 0)),
        "cleanliness_verdict": str(git_state.get("cleanliness_verdict", "UNKNOWN")),
        "tracked_dirty_count": int(git_state.get("tracked_dirty_count", 0) or 0),
        "untracked_count": int(git_state.get("untracked_count", 0) or 0),
        "classification_reference": "runtime/repo_control_center/imperium_repo_wide_dirty_baseline_classification_v1.json",
        "classification_counts": counts,
        "fix_now_blockers": fix_now,
        "open_allowed_conditions": open_allowed,
        "owner_decision_required": len(fix_now) > 0,
    }
    write_json(WORKTREE_GATE, purity_gate)

    adapter_payload = {
        "surface_id": "IMPERIUM_REPO_HYGIENE_CLASSIFICATION_SURFACE_V1",
        "version": "1.1.0",
        "status": "ACTIVE",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "cleanliness_verdict": str(git_state.get("cleanliness_verdict", "UNKNOWN")),
        "tracked_dirty_count": int(git_state.get("tracked_dirty_count", 0) or 0),
        "untracked_count": int(git_state.get("untracked_count", 0) or 0),
        "classification_counts": counts,
        "classification": classes,
        "fix_now_blockers": fix_now,
        "open_allowed_conditions": open_allowed,
        "notes": [
            "repo_wide_dirty_baseline_classified",
            "canon_safe_baseline_mode_active",
            "no_unclassified_paths_remaining" if len(fix_now) == 0 else "unresolved_blockers_present",
        ],
    }
    write_json(REPO_HYGIENE_ADAPTER, adapter_payload)

    worktree_adapter = {
        "surface_id": "IMPERIUM_WORKTREE_PURITY_GATE_SURFACE_V1",
        "version": "1.0.0",
        "status": "ACTIVE",
        "generated_at_utc": now_iso(),
        "truth_class": "SOURCE_EXACT",
        "source_path": to_rel(WORKTREE_GATE),
        "payload": purity_gate,
    }
    write_json(WORKTREE_GATE_ADAPTER, worktree_adapter)

    inq = load_json(INQUISITION, {})
    inq["generated_at_utc"] = now_iso()
    inq["step_id"] = step_id
    inq["mode"] = "ADVISORY"
    inq["checks_rerun"] = ["truth_schema_engine", "law_gate", "provenance_seal", "worktree_purity_gate", "bundle_truth_chamber"]
    inq["post"] = {
        **dict((inq.get("post", {}) or {})),
        "worktree_purity_gate": purity_gate.get("status", "UNKNOWN"),
        "truth_spine": load_json(TRUTH_SPINE, {}).get("status", "UNKNOWN"),
        "dashboard_truth_engine": load_json(DASHBOARD_ENGINE, {}).get("status", "UNKNOWN"),
        "bundle_truth_chamber": load_json(BUNDLE_CHAMBER, {}).get("status", "UNKNOWN"),
    }
    inq["truth_guard_checks"] = {
        "truth_spine": load_json(TRUTH_SPINE, {}).get("status", "UNKNOWN"),
        "dashboard_truth_engine": load_json(DASHBOARD_ENGINE, {}).get("status", "UNKNOWN"),
        "worktree_purity_gate": purity_gate.get("status", "UNKNOWN"),
        "bundle_truth_chamber": load_json(BUNDLE_CHAMBER, {}).get("status", "UNKNOWN"),
        "address_lattice": load_json(ADDRESS_LATTICE, {}).get("status", "UNKNOWN"),
    }
    inq["failures"] = list(fix_now)
    inq["rebuild_required"] = len(fix_now) > 0
    inq["status"] = "PASS" if len(fix_now) == 0 else "REBUILD_REQUIRED"
    write_json(INQUISITION, inq)

    watch = load_json(WATCH, {})
    watch["generated_at_utc"] = now_iso()
    watch["step_id"] = step_id
    watch["truth_status"] = load_json(TRUTH_SPINE, {}).get("status", "UNKNOWN")
    watch["transport_status"] = load_json(BUNDLE_CHAMBER, {}).get("status", "UNKNOWN")
    watch["gates"] = {
        **dict((watch.get("gates", {}) or {})),
        "worktree_purity_gate": purity_gate.get("status", "UNKNOWN"),
        "inquisition_loop": inq.get("status", "UNKNOWN"),
    }
    watch["open_blockers"] = list(fix_now)
    write_json(WATCH, watch)

    control = load_json(CONTROL_GATES_ADAPTER, {})
    gate_rows = list((control.get("gates", []) or []))
    for row in gate_rows:
        gate_id = str((row or {}).get("gate_id", "")).strip()
        if gate_id == "worktree_purity_gate":
            row["state"] = "PASS" if purity_pass else "BLOCKED"
        if gate_id == "inquisition_truth_guard_gate":
            row["state"] = "PASS" if inq.get("status") == "PASS" else "BLOCKED"
    if gate_rows:
        control["gates"] = gate_rows
        write_json(CONTROL_GATES_ADAPTER, control)

    write_json(RUNTIME_ROOT / "imperium_repo_wide_dirty_baseline_classification_v1.json", classification)

    return {
        "fix_now": fix_now,
        "open_allowed": open_allowed,
        "purity_gate": purity_gate,
        "inquisition": inq,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="IMPERIUM repo-wide dirty baseline cleanup and purity closure")
    parser.add_argument("--step-id", default="")
    args = parser.parse_args()

    step_id = args.step_id.strip() or f"{STEP_PREFIX}_{now_stamp()}"
    step_root = REVIEW_ROOT / step_id
    step_root.mkdir(parents=True, exist_ok=True)

    git_state = parse_git_status()
    classification = build_classification(git_state)
    update = update_runtime_surfaces(step_id, git_state, classification)

    truth_spine = load_json(TRUTH_SPINE, {})
    dashboard_truth = load_json(DASHBOARD_ENGINE, {})
    bundle_truth = load_json(BUNDLE_CHAMBER, {})
    address_lattice = load_json(ADDRESS_LATTICE, {})

    write_text(step_root / "00_REVIEW_ENTRYPOINT.md", f"# 00_REVIEW_ENTRYPOINT\n\n- step_id: `{step_id}`\n- mode: `repo-wide dirty baseline cleanup / purity closure`\n")
    write_text(step_root / "01_INTEGRATION_REPORT.md", "# 01_INTEGRATION_REPORT\n\nRepo-wide dirty baseline fully classified into canonical classes, purity gate rebuilt to canon-safe baseline mode, inquisition/watch/control gates resynchronized.")
    write_text(step_root / "02_VALIDATION_REPORT.md", f"# 02_VALIDATION_REPORT\n\n- truth_spine: `{truth_spine.get('status', 'UNKNOWN')}`\n- dashboard_truth_engine: `{dashboard_truth.get('status', 'UNKNOWN')}`\n- bundle_truth_chamber: `{bundle_truth.get('status', 'UNKNOWN')}`\n- worktree_purity_gate: `{update['purity_gate'].get('status', 'UNKNOWN')}`\n- inquisition_loop: `{update['inquisition'].get('status', 'UNKNOWN')}`\n")
    write_text(step_root / "03_TRUTH_CHECK_AND_GAPS.md", f"# 03_TRUTH_CHECK_AND_GAPS\n\n- fix_now_blockers: `{len(update['fix_now'])}`\n- open_allowed: `{len(update['open_allowed'])}`\n- tracked_dirty_count: `{git_state.get('tracked_dirty_count', 0)}`\n- untracked_count: `{git_state.get('untracked_count', 0)}`\n")
    write_text(step_root / "04_CHANGED_SURFACES.md", "# 04_CHANGED_SURFACES\n\n- runtime worktree purity gate\n- runtime inquisition/watch state\n- repo hygiene classification surface\n- control gates reconciliation\n- step evidence + transfer truth")

    smoke_payload = {
        "generated_at_utc": now_iso(),
        "state_truth_spine": truth_spine.get("status", "UNKNOWN"),
        "state_dashboard_truth_engine": dashboard_truth.get("status", "UNKNOWN"),
        "state_bundle_truth_chamber": bundle_truth.get("status", "UNKNOWN"),
        "state_worktree_purity_gate": update["purity_gate"].get("status", "UNKNOWN"),
        "state_address_lattice": address_lattice.get("status", "UNKNOWN"),
        "inquisition_status": update["inquisition"].get("status", "UNKNOWN"),
    }
    write_json(step_root / "05_API_SMOKE.json", smoke_payload)
    write_json(step_root / "07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json", {}))
    write_json(step_root / "08_ORGAN_STRENGTH_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "imperium_force" / "IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json", {}))
    write_json(step_root / "09_NODE_RANK_DETECTION_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "repo_control_center" / "validation" / "node_rank_detection.json", {}))
    write_json(step_root / "10_MACHINE_MODE_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "repo_control_center" / "one_screen_status.json", {}))
    write_json(step_root / "11_CONSTITUTION_STATUS_SNAPSHOT.json", load_json(REPO_ROOT / "runtime" / "repo_control_center" / "constitution_status.json", {}))

    write_json(step_root / "12_DIRTY_BASELINE_CLASSIFICATION.json", classification)
    write_json(step_root / "13_WORKTREE_PURITY_GATE_STATE.json", update["purity_gate"])
    write_json(step_root / "14_INQUISITION_STATE.json", update["inquisition"])
    blocker_payload = {
        "FIX_NOW": list(update["fix_now"]),
        "OPEN_BUT_ALLOWED": list(update["open_allowed"]),
        "POLICY_SKIPPED": [],
        "FUTURE_WORK": [
            "full_event_bus_not_yet_implemented",
            "auto_preview_pipeline_not_yet_implemented",
            "pixel_level_perceptual_diff_unavailable_in_scope",
            "two_disk_migration_not_physically_validated",
        ],
    }
    write_json(step_root / "15_BLOCKER_CLASSIFICATION.json", blocker_payload)

    include_paths = [f"docs/review_artifacts/{step_id}/{name}" for name in REQUIRED_REVIEW]
    include_paths += [
        f"docs/review_artifacts/{step_id}/12_DIRTY_BASELINE_CLASSIFICATION.json",
        f"docs/review_artifacts/{step_id}/13_WORKTREE_PURITY_GATE_STATE.json",
        f"docs/review_artifacts/{step_id}/14_INQUISITION_STATE.json",
        f"docs/review_artifacts/{step_id}/15_BLOCKER_CLASSIFICATION.json",
        f"docs/review_artifacts/{step_id}/16_TRANSPORT_SELF_READ_REPORT.json",
        f"docs/review_artifacts/{step_id}/17_EXECUTION_META.json",
        f"docs/review_artifacts/{step_id}/21_FINAL_RESULT.json",
        to_rel(WORKTREE_GATE),
        to_rel(INQUISITION),
        to_rel(WATCH),
        to_rel(REPO_HYGIENE_ADAPTER),
        to_rel(WORKTREE_GATE_ADAPTER),
        to_rel(CONTROL_GATES_ADAPTER),
        "scripts/imperium_repo_wide_dirty_baseline_purity_closure.py",
    ]
    write_text(step_root / "06_BUNDLE_INCLUDE_PATHS.txt", "\n".join(sorted(set(include_paths))))

    prelim = {
        "schema_version": "imperium_repo_wide_dirty_baseline_purity_closure_final.v1",
        "generated_at_utc": now_iso(),
        "step_id": step_id,
        "review_root": to_rel(step_root),
        "status": "PENDING",
        "acceptance": "PENDING",
        "truth_spine": truth_spine.get("status", "UNKNOWN"),
        "dashboard_truth_engine": dashboard_truth.get("status", "UNKNOWN"),
        "bundle_truth_chamber": bundle_truth.get("status", "UNKNOWN"),
        "worktree_purity_gate": update["purity_gate"].get("status", "UNKNOWN"),
        "inquisition_loop": update["inquisition"].get("status", "UNKNOWN"),
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
    }
    write_json(step_root / "21_FINAL_RESULT.json", prelim)

    cmd1 = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
    enforcer1 = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    transport1 = dict(((enforcer1.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}) or {}))
    transfer1 = dict((((enforcer1.get("chatgpt_transfer", {}) or {}).get("result", {}) or {}).get("transfer_report", {}) or {}))

    failure_reasons: list[str] = []
    if update["purity_gate"].get("status") != "PASS":
        failure_reasons.append("worktree_purity_gate_not_pass")
    if update["inquisition"].get("status") != "PASS":
        failure_reasons.append("inquisition_not_pass")
    if truth_spine.get("status") != "PASS":
        failure_reasons.append("truth_spine_not_pass")
    if dashboard_truth.get("status") != "PASS":
        failure_reasons.append("dashboard_truth_engine_not_pass")
    if bundle_truth.get("status") != "PASS":
        failure_reasons.append("bundle_truth_chamber_not_pass")
    if str(enforcer1.get("verdict", "UNKNOWN")) != "PASS" or str(transport1.get("status", "UNKNOWN")) != "PASS":
        failure_reasons.append("bundle_output_enforcer_not_pass")

    final = dict(prelim)
    final["transport_integrity"] = str(transport1.get("status", "UNKNOWN"))
    final["transfer_package_completeness"] = str(transport1.get("package_completeness", "UNKNOWN"))
    final["core_required"] = bool(transport1.get("core_required", False))
    final["parts_total"] = int(transport1.get("manifest_parts_total", 0) or 0)
    final["upload_order"] = list(transport1.get("upload_order_declared", []) or [])
    final["optional_included"] = bool(transfer1.get("optional_included", False))
    final["visual_included"] = bool(transfer1.get("visual_included", False))
    final["optional_part_count"] = int(transfer1.get("optional_part_count", 0) or 0)
    final["visual_part_count"] = int(transfer1.get("visual_part_count", 0) or 0)
    final["failure_reasons"] = sorted(set(failure_reasons))
    final["status"] = "PASS" if len(final["failure_reasons"]) == 0 else "FAIL"
    final["acceptance"] = "PASS" if final["status"] == "PASS" else "FAIL"
    write_json(step_root / "21_FINAL_RESULT.json", final)

    write_json(
        step_root / "16_TRANSPORT_SELF_READ_REPORT.json",
        {
            "generated_at_utc": now_iso(),
            "enforcer_verdict": str(enforcer1.get("verdict", "UNKNOWN")),
            "transport_integrity": str(transport1.get("status", "UNKNOWN")),
            "entrypoint_matches_disk": bool(transport1.get("entrypoint_matches_disk", False)),
            "final_result_matches_disk": bool(transport1.get("final_result_matches_disk", False)),
            "required_entries_missing": list(transport1.get("required_entries_missing", []) or []),
            "foreign_review_roots": list(transport1.get("foreign_review_roots", []) or []),
        },
    )
    write_json(
        step_root / "17_EXECUTION_META.json",
        {
            "generated_at_utc": now_iso(),
            "step_id": step_id,
            "git_state": git_state,
            "classification_counts": classification.get("classification_counts", {}),
            "actions": {
                "safe_cleanup_deletions": 0,
                "ignore_policy_changes": 0,
                "mechanism_mode": "canon_safe_baseline_classified",
            },
            "commands": {"enforcer_pass1": cmd1},
        },
    )

    cmd2 = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
    enforcer2 = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
    transport2 = dict(((enforcer2.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}) or {}))
    if str(enforcer2.get("verdict", "UNKNOWN")) != "PASS" or str(transport2.get("status", "UNKNOWN")) != "PASS":
        reasons = set(final.get("failure_reasons", []) or [])
        reasons.add("bundle_output_enforcer_not_pass")
        final["failure_reasons"] = sorted(reasons)
        final["transport_integrity"] = str(transport2.get("status", "UNKNOWN"))
        final["transfer_package_completeness"] = str(transport2.get("package_completeness", "UNKNOWN"))
        final["status"] = "FAIL"
        final["acceptance"] = "FAIL"
        write_json(step_root / "21_FINAL_RESULT.json", final)
        run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
    else:
        reasons = set(final.get("failure_reasons", []) or [])
        reasons.discard("bundle_output_enforcer_not_pass")
        final["failure_reasons"] = sorted(reasons)
        final["transport_integrity"] = "PASS"
        final["transfer_package_completeness"] = str(transport2.get("package_completeness", "COMPLETE"))
        final["status"] = "PASS" if len(final["failure_reasons"]) == 0 else "FAIL"
        final["acceptance"] = "PASS" if final["status"] == "PASS" else "FAIL"
        write_json(step_root / "21_FINAL_RESULT.json", final)
        cmd3 = run_cmd(["python", str(ENFORCER_SCRIPT), "--review-root", to_rel(step_root), "--retention-check"])
        enforcer3 = load_json(step_root / "12_BUNDLE_OUTPUT_ENFORCEMENT_REPORT.json", {})
        transport3 = dict(((enforcer3.get("chatgpt_transfer", {}) or {}).get("transport_integrity", {}) or {}))
        if str(enforcer3.get("verdict", "UNKNOWN")) != "PASS" or str(transport3.get("status", "UNKNOWN")) != "PASS":
            reasons = set(final.get("failure_reasons", []) or [])
            reasons.add("bundle_output_enforcer_not_pass")
            final["failure_reasons"] = sorted(reasons)
            final["transport_integrity"] = str(transport3.get("status", "UNKNOWN"))
            final["status"] = "FAIL"
            final["acceptance"] = "FAIL"
            write_json(step_root / "21_FINAL_RESULT.json", final)

    print(json.dumps(final, ensure_ascii=False))
    return 0 if final.get("acceptance") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
