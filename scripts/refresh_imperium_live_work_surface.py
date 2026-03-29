#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = (
    REPO_ROOT
    / "shared_systems"
    / "factory_observation_window_v1"
    / "adapters"
    / "IMPERIUM_LIVE_WORK_VISIBILITY_SURFACE_V1.json"
)
DEFAULT_STEP_ID = "IMPERIUM_CONSTITUTION_GREEN_CHAIN_REPO_HYGIENE_COVERAGE_AND_LIVE_WORK_VISIBILITY_DELTA"
CONSTITUTION_STATUS_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "constitution_status.json"
ONE_SCREEN_STATUS_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "one_screen_status.json"
REPO_CONTROL_STATUS_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "repo_control_status.json"
DOMINANCE_SURFACE_PATH = (
    REPO_ROOT
    / "shared_systems"
    / "factory_observation_window_v1"
    / "adapters"
    / "IMPERIUM_TRUTH_DOMINANCE_SURFACE_V1.json"
)
CODE_BANK_SURFACE_PATH = (
    REPO_ROOT
    / "shared_systems"
    / "factory_observation_window_v1"
    / "adapters"
    / "IMPERIUM_CODE_BANK_STATE_SURFACE_V1.json"
)
COVERAGE_SURFACE_PATH = (
    REPO_ROOT
    / "shared_systems"
    / "factory_observation_window_v1"
    / "adapters"
    / "IMPERIUM_DASHBOARD_COVERAGE_SURFACE_V1.json"
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return str(completed.stdout or "").strip()


def parse_status_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    raw = run_git(["status", "--porcelain=v1"])
    for line in raw.splitlines():
        if len(line) < 3:
            continue
        code = line[:2]
        raw_path = line[3:].strip()
        path = raw_path
        if " -> " in raw_path:
            path = raw_path.split(" -> ", 1)[1]
        rel = normalize(path)
        if not rel:
            continue
        change_type = "MODIFIED"
        upper_code = code.upper()
        if upper_code == "??":
            change_type = "UNTRACKED"
        elif "A" in upper_code:
            change_type = "ADDED"
        elif "D" in upper_code:
            change_type = "DELETED"
        elif "R" in upper_code:
            change_type = "RENAMED"
        rows.append({"status_code": code, "change_type": change_type, "path": rel})
    return rows


def touched_groups(rows: list[dict[str, str]], limit: int = 10) -> list[dict[str, Any]]:
    bucket: Counter[str] = Counter()
    for item in rows:
        rel = str(item.get("path", ""))
        parts = [p for p in rel.split("/") if p]
        if not parts:
            continue
        key = parts[0] if len(parts) == 1 else f"{parts[0]}/{parts[1]}"
        bucket[key] += 1
    result = [{"group_id": key, "changes_count": int(value)} for key, value in bucket.most_common(limit)]
    return result


def infer_operation_class(rows: list[dict[str, str]], fallback: str) -> str:
    if fallback:
        return fallback
    change_types = {str(item.get("change_type", "")) for item in rows}
    if "UNTRACKED" in change_types or "ADDED" in change_types or "MODIFIED" in change_types:
        return "PATCH"
    return "READ"


def build_surface(
    *,
    step_id: str,
    phase_id: str,
    phase_index: int,
    phase_total: int,
    operation_class: str,
) -> dict[str, Any]:
    constitution = load_json_if_exists(CONSTITUTION_STATUS_PATH)
    one_screen = load_json_if_exists(ONE_SCREEN_STATUS_PATH)
    repo_control = load_json_if_exists(REPO_CONTROL_STATUS_PATH)
    dominance = load_json_if_exists(DOMINANCE_SURFACE_PATH)
    code_bank = load_json_if_exists(CODE_BANK_SURFACE_PATH)
    coverage = load_json_if_exists(COVERAGE_SURFACE_PATH)
    git_rows = parse_status_rows()
    op_class = infer_operation_class(git_rows, operation_class.strip().upper())

    governance_verdict = str(constitution.get("governance_acceptance", "UNKNOWN")).upper()
    sync_verdict = str(constitution.get("sync_status", "UNKNOWN")).upper()
    trust_verdict = str(constitution.get("trust_status", "UNKNOWN")).upper()
    constitution_overall = str(constitution.get("overall_verdict", "UNKNOWN")).upper()
    blocker_reason = str(one_screen.get("blocking_reason_detail", "")).strip()
    blocker_category = str(one_screen.get("blocking_reason_category", "NONE")).upper()

    if blocker_reason:
        wait_reason = blocker_reason
    elif constitution_overall == "FAIL":
        wait_reason = "constitution цепочка не зелёная: требуется закрыть governance/trust/sync блокеры"
    else:
        wait_reason = "active progression"

    progress_ratio = 0.0
    if phase_total > 0 and phase_index > 0:
        progress_ratio = min(1.0, max(0.0, phase_index / float(phase_total)))

    top_changes = git_rows[:25]
    changed_groups = touched_groups(git_rows)
    tracked_dirty = len([x for x in git_rows if x["change_type"] != "UNTRACKED"])
    untracked_count = len([x for x in git_rows if x["change_type"] == "UNTRACKED"])
    stale_rules = int(dominance.get("stale_rules_count", 0) or 0)
    code_status = str((code_bank.get("summary", {}) or {}).get("status_classification", "UNKNOWN"))
    coverage_verdict = str(coverage.get("coverage_verdict", "UNKNOWN"))
    pointer_only = int(coverage.get("pointer_only_count", 0) or 0)

    return {
        "surface_id": "IMPERIUM_LIVE_WORK_VISIBILITY_SURFACE_V1",
        "version": "1.0.0",
        "status": "ACTIVE",
        "truth_class": "SOURCE_EXACT",
        "generated_at_utc": utc_now_iso(),
        "source_path": "scripts/refresh_imperium_live_work_surface.py",
        "live_stream_mode": {
            "status": "PARTIALLY_IMPLEMENTED",
            "class": "DERIVED_CANONICAL",
            "event_bus_status": "NOT_YET_IMPLEMENTED",
            "update_method": "git_status_plus_runtime_surfaces",
        },
        "current_active_step": {
            "step_id": step_id,
            "scope_class": "bounded_canonical_step",
            "owner_visibility": "EXPLICIT",
        },
        "current_phase": {
            "phase_id": phase_id,
            "phase_index": max(1, int(phase_index)),
            "phase_total": max(1, int(phase_total)),
            "progress_ratio": round(progress_ratio, 3),
        },
        "current_operation": {
            "operation_class": op_class,
            "operation_class_ru": {
                "READ": "чтение",
                "DIFF": "сверка",
                "PATCH": "правка",
                "VALIDATE": "валидация",
                "BUNDLE": "упаковка",
                "AUDIT": "аудит",
            }.get(op_class, "операция"),
            "transport": "derived_live_lane",
        },
        "progress_markers": {
            "tracked_dirty_changes": tracked_dirty,
            "untracked_changes": untracked_count,
            "changed_groups_count": len(changed_groups),
            "coverage_verdict": coverage_verdict,
            "pointer_only_count": pointer_only,
            "code_bank_status": code_status,
            "stale_dominance_rules_count": stale_rules,
            "sync_status": sync_verdict,
            "trust_status": trust_verdict,
            "governance_acceptance": governance_verdict,
        },
        "touched_surface_groups": changed_groups,
        "recent_changes": top_changes,
        "blocker_or_wait": {
            "category": blocker_category if blocker_category else "NONE",
            "reason_ru": wait_reason,
            "operator_action_required": bool(one_screen.get("operator_action_required", False)),
        },
        "notes": [
            "No fake full realtime: lane is derived from git/runtime surfaces.",
            "Event bus remains explicitly NOT_YET_IMPLEMENTED.",
            "Owner-readable fields are primary; technical feed is secondary.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh IMPERIUM live-work visibility surface.")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--step-id", default=DEFAULT_STEP_ID, help="Current bounded step id")
    parser.add_argument("--phase-id", default="PHASE_5_LIVE_WORK_VISIBILITY", help="Current phase id")
    parser.add_argument("--phase-index", type=int, default=5, help="Current phase ordinal")
    parser.add_argument("--phase-total", type=int, default=6, help="Total phases for current step")
    parser.add_argument(
        "--operation-class",
        default="",
        help="Optional forced operation class: READ/DIFF/PATCH/VALIDATE/BUNDLE/AUDIT",
    )
    args = parser.parse_args()

    out_path = Path(args.out).expanduser()
    if not out_path.is_absolute():
        out_path = (REPO_ROOT / out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_surface(
        step_id=str(args.step_id).strip() or DEFAULT_STEP_ID,
        phase_id=str(args.phase_id).strip() or "PHASE_5_LIVE_WORK_VISIBILITY",
        phase_index=int(args.phase_index),
        phase_total=int(args.phase_total),
        operation_class=str(args.operation_class),
    )
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "output": str(out_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
