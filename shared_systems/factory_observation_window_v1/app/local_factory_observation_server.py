#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DEFAULT_ADAPTER_PATH = "shared_systems/factory_observation_window_v1/adapters/TIKTOK_BUNDLE_ADAPTER_V1.json"
DEFAULT_FACTORY_STATE_MODEL_PATH = "shared_systems/factory_observation_window_v1/adapters/FACTORY_STATE_VIEW_MODEL_V1.json"
DEFAULT_DEPARTMENT_FLOOR_MODEL_PATH = "shared_systems/factory_observation_window_v1/adapters/DEPARTMENT_FLOOR_VIEW_MODEL_V1.json"
DEFAULT_PRODUCT_LANE_MODEL_PATH = "shared_systems/factory_observation_window_v1/adapters/PRODUCT_LANE_BOARD_MODEL_V1.json"
DEFAULT_QUEUE_MONITOR_MODEL_PATH = "shared_systems/factory_observation_window_v1/adapters/QUEUE_MONITOR_MODEL_V1.json"
DEFAULT_FORCE_MAP_MODEL_PATH = "shared_systems/factory_observation_window_v1/adapters/FORCE_MAP_VISUAL_MODEL_V1.json"
DEFAULT_PRODUCTION_HISTORY_SEED_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/TIKTOK_WAVE1_PRODUCTION_HISTORY_SEED_V1.json"
)
DEFAULT_LIVE_STATE_MODEL_PATH = "shared_systems/factory_observation_window_v1/adapters/LIVE_OBSERVATION_STATE_MODEL_V1.json"
DEFAULT_LIVE_EVENT_MODEL_PATH = "shared_systems/factory_observation_window_v1/adapters/FACTORY_LIVE_EVENT_MODEL_V1.json"
DEFAULT_CANON_STATE_SYNC_PATH = "shared_systems/factory_observation_window_v1/adapters/CURRENT_FACTORY_CANON_STATE_V1.json"
DEFAULT_WAVE1_CONTROL_SURFACES_PATH = "shared_systems/factory_observation_window_v1/adapters/TIKTOK_WAVE1_CONTROL_SURFACES_V1.json"
DEFAULT_SYSTEM_SEMANTIC_STATE_MODEL_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/SYSTEM_SEMANTIC_STATE_SURFACES_V1.json"
)
DEFAULT_IMPERIUM_EVOLUTION_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_EVOLUTION_STATE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_INQUISITION_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_INQUISITION_STATE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_FACTORY_PRODUCTION_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_FACTORY_PRODUCTION_STATE_V1.json"
)
DEFAULT_IMPERIUM_PRODUCT_EVOLUTION_MAP_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_PRODUCT_EVOLUTION_MAP_V1.json"
)
DEFAULT_IMPERIUM_EVENT_FLOW_SPINE_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_EVENT_FLOW_SPINE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_DIFF_PREVIEW_PIPELINE_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_DIFF_PREVIEW_PIPELINE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_GOLDEN_THRONE_DISCOVERABILITY_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_GOLDEN_THRONE_DISCOVERABILITY_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_TRUE_FORM_MATRYOSHKA_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_TRUE_FORM_MATRYOSHKA_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_CUSTODES_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADEPTUS_CUSTODES_STATE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_MECHANICUS_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADEPTUS_MECHANICUS_STATE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_ADMINISTRATUM_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADMINISTRATUM_STATE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_FORCE_DOCTRINE_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_FORCE_DOCTRINE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_PALACE_ARCHIVE_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_PALACE_AND_ARCHIVE_STATE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_CONTROL_GATES_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_CONTROL_GATES_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_CODE_BANK_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_CODE_BANK_STATE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_DASHBOARD_COVERAGE_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_DASHBOARD_COVERAGE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_TRUTH_DOMINANCE_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_TRUTH_DOMINANCE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_STORAGE_HEALTH_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_STORAGE_HEALTH_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_REPO_HYGIENE_CLASSIFICATION_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_REPO_HYGIENE_CLASSIFICATION_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_LIVE_WORK_VISIBILITY_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_LIVE_WORK_VISIBILITY_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_DOCTRINE_INTEGRITY_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_DOCTRINE_INTEGRITY_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_TRUTH_SPINE_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_TRUTH_SPINE_STATE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_DASHBOARD_TRUTH_ENGINE_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_DASHBOARD_TRUTH_ENGINE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_BUNDLE_TRUTH_CHAMBER_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_BUNDLE_TRUTH_CHAMBER_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_WORKTREE_PURITY_GATE_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_WORKTREE_PURITY_GATE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_ADDRESS_LATTICE_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADDRESS_LATTICE_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_ANTI_LIE_MODEL_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ANTI_LIE_MODEL_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_LIVE_TRUTH_SUPPORT_LOOP_SURFACE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_LIVE_TRUTH_SUPPORT_LOOP_SURFACE_V1.json"
)
DEFAULT_VISUAL_EVIDENCE_ROOT = "docs/review_artifacts/visual_evidence"
DEFAULT_LIVE_EVENT_LOG_PATH = "runtime/factory_observation/live_events.jsonl"
DEFAULT_LIVE_STATE_SNAPSHOT_PATH = "runtime/factory_observation/live_state_snapshot.json"
DEFAULT_ONE_SCREEN_STATUS_PATH = "runtime/repo_control_center/one_screen_status.json"
DEFAULT_REPO_CONTROL_STATUS_PATH = "runtime/repo_control_center/repo_control_status.json"
DEFAULT_OPERATOR_MISSION_CONSISTENCY_PATH = "runtime/repo_control_center/operator_mission_consistency.json"
DEFAULT_OPERATOR_TASK_PROGRAM_CONSISTENCY_PATH = "runtime/repo_control_center/operator_task_program_consistency.json"
DEFAULT_OPERATOR_COMMAND_SURFACE_SCRIPT_PATH = "scripts/operator_command_surface.py"
DEFAULT_OPERATOR_COMMAND_SURFACE_STATUS_PATH = "runtime/operator_command_layer/command_surface_status.json"
DEFAULT_TIKTOK_PROJECT_CORE_ROOT = "projects/wild_hunt_command_citadel/tiktok_agent_platform/core"
DEFAULT_TIKTOK_RUNTIME_OBSERVABILITY_SNAPSHOT_PATH = (
    "projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/runtime_observability_snapshot.json"
)
DEFAULT_TIKTOK_RUNTIME_LOG_PATH = (
    "projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/logs/runtime_logs.jsonl"
)
DEFAULT_ACTIVE_EVIDENCE_BUNDLE_PATH = (
    "runtime/chatgpt_bundle_exports/imperium_remediation_consolidation_supreme_brain_delta_primary_truth_bundle_latest.zip"
)
DEFAULT_FALLBACK_BUNDLE_PATH = (
    "runtime/chatgpt_bundle_exports/imperium_remediation_consolidation_supreme_brain_delta_primary_truth_bundle_latest.zip"
)
DEFAULT_COMPANION_BUNDLE_PATH = (
    "runtime/chatgpt_bundle_exports/tiktok_agent_owner_gate_review_manual_safe_bundle_20260321T202031Z.zip"
)
DEFAULT_GOLDEN_THRONE_AUTHORITY_ANCHOR_PATH = "docs/governance/GOLDEN_THRONE_AUTHORITY_ANCHOR_V1.json"
DEFAULT_NODE_RANK_DETECTION_STATUS_PATH = "runtime/repo_control_center/validation/node_rank_detection.json"
DEFAULT_IMPERIUM_MACHINE_CAPABILITY_MANIFEST_PATH = (
    "runtime/imperium_force/IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json"
)
DEFAULT_IMPERIUM_ORGAN_STRENGTH_SURFACE_PATH = (
    "runtime/imperium_force/IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json"
)
DEFAULT_IMPERIUM_ACTIVE_MISSION_CONTRACT_PATH = (
    "runtime/administratum/IMPERIUM_ACTIVE_MISSION_CONTRACT_V1.json"
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_rel(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def read_zip_text(zf: zipfile.ZipFile, member: str) -> str:
    with zf.open(member) as fh:
        return fh.read().decode("utf-8", errors="replace")


def find_member_by_suffix(names: list[str], suffix: str) -> str | None:
    target = normalize_rel(suffix)
    for name in names:
        if normalize_rel(name).endswith(target):
            return name
    return None


def load_json_file(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_json_file_if_exists(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return load_json_file(path)
    except Exception:
        return {}


def run_git_command(repo_root: Path, args: list[str]) -> tuple[int, str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode, str(completed.stdout or "").strip()


def collect_repo_worktree_hygiene(repo_root: Path) -> dict:
    status_code, status_text = run_git_command(repo_root, ["status", "--porcelain=v1", "--branch"])
    branch_name = "UNKNOWN"
    upstream = ""
    ahead = 0
    behind = 0
    staged: list[str] = []
    unstaged: list[str] = []
    untracked: list[str] = []
    deleted: list[str] = []
    renamed: list[str] = []
    modified: list[str] = []

    if status_code == 0 and status_text:
        for idx, raw in enumerate(status_text.splitlines()):
            line = str(raw or "")
            if idx == 0 and line.startswith("##"):
                header = line[2:].strip()
                branch_name = header.split("...")[0].strip() or branch_name
                if "..." in header:
                    upstream = header.split("...", 1)[1].split(" ")[0].strip()
                ahead_match = re.search(r"ahead (\d+)", header)
                behind_match = re.search(r"behind (\d+)", header)
                if ahead_match:
                    ahead = int(ahead_match.group(1))
                if behind_match:
                    behind = int(behind_match.group(1))
                continue
            if line.startswith("?? "):
                path_value = normalize_rel(line[3:])
                if path_value:
                    untracked.append(path_value)
                continue
            if len(line) < 4:
                continue
            x = line[0]
            y = line[1]
            payload = line[3:].strip()
            if " -> " in payload:
                before, after = payload.split(" -> ", 1)
                before_norm = normalize_rel(before)
                after_norm = normalize_rel(after)
                renamed.append(f"{before_norm} -> {after_norm}")
                path_norm = after_norm
            else:
                path_norm = normalize_rel(payload)
            if not path_norm:
                continue
            if x not in {" ", "?"}:
                staged.append(path_norm)
            if y not in {" ", "?"}:
                unstaged.append(path_norm)
            if "D" in {x, y}:
                deleted.append(path_norm)
            if "M" in {x, y}:
                modified.append(path_norm)

    def unique(items: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in items:
            if item in seen:
                continue
            seen.add(item)
            out.append(item)
        return out

    staged = unique(staged)
    unstaged = unique(unstaged)
    untracked = unique(untracked)
    deleted = unique(deleted)
    renamed = unique(renamed)
    modified = unique(modified)

    tracked_dirty_count = len(staged) + len(unstaged) + len(deleted) + len(renamed)
    untracked_count = len(untracked)
    if tracked_dirty_count == 0 and untracked_count == 0:
        cleanliness_verdict = "CLEAN"
    elif tracked_dirty_count > 0 and untracked_count == 0:
        cleanliness_verdict = "DIRTY_TRACKED_ONLY"
    elif tracked_dirty_count == 0 and untracked_count > 0:
        cleanliness_verdict = "DIRTY_UNTRACKED_ONLY"
    elif tracked_dirty_count > 0 and untracked_count > 0:
        cleanliness_verdict = "DIRTY_MIXED"
    else:
        cleanliness_verdict = "UNKNOWN"

    _, head_hash = run_git_command(repo_root, ["rev-parse", "HEAD"])
    _, stash_raw = run_git_command(repo_root, ["stash", "list"])
    _, diff_stat = run_git_command(repo_root, ["diff", "--stat"])
    _, diff_shortstat = run_git_command(repo_root, ["diff", "--shortstat"])
    _, diff_cached_stat = run_git_command(repo_root, ["diff", "--cached", "--stat"])
    _, diff_cached_shortstat = run_git_command(repo_root, ["diff", "--cached", "--shortstat"])

    stash_entries = [line for line in stash_raw.splitlines() if str(line).strip()]

    return {
        "state_id": "imperium_repo_worktree_hygiene_v1",
        "truth_class": "SOURCE_EXACT",
        "branch": branch_name,
        "upstream": upstream,
        "ahead": ahead,
        "behind": behind,
        "head_commit": head_hash,
        "cleanliness_verdict": cleanliness_verdict,
        "worktree_clean": cleanliness_verdict == "CLEAN",
        "tracked_dirty_count": tracked_dirty_count,
        "untracked_count": untracked_count,
        "staged_paths": staged,
        "unstaged_paths": unstaged,
        "modified_paths": modified,
        "deleted_paths": deleted,
        "renamed_paths": renamed,
        "untracked_paths": untracked,
        "stash_count": len(stash_entries),
        "stash_entries": stash_entries,
        "diff_stat": diff_stat,
        "diff_shortstat": diff_shortstat,
        "diff_cached_stat": diff_cached_stat,
        "diff_cached_shortstat": diff_cached_shortstat,
        "generated_at": utc_now_iso(),
    }


def extract_surface_timestamp(payload: dict) -> str:
    if not isinstance(payload, dict):
        return ""
    for key_name in [
        "generated_at_utc",
        "generated_at",
        "captured_at_utc",
        "last_checked_at",
        "updated_at_utc",
    ]:
        value = str(payload.get(key_name, "")).strip()
        if value:
            return value
    return ""


def evaluate_surface_freshness(
    repo_root: Path,
    *,
    source_path: str,
    stale_after_minutes: int = 120,
) -> dict:
    resolved = resolve_path(repo_root, source_path)
    if not resolved.exists():
        return {
            "path": source_path,
            "exists": False,
            "generated_at": "",
            "age_minutes": None,
            "freshness_tier": "MISSING",
        }
    payload = load_json_file_if_exists(resolved)
    generated_at = extract_surface_timestamp(payload) or file_mtime_iso(resolved)
    age_minutes = human_age_minutes(generated_at)
    freshness_tier = "UNKNOWN"
    if age_minutes is None:
        freshness_tier = "UNKNOWN"
    elif age_minutes <= max(1, stale_after_minutes):
        freshness_tier = "FRESH"
    elif age_minutes <= max(1, stale_after_minutes * 3):
        freshness_tier = "AGING"
    else:
        freshness_tier = "STALE"
    return {
        "path": rel_or_abs(resolved, repo_root),
        "exists": True,
        "generated_at": generated_at,
        "age_minutes": age_minutes,
        "freshness_tier": freshness_tier,
    }


def build_truth_dominance_state(repo_root: Path, surface: dict) -> dict:
    if not isinstance(surface, dict) or not surface:
        return {
            "surface_id": "IMPERIUM_TRUTH_DOMINANCE_SURFACE_V1",
            "status": "NOT_YET_IMPLEMENTED",
            "truth_class": "DERIVED_CANONICAL",
            "dominance_rules": [],
            "stale_rules_count": 0,
            "missing_rules_count": 0,
            "winner_rules_count": 0,
        }

    rules = list(surface.get("dominance_rules", []) or [])
    authority_rank = {
        "PRIMARY": 4,
        "HIGH": 3,
        "SECONDARY": 2,
        "FALLBACK": 1,
        "UNKNOWN": 0,
    }
    freshness_rank = {
        "FRESH": 4,
        "AGING": 3,
        "UNKNOWN": 2,
        "STALE": 1,
        "MISSING": 0,
    }
    evaluated_rules: list[dict] = []
    stale_rules_count = 0
    missing_rules_count = 0
    winner_rules_count = 0
    for rule in rules:
        candidates = list((rule or {}).get("candidates", []) or [])
        stale_after_minutes = int((rule or {}).get("stale_after_minutes", 120) or 120)
        candidate_evaluations: list[dict] = []
        winner: dict = {}
        for candidate in candidates:
            source_path = str((candidate or {}).get("source_path", "")).strip()
            if not source_path:
                continue
            freshness = evaluate_surface_freshness(
                repo_root,
                source_path=source_path,
                stale_after_minutes=stale_after_minutes,
            )
            evaluated = {
                "surface_id": str((candidate or {}).get("surface_id", source_path)),
                "authority_tier": str((candidate or {}).get("authority_tier", "UNKNOWN")),
                "truth_class": str((candidate or {}).get("truth_class", "UNKNOWN")),
                "winner_priority": int((candidate or {}).get("winner_priority", 0) or 0),
                **freshness,
            }
            candidate_evaluations.append(evaluated)
        ranked_candidates: list[tuple[int, int, int, dict]] = []
        for item in candidate_evaluations:
            if not item.get("exists"):
                continue
            fr = freshness_rank.get(str(item.get("freshness_tier", "UNKNOWN")), 0)
            ar = authority_rank.get(str(item.get("authority_tier", "UNKNOWN")).upper(), 0)
            pr = int(item.get("winner_priority", 0) or 0)
            ranked_candidates.append((fr, ar, pr, item))
        if ranked_candidates:
            ranked_candidates.sort(key=lambda row: (row[0], row[1], row[2]), reverse=True)
            winner = ranked_candidates[0][3]

        rule_status = "MISSING"
        if winner:
            winner_rules_count += 1
            tier = str(winner.get("freshness_tier", "UNKNOWN"))
            if tier == "STALE":
                stale_rules_count += 1
                rule_status = "STALE"
            else:
                rule_status = "ACTIVE"
        else:
            missing_rules_count += 1

        evaluated_rules.append(
            {
                "rule_id": str((rule or {}).get("rule_id", "dominance_rule")),
                "description": str((rule or {}).get("description", "")),
                "rule_status": rule_status,
                "winner": winner,
                "candidates": candidate_evaluations,
            }
        )

    status = "OK"
    if missing_rules_count > 0:
        status = "PARTIAL"
    if stale_rules_count > 0:
        status = "STALE_WARNING"

    return {
        "surface_id": str(surface.get("surface_id", "IMPERIUM_TRUTH_DOMINANCE_SURFACE_V1")),
        "status": status,
        "truth_class": str(surface.get("truth_class", "DERIVED_CANONICAL")),
        "winner_strategy": str(
            ((surface.get("dominance_policy", {}) or {}).get("winner_strategy", "freshness_then_authority_then_priority"))
        ),
        "dominance_rules": evaluated_rules,
        "stale_rules_count": stale_rules_count,
        "missing_rules_count": missing_rules_count,
        "winner_rules_count": winner_rules_count,
        "source_path": DEFAULT_IMPERIUM_TRUTH_DOMINANCE_SURFACE_PATH,
        "generated_at": utc_now_iso(),
    }


def build_code_bank_state(repo_root: Path, surface: dict) -> dict:
    if not isinstance(surface, dict) or not surface:
        return {
            "surface_id": "IMPERIUM_CODE_BANK_STATE_SURFACE_V1",
            "status": "NOT_YET_IMPLEMENTED",
            "truth_class": "DERIVED_CANONICAL",
            "summary": {},
            "top_monoliths": [],
            "anomaly_ledger": {},
            "source_path": DEFAULT_IMPERIUM_CODE_BANK_SURFACE_PATH,
        }

    summary = dict(surface.get("summary", {}) or {})
    top_monoliths = list(surface.get("top_monoliths", []) or [])
    anomaly_ledger = dict(surface.get("anomaly_ledger", {}) or {})
    generated_at = extract_surface_timestamp(surface)
    age_minutes = human_age_minutes(generated_at) if generated_at else None
    severe_monoliths = len([item for item in top_monoliths if int((item or {}).get("loc", 0) or 0) >= 3000])
    monolith_count = len(top_monoliths)
    status = str(summary.get("status_classification", "WATCH"))
    if severe_monoliths > 0:
        status = "MONOLITH_RISK"
    elif monolith_count == 0:
        status = "HEALTHY"
    return {
        **surface,
        "surface_id": str(surface.get("surface_id", "IMPERIUM_CODE_BANK_STATE_SURFACE_V1")),
        "status": status,
        "summary": summary,
        "top_monoliths": top_monoliths,
        "anomaly_ledger": anomaly_ledger,
        "generated_at": generated_at,
        "age_minutes": age_minutes,
        "severe_monoliths_count": severe_monoliths,
        "monolith_count": monolith_count,
        "source_path": DEFAULT_IMPERIUM_CODE_BANK_SURFACE_PATH,
        "truth_class": str(surface.get("truth_class", "SOURCE_EXACT")),
    }


def build_dashboard_coverage_state(repo_root: Path, surface: dict) -> dict:
    if not isinstance(surface, dict) or not surface:
        return {
            "surface_id": "IMPERIUM_DASHBOARD_COVERAGE_SURFACE_V1",
            "coverage_verdict": "UNKNOWN",
            "full_coverage_claimable": False,
            "rows": [],
            "truth_class": "DERIVED_CANONICAL",
            "source_path": DEFAULT_IMPERIUM_DASHBOARD_COVERAGE_SURFACE_PATH,
        }

    rows_in = list(surface.get("rows", []) or [])
    rows_out: list[dict] = []
    represented_count = 0
    exact_count = 0
    pointer_only_count = 0
    missing_count = 0
    partial_rows = 0
    for row in rows_in:
        source_path = str((row or {}).get("source_path", "")).strip()
        source_exists = source_path_exists(repo_root, source_path) if source_path else False
        truth_class = str((row or {}).get("truth_class", "UNKNOWN")).upper()
        represented = bool((row or {}).get("represented_in_dashboard", False))
        representation_status = str((row or {}).get("representation_status", "UNKNOWN")).upper()
        if represented:
            represented_count += 1
        if truth_class == "SOURCE_EXACT":
            exact_count += 1
        if truth_class == "POINTER_ONLY":
            pointer_only_count += 1
        if truth_class in {"MISSING", "UNKNOWN"} or not source_exists:
            missing_count += 1
        if representation_status != "FULL":
            partial_rows += 1
        rows_out.append(
            {
                **row,
                "source_exists": source_exists,
                "truth_class": truth_class,
                "representation_status": representation_status,
            }
        )

    full_coverage_claimable = missing_count == 0 and pointer_only_count == 0 and partial_rows == 0
    coverage_verdict = "FULL_COVERAGE" if full_coverage_claimable else "PARTIAL_COVERAGE"
    generated_at = extract_surface_timestamp(surface)
    return {
        **surface,
        "surface_id": str(surface.get("surface_id", "IMPERIUM_DASHBOARD_COVERAGE_SURFACE_V1")),
        "coverage_verdict": coverage_verdict,
        "full_coverage_claimable": full_coverage_claimable,
        "rows": rows_out,
        "rows_total": len(rows_out),
        "represented_count": represented_count,
        "exact_count": exact_count,
        "pointer_only_count": pointer_only_count,
        "missing_count": missing_count,
        "partial_rows": partial_rows,
        "generated_at": generated_at,
        "age_minutes": human_age_minutes(generated_at) if generated_at else None,
        "source_path": DEFAULT_IMPERIUM_DASHBOARD_COVERAGE_SURFACE_PATH,
        "truth_class": str(surface.get("truth_class", "SOURCE_EXACT")),
    }


def build_custodes_state(
    *,
    surface: dict,
    system_brain_state: dict,
    coverage_state: dict,
    truth_dominance_state: dict,
) -> dict:
    if not isinstance(surface, dict) or not surface:
        return {
            "surface_id": "IMPERIUM_ADEPTUS_CUSTODES_STATE_SURFACE_V1",
            "status": "NOT_YET_IMPLEMENTED",
            "vigilance_state": "UNKNOWN",
            "foundation_lock_mode": "UNKNOWN",
            "truth_class": "DERIVED_CANONICAL",
            "source_path": DEFAULT_IMPERIUM_CUSTODES_SURFACE_PATH,
        }

    conflicts = list((system_brain_state.get("conflicts", []) or []))
    hygiene = dict((system_brain_state.get("repo_worktree_hygiene", {}) or {}))
    constitution = dict((system_brain_state.get("constitution", {}) or {}))
    throne_authority = dict((system_brain_state.get("throne_authority", {}) or {}))
    lock_policy = dict((surface.get("foundation_lock_policy", {}) or {}))
    threat_reasons: list[str] = []
    if str(hygiene.get("cleanliness_verdict", "UNKNOWN")) != "CLEAN":
        threat_reasons.append("repo_worktree_not_clean")
    if str(system_brain_state.get("conflict_state", "UNKNOWN")).upper() == "CONFLICT":
        threat_reasons.append("brain_conflict_active")
    if str(coverage_state.get("coverage_verdict", "PARTIAL_COVERAGE")).upper() != "FULL_COVERAGE":
        threat_reasons.append("coverage_not_full")
    if int(truth_dominance_state.get("stale_rules_count", 0) or 0) > 0:
        threat_reasons.append("stale_dominance_lane")
    if bool(throne_authority.get("emperor_status_blocked", False)):
        threat_reasons.append("throne_authority_anchor_blocked")
    if str(constitution.get("overall_verdict", "UNKNOWN")).upper() not in {"PASS", "TRUSTED", "GUARDED"}:
        threat_reasons.append("constitution_not_green")

    vigilance_state = "DORMANT"
    if threat_reasons:
        vigilance_state = "AWAKE"

    lock_mode = str(lock_policy.get("default_mode", "ATTESTATION"))
    if len(threat_reasons) >= 3:
        lock_mode = "LOCK_RECOMMENDED"
    if any(str((c or {}).get("severity", "")).lower() == "critical" for c in conflicts):
        lock_mode = "LOCK_ASSERTED"

    owner_ack_required = lock_mode in {"LOCK_RECOMMENDED", "LOCK_ASSERTED"} or bool(
        lock_policy.get("owner_ack_on_foundation_threat", True)
    )
    return {
        **surface,
        "surface_id": str(surface.get("surface_id", "IMPERIUM_ADEPTUS_CUSTODES_STATE_SURFACE_V1")),
        "status": "ACTIVE",
        "vigilance_state": vigilance_state,
        "threat_reasons": threat_reasons,
        "foundation_lock_mode": lock_mode,
        "owner_ack_required": owner_ack_required,
        "conflict_count": len(conflicts),
        "truth_class": str(surface.get("truth_class", "SOURCE_EXACT")),
        "source_path": DEFAULT_IMPERIUM_CUSTODES_SURFACE_PATH,
    }


def build_throne_authority_state(repo_root: Path) -> dict:
    anchor_path = resolve_path(repo_root, DEFAULT_GOLDEN_THRONE_AUTHORITY_ANCHOR_PATH)
    node_rank_path = resolve_path(repo_root, DEFAULT_NODE_RANK_DETECTION_STATUS_PATH)

    anchor_payload = load_json_file_if_exists(anchor_path)
    node_rank = load_json_file_if_exists(node_rank_path)
    emperor_proof = dict((node_rank.get("proof_status", {}) or {}).get("emperor", {}) or {})
    emperor_details = dict(emperor_proof.get("details", {}) or {})
    anchor_exists = anchor_path.exists()
    anchor_payload_loaded = bool(anchor_payload)
    proof_status = str(emperor_proof.get("status", "EMPEROR_STATUS_BLOCKED"))
    emperor_status = str(node_rank.get("emperor_status", proof_status or "EMPEROR_STATUS_BLOCKED"))
    emperor_status_blocked = bool(node_rank.get("emperor_status_blocked", emperor_status != "VALID"))
    throne_breach = bool(node_rank.get("throne_breach", emperor_status != "VALID"))
    raw_detected_rank = str(node_rank.get("detected_rank", "UNKNOWN"))

    canonical_anchor_in_payload = str(anchor_payload.get("canonical_anchor_path", "")).strip()
    canonical_path_match = bool(
        canonical_anchor_in_payload
        and canonical_anchor_in_payload.lower() == str(anchor_path.resolve()).lower()
    )
    anchor_rank_ok = str(anchor_payload.get("rank", "")).strip().upper() == "EMPEROR"
    anchor_mode_ok = str(anchor_payload.get("machine_mode", "")).strip().lower() == "emperor"
    anchor_authority_ok = bool(anchor_payload.get("full_system_authority", False))
    anchor_active_ok = bool(anchor_payload.get("active", False))

    sovereign_proof_blockers: list[str] = []
    if not anchor_exists:
        sovereign_proof_blockers.append("throne_anchor_missing")
    if anchor_exists and not anchor_payload_loaded:
        sovereign_proof_blockers.append("throne_anchor_unreadable_or_empty")
    if anchor_payload_loaded and not canonical_path_match:
        sovereign_proof_blockers.append("throne_anchor_path_mismatch")
    if anchor_payload_loaded and not anchor_rank_ok:
        sovereign_proof_blockers.append("throne_anchor_rank_field_invalid")
    if anchor_payload_loaded and not anchor_mode_ok:
        sovereign_proof_blockers.append("throne_anchor_machine_mode_invalid")
    if anchor_payload_loaded and not anchor_authority_ok:
        sovereign_proof_blockers.append("throne_anchor_full_system_authority_false")
    if anchor_payload_loaded and not anchor_active_ok:
        sovereign_proof_blockers.append("throne_anchor_inactive")
    if emperor_status != "VALID" or emperor_status_blocked:
        sovereign_proof_blockers.append("emperor_status_blocked")
    if throne_breach:
        sovereign_proof_blockers.append("throne_breach")

    anchor_state = "VALID"
    if not anchor_exists:
        anchor_state = "MISSING"
    elif anchor_payload_loaded and not canonical_path_match:
        anchor_state = "PATH_MISMATCH"
    elif sovereign_proof_blockers:
        anchor_state = "INVALID"

    anchor_valid = anchor_state == "VALID" and not sovereign_proof_blockers
    if anchor_valid:
        display_rank = "EMPEROR"
        display_mode = "emperor"
        emperor_status_effective = "VALID"
        emperor_status_blocked_effective = False
        throne_breach_effective = False
        full_system_authority = True
    else:
        display_rank = "UNKNOWN"
        display_mode = "blocked"
        emperor_status_effective = "EMPEROR_STATUS_BLOCKED"
        emperor_status_blocked_effective = True
        throne_breach_effective = True
        full_system_authority = False
    status = "VALID" if anchor_valid else "EMPEROR_STATUS_BLOCKED"
    return {
        "surface_id": "IMPERIUM_GOLDEN_THRONE_AUTHORITY_ANCHOR_STATE_V1",
        "status": status,
        "anchor_state": anchor_state,
        "authority_source": "GOLDEN_THRONE_AUTHORITY_ANCHOR_V1",
        "authority_anchor_path": DEFAULT_GOLDEN_THRONE_AUTHORITY_ANCHOR_PATH,
        "anchor_exists": anchor_exists,
        "anchor_payload_loaded": anchor_payload_loaded,
        "anchor_valid": anchor_valid,
        "canonical_path_match": canonical_path_match,
        "detected_rank": display_rank,
        "detected_rank_raw": raw_detected_rank,
        "emperor_status": emperor_status_effective,
        "emperor_status_raw": emperor_status,
        "emperor_status_blocked": emperor_status_blocked_effective,
        "throne_breach": throne_breach_effective,
        "throne_breach_raw": throne_breach,
        "machine_mode": display_mode,
        "machine_mode_raw": str(anchor_payload.get("machine_mode", emperor_details.get("expected_machine_mode", "unknown"))),
        "full_system_authority": full_system_authority,
        "foundation_lock_posture": "LOCK_ASSERTED" if emperor_status_blocked_effective else "ATTESTATION",
        "sovereign_display_rank": display_rank,
        "sovereign_display_machine_mode": display_mode,
        "sovereign_proof_blockers": sovereign_proof_blockers,
        "sovereign_display_alignment": "ALIGNED" if anchor_valid else "BLOCKED",
        "non_authority_inputs": {
            "constitution_rank_non_authority": True,
            "discoverability_non_authority": True,
        },
        "source_path": DEFAULT_GOLDEN_THRONE_AUTHORITY_ANCHOR_PATH,
        "source_class": "SOURCE_EXACT" if anchor_state == "VALID" else anchor_state,
        "rank_detection_source_path": DEFAULT_NODE_RANK_DETECTION_STATUS_PATH,
        "truth_class": "SOURCE_EXACT",
    }


def build_mechanicus_state(
    *,
    surface: dict,
    machine_manifest: dict,
    organ_strength_surface: dict,
    code_bank_state: dict,
    repo_worktree_hygiene: dict,
) -> dict:
    if not isinstance(surface, dict) or not surface:
        return {
            "surface_id": "IMPERIUM_ADEPTUS_MECHANICUS_STATE_SURFACE_V1",
            "status": "NOT_YET_IMPLEMENTED",
            "truth_class": "DERIVED_CANONICAL",
            "source_path": DEFAULT_IMPERIUM_MECHANICUS_SURFACE_PATH,
        }

    machine_compute = dict((machine_manifest.get("compute_power", {}) or {}))
    execution_power = dict((machine_manifest.get("execution_power", {}) or {}))
    force_assessment = dict((machine_manifest.get("force_assessment", {}) or {}))
    organ_rows = list((organ_strength_surface.get("organ_strength", []) or []))
    mechanicus_row = next(
        (
            item
            for item in organ_rows
            if str((item or {}).get("organ_id", "")).strip().lower() == "mechanicus"
        ),
        {},
    )

    code_status = str((code_bank_state.get("summary", {}) or {}).get("status_classification", "UNKNOWN"))
    monolith_count = int(code_bank_state.get("monolith_count", 0) or 0)
    cleanliness_verdict = str(repo_worktree_hygiene.get("cleanliness_verdict", "UNKNOWN"))
    stop_reasons: list[str] = []
    if code_status.upper() == "MONOLITH_RISK":
        stop_reasons.append("code_monolith_pressure")
    if cleanliness_verdict != "CLEAN":
        stop_reasons.append("repo_hygiene_not_clean")
    if str(force_assessment.get("readiness_band", "UNKNOWN")).upper() == "BLOCKED":
        stop_reasons.append("force_readiness_blocked")

    readiness_score = int(mechanicus_row.get("readiness", 70) or 70)
    if stop_reasons:
        readiness_score = max(35, readiness_score - 15)

    return {
        **surface,
        "surface_id": str(surface.get("surface_id", "IMPERIUM_ADEPTUS_MECHANICUS_STATE_SURFACE_V1")),
        "status": "ACTIVE",
        "truth_class": str(surface.get("truth_class", "SOURCE_EXACT")),
        "source_path": DEFAULT_IMPERIUM_MECHANICUS_SURFACE_PATH,
        "machine_compute": {
            "cpu_logical_cores": int(machine_compute.get("cpu_logical_cores", 0) or 0),
            "memory_total_gb": machine_compute.get("memory_total_gb"),
            "disk_free_gb": machine_compute.get("disk_free_gb"),
        },
        "execution_power": execution_power,
        "code_bank_status": code_status,
        "code_bank_monolith_count": monolith_count,
        "repo_hygiene_verdict": cleanliness_verdict,
        "readiness_score": readiness_score,
        "bottleneck": str(mechanicus_row.get("bottleneck", "none")),
        "stop_reasons": stop_reasons,
        "large_step_readiness": "BLOCKED" if stop_reasons else "READY",
    }


def build_administratum_state(
    *,
    surface: dict,
    active_contract: dict,
) -> dict:
    if not isinstance(surface, dict) or not surface:
        return {
            "surface_id": "IMPERIUM_ADMINISTRATUM_STATE_SURFACE_V1",
            "status": "NOT_YET_IMPLEMENTED",
            "truth_class": "DERIVED_CANONICAL",
            "source_path": DEFAULT_IMPERIUM_ADMINISTRATUM_SURFACE_PATH,
        }

    gate = dict((surface.get("contract_gate", {}) or {}))
    required_fields = list(gate.get("required_fields", []) or [])
    unknowns_red = int(((gate.get("severity_thresholds", {}) or {}).get("unknowns_red_threshold", 3)) or 3)
    assumptions_red = int(((gate.get("severity_thresholds", {}) or {}).get("assumptions_red_threshold", 3)) or 3)

    contract_present = bool(active_contract)
    missing_required = [field for field in required_fields if field not in active_contract]
    unknowns = list(active_contract.get("unknowns", []) or [])
    assumptions = list(active_contract.get("assumptions", []) or [])
    stop_triggers = list(active_contract.get("stop_triggers", []) or [])
    owner_ack_required = bool(active_contract.get("owner_ack_required", False))

    gate_state = "GREEN"
    if not contract_present or missing_required:
        gate_state = "RED_BLOCK"
    elif len(unknowns) >= unknowns_red or len(assumptions) >= assumptions_red:
        gate_state = "AMBER"

    return {
        **surface,
        "surface_id": str(surface.get("surface_id", "IMPERIUM_ADMINISTRATUM_STATE_SURFACE_V1")),
        "status": "ACTIVE",
        "truth_class": str(surface.get("truth_class", "SOURCE_EXACT")),
        "source_path": DEFAULT_IMPERIUM_ADMINISTRATUM_SURFACE_PATH,
        "active_contract_path": DEFAULT_IMPERIUM_ACTIVE_MISSION_CONTRACT_PATH,
        "contract_present": contract_present,
        "active_contract_id": str(active_contract.get("contract_id", "UNKNOWN")),
        "missing_required_fields": missing_required,
        "unknowns_count": len(unknowns),
        "assumptions_count": len(assumptions),
        "stop_triggers_count": len(stop_triggers),
        "gate_state": gate_state,
        "owner_ack_required": owner_ack_required,
        "escalation_rule": str(active_contract.get("escalation_rule", "")),
    }


def build_force_state(
    *,
    surface: dict,
    machine_manifest: dict,
    organ_strength_surface: dict,
    administratum_state: dict,
    mechanicus_state: dict,
) -> dict:
    if not isinstance(surface, dict) or not surface:
        return {
            "surface_id": "IMPERIUM_FORCE_DOCTRINE_SURFACE_V1",
            "status": "NOT_YET_IMPLEMENTED",
            "truth_class": "DERIVED_CANONICAL",
            "source_path": DEFAULT_IMPERIUM_FORCE_DOCTRINE_SURFACE_PATH,
        }
    organ_strength_rows = list((organ_strength_surface.get("organ_strength", []) or []))
    mission_cost = dict((organ_strength_surface.get("mission_cost_context", {}) or {}))
    readiness_band = str((machine_manifest.get("force_assessment", {}) or {}).get("readiness_band", "UNKNOWN"))
    bottlenecks = list((machine_manifest.get("force_assessment", {}) or {}).get("bottlenecks", []) or [])
    return {
        **surface,
        "surface_id": str(surface.get("surface_id", "IMPERIUM_FORCE_DOCTRINE_SURFACE_V1")),
        "status": "ACTIVE",
        "truth_class": str(surface.get("truth_class", "SOURCE_EXACT")),
        "source_path": DEFAULT_IMPERIUM_FORCE_DOCTRINE_SURFACE_PATH,
        "machine_capability_manifest_path": DEFAULT_IMPERIUM_MACHINE_CAPABILITY_MANIFEST_PATH,
        "organ_strength_surface_path": DEFAULT_IMPERIUM_ORGAN_STRENGTH_SURFACE_PATH,
        "readiness_band": readiness_band,
        "bottlenecks": bottlenecks,
        "organ_strength_count": len(organ_strength_rows),
        "mission_cost_context": mission_cost,
        "contract_gate_state": str(administratum_state.get("gate_state", "UNKNOWN")),
        "mechanicus_large_step_readiness": str(mechanicus_state.get("large_step_readiness", "UNKNOWN")),
    }


def build_palace_archive_state(
    *,
    surface: dict,
    storage_health: dict,
    throne_authority_state: dict,
) -> dict:
    if not isinstance(surface, dict) or not surface:
        return {
            "surface_id": "IMPERIUM_PALACE_AND_ARCHIVE_STATE_SURFACE_V1",
            "status": "NOT_YET_IMPLEMENTED",
            "truth_class": "DERIVED_CANONICAL",
            "source_path": DEFAULT_IMPERIUM_PALACE_ARCHIVE_SURFACE_PATH,
        }
    palace = dict((surface.get("palace_state", {}) or {}))
    archive = dict((surface.get("archive_resurrection_state", {}) or {}))
    node = dict((surface.get("node_prep_state", {}) or {}))
    storage_posture = str(
        storage_health.get("storage_posture")
        or storage_health.get("overall_posture")
        or "UNKNOWN"
    )
    throne_status = str(
        throne_authority_state.get("emperor_status")
        or throne_authority_state.get("status")
        or "UNKNOWN"
    )
    return {
        **surface,
        "surface_id": str(surface.get("surface_id", "IMPERIUM_PALACE_AND_ARCHIVE_STATE_SURFACE_V1")),
        "status": "ACTIVE",
        "truth_class": str(surface.get("truth_class", "SOURCE_EXACT")),
        "source_path": DEFAULT_IMPERIUM_PALACE_ARCHIVE_SURFACE_PATH,
        "palace_state": palace,
        "archive_resurrection_state": archive,
        "node_prep_state": node,
        "storage_posture": storage_posture,
        "throne_authority_status": throne_status,
    }


def build_control_gates_state(
    *,
    surface: dict,
    throne_authority_state: dict,
    truth_dominance_state: dict,
    dashboard_coverage_state: dict,
    evolution_state: dict,
    runtime_state: dict,
    administratum_state: dict,
) -> dict:
    if not isinstance(surface, dict) or not surface:
        return {
            "surface_id": "IMPERIUM_CONTROL_GATES_SURFACE_V1",
            "status": "NOT_YET_IMPLEMENTED",
            "truth_class": "DERIVED_CANONICAL",
            "source_path": DEFAULT_IMPERIUM_CONTROL_GATES_SURFACE_PATH,
            "gates": [],
        }
    gates = list((surface.get("gates", []) or []))
    stale_count = int(truth_dominance_state.get("stale_rules_count", 0) or 0)
    coverage_verdict = str(dashboard_coverage_state.get("coverage_verdict", "UNKNOWN"))
    emperor_blocked = bool(throne_authority_state.get("emperor_status_blocked", False))
    evolution_health = str(evolution_state.get("health", "UNKNOWN"))
    runtime_process = str(runtime_state.get("process_state", "UNKNOWN"))
    contract_gate_state = str(administratum_state.get("gate_state", "UNKNOWN"))

    gate_state_map = {
        "throne_proof_control": "BLOCKED" if emperor_blocked else "PASS",
        "truth_dominance_chamber": "WARNING" if stale_count > 0 else "PASS",
        "chronology_continuity_guard": "PASS",
        "review_integrity_gate": "PASS",
        "coverage_authority_control": "PASS" if coverage_verdict == "FULL_COVERAGE" else "WARNING",
        "evolution_gate": "PASS" if evolution_health in {"STABLE", "HEALTHY"} else "WARNING",
        "runtime_claim_gate": "PASS" if runtime_process in {"PROCESSING", "WAIT"} else "WARNING",
        "truth_spine_gate": "PASS" if str(runtime_state.get("truth_spine_status", "UNKNOWN")).upper() == "PASS" else "BLOCKED",
        "dashboard_truth_engine_gate": "PASS"
        if str(runtime_state.get("dashboard_truth_engine_status", "UNKNOWN")).upper() == "PASS"
        else "BLOCKED",
        "bundle_truth_chamber_gate": "PASS"
        if str(runtime_state.get("bundle_truth_chamber_status", "UNKNOWN")).upper() == "PASS"
        else "BLOCKED",
        "worktree_purity_gate": "PASS"
        if str(runtime_state.get("worktree_purity_gate_status", "UNKNOWN")).upper() == "PASS"
        else "BLOCKED",
        "address_lattice_gate": "PASS"
        if str(runtime_state.get("address_lattice_status", "UNKNOWN")).upper() == "PASS"
        else "BLOCKED",
        "anti_lie_foundation_gate": "PASS"
        if str(runtime_state.get("anti_lie_model_status", "UNKNOWN")).upper() == "PASS"
        else "BLOCKED",
        "live_truth_support_loop_gate": "PASS"
        if str(runtime_state.get("live_truth_support_loop_status", "UNKNOWN")).upper() == "PASS"
        else "BLOCKED",
        "inquisition_truth_guard_gate": "PASS"
        if str(runtime_state.get("inquisition_truth_guard_status", "UNKNOWN")).upper() == "PASS"
        else "BLOCKED",
    }
    if contract_gate_state == "RED_BLOCK":
        gate_state_map["runtime_claim_gate"] = "BLOCKED"

    rendered_gates: list[dict] = []
    for item in gates:
        row = dict(item or {})
        gate_id = str(row.get("gate_id", "")).strip()
        if gate_id:
            row["state"] = gate_state_map.get(gate_id, str(row.get("state", "UNKNOWN")))
        rendered_gates.append(row)

    blocked_count = len([x for x in rendered_gates if str((x or {}).get("state", "")).upper() == "BLOCKED"])
    warning_count = len([x for x in rendered_gates if str((x or {}).get("state", "")).upper() == "WARNING"])
    return {
        **surface,
        "surface_id": str(surface.get("surface_id", "IMPERIUM_CONTROL_GATES_SURFACE_V1")),
        "status": "ACTIVE",
        "truth_class": str(surface.get("truth_class", "SOURCE_EXACT")),
        "source_path": DEFAULT_IMPERIUM_CONTROL_GATES_SURFACE_PATH,
        "gates": rendered_gates,
        "blocked_count": blocked_count,
        "warning_count": warning_count,
        "gate_summary": "BLOCKED" if blocked_count > 0 else ("WARNING" if warning_count > 0 else "PASS"),
    }


def build_brain_v2_layers(
    *,
    system_brain_state: dict,
    throne_authority_state: dict,
    custodes_state: dict,
    inquisition_state: dict,
    mechanicus_state: dict,
    administratum_state: dict,
    force_state: dict,
    palace_state: dict,
    control_gates_state: dict,
) -> dict:
    one_screen = dict((system_brain_state.get("one_screen", {}) or {}))
    repo_control = dict((system_brain_state.get("repo_control", {}) or {}))
    coverage = dict((system_brain_state.get("dashboard_coverage", {}) or {}))
    dominance = dict((system_brain_state.get("truth_dominance", {}) or {}))
    code_bank = dict((system_brain_state.get("code_bank", {}) or {}))
    repo_hygiene = dict((system_brain_state.get("repo_worktree_hygiene", {}) or {}))
    constitution = dict((system_brain_state.get("constitution", {}) or {}))
    conflicts = list((system_brain_state.get("conflicts", []) or []))
    control_age = dict((system_brain_state.get("age_axis", {}) or {}))
    blocker_classes = dict((system_brain_state.get("blocker_classes", {}) or {}))
    governance_blockers = list((blocker_classes.get("governance_blockers", []) or []))
    trust_blockers = list((blocker_classes.get("trust_blockers", []) or []))
    sync_blockers = list((blocker_classes.get("sync_blockers", []) or []))
    repo_hygiene_blockers = list((blocker_classes.get("repo_hygiene_blockers", []) or []))
    runtime_transport_blockers = list((blocker_classes.get("runtime_transport_blockers", []) or []))
    sovereign_proof_blockers = list((blocker_classes.get("sovereign_proof_blockers", []) or []))

    return {
        "model_id": "IMPERIUM_SUPREME_BRAIN_V2_LAYERS",
        "truth_class": "DERIVED_CANONICAL",
        "generated_at_utc": utc_now_iso(),
        "layer_1_sovereignty": {
            "emperor_proof": str(throne_authority_state.get("emperor_status", "UNKNOWN")),
            "throne_anchor_state": str(throne_authority_state.get("status", "UNKNOWN")),
            "sovereign_display_rank": str(throne_authority_state.get("sovereign_display_rank", "UNKNOWN")),
            "sovereign_display_machine_mode": str(throne_authority_state.get("sovereign_display_machine_mode", "UNKNOWN")),
            "sovereign_display_alignment": str(throne_authority_state.get("sovereign_display_alignment", "UNKNOWN")),
            "custodes_posture": str(custodes_state.get("vigilance_state", "UNKNOWN")),
            "foundation_lock_posture": str(throne_authority_state.get("foundation_lock_posture", "UNKNOWN")),
            "throne_breach": bool(throne_authority_state.get("throne_breach", False)),
            "sovereign_proof_blockers": sovereign_proof_blockers,
        },
        "layer_2_truth_governance": {
            "truth_dominance_status": str(dominance.get("status", "UNKNOWN")),
            "stale_rules_count": int(dominance.get("stale_rules_count", 0) or 0),
            "coverage_verdict": str(coverage.get("coverage_verdict", "UNKNOWN")),
            "coverage_pointer_only_count": int(coverage.get("pointer_only_count", 0) or 0),
            "conflict_count": len(conflicts),
            "owner_ack_required": bool(custodes_state.get("owner_ack_required", False)),
            "governance_blocker_count": len(governance_blockers),
            "trust_blocker_count": len(trust_blockers),
            "sync_blocker_count": len(sync_blockers),
            "repo_hygiene_blocker_count": len(repo_hygiene_blockers),
            "runtime_transport_blocker_count": len(runtime_transport_blockers),
            "governance_blockers": governance_blockers,
            "trust_blockers": trust_blockers,
            "sync_blockers": sync_blockers,
            "repo_hygiene_blockers": repo_hygiene_blockers,
            "runtime_transport_blockers": runtime_transport_blockers,
        },
        "layer_3_system_health": {
            "repo_hygiene": str(repo_hygiene.get("cleanliness_verdict", "UNKNOWN")),
            "repo_health": str(repo_control.get("repo_health", "UNKNOWN")),
            "workspace_health": str(repo_control.get("workspace_health", "UNKNOWN")),
            "code_bank_status": str((code_bank.get("summary", {}) or {}).get("status_classification", "UNKNOWN")),
            "code_monolith_count": int(code_bank.get("monolith_count", 0) or 0),
            "control_plane_age_minutes": control_age.get("control_plane_last_refresh_age_minutes"),
            "repo_control_generated_at": str(repo_control.get("generated_at", "")),
            "one_screen_generated_at": str(one_screen.get("generated_at", "")),
        },
        "layer_4_force_capacity": {
            "force_readiness_band": str(force_state.get("readiness_band", "UNKNOWN")),
            "mechanicus_large_step_readiness": str(mechanicus_state.get("large_step_readiness", "UNKNOWN")),
            "administratum_gate_state": str(administratum_state.get("gate_state", "UNKNOWN")),
            "bottlenecks": list(force_state.get("bottlenecks", []) or []),
            "mission_cost_context": dict(force_state.get("mission_cost_context", {}) or {}),
        },
        "layer_5_organs": {
            "custodes": {
                "state": str(custodes_state.get("vigilance_state", "UNKNOWN")),
                "lock_mode": str(custodes_state.get("foundation_lock_mode", "UNKNOWN")),
            },
            "inquisition": {
                "state": str(inquisition_state.get("status", "UNKNOWN")),
                "alerts": int(inquisition_state.get("active_heresy_alerts_count", 0) or 0),
            },
            "mechanicus": {
                "state": str(mechanicus_state.get("status", "UNKNOWN")),
                "readiness_score": int(mechanicus_state.get("readiness_score", 0) or 0),
            },
            "administratum": {
                "state": str(administratum_state.get("status", "UNKNOWN")),
                "gate_state": str(administratum_state.get("gate_state", "UNKNOWN")),
            },
        },
        "layer_6_nested_worlds": {
            "factory": "SEPARATE_PRODUCTION_ORGANISM",
            "tiktok": "PRODUCT_IN_FACTORY",
            "storage_palace_archive": str(palace_state.get("status", "UNKNOWN")),
            "review_pipeline": str(control_gates_state.get("gate_summary", "UNKNOWN")),
            "evolution": "PARALLEL_CHANNEL",
            "inquisition": "PARALLEL_CHANNEL",
        },
    }


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8-sig")
    except Exception:
        return ""


def file_mtime_iso(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def parse_bool(value: object, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return default


def extract_canon_truth(canon_sync_payload: dict) -> dict:
    if not isinstance(canon_sync_payload, dict):
        return {}
    nested = canon_sync_payload.get("current_truth")
    if isinstance(nested, dict):
        return nested
    return canon_sync_payload


def classify_field_state(value: object) -> str:
    if value is None:
        return "UNKNOWN"
    text = str(value).strip()
    if not text:
        return "UNKNOWN"
    upper = text.upper()
    if upper in {"UNKNOWN", "N/A"}:
        return "UNKNOWN"
    if "NOT_YET_IMPLEMENTED" in upper:
        return "NOT_YET_IMPLEMENTED"
    if "PLACEHOLDER" in upper:
        return "PLACEHOLDER"
    return "DERIVED"


def source_path_exists(repo_root: Path, source_path: str) -> bool:
    path_value = str(source_path or "").strip()
    if not path_value:
        return False
    try:
        return resolve_path(repo_root, path_value).exists()
    except Exception:
        return False


def classify_uncertainty_reason(
    value: object,
    *,
    source_exists: bool,
    mapped: bool,
    owner_decision_pending: bool = False,
    unavailable_in_step_scope: bool = False,
) -> str:
    state = classify_field_state(value)
    upper = str(value or "").strip().upper()
    if state == "NOT_YET_IMPLEMENTED":
        return "not_implemented"
    if state == "PLACEHOLDER":
        return "unavailable_in_step_scope"
    if state != "UNKNOWN":
        return ""
    if not source_exists:
        return "stale_source"
    if owner_decision_pending or "PENDING" in upper:
        return "owner_decision_pending"
    if unavailable_in_step_scope:
        return "unavailable_in_step_scope"
    if not mapped:
        return "not_mapped"
    return "not_mapped"


def classify_field_state_with_reason(
    value: object,
    *,
    source_exists: bool,
    mapped: bool,
    owner_decision_pending: bool = False,
    unavailable_in_step_scope: bool = False,
) -> dict:
    state = classify_field_state(value)
    reason = classify_uncertainty_reason(
        value,
        source_exists=source_exists,
        mapped=mapped,
        owner_decision_pending=owner_decision_pending,
        unavailable_in_step_scope=unavailable_in_step_scope,
    )
    semantic_state = {
        "state": state,
        "unknown_reason": reason,
    }
    return semantic_state


def verdict_to_live_state(value: str) -> str:
    normalized = (value or "").upper()
    if normalized in {"PASS", "IN_SYNC", "TRUSTED", "ADMISSIBLE", "COMPLIANT"}:
        return "stable"
    if normalized in {"WARNING", "PARTIAL", "PREPARE"}:
        return "warning"
    if normalized in {"FAIL", "REJECTED", "DRIFTED"}:
        return "critical"
    return "warning"


def count_wave_markers(path: Path) -> int:
    text = read_text_if_exists(path)
    if not text:
        return 0
    matches = re.findall(r"\bWave\s+(\d+)\b", text, flags=re.IGNORECASE)
    return len(set(matches))


def count_owner_gate_markers(path: Path) -> int:
    text = read_text_if_exists(path)
    if not text:
        return 0
    matches = re.findall(r"\bGate\s+[A-F]\b", text, flags=re.IGNORECASE)
    return len(set(match.upper() for match in matches))


def parse_utc(value: str) -> datetime:
    raw = str(value or "").strip()
    if not raw:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return datetime.fromtimestamp(0, tz=timezone.utc)


def human_age_minutes(value: str, *, now: datetime | None = None) -> int | None:
    dt = parse_utc(value)
    if dt == datetime.fromtimestamp(0, tz=timezone.utc):
        return None
    now_dt = now or datetime.now(timezone.utc)
    delta = now_dt - dt
    return max(0, int(delta.total_seconds() // 60))


def short_text(value: str, *, limit: int = 220) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return f"{text[: max(20, limit - 3)]}..."


def summarize_truth_layers(payload: object) -> dict:
    counts = {
        "exact": 0,
        "derived": 0,
        "gap": 0,
        "stale": 0,
    }

    def walk(node: object) -> None:
        if isinstance(node, dict):
            truth_class = str(node.get("truth_class", "")).upper()
            if truth_class == "SOURCE_EXACT":
                counts["exact"] += 1
            elif truth_class.startswith("DERIVED"):
                counts["derived"] += 1
            elif truth_class in {"NOT_YET_IMPLEMENTED", "PLACEHOLDER", "UNKNOWN", "STALE_SOURCE"}:
                counts["gap"] += 1
                if truth_class == "STALE_SOURCE":
                    counts["stale"] += 1
            unknown_reason = str(node.get("unknown_reason", "")).strip()
            if unknown_reason == "stale_source":
                counts["stale"] += 1
            for value in node.values():
                walk(value)
            return
        if isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    return counts


def unknown_reason_breakdown(items: list[dict]) -> dict:
    result = {
        "not_implemented": 0,
        "not_mapped": 0,
        "stale_source": 0,
        "owner_decision_pending": 0,
        "unavailable_in_step_scope": 0,
    }
    for item in items:
        reason = str((item or {}).get("unknown_reason", "")).strip()
        if reason in result:
            result[reason] += 1
    return result


def lineage_digest(parts: list[str]) -> str:
    payload = "|".join(parts).encode("utf-8", errors="ignore")
    return hashlib.sha256(payload).hexdigest()[:16]


def find_latest_verify_dir(project_core_root: Path) -> Path | None:
    verification_root = project_core_root / "runtime" / "verification"
    if not verification_root.exists():
        return None
    candidates = [p for p in verification_root.glob("verify-*") if p.is_dir()]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.name, reverse=True)
    return candidates[0]


def build_prompt_lineage_state(repo_root: Path) -> dict:
    project_core_root = resolve_path(repo_root, DEFAULT_TIKTOK_PROJECT_CORE_ROOT)
    manifest_path = project_core_root / "PROJECT_MANIFEST.json"
    prompt_path = project_core_root / "PROMPT_FOR_CODEX.txt"
    manifest = load_json_file_if_exists(manifest_path)
    prompt_text = read_text_if_exists(prompt_path)
    prompt_present = bool(str(prompt_text).strip())
    prompt_line_count = len(str(prompt_text).splitlines()) if prompt_present else 0

    lineage_parts = [
        str(manifest.get("schema_version", "")),
        str(manifest.get("slug", "")),
        str(manifest.get("name", "")),
        str(prompt_path.name if prompt_path.exists() else "MISSING_PROMPT_FOR_CODEX"),
        str(len(prompt_text)),
    ]
    lineage_id = f"prompt-lineage-{lineage_digest(lineage_parts)}"
    missing_fields: list[str] = []
    if not manifest:
        missing_fields.append("PROJECT_MANIFEST.json")
    if not prompt_present:
        missing_fields.append("PROMPT_FOR_CODEX.txt")

    if missing_fields:
        trust_boundary = "MISSING_TEXT_BOUNDARY"
        active_prompt_state = "PROMPT_LINEAGE_INCOMPLETE"
    else:
        trust_boundary = "PARTIAL_TEXT_ONLY"
        active_prompt_state = "PROMPT_LINEAGE_TRACKED_BRIEF_ONLY"

    latest_verify_dir = find_latest_verify_dir(project_core_root)
    verification_summary = {}
    readiness_summary = {}
    verify_run_id = "UNKNOWN"
    if latest_verify_dir:
        verification_summary = load_json_file_if_exists(latest_verify_dir / "verification_summary.json")
        readiness_summary = load_json_file_if_exists(latest_verify_dir / "readiness_summary.json")
        verify_run_id = str(verification_summary.get("run_id") or readiness_summary.get("run_id") or latest_verify_dir.name)

    backend_statuses = (readiness_summary.get("ui_backend_statuses", {}) or {})
    prompt_lineage_http = backend_statuses.get("workspace_prompt_lineage")
    module_status = verification_summary.get("module_status", {}) or {}
    prompt_lineage_observability = module_status.get("prompt_lineage_observability", "unknown")
    prompt_lineage_service_state = "VERIFIED" if str(prompt_lineage_observability).lower() == "verified" else "PARTIAL"

    return {
        "state_id": "tiktok_prompt_lineage_observability_v1",
        "truth_class": "SOURCE_EXACT",
        "project_core_root": rel_or_abs(project_core_root, repo_root),
        "active_prompt_state": active_prompt_state,
        "lineage_id": lineage_id,
        "trusted_boundary": trust_boundary,
        "source_paths": {
            "manifest_path": rel_or_abs(manifest_path, repo_root),
            "prompt_path": rel_or_abs(prompt_path, repo_root),
            "latest_verify_dir": rel_or_abs(latest_verify_dir, repo_root) if latest_verify_dir else "missing",
        },
        "lineage": {
            "project_name": str(manifest.get("name", "unknown_project")),
            "project_slug": str(manifest.get("slug", "unknown_slug")),
            "manifest_schema_version": str(manifest.get("schema_version", "unknown")),
            "prompt_file_present": prompt_present,
            "prompt_line_count": prompt_line_count,
        },
        "source_brief": {
            "manifest_notes_excerpt": short_text(
                " ".join(manifest.get("notes", []))
                if isinstance(manifest.get("notes"), list)
                else "n/a"
            ),
            "prompt_excerpt": short_text(prompt_text, limit=260) if prompt_present else "missing",
        },
        "text_boundary": {
            "full_prompt_text_exposed": False,
            "full_prompt_text_available_locally": prompt_present,
            "boundary_note": (
                "Полный prompt text не публикуется в owner API; отображается только lineage и brief."
                if prompt_present
                else "Prompt text отсутствует в локальном core root."
            ),
        },
        "runtime_observability": {
            "verify_run_id": verify_run_id,
            "workspace_prompt_lineage_http": prompt_lineage_http,
            "service_status_classification": prompt_lineage_service_state,
            "truth_class": "DERIVED_CANONICAL",
            "implementation_label": "PARTIALLY_IMPLEMENTED",
        },
        "integrity": {
            "missing_fields": missing_fields,
            "trusted_fields": [
                "project_name",
                "project_slug",
                "manifest_schema_version",
                "lineage_id",
                "prompt_excerpt",
                "workspace_prompt_lineage_http",
            ],
        },
    }


def classify_runtime_process_state(*, event_name: str, level: str) -> tuple[str, str]:
    key = str(event_name or "").strip().lower()
    lvl = str(level or "").strip().upper()
    error_tokens = ("error", "failed", "exception", "not_ready", "timeout", "degraded")
    active_tokens = ("started", "ready", "refresh", "switch_page", "validation", "verify", "open")
    wait_tokens = ("wait", "idle", "stopped", "shutdown")

    if lvl in {"ERROR", "CRITICAL"} or any(token in key for token in error_tokens):
        return "ERROR", "runtime_error_signal_detected"
    if any(token in key for token in active_tokens):
        return "PROCESSING", "runtime_activity_signal_detected"
    if any(token in key for token in wait_tokens):
        return "WAIT", "runtime_wait_signal_detected"
    return "WAIT", "runtime_signal_not_classified"


def read_jsonl_tail(path: Path, *, limit: int = 24) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows[-limit:]


def normalize_runtime_log_event(record: dict, *, idx: int, log_path: Path, repo_root: Path) -> dict:
    payload = record.get("payload", {}) if isinstance(record.get("payload"), dict) else {}
    event_name = str(record.get("event", "runtime_event")).strip() or "runtime_event"
    level = str(record.get("level", "INFO")).strip().lower() or "info"
    summary = str(payload.get("summary", "")).strip() or event_name.replace("_", " ")
    occurred_at = str(record.get("timestamp", "")).strip() or utc_now_iso()
    source_path = rel_or_abs(log_path, repo_root)
    return {
        "event_id": f"runtime_{event_name}_{idx:03d}",
        "event_type": "runtime_activity",
        "event_name": event_name,
        "occurred_at_utc": occurred_at,
        "severity": level,
        "summary": short_text(summary, limit=220),
        "source_path": source_path,
        "truth_class": "SOURCE_EXACT",
        "producer": "tiktok_runtime_logs",
        "failure_reason": str(payload.get("failure_reason", "")).strip(),
        "recovery_signal": str(payload.get("recovery_signal", "")).strip(),
    }


def build_tiktok_runtime_observability_state(repo_root: Path) -> dict:
    snapshot_path = resolve_path(repo_root, DEFAULT_TIKTOK_RUNTIME_OBSERVABILITY_SNAPSHOT_PATH)
    snapshot_payload = load_json_file_if_exists(snapshot_path)
    if snapshot_payload and snapshot_payload.get("state_id"):
        payload = dict(snapshot_payload)
        payload.setdefault("source_mode", "SNAPSHOT_FILE")
        payload.setdefault("truth_class", "SOURCE_EXACT")
        payload.setdefault("source_paths", {})
        payload["source_paths"]["snapshot_path"] = rel_or_abs(snapshot_path, repo_root)
        return payload

    log_path = resolve_path(repo_root, DEFAULT_TIKTOK_RUNTIME_LOG_PATH)
    records = read_jsonl_tail(log_path, limit=32)
    normalized_events = [
        normalize_runtime_log_event(record=item, idx=idx, log_path=log_path, repo_root=repo_root)
        for idx, item in enumerate(records[-12:], start=1)
    ]
    normalized_events = sort_events_latest(normalized_events)
    latest = normalized_events[0] if normalized_events else {}
    process_state, process_reason = classify_runtime_process_state(
        event_name=str(latest.get("event_name", "")),
        level=str(latest.get("severity", "info")),
    )
    failure_reason = str(latest.get("failure_reason", "")).strip()
    recovery_signal = str(latest.get("recovery_signal", "")).strip()
    if not failure_reason:
        failure_reason = "none" if process_state != "ERROR" else process_reason
    if not recovery_signal:
        recovery_signal = "none" if process_state != "ERROR" else "inspect_runtime_logs"

    latest_verify_dir = find_latest_verify_dir(resolve_path(repo_root, DEFAULT_TIKTOK_PROJECT_CORE_ROOT))
    verification_summary = load_json_file_if_exists(latest_verify_dir / "verification_summary.json") if latest_verify_dir else {}
    readiness_summary = load_json_file_if_exists(latest_verify_dir / "readiness_summary.json") if latest_verify_dir else {}

    return {
        "state_id": "tiktok_runtime_observability_v1",
        "generated_at_utc": utc_now_iso(),
        "truth_class": "DERIVED_CANONICAL",
        "source_mode": "DERIVED_RUNTIME_LOG",
        "process_state": process_state,
        "process_reason": process_reason,
        "current_operation_code": str(latest.get("event_name", "RUNTIME_IDLE")).upper(),
        "current_operation_ru": (
            "Идет активная операция агента"
            if process_state == "PROCESSING"
            else "Обнаружен runtime-сбой агента"
            if process_state == "ERROR"
            else "Агент в ожидании следующей операции"
        ),
        "latest_change_summary": str(latest.get("summary", "runtime log has no events yet")),
        "latest_event_at_utc": str(latest.get("occurred_at_utc", "")),
        "failure_reason": failure_reason,
        "recovery_signal": recovery_signal,
        "recent_events": normalized_events,
        "verification_context": {
            "latest_verify_run_id": str(verification_summary.get("run_id") or readiness_summary.get("run_id") or "unknown"),
            "overall_gate_status": str(verification_summary.get("overall_gate_status", "UNKNOWN")),
            "readiness_status": str(readiness_summary.get("status", "UNKNOWN")),
            "runtime_readiness_stage": str(
                ((verification_summary.get("module_status", {}) or {}).get("runtime_readiness", "UNKNOWN"))
            ),
            "ui_backend_integration_stage": str(
                ((verification_summary.get("module_status", {}) or {}).get("ui_backend_integration", "UNKNOWN"))
            ),
            "prompt_lineage_observability_stage": str(
                ((verification_summary.get("module_status", {}) or {}).get("prompt_lineage_observability", "UNKNOWN"))
            ),
            "truth_class": "SOURCE_EXACT",
        },
        "source_paths": {
            "runtime_log_path": rel_or_abs(log_path, repo_root),
            "snapshot_path": rel_or_abs(snapshot_path, repo_root),
            "latest_verify_dir": rel_or_abs(latest_verify_dir, repo_root) if latest_verify_dir else "missing",
        },
        "integrity": {
            "runtime_log_present": log_path.exists(),
            "runtime_log_events_count": len(records),
            "recent_events_emitted": len(normalized_events),
            "verification_context_available": bool(verification_summary) or bool(readiness_summary),
        },
    }


def is_controlled_classified_dirty(repo_worktree_hygiene: dict, hygiene_classification_state: dict) -> bool:
    cleanliness_verdict = str((repo_worktree_hygiene or {}).get("cleanliness_verdict", "UNKNOWN")).upper()
    if cleanliness_verdict in {"UNKNOWN", "CLEAN"}:
        return False

    class_counts = dict((hygiene_classification_state or {}).get("classification_counts", {}) or {})
    canonical_intended = int(class_counts.get("CANONICAL_INTENDED_TRACKED", 0) or 0)
    generated_runtime_only = int(class_counts.get("GENERATED_RUNTIME_ONLY", 0) or 0)
    review_artifact_retention = int(class_counts.get("REVIEW_ARTIFACT_RETENTION", 0) or 0)
    needs_owner_decision = int(class_counts.get("NEEDS_OWNER_DECISION", 0) or 0)
    junk_or_residue = int(class_counts.get("JUNK_OR_RESIDUE", 0) or 0)
    suspicious = int(class_counts.get("SUSPICIOUS_INQUISITION_ATTENTION", 0) or 0)
    controlled_total = canonical_intended + generated_runtime_only + review_artifact_retention

    return (
        needs_owner_decision == 0
        and junk_or_residue == 0
        and suspicious == 0
        and controlled_total > 0
    )


def build_system_brain_state(
    repo_root: Path,
    *,
    repo_worktree_hygiene: dict | None = None,
    code_bank_state: dict | None = None,
    dashboard_coverage_state: dict | None = None,
    truth_dominance_state: dict | None = None,
    custodes_state: dict | None = None,
    throne_authority_state: dict | None = None,
    hygiene_classification_state: dict | None = None,
) -> dict:
    one_screen_path = resolve_path(repo_root, DEFAULT_ONE_SCREEN_STATUS_PATH)
    repo_control_path = resolve_path(repo_root, DEFAULT_REPO_CONTROL_STATUS_PATH)
    constitution_path = resolve_path(repo_root, "runtime/repo_control_center/constitution_status.json")
    mission_consistency_path = resolve_path(repo_root, DEFAULT_OPERATOR_MISSION_CONSISTENCY_PATH)
    task_program_consistency_path = resolve_path(repo_root, DEFAULT_OPERATOR_TASK_PROGRAM_CONSISTENCY_PATH)
    command_surface_script_path = resolve_path(repo_root, DEFAULT_OPERATOR_COMMAND_SURFACE_SCRIPT_PATH)
    command_surface_status_path = resolve_path(repo_root, DEFAULT_OPERATOR_COMMAND_SURFACE_STATUS_PATH)

    one_screen = load_json_file_if_exists(one_screen_path)
    repo_control = load_json_file_if_exists(repo_control_path)
    constitution = load_json_file_if_exists(constitution_path)
    mission_consistency = load_json_file_if_exists(mission_consistency_path)
    task_program_consistency = load_json_file_if_exists(task_program_consistency_path)
    command_surface_status = load_json_file_if_exists(command_surface_status_path)
    if repo_worktree_hygiene is None:
        repo_worktree_hygiene = collect_repo_worktree_hygiene(repo_root)
    if code_bank_state is None:
        code_bank_state = build_code_bank_state(
            repo_root,
            load_json_file_if_exists(resolve_path(repo_root, DEFAULT_IMPERIUM_CODE_BANK_SURFACE_PATH)),
        )
    if dashboard_coverage_state is None:
        dashboard_coverage_state = build_dashboard_coverage_state(
            repo_root,
            load_json_file_if_exists(resolve_path(repo_root, DEFAULT_IMPERIUM_DASHBOARD_COVERAGE_SURFACE_PATH)),
        )
    if truth_dominance_state is None:
        truth_dominance_state = build_truth_dominance_state(
            repo_root,
            load_json_file_if_exists(resolve_path(repo_root, DEFAULT_IMPERIUM_TRUTH_DOMINANCE_SURFACE_PATH)),
        )
    if hygiene_classification_state is None:
        hygiene_classification_state = load_json_file_if_exists(
            resolve_path(repo_root, DEFAULT_IMPERIUM_REPO_HYGIENE_CLASSIFICATION_SURFACE_PATH)
        )
    if custodes_state is None:
        custodes_state = {}
    if throne_authority_state is None:
        throne_authority_state = build_throne_authority_state(repo_root)

    one_screen_sync = str(one_screen.get("sync_verdict", "UNKNOWN"))
    repo_control_sync = str(((repo_control.get("verdicts", {}) or {}).get("sync", {}) or {}).get("verdict", "UNKNOWN"))
    one_screen_critical = int(one_screen.get("critical_contradictions", 0) or 0)
    repo_control_critical = int(((repo_control.get("checks", {}) or {}).get("contradictions", {}) or {}).get("critical_count", 0) or 0)
    mission_verdict = str(mission_consistency.get("verdict", "UNKNOWN"))
    task_verdict = str(task_program_consistency.get("verdict", "UNKNOWN"))
    command_verdict = str(command_surface_status.get("latest_execution_verdict", "UNKNOWN"))

    conflicts: list[dict] = []
    if one_screen_sync != "UNKNOWN" and repo_control_sync != "UNKNOWN" and one_screen_sync != repo_control_sync:
        conflicts.append(
            {
                "id": "sync_verdict_divergence",
                "severity": "warning",
                "reason": f"one_screen.sync={one_screen_sync} vs repo_control.sync={repo_control_sync}",
                "truth_class": "DERIVED_CANONICAL",
            }
        )
    if one_screen_critical != repo_control_critical:
        conflicts.append(
            {
                "id": "critical_contradiction_count_divergence",
                "severity": "warning",
                "reason": f"one_screen.critical={one_screen_critical} vs repo_control.critical={repo_control_critical}",
                "truth_class": "DERIVED_CANONICAL",
            }
        )
    if mission_verdict.upper() != "PASS":
        conflicts.append(
            {
                "id": "operator_mission_consistency_not_pass",
                "severity": "high",
                "reason": f"mission consistency verdict={mission_verdict}",
                "truth_class": "SOURCE_EXACT",
            }
        )
    if task_verdict.upper() != "PASS":
        conflicts.append(
            {
                "id": "operator_task_program_consistency_not_pass",
                "severity": "high",
                "reason": f"task program consistency verdict={task_verdict}",
                "truth_class": "SOURCE_EXACT",
            }
        )
    if parse_bool(one_screen.get("operator_action_required"), False):
        conflicts.append(
            {
                "id": "operator_action_required_flag",
                "severity": "medium",
                "reason": str(one_screen.get("blocking_reason_detail", "operator action required")),
                "truth_class": "SOURCE_EXACT",
            }
        )
    cleanliness_verdict = str((repo_worktree_hygiene or {}).get("cleanliness_verdict", "UNKNOWN"))
    controlled_classified_dirty = is_controlled_classified_dirty(
        repo_worktree_hygiene or {},
        hygiene_classification_state or {},
    )
    if cleanliness_verdict != "CLEAN" and not controlled_classified_dirty:
        conflicts.append(
            {
                "id": "repo_worktree_not_clean",
                "severity": "high",
                "reason": f"worktree verdict={cleanliness_verdict}",
                "truth_class": "SOURCE_EXACT",
            }
        )
    coverage_verdict = str((dashboard_coverage_state or {}).get("coverage_verdict", "UNKNOWN"))
    if coverage_verdict != "FULL_COVERAGE":
        conflicts.append(
            {
                "id": "dashboard_coverage_not_full",
                "severity": "warning",
                "reason": f"coverage verdict={coverage_verdict}",
                "truth_class": "DERIVED_CANONICAL",
            }
        )
    stale_rules_count = int((truth_dominance_state or {}).get("stale_rules_count", 0) or 0)
    if stale_rules_count > 0:
        conflicts.append(
            {
                "id": "truth_dominance_stale_rules",
                "severity": "warning",
                "reason": f"stale dominance rules={stale_rules_count}",
                "truth_class": "DERIVED_CANONICAL",
            }
        )
    if bool((throne_authority_state or {}).get("emperor_status_blocked", False)):
        conflicts.append(
            {
                "id": "throne_authority_anchor_blocked",
                "severity": "critical",
                "reason": str((throne_authority_state or {}).get("emperor_status", "EMPEROR_STATUS_BLOCKED")),
                "truth_class": "SOURCE_EXACT",
            }
        )

    blocker_classes: dict[str, list[dict]] = {
        "sovereign_proof_blockers": [],
        "governance_blockers": [],
        "trust_blockers": [],
        "sync_blockers": [],
        "repo_hygiene_blockers": [],
        "runtime_transport_blockers": [],
    }

    def add_blocker(class_key: str, *, blocker_id: str, reason: str, severity: str, truth_class: str) -> None:
        blocker_classes[class_key].append(
            {
                "id": blocker_id,
                "reason": reason,
                "severity": severity,
                "truth_class": truth_class,
            }
        )

    if bool((throne_authority_state or {}).get("emperor_status_blocked", False)):
        add_blocker(
            "sovereign_proof_blockers",
            blocker_id="throne_authority_anchor_blocked",
            reason=str((throne_authority_state or {}).get("emperor_status", "EMPEROR_STATUS_BLOCKED")),
            severity="critical",
            truth_class="SOURCE_EXACT",
        )

    for item in list((throne_authority_state or {}).get("sovereign_proof_blockers", []) or []):
        blocker_id = str(item).strip()
        if not blocker_id:
            continue
        add_blocker(
            "sovereign_proof_blockers",
            blocker_id=blocker_id,
            reason=blocker_id,
            severity="critical",
            truth_class="SOURCE_EXACT",
        )

    for item in list(constitution.get("blockers", []) or []):
        if isinstance(item, dict):
            blocker_id = str(item.get("check", "") or item.get("id", "") or "governance_blocker").strip()
            reason = str(item.get("reason", "") or item.get("status", "") or blocker_id)
        else:
            blocker_id = str(item).strip() or "governance_blocker"
            reason = blocker_id
        add_blocker(
            "governance_blockers",
            blocker_id=blocker_id,
            reason=reason,
            severity="high",
            truth_class="SOURCE_EXACT",
        )

    constitution_governance = str(constitution.get("governance_acceptance", "UNKNOWN")).upper()
    one_screen_governance = str(one_screen.get("governance_acceptance_verdict", "UNKNOWN")).upper()
    if constitution_governance in {"FAIL", "REJECTED", "BLOCKED"}:
        add_blocker(
            "governance_blockers",
            blocker_id="constitution_governance_acceptance_failed",
            reason=f"constitution.governance_acceptance={constitution_governance}",
            severity="high",
            truth_class="SOURCE_EXACT",
        )
    if one_screen_governance in {"FAIL", "REJECTED", "BLOCKED"}:
        add_blocker(
            "governance_blockers",
            blocker_id="one_screen_governance_acceptance_failed",
            reason=f"one_screen.governance_acceptance_verdict={one_screen_governance}",
            severity="high",
            truth_class="SOURCE_EXACT",
        )

    trust_verdict = str(one_screen.get("trust_verdict", "UNKNOWN")).upper()
    constitution_trust = str(constitution.get("trust_status", "UNKNOWN")).upper()
    if trust_verdict not in {"TRUSTED", "PASS"}:
        add_blocker(
            "trust_blockers",
            blocker_id="one_screen_trust_not_trusted",
            reason=f"one_screen.trust_verdict={trust_verdict}",
            severity="high",
            truth_class="SOURCE_EXACT",
        )
    if constitution_trust not in {"TRUSTED", "PASS", "UNKNOWN"}:
        add_blocker(
            "trust_blockers",
            blocker_id="constitution_trust_not_trusted",
            reason=f"constitution.trust_status={constitution_trust}",
            severity="high",
            truth_class="SOURCE_EXACT",
        )

    constitution_sync = str(constitution.get("sync_status", "UNKNOWN")).upper()
    sync_ok_values = {"IN_SYNC", "IN_SYNC_CLASSIFIED", "PASS"}
    if one_screen_sync not in sync_ok_values:
        add_blocker(
            "sync_blockers",
            blocker_id="one_screen_sync_not_in_sync",
            reason=f"one_screen.sync_verdict={one_screen_sync}",
            severity="high",
            truth_class="SOURCE_EXACT",
        )
    if repo_control_sync not in {*sync_ok_values, "UNKNOWN"}:
        add_blocker(
            "sync_blockers",
            blocker_id="repo_control_sync_not_in_sync",
            reason=f"repo_control.sync_verdict={repo_control_sync}",
            severity="high",
            truth_class="SOURCE_EXACT",
        )
    if constitution_sync not in {*sync_ok_values, "UNKNOWN"}:
        add_blocker(
            "sync_blockers",
            blocker_id="constitution_sync_not_in_sync",
            reason=f"constitution.sync_status={constitution_sync}",
            severity="high",
            truth_class="SOURCE_EXACT",
        )

    if cleanliness_verdict != "CLEAN" and not controlled_classified_dirty:
        add_blocker(
            "repo_hygiene_blockers",
            blocker_id="repo_worktree_not_clean",
            reason=f"worktree_verdict={cleanliness_verdict}",
            severity="high",
            truth_class="SOURCE_EXACT",
        )

    if not command_surface_script_path.exists():
        add_blocker(
            "runtime_transport_blockers",
            blocker_id="command_surface_script_missing",
            reason=f"missing:{rel_or_abs(command_surface_script_path, repo_root)}",
            severity="medium",
            truth_class="SOURCE_EXACT",
        )
    if not command_surface_status:
        add_blocker(
            "runtime_transport_blockers",
            blocker_id="command_surface_status_missing",
            reason=f"missing:{rel_or_abs(command_surface_status_path, repo_root)}",
            severity="medium",
            truth_class="SOURCE_EXACT",
        )

    blocker_counts = {key: len(value) for key, value in blocker_classes.items()}

    conflict_state = "CONFLICT" if conflicts else "CONSISTENT"
    trust_state = "TRUSTED"
    if str(one_screen.get("trust_verdict", "UNKNOWN")).upper() not in {"TRUSTED", "PASS"}:
        trust_state = "WARNING"
    if conflicts:
        trust_state = "WARNING"

    one_screen_age = human_age_minutes(str(one_screen.get("generated_at", "")))
    repo_control_age = human_age_minutes(str(repo_control.get("generated_at", "")))
    command_surface_age = human_age_minutes(str(command_surface_status.get("generated_at", "")))
    constitution_checked_at = str(constitution.get("last_checked_at", ""))
    constitution_age = human_age_minutes(constitution_checked_at)
    control_age_candidates = [
        value
        for value in [one_screen_age, repo_control_age, command_surface_age, constitution_age]
        if value is not None
    ]
    control_plane_last_refresh_age_minutes = min(control_age_candidates) if control_age_candidates else None

    return {
        "state_id": "factory_control_brain_state_v1",
        "truth_class": "DERIVED_CANONICAL",
        "conflict_state": conflict_state,
        "trust_state": trust_state,
        "one_screen": {
            "trust_verdict": str(one_screen.get("trust_verdict", "UNKNOWN")),
            "sync_verdict": one_screen_sync,
            "governance_acceptance_verdict": str(one_screen.get("governance_acceptance_verdict", "UNKNOWN")),
            "admission_verdict": str(one_screen.get("admission_verdict", "UNKNOWN")),
            "operator_action_required": parse_bool(one_screen.get("operator_action_required"), False),
            "critical_contradictions": one_screen_critical,
            "major_contradictions": int(one_screen.get("major_contradictions", 0) or 0),
            "generated_at": str(one_screen.get("generated_at", "")),
            "age_minutes": one_screen_age,
            "source_path": rel_or_abs(one_screen_path, repo_root),
            "source_class": "SOURCE_EXACT",
        },
        "repo_control": {
            "repo_health": str(((repo_control.get("repo", {}) or {}).get("repo_health", "UNKNOWN"))),
            "workspace_health": str(((repo_control.get("repo", {}) or {}).get("workspace_health", "UNKNOWN"))),
            "sync_verdict": repo_control_sync,
            "critical_contradictions": repo_control_critical,
            "generated_at": str(repo_control.get("generated_at", "")),
            "age_minutes": repo_control_age,
            "source_path": rel_or_abs(repo_control_path, repo_root),
            "source_class": "SOURCE_EXACT",
        },
        "constitution": {
            "overall_verdict": str(constitution.get("overall_verdict", "UNKNOWN")),
            "governance_acceptance": str(constitution.get("governance_acceptance", "UNKNOWN")),
            "trust_status": str(constitution.get("trust_status", "UNKNOWN")),
            "sync_status": str(constitution.get("sync_status", "UNKNOWN")),
            "detected_node_rank": str(constitution.get("detected_node_rank", "UNKNOWN")),
            "last_checked_at": constitution_checked_at,
            "age_minutes": constitution_age,
            "blockers": list(constitution.get("blockers", []) or []),
            "warnings": list(constitution.get("warnings", []) or []),
            "source_path": rel_or_abs(constitution_path, repo_root),
            "source_class": "SOURCE_EXACT" if constitution else "NOT_YET_IMPLEMENTED",
        },
        "mission_consistency": {
            "verdict": mission_verdict,
            "failed": int(mission_consistency.get("failed", 0) or 0),
            "generated_at": str(mission_consistency.get("generated_at", "")),
            "age_minutes": human_age_minutes(str(mission_consistency.get("generated_at", ""))),
            "source_path": rel_or_abs(mission_consistency_path, repo_root),
            "source_class": "SOURCE_EXACT",
        },
        "task_program_consistency": {
            "verdict": task_verdict,
            "failed": int(task_program_consistency.get("failed", 0) or 0),
            "generated_at": str(task_program_consistency.get("generated_at", "")),
            "age_minutes": human_age_minutes(str(task_program_consistency.get("generated_at", ""))),
            "source_path": rel_or_abs(task_program_consistency_path, repo_root),
            "source_class": "SOURCE_EXACT",
        },
        "command_surface": {
            "script_exists": command_surface_script_path.exists(),
            "script_path": rel_or_abs(command_surface_script_path, repo_root),
            "latest_execution_verdict": command_verdict,
            "latest_execution_mode": str(command_surface_status.get("latest_execution_mode", "UNKNOWN")),
            "generated_at": str(command_surface_status.get("generated_at", "")),
            "age_minutes": command_surface_age,
            "status_source_path": rel_or_abs(command_surface_status_path, repo_root),
            "source_class": "SOURCE_EXACT" if command_surface_status else "NOT_YET_IMPLEMENTED",
        },
        "limits": {
            "operator_action_required": parse_bool(one_screen.get("operator_action_required"), False),
            "blocking_reason_category": str(one_screen.get("blocking_reason_category", "UNKNOWN")),
            "blocking_reason_detail": str(one_screen.get("blocking_reason_detail", "")),
            "governance_acceptance_verdict": str(one_screen.get("governance_acceptance_verdict", "UNKNOWN")),
            "admission_verdict": str(one_screen.get("admission_verdict", "UNKNOWN")),
            "evolution_verdict": str(one_screen.get("evolution_verdict", "UNKNOWN")),
            "workspace_health": str(one_screen.get("workspace_health", "UNKNOWN")),
            "source_path": rel_or_abs(one_screen_path, repo_root),
            "source_class": "SOURCE_EXACT",
        },
        "age_axis": {
            "control_plane_last_refresh_age_minutes": control_plane_last_refresh_age_minutes,
            "one_screen_age_minutes": one_screen_age,
            "repo_control_age_minutes": repo_control_age,
            "constitution_age_minutes": constitution_age,
            "command_surface_age_minutes": command_surface_age,
            "truth_class": "DERIVED_CANONICAL",
        },
        "repo_worktree_hygiene": repo_worktree_hygiene,
        "repo_hygiene_classification": hygiene_classification_state,
        "code_bank": code_bank_state,
        "dashboard_coverage": dashboard_coverage_state,
        "truth_dominance": truth_dominance_state,
        "throne_authority": throne_authority_state,
        "custodes": custodes_state,
        "blocker_classes": blocker_classes,
        "blocker_counts": blocker_counts,
        "conflicts": conflicts,
        "summary_note": "Control-core metrics include explicit blocker classes; sovereign proof is separated from governance/trust/sync/repo/runtime blockers.",
    }


def build_system_semantic_state_surfaces(
    repo_root: Path,
    *,
    canon_truth: dict,
    system_brain_state: dict,
    prompt_lineage_state: dict,
    tiktok_runtime_state: dict,
    wave1_control: dict,
    production_history_seed: dict,
    semantic_model: dict | None = None,
) -> dict:
    owner_gates = (canon_truth.get("owner_gates", {}) or {})
    tiktok_truth = (canon_truth.get("tiktok_agent", {}) or {})
    post_wave_stage = (tiktok_truth.get("post_wave1_stage", {}) or {})
    growth_truth = (canon_truth.get("growth_distribution", {}) or {})
    live_layer = (canon_truth.get("live_layer", {}) or {})
    visual_doctrine = (canon_truth.get("visual_doctrine", {}) or {})

    one_screen = system_brain_state.get("one_screen", {}) or {}
    repo_control = system_brain_state.get("repo_control", {}) or {}
    constitution = system_brain_state.get("constitution", {}) or {}
    limits = system_brain_state.get("limits", {}) or {}
    mission = system_brain_state.get("mission_consistency", {}) or {}
    task_program = system_brain_state.get("task_program_consistency", {}) or {}
    command_surface = system_brain_state.get("command_surface", {}) or {}
    conflicts = list(system_brain_state.get("conflicts", []) or [])

    contradiction_ledger = wave1_control.get("contradiction_ledger", {}) or {}
    open_contradictions = list(contradiction_ledger.get("open", []) or [])
    closed_contradictions = list(contradiction_ledger.get("closed", []) or [])
    open_contradiction_ids = [str((item or {}).get("id", "")) for item in open_contradictions if str((item or {}).get("id", "")).strip()]
    open_contradiction_ids = [item for item in open_contradiction_ids if item]

    constitution_overall = str(constitution.get("overall_verdict", "UNKNOWN"))
    constitution_governance = str(constitution.get("governance_acceptance", "UNKNOWN"))
    constitution_trust = str(constitution.get("trust_status", "UNKNOWN"))
    constitution_sync = str(constitution.get("sync_status", "UNKNOWN"))
    constitution_blockers = list(constitution.get("blockers", []) or [])
    constitution_warnings = list(constitution.get("warnings", []) or [])

    constitution_overall_upper = constitution_overall.upper()
    constitution_governance_upper = constitution_governance.upper()
    trust_state_upper = str(system_brain_state.get("trust_state", "UNKNOWN")).upper()

    if (
        constitution_overall_upper in {"FAIL", "REJECTED"}
        or constitution_governance_upper in {"FAIL", "REJECTED", "BLOCK"}
        or len(constitution_blockers) > 0
    ):
        canon_drift_risk = "HIGH_CANON_DRIFT_RISK"
    elif conflicts or constitution_warnings or trust_state_upper in {"WARNING", "PARTIAL"}:
        canon_drift_risk = "MEDIUM_CANON_DRIFT_RISK"
    else:
        canon_drift_risk = "LOW_CANON_DRIFT_RISK"

    if constitution_governance_upper in {"PASS", "ACCEPTED"} and constitution_overall_upper in {"PASS", "PARTIAL"}:
        doctrine_posture = "ACTIVE_CANON_ENFORCEMENT"
    elif constitution_overall_upper == "UNKNOWN":
        doctrine_posture = "CANON_STATE_UNKNOWN"
    else:
        doctrine_posture = "CANON_GUARDED_WARNING"

    owner_decision_triggers: list[str] = []
    if parse_bool(limits.get("operator_action_required"), False):
        owner_decision_triggers.append("operator_action_required")
    if open_contradictions:
        owner_decision_triggers.append("open_contradiction_boundary")
    gate_d = str(owner_gates.get("gate_d", "UNKNOWN")).upper()
    if "PENDING" in gate_d or "NEXT" in gate_d:
        owner_decision_triggers.append("owner_gate_d_pending")
    owner_decision_triggers = list(dict.fromkeys(owner_decision_triggers))

    command_verdict = str(command_surface.get("latest_execution_verdict", "UNKNOWN")).upper()
    mission_verdict = str(mission.get("verdict", "UNKNOWN")).upper()
    task_verdict = str(task_program.get("verdict", "UNKNOWN")).upper()
    conflict_state = str(system_brain_state.get("conflict_state", "UNKNOWN")).upper()
    governance_verdict = str(one_screen.get("governance_acceptance_verdict", "UNKNOWN")).upper()
    verification_verdict = str(one_screen.get("admission_verdict", "UNKNOWN")).upper()

    if (
        command_verdict in {"FAIL", "ERROR"}
        or mission_verdict in {"FAIL", "ERROR"}
        or task_verdict in {"FAIL", "ERROR"}
        or conflict_state == "CONFLICT"
    ):
        control_health_state = "AT_RISK"
    elif (
        command_verdict in {"SUCCESS", "PASS", "VERIFIED"}
        and mission_verdict == "PASS"
        and task_verdict == "PASS"
        and conflict_state != "CONFLICT"
    ):
        control_health_state = "HEALTHY"
    else:
        control_health_state = "PARTIAL"

    history_nodes = list((production_history_seed.get("nodes", []) or []))
    history_times = [
        parse_utc(str(item.get("occurred_at_utc", "")))
        for item in history_nodes
        if str(item.get("occurred_at_utc", "")).strip()
    ]
    history_times = [value for value in history_times if value > datetime.fromtimestamp(0, tz=timezone.utc)]
    system_started_at = min(history_times).isoformat() if history_times else ""

    regime_started_at = str(post_wave_stage.get("started_at_utc", "")).strip()
    product_started_candidates = [
        str((wave1_control.get("first_tranche_execution", {}) or {}).get("started_at_utc", "")).strip(),
        regime_started_at,
    ]
    product_started_candidates = [value for value in product_started_candidates if value]
    parsed_product_start = [parse_utc(value) for value in product_started_candidates]
    parsed_product_start = [value for value in parsed_product_start if value > datetime.fromtimestamp(0, tz=timezone.utc)]
    product_started_at = min(parsed_product_start).isoformat() if parsed_product_start else ""

    one_screen_generated_at = str(one_screen.get("generated_at", "")).strip()
    repo_control_generated_at = str(repo_control.get("generated_at", "")).strip()
    last_stable_point_at = ""
    if one_screen_generated_at and str(one_screen.get("sync_verdict", "")).upper() == "IN_SYNC" and str(one_screen.get("trust_verdict", "")).upper() in {"TRUSTED", "PASS"}:
        last_stable_point_at = one_screen_generated_at
    elif repo_control_generated_at and str(repo_control.get("repo_health", "")).upper() == "PASS":
        last_stable_point_at = repo_control_generated_at

    age_axis = {
        "system_started_at_utc": system_started_at,
        "system_age_minutes": human_age_minutes(system_started_at),
        "regime_started_at_utc": regime_started_at,
        "regime_age_minutes": human_age_minutes(regime_started_at),
        "product_started_at_utc": product_started_at,
        "product_age_minutes": human_age_minutes(product_started_at),
        "last_stable_point_at_utc": last_stable_point_at,
        "last_stable_point_age_minutes": human_age_minutes(last_stable_point_at),
        "truth_class": "DERIVED_CANONICAL",
    }

    source_of_truth = str(canon_truth.get("source_of_truth", "UNKNOWN"))
    safe_mirror_role = str(canon_truth.get("safe_mirror_role", "UNKNOWN"))
    live_mode = str(live_layer.get("mode", "UNKNOWN"))
    source_of_truth_matches_repo = source_of_truth.strip().lower() == str(repo_root).strip().lower()
    safe_mirror_non_sovereign = "NON_SOVEREIGN" in safe_mirror_role.upper()

    canon_source_exists = source_path_exists(repo_root, DEFAULT_CANON_STATE_SYNC_PATH)
    wave_surface_source_exists = source_path_exists(repo_root, DEFAULT_WAVE1_CONTROL_SURFACES_PATH)
    one_screen_source_exists = source_path_exists(repo_root, DEFAULT_ONE_SCREEN_STATUS_PATH)
    repo_control_source_exists = source_path_exists(repo_root, DEFAULT_REPO_CONTROL_STATUS_PATH)
    runtime_log_source_path = str(
        tiktok_runtime_state.get("source_paths", {}).get("runtime_log_path", DEFAULT_TIKTOK_RUNTIME_LOG_PATH)
    )
    runtime_log_source_exists = source_path_exists(repo_root, runtime_log_source_path)
    prompt_manifest_source_path = str(
        prompt_lineage_state.get("source_paths", {}).get("manifest_path", "missing")
    )
    prompt_manifest_source_exists = source_path_exists(repo_root, prompt_manifest_source_path)

    if source_of_truth_matches_repo and "LOCALHOST_ONLY" in live_mode.upper():
        sovereignty_posture = "LOCAL_ONLY_SOVEREIGN_ENFORCED"
    elif source_of_truth_matches_repo:
        sovereignty_posture = "LOCAL_SOVEREIGN_WITH_MODE_WARNING"
    else:
        sovereignty_posture = "SOVEREIGN_ROOT_MISMATCH"

    if safe_mirror_non_sovereign:
        external_exposure_state = "MANUAL_SAFE_EXPORT_ONLY_NON_SOVEREIGN"
    else:
        external_exposure_state = "EXTERNAL_EXPOSURE_POSTURE_UNVERIFIED"

    doctrine_paths = [
        "docs/governance/REPOSITORY_SOVEREIGNTY_EXTERNAL_SURFACE_POLICY_V1.md",
        "docs/governance/PORTABLE_EMPEROR_MACHINE_BOOTSTRAP_VECTOR_V1.md",
        "docs/governance/TWO_DISK_AND_N_BACKUP_STORAGE_DOCTRINE_V1.md",
        "docs/governance/DISASTER_RECOVERY_TO_LAST_CANONICAL_STEP_VECTOR_V1.md",
        "docs/governance/IMPERIAL_DASHBOARD_VECTOR_DOCTRINE_V1.md",
        "docs/governance/OWNER_DECISION_ESCALATION_DOCTRINE_V1.md",
    ]
    doctrine_present = [path for path in doctrine_paths if resolve_path(repo_root, path).exists()]
    recovery_readiness_posture = (
        "DOCTRINE_READY_NOT_FULLY_IMPLEMENTED"
        if len(doctrine_present) == len(doctrine_paths)
        else "PARTIAL_DOCTRINE_COVERAGE"
    )

    prompt_boundary = prompt_lineage_state.get("trusted_boundary", "UNKNOWN")
    prompt_text_boundary = (prompt_lineage_state.get("text_boundary", {}) or {}).get("boundary_note", "")
    runtime_process_state = str(tiktok_runtime_state.get("process_state", "UNKNOWN"))

    known_now = [
        f"selected_option={tiktok_truth.get('selected_option', 'UNKNOWN')}",
        f"wave_status={tiktok_truth.get('wave_1_status', 'UNKNOWN')}",
        f"gate_d={owner_gates.get('gate_d', 'UNKNOWN')}",
        f"post_wave_stage={post_wave_stage.get('status', 'UNKNOWN')}",
        f"growth_distribution={growth_truth.get('department_status', 'UNKNOWN')}",
    ]
    open_now = [
        f"open_contradictions={len(open_contradictions)}",
        f"owner_triggers={','.join(owner_decision_triggers) if owner_decision_triggers else 'none'}",
        f"live_layer={live_layer.get('implementation_status', 'UNKNOWN')}",
    ]
    next_vector = str(tiktok_truth.get("execution_lane_next", post_wave_stage.get("active_tranche", "UNKNOWN")))

    gap_source_candidates = [
        "docs/review_artifacts/SYSTEM_SEMANTIC_STATE_SURFACES_EXPANSION_DELTA_REMAINING_GAPS_V1.md",
        "docs/review_artifacts/IMPERIAL_DASHBOARD_VISUAL_REVOLUTION_TRANCHE_A_REMAINING_GAPS_V1.md",
        "docs/review_artifacts/TIKTOK_OWNER_DASHBOARD_HARDENING_TRANCHE_B_REMAINING_GAPS_V1.md",
    ]
    selected_gap_source_path = next(
        (path for path in gap_source_candidates if source_path_exists(repo_root, path)),
        gap_source_candidates[0],
    )
    selected_gap_source_exists = source_path_exists(repo_root, selected_gap_source_path)

    def make_gap_entry(gap_id: str, status: str, *, unavailable_in_step_scope: bool = False) -> dict:
        reason = classify_uncertainty_reason(
            status,
            source_exists=selected_gap_source_exists,
            mapped=True,
            unavailable_in_step_scope=unavailable_in_step_scope,
        )
        if "NOT_YET_IMPLEMENTED" in status.upper():
            truth_class = "NOT_YET_IMPLEMENTED"
        elif "PARTIALLY_IMPLEMENTED" in status.upper():
            truth_class = "DERIVED_CANONICAL"
        else:
            truth_class = "STALE_SOURCE" if not selected_gap_source_exists else "UNKNOWN"
        return {
            "id": gap_id,
            "status": status,
            "truth_class": truth_class,
            "source_path": selected_gap_source_path,
            "source_exists": selected_gap_source_exists,
            "unknown_reason": reason,
        }

    known_gaps = [
        make_gap_entry("full_event_bus", "NOT_YET_IMPLEMENTED"),
        make_gap_entry("before_after_diff_engine", "PARTIALLY_IMPLEMENTED"),
        make_gap_entry("auto_preview_pipeline", "NOT_YET_IMPLEMENTED"),
    ]

    unknown_reason_registry: list[dict] = []

    def append_unknown_registry(
        *,
        field_id: str,
        value: object,
        mapped: bool,
        source_path: str,
        source_exists: bool,
        owner_decision_pending: bool = False,
        unavailable_in_step_scope: bool = False,
    ) -> None:
        classification = classify_field_state_with_reason(
            value,
            source_exists=source_exists,
            mapped=mapped,
            owner_decision_pending=owner_decision_pending,
            unavailable_in_step_scope=unavailable_in_step_scope,
        )
        unknown_reason_registry.append(
            {
                "field_id": field_id,
                "value": str(value if value is not None else ""),
                "state": classification["state"],
                "unknown_reason": classification["unknown_reason"],
                "source_path": source_path,
                "source_exists": source_exists,
                "truth_class": "SOURCE_EXACT" if source_exists else "STALE_SOURCE",
            }
        )

    append_unknown_registry(
        field_id="tiktok.selected_option",
        value=tiktok_truth.get("selected_option"),
        mapped="selected_option" in tiktok_truth,
        source_path=DEFAULT_CANON_STATE_SYNC_PATH,
        source_exists=canon_source_exists,
    )
    append_unknown_registry(
        field_id="tiktok.wave_1_status",
        value=tiktok_truth.get("wave_1_status"),
        mapped="wave_1_status" in tiktok_truth,
        source_path=DEFAULT_CANON_STATE_SYNC_PATH,
        source_exists=canon_source_exists,
    )
    gate_d_value = owner_gates.get("gate_d")
    append_unknown_registry(
        field_id="owner_gates.gate_d",
        value=gate_d_value,
        mapped="gate_d" in owner_gates,
        source_path=DEFAULT_CANON_STATE_SYNC_PATH,
        source_exists=canon_source_exists,
        owner_decision_pending="PENDING" in str(gate_d_value or "").upper(),
    )
    append_unknown_registry(
        field_id="live_layer.implementation_status",
        value=live_layer.get("implementation_status"),
        mapped="implementation_status" in live_layer,
        source_path=DEFAULT_CANON_STATE_SYNC_PATH,
        source_exists=canon_source_exists,
    )
    append_unknown_registry(
        field_id="brain.command_surface_verdict",
        value=command_surface.get("latest_execution_verdict"),
        mapped="latest_execution_verdict" in command_surface,
        source_path=str(command_surface.get("status_source_path", DEFAULT_OPERATOR_COMMAND_SURFACE_STATUS_PATH)),
        source_exists=source_path_exists(
            repo_root,
            str(command_surface.get("status_source_path", DEFAULT_OPERATOR_COMMAND_SURFACE_STATUS_PATH)),
        ),
    )
    append_unknown_registry(
        field_id="brain.mission_consistency_verdict",
        value=mission.get("verdict"),
        mapped="verdict" in mission,
        source_path=str(mission.get("source_path", DEFAULT_OPERATOR_MISSION_CONSISTENCY_PATH)),
        source_exists=source_path_exists(
            repo_root,
            str(mission.get("source_path", DEFAULT_OPERATOR_MISSION_CONSISTENCY_PATH)),
        ),
    )
    append_unknown_registry(
        field_id="brain.task_program_consistency_verdict",
        value=task_program.get("verdict"),
        mapped="verdict" in task_program,
        source_path=str(task_program.get("source_path", DEFAULT_OPERATOR_TASK_PROGRAM_CONSISTENCY_PATH)),
        source_exists=source_path_exists(
            repo_root,
            str(task_program.get("source_path", DEFAULT_OPERATOR_TASK_PROGRAM_CONSISTENCY_PATH)),
        ),
    )
    append_unknown_registry(
        field_id="runtime.process_state",
        value=runtime_process_state,
        mapped="process_state" in tiktok_runtime_state,
        source_path=runtime_log_source_path,
        source_exists=runtime_log_source_exists,
    )
    append_unknown_registry(
        field_id="prompt_lineage.trusted_boundary",
        value=prompt_boundary,
        mapped="trusted_boundary" in prompt_lineage_state,
        source_path=prompt_manifest_source_path,
        source_exists=prompt_manifest_source_exists,
    )

    unknown_reasons = unknown_reason_breakdown(unknown_reason_registry + known_gaps)

    semantic_state = {
        "state_id": "system_semantic_state_surfaces_v1",
        "truth_class": "DERIVED_CANONICAL",
        "surface_model_path": DEFAULT_SYSTEM_SEMANTIC_STATE_MODEL_PATH,
        "surface_model_loaded": bool(semantic_model),
        "constitution_state": {
            "doctrine_posture": doctrine_posture,
            "canon_drift_risk": canon_drift_risk,
            "active_doctrine_pack": str(visual_doctrine.get("active_pack", "UNKNOWN")),
            "overall_verdict": constitution_overall,
            "governance_acceptance": constitution_governance,
            "trust_status": constitution_trust,
            "sync_status": constitution_sync,
            "breach_count": len(constitution_blockers),
            "warning_count": len(constitution_warnings),
            "breaches": constitution_blockers,
            "warnings": constitution_warnings,
            "exact_boundaries": [
                {
                    "id": "source_of_truth_root",
                    "value": source_of_truth,
                    "status": "ENFORCED" if source_of_truth_matches_repo else "MISMATCH",
                    "truth_class": "SOURCE_EXACT" if canon_source_exists else "STALE_SOURCE",
                    "source_path": DEFAULT_CANON_STATE_SYNC_PATH,
                    "source_exists": canon_source_exists,
                    "unknown_reason": "" if canon_source_exists else "stale_source",
                },
                {
                    "id": "gate_d_owner_boundary",
                    "value": str(owner_gates.get("gate_d", "UNKNOWN")),
                    "status": "CLOSED_BY_OWNER" if "CLOSED_BY_OWNER" in str(owner_gates.get("gate_d", "")).upper() else "OPEN_OR_UNKNOWN",
                    "truth_class": "SOURCE_EXACT" if canon_source_exists else "STALE_SOURCE",
                    "source_path": DEFAULT_CANON_STATE_SYNC_PATH,
                    "source_exists": canon_source_exists,
                    "unknown_reason": "" if canon_source_exists else "stale_source",
                },
            ],
            "source_integrity": {
                "canon_source_exists": canon_source_exists,
                "constitution_source_exists": source_path_exists(
                    repo_root,
                    str(constitution.get("source_path", "runtime/repo_control_center/constitution_status.json")),
                ),
            },
            "source_path": str(constitution.get("source_path", "runtime/repo_control_center/constitution_status.json")),
            "source_class": str(constitution.get("source_class", "SOURCE_EXACT")),
        },
        "brain_reason_control_state": {
            "mission_consistency_verdict": str(mission.get("verdict", "UNKNOWN")),
            "task_program_consistency_verdict": str(task_program.get("verdict", "UNKNOWN")),
            "command_surface_verdict": str(command_surface.get("latest_execution_verdict", "UNKNOWN")),
            "command_surface_mode": str(command_surface.get("latest_execution_mode", "UNKNOWN")),
            "contradiction_state": str(system_brain_state.get("conflict_state", "UNKNOWN")),
            "open_contradiction_count": len(open_contradictions),
            "closed_contradiction_count": len(closed_contradictions),
            "owner_decision_trigger_state": owner_decision_triggers,
            "trust_state": str(system_brain_state.get("trust_state", "UNKNOWN")),
            "verification_state": verification_verdict,
            "governance_state": governance_verdict,
            "control_health_state": control_health_state,
            "consistency_matrix": {
                "mission_task_aligned": mission_verdict == "PASS" and task_verdict == "PASS",
                "command_governance_aligned": command_verdict in {"PASS", "SUCCESS", "VERIFIED"} and governance_verdict in {"PASS", "ACCEPTED"},
                "conflict_free": conflict_state != "CONFLICT",
            },
            "source_paths": {
                "one_screen": str(one_screen.get("source_path", DEFAULT_ONE_SCREEN_STATUS_PATH)),
                "mission_consistency": str(mission.get("source_path", DEFAULT_OPERATOR_MISSION_CONSISTENCY_PATH)),
                "task_program_consistency": str(task_program.get("source_path", DEFAULT_OPERATOR_TASK_PROGRAM_CONSISTENCY_PATH)),
                "command_surface_status": str(command_surface.get("status_source_path", DEFAULT_OPERATOR_COMMAND_SURFACE_STATUS_PATH)),
            },
            "source_integrity": {
                "one_screen_source_exists": one_screen_source_exists,
                "repo_control_source_exists": repo_control_source_exists,
            },
            "truth_class": "DERIVED_CANONICAL",
        },
        "memory_chronology_knowledge_state": {
            "known_now": known_now,
            "open_now": open_now,
            "next_vector": next_vector,
            "last_working_canonical_step_id": str(post_wave_stage.get("active_tranche", wave1_control.get("wave_id", "UNKNOWN"))),
            "last_working_canonical_step_status": str(post_wave_stage.get("status", wave1_control.get("wave_status_surface", {}).get("status", "UNKNOWN"))),
            "last_stable_point_at_utc": age_axis.get("last_stable_point_at_utc"),
            "age_axis": age_axis,
            "chronology_nodes": history_nodes,
            "known_state_integrity": {
                "history_seed_nodes_count": len(history_nodes),
                "wave_surface_source_exists": wave_surface_source_exists,
                "canon_source_exists": canon_source_exists,
            },
            "truth_class": "DERIVED_CANONICAL",
            "source_paths": {
                "production_history_seed": DEFAULT_PRODUCTION_HISTORY_SEED_PATH,
                "canon_state_sync": DEFAULT_CANON_STATE_SYNC_PATH,
                "wave_control_surface": DEFAULT_WAVE1_CONTROL_SURFACES_PATH,
            },
        },
        "product_state_integration": {
            "product_id": "tiktok_agent_platform",
            "training_ground_posture": "TRAINING_GROUND_NOT_FULL_SYSTEM",
            "runtime_process_state": runtime_process_state,
            "runtime_failure_reason": str(tiktok_runtime_state.get("failure_reason", "none")),
            "runtime_recovery_signal": str(tiktok_runtime_state.get("recovery_signal", "none")),
            "prompt_lineage_honesty": {
                "lineage_id": str(prompt_lineage_state.get("lineage_id", "UNKNOWN")),
                "active_prompt_state": str(prompt_lineage_state.get("active_prompt_state", "UNKNOWN")),
                "trusted_boundary": str(prompt_boundary),
                "boundary_note": str(prompt_text_boundary),
                "full_text_exposed": bool((prompt_lineage_state.get("text_boundary", {}) or {}).get("full_prompt_text_exposed", False)),
            },
            "wave_status": str(tiktok_truth.get("wave_1_status", "UNKNOWN")),
            "post_wave_stage_status": str(post_wave_stage.get("status", "UNKNOWN")),
            "blocker_recovery_interpretation": {
                "open_contradiction_count": len(open_contradictions),
                "owner_decision_trigger_count": len(owner_decision_triggers),
                "recovery_signal_state": "PRESENT" if str(tiktok_runtime_state.get("recovery_signal", "")).strip() else "MISSING",
            },
            "source_integrity": {
                "runtime_log_source_exists": runtime_log_source_exists,
                "prompt_manifest_source_exists": prompt_manifest_source_exists,
            },
            "truth_class": "DERIVED_CANONICAL",
            "source_paths": {
                "runtime_observability": runtime_log_source_path,
                "prompt_lineage": prompt_manifest_source_path,
                "wave_control": DEFAULT_WAVE1_CONTROL_SURFACES_PATH,
            },
        },
        "security_sovereignty_posture_state": {
            "sovereignty_posture": sovereignty_posture,
            "external_exposure_state": external_exposure_state,
            "visibility_restrictions_posture": (
                "OWNER_FULL_LOCALHOST_ONLY_WORKER_ROLE_FILTERED_FUTURE"
                if "LOCALHOST_ONLY" in live_mode.upper()
                else "VISIBILITY_POSTURE_UNVERIFIED"
            ),
            "local_runtime_boundary": live_mode,
            "recovery_readiness_posture": recovery_readiness_posture,
            "doctrine_surfaces_present": len(doctrine_present),
            "doctrine_surfaces_total": len(doctrine_paths),
            "doctrine_missing_paths": [path for path in doctrine_paths if path not in doctrine_present],
            "source_integrity": {
                "canon_source_exists": canon_source_exists,
                "doctrine_surface_coverage": f"{len(doctrine_present)}/{len(doctrine_paths)}",
            },
            "truth_class": "DERIVED_CANONICAL",
            "source_paths": {
                "canon_state_sync": DEFAULT_CANON_STATE_SYNC_PATH,
                "one_screen_status": DEFAULT_ONE_SCREEN_STATUS_PATH,
                "sovereignty_doctrine": "docs/governance/SYSTEM_SOVEREIGNTY_PORTABILITY_AND_IMPERIAL_VECTOR_DOCTRINE_V1.md",
            },
        },
        "exact_derived_gap_disclosure": {
            "exact_count": 0,
            "derived_count": 0,
            "gap_count": len(known_gaps),
            "stale_source_count": 0,
            "known_gaps": known_gaps,
            "unknown_reason_registry": unknown_reason_registry,
            "unknown_reason_breakdown": unknown_reasons,
            "disclosure_note": "UNKNOWN разделен по причинам: not_implemented/not_mapped/stale_source/owner_decision_pending/unavailable_in_step_scope.",
            "truth_class": "DERIVED_CANONICAL",
        },
        "source_paths": {
            "canon_state_sync": DEFAULT_CANON_STATE_SYNC_PATH,
            "wave1_control_surfaces": DEFAULT_WAVE1_CONTROL_SURFACES_PATH,
            "one_screen_status": DEFAULT_ONE_SCREEN_STATUS_PATH,
            "repo_control_status": DEFAULT_REPO_CONTROL_STATUS_PATH,
            "constitution_status": "runtime/repo_control_center/constitution_status.json",
            "semantic_model": DEFAULT_SYSTEM_SEMANTIC_STATE_MODEL_PATH,
        },
    }
    truth_stats = summarize_truth_layers(
        {
            "constitution_state": semantic_state["constitution_state"],
            "brain_reason_control_state": semantic_state["brain_reason_control_state"],
            "memory_chronology_knowledge_state": semantic_state["memory_chronology_knowledge_state"],
            "product_state_integration": semantic_state["product_state_integration"],
            "security_sovereignty_posture_state": semantic_state["security_sovereignty_posture_state"],
            "known_gaps": semantic_state["exact_derived_gap_disclosure"]["known_gaps"],
            "unknown_reason_registry": semantic_state["exact_derived_gap_disclosure"]["unknown_reason_registry"],
        }
    )
    semantic_state["exact_derived_gap_disclosure"]["exact_count"] = truth_stats["exact"]
    semantic_state["exact_derived_gap_disclosure"]["derived_count"] = truth_stats["derived"]
    semantic_state["exact_derived_gap_disclosure"]["gap_count"] = max(
        len(known_gaps),
        truth_stats["gap"],
    )
    semantic_state["exact_derived_gap_disclosure"]["stale_source_count"] = truth_stats["stale"]
    return semantic_state


def build_imperium_parallel_channels(
    *,
    evolution_surface: dict,
    inquisition_surface: dict,
    custodes_surface: dict,
    mechanicus_surface: dict,
    administratum_surface: dict,
    force_surface: dict,
    palace_archive_surface: dict,
    control_gates_surface: dict,
    factory_surface: dict,
    product_map_surface: dict,
    canon_truth: dict,
    wave1_control: dict,
    system_semantic_state: dict,
) -> dict:
    tiktok_truth = (canon_truth.get("tiktok_agent", {}) or {})
    post_wave_stage = (tiktok_truth.get("post_wave1_stage", {}) or {})
    owner_gates = (canon_truth.get("owner_gates", {}) or {})
    contradiction_ledger = (wave1_control.get("contradiction_ledger", {}) or {})
    open_contradictions = list(contradiction_ledger.get("open", []) or [])
    semantic_product = (
        (system_semantic_state.get("product_state_integration", {}) or {})
        if isinstance(system_semantic_state, dict)
        else {}
    )
    semantic_constitution = (
        (system_semantic_state.get("constitution_state", {}) or {})
        if isinstance(system_semantic_state, dict)
        else {}
    )
    semantic_security = (
        (system_semantic_state.get("security_sovereignty_posture_state", {}) or {})
        if isinstance(system_semantic_state, dict)
        else {}
    )

    evolution_stage_map = list((evolution_surface.get("system_stage_map", []) or []))
    evolution_insights = list((evolution_surface.get("insight_candidates", []) or []))
    evolution_owner_queue = list((evolution_surface.get("owner_approval_queue", []) or []))
    accepted_gains = list((evolution_surface.get("accepted_transfer_gains", []) or []))
    inquisition_alerts = list((inquisition_surface.get("active_heresy_alerts", []) or []))
    inquisition_classes = list((inquisition_surface.get("heresy_classes", []) or []))
    inquisition_holding = (inquisition_surface.get("review_holding_zone", {}) or {})
    inquisition_integrity_state = (inquisition_surface.get("current_integrity_state", {}) or {})
    factory_products = list((factory_surface.get("products", []) or []))
    product_lines = list((product_map_surface.get("lines", []) or []))
    conveyor_lanes = list((factory_surface.get("conveyor_lanes", []) or []))
    stage_transition_matrix = list((factory_surface.get("stage_transition_matrix", []) or []))
    stage_gates = list((factory_surface.get("stage_gates", []) or []))
    quality_checkpoints = list((factory_surface.get("quality_checkpoints", []) or []))
    factory_morphology_profile = dict((factory_surface.get("factory_morphology_profile", {}) or {}))
    living_flow_relations = dict((factory_surface.get("living_flow_relations", {}) or {}))
    tiktok_line = next(
        (x for x in product_lines if str((x or {}).get("product_id", "")).strip().lower() == "tiktok_agent_platform"),
        {},
    )
    tiktok_product = next(
        (x for x in factory_products if str((x or {}).get("product_id", "")).strip().lower() == "tiktok_agent_platform"),
        {},
    )
    tiktok_ascent_track = dict((tiktok_line.get("ascent_track", {}) or {}))
    tiktok_live_flow_markers = dict((tiktok_product.get("live_flow_markers", {}) or {}))
    tiktok_ascent_lane = list((tiktok_ascent_track.get("ascent_lane", []) or []))
    tiktok_assembly_corridors = list((tiktok_product.get("assembly_corridors", []) or []))

    evolution_health = "STABLE"
    if open_contradictions:
        evolution_health = "ATTENTION_REQUIRED"
    if str(post_wave_stage.get("status", "")).upper() in {"BLOCKED", "ERROR"}:
        evolution_health = "AT_RISK"

    inquisition_drift_level = str(
        ((inquisition_surface.get("current_integrity_state", {}) or {}).get("drift_level", "UNKNOWN"))
    )
    if inquisition_drift_level.upper() == "UNKNOWN":
        inquisition_drift_level = str(semantic_constitution.get("canon_drift_risk", "UNKNOWN"))

    open_heresy_count = len([x for x in inquisition_alerts if "OPEN" in str((x or {}).get("status", "")).upper()])
    unresolved_review_cases = open_heresy_count
    owner_gate_pending = "PENDING" in str(owner_gates.get("gate_d", "")).upper() or "NEXT" in str(owner_gates.get("gate_d", "")).upper()
    custodes_lock_mode = str(custodes_surface.get("foundation_lock_mode", "UNKNOWN"))
    custodes_vigilance = str(custodes_surface.get("vigilance_state", "UNKNOWN"))
    custodes_threat_reasons = list((custodes_surface.get("threat_reasons", []) or []))

    return {
        "state_id": "imperium_parallel_channels_v1",
        "truth_class": "DERIVED_CANONICAL",
        "evolution": {
            "surface_id": str(evolution_surface.get("surface_id", "IMPERIUM_EVOLUTION_STATE_SURFACE_V1")),
            "version": str(evolution_surface.get("version", "")),
            "status": str(evolution_surface.get("status", "UNKNOWN")),
            "current_mode": str((evolution_surface.get("channel_mode", {}) or {}).get("default", "UNKNOWN")),
            "resource_profile": str((evolution_surface.get("channel_mode", {}) or {}).get("resource_profile", "UNKNOWN")),
            "active_fronts_count": len(evolution_stage_map),
            "insight_candidates_count": len(evolution_insights),
            "owner_approval_queue_count": len(evolution_owner_queue),
            "accepted_transfer_gains_count": len(accepted_gains),
            "health": evolution_health,
            "stage_map": evolution_stage_map,
            "insight_candidates": evolution_insights,
            "owner_approval_queue": evolution_owner_queue,
            "accepted_transfer_gains": accepted_gains,
            "target_focus": str(post_wave_stage.get("active_tranche", "UNKNOWN")),
            "source_path": DEFAULT_IMPERIUM_EVOLUTION_SURFACE_PATH,
            "source_class": "SOURCE_EXACT" if evolution_surface else "NOT_YET_IMPLEMENTED",
        },
        "inquisition": {
            "surface_id": str(inquisition_surface.get("surface_id", "IMPERIUM_INQUISITION_STATE_SURFACE_V1")),
            "version": str(inquisition_surface.get("version", "")),
            "status": str(inquisition_surface.get("status", "UNKNOWN")),
            "current_mode": str((inquisition_surface.get("channel_mode", {}) or {}).get("default", "UNKNOWN")),
            "drift_level": inquisition_drift_level,
            "canon_integrity": str(inquisition_integrity_state.get("canon_integrity", "UNKNOWN")),
            "current_integrity_state": inquisition_integrity_state,
            "last_verified_sectors": list(inquisition_integrity_state.get("last_verified_sectors", []) or []),
            "active_heresy_alerts_count": open_heresy_count,
            "unresolved_review_cases_count": unresolved_review_cases,
            "heresy_classes_count": len(inquisition_classes),
            "owner_review_required": bool(inquisition_holding.get("owner_review_required", True)),
            "auto_delete_allowed": not bool(inquisition_holding.get("policy", "").upper() == "NO_AUTO_DELETE"),
            "active_heresy_alerts": inquisition_alerts,
            "heresy_classes": inquisition_classes,
            "exterminatus_candidates": list((inquisition_surface.get("exterminatus_candidates", []) or [])),
            "source_path": DEFAULT_IMPERIUM_INQUISITION_SURFACE_PATH,
            "source_class": "SOURCE_EXACT" if inquisition_surface else "NOT_YET_IMPLEMENTED",
        },
        "custodes": {
            "surface_id": str(custodes_surface.get("surface_id", "IMPERIUM_ADEPTUS_CUSTODES_STATE_SURFACE_V1")),
            "status": str(custodes_surface.get("status", "UNKNOWN")),
            "vigilance_state": custodes_vigilance,
            "foundation_lock_mode": custodes_lock_mode,
            "owner_ack_required": bool(custodes_surface.get("owner_ack_required", False)),
            "threat_reasons": custodes_threat_reasons,
            "guardian_scope": list((custodes_surface.get("guardian_scope", []) or [])),
            "source_path": DEFAULT_IMPERIUM_CUSTODES_SURFACE_PATH,
            "source_class": "SOURCE_EXACT" if custodes_surface else "NOT_YET_IMPLEMENTED",
        },
        "mechanicus": {
            "surface_id": str(mechanicus_surface.get("surface_id", "IMPERIUM_ADEPTUS_MECHANICUS_STATE_SURFACE_V1")),
            "status": str(mechanicus_surface.get("status", "UNKNOWN")),
            "role": str(mechanicus_surface.get("role", "HEART_OF_CODE_ARCHITECTURE_EXECUTION_CAPACITY")),
            "readiness_score": int(mechanicus_surface.get("readiness_score", 0) or 0),
            "large_step_readiness": str(mechanicus_surface.get("large_step_readiness", "UNKNOWN")),
            "stop_reasons": list(mechanicus_surface.get("stop_reasons", []) or []),
            "code_bank_status": str(mechanicus_surface.get("code_bank_status", "UNKNOWN")),
            "repo_hygiene_verdict": str(mechanicus_surface.get("repo_hygiene_verdict", "UNKNOWN")),
            "source_path": DEFAULT_IMPERIUM_MECHANICUS_SURFACE_PATH,
            "source_class": "SOURCE_EXACT" if mechanicus_surface else "NOT_YET_IMPLEMENTED",
        },
        "administratum": {
            "surface_id": str(administratum_surface.get("surface_id", "IMPERIUM_ADMINISTRATUM_STATE_SURFACE_V1")),
            "status": str(administratum_surface.get("status", "UNKNOWN")),
            "role": str(administratum_surface.get("role", "OWNER_INTENT_TO_EXECUTION_CONTRACT_NORMALIZATION")),
            "gate_state": str(administratum_surface.get("gate_state", "UNKNOWN")),
            "active_contract_id": str(administratum_surface.get("active_contract_id", "UNKNOWN")),
            "missing_required_fields": list(administratum_surface.get("missing_required_fields", []) or []),
            "unknowns_count": int(administratum_surface.get("unknowns_count", 0) or 0),
            "assumptions_count": int(administratum_surface.get("assumptions_count", 0) or 0),
            "owner_ack_required": bool(administratum_surface.get("owner_ack_required", False)),
            "source_path": DEFAULT_IMPERIUM_ADMINISTRATUM_SURFACE_PATH,
            "source_class": "SOURCE_EXACT" if administratum_surface else "NOT_YET_IMPLEMENTED",
        },
        "force": {
            "surface_id": str(force_surface.get("surface_id", "IMPERIUM_FORCE_DOCTRINE_SURFACE_V1")),
            "status": str(force_surface.get("status", "UNKNOWN")),
            "readiness_band": str(force_surface.get("readiness_band", "UNKNOWN")),
            "bottlenecks": list(force_surface.get("bottlenecks", []) or []),
            "organ_strength_count": int(force_surface.get("organ_strength_count", 0) or 0),
            "mission_cost_context": dict(force_surface.get("mission_cost_context", {}) or {}),
            "contract_gate_state": str(force_surface.get("contract_gate_state", "UNKNOWN")),
            "mechanicus_large_step_readiness": str(force_surface.get("mechanicus_large_step_readiness", "UNKNOWN")),
            "source_path": DEFAULT_IMPERIUM_FORCE_DOCTRINE_SURFACE_PATH,
            "source_class": "SOURCE_EXACT" if force_surface else "NOT_YET_IMPLEMENTED",
        },
        "palace_archive": {
            "surface_id": str(palace_archive_surface.get("surface_id", "IMPERIUM_PALACE_AND_ARCHIVE_STATE_SURFACE_V1")),
            "status": str(palace_archive_surface.get("status", "UNKNOWN")),
            "storage_posture": str(palace_archive_surface.get("storage_posture", "UNKNOWN")),
            "throne_authority_status": str(palace_archive_surface.get("throne_authority_status", "UNKNOWN")),
            "palace_state": dict(palace_archive_surface.get("palace_state", {}) or {}),
            "archive_resurrection_state": dict(palace_archive_surface.get("archive_resurrection_state", {}) or {}),
            "node_prep_state": dict(palace_archive_surface.get("node_prep_state", {}) or {}),
            "source_path": DEFAULT_IMPERIUM_PALACE_ARCHIVE_SURFACE_PATH,
            "source_class": "SOURCE_EXACT" if palace_archive_surface else "NOT_YET_IMPLEMENTED",
        },
        "control_gates": {
            "surface_id": str(control_gates_surface.get("surface_id", "IMPERIUM_CONTROL_GATES_SURFACE_V1")),
            "status": str(control_gates_surface.get("status", "UNKNOWN")),
            "gate_summary": str(control_gates_surface.get("gate_summary", "UNKNOWN")),
            "blocked_count": int(control_gates_surface.get("blocked_count", 0) or 0),
            "warning_count": int(control_gates_surface.get("warning_count", 0) or 0),
            "gates": list(control_gates_surface.get("gates", []) or []),
            "source_path": DEFAULT_IMPERIUM_CONTROL_GATES_SURFACE_PATH,
            "source_class": "SOURCE_EXACT" if control_gates_surface else "NOT_YET_IMPLEMENTED",
        },
        "factory": {
            "surface_id": str(factory_surface.get("surface_id", "IMPERIUM_FACTORY_PRODUCTION_STATE_V1")),
            "version": str(factory_surface.get("version", "")),
            "status": str(factory_surface.get("status", "UNKNOWN")),
            "factory_name": str(((factory_surface.get("factory_identity", {}) or {}).get("name", "Factory of Imperium"))),
            "vector_state": str(((factory_surface.get("factory_identity", {}) or {}).get("vector_state", "UNKNOWN"))),
            "products_count": len(factory_products),
            "production_stages": list((factory_surface.get("production_stages", []) or [])),
            "factory_morphology_profile": factory_morphology_profile,
            "conveyor_lanes": conveyor_lanes,
            "stage_transition_matrix": stage_transition_matrix,
            "stage_gates": stage_gates,
            "quality_checkpoints": quality_checkpoints,
            "living_flow_relations": living_flow_relations,
            "products": factory_products,
            "product_evolution_lines": product_lines,
            "tiktok_current_point": str(next((x.get("current_point") for x in product_lines if str(x.get("product_id", "")) == "tiktok_agent_platform"), "UNKNOWN")),
            "tiktok_target_point": str(next((x.get("target_point") for x in product_lines if str(x.get("product_id", "")) == "tiktok_agent_platform"), "UNKNOWN")),
            "tiktok_ascent_track": tiktok_ascent_track,
            "tiktok_ascent_lane": tiktok_ascent_lane,
            "tiktok_assembly_corridors": tiktok_assembly_corridors,
            "tiktok_live_flow_markers": tiktok_live_flow_markers,
            "runtime_process_state": str(semantic_product.get("runtime_process_state", "UNKNOWN")),
            "runtime_recovery_signal": str(semantic_product.get("runtime_recovery_signal", "none")),
            "owner_gate_pending": owner_gate_pending,
            "sovereignty_posture": str(semantic_security.get("sovereignty_posture", "UNKNOWN")),
            "source_path": DEFAULT_IMPERIUM_FACTORY_PRODUCTION_SURFACE_PATH,
            "source_class": "SOURCE_EXACT" if factory_surface else "NOT_YET_IMPLEMENTED",
            "product_map_source_path": DEFAULT_IMPERIUM_PRODUCT_EVOLUTION_MAP_PATH,
            "product_map_version": str(product_map_surface.get("version", "")),
            "product_map_source_class": "SOURCE_EXACT" if product_map_surface else "NOT_YET_IMPLEMENTED",
        },
    }


def sort_events_latest(events: list[dict]) -> list[dict]:
    return sorted(events, key=lambda item: parse_utc(str(item.get("occurred_at_utc", ""))), reverse=True)


def infer_route_node_from_source(source_path: str, default_node: str) -> str:
    key = str(source_path or "").lower()
    if not key:
        return default_node
    if "verification" in key or "validation" in key or "constitution" in key:
        return "verification_department"
    if "release" in key or "bundle_report" in key or "export" in key:
        return "release_integration_department"
    if "growth" in key or "distribution" in key or "campaign" in key:
        return "growth_distribution_department"
    if "engineering" in key or "web/" in key or "app/" in key or "shared_systems/" in key:
        return "engineering_department"
    if "tooling" in key or "infrastructure" in key:
        return "tooling_infrastructure_department"
    if "research" in key or "intelligence" in key:
        return "product_intelligence_research_department"
    if "analytics" in key or "tiktok_wave1_" in key or "status_surface" in key:
        return "analytics_department"
    return default_node


def pick_latest_event(events: list[dict], predicate) -> dict:
    for item in sort_events_latest(events):
        try:
            if predicate(item):
                return item
        except Exception:
            continue
    return {}


def build_live_signature(live_payload: dict) -> str:
    feed = sort_events_latest(list(live_payload.get("live_change_feed", [])))
    top = feed[0] if feed else {}
    gate = dict(live_payload.get("live_gate_state", {}))
    ctr = dict(live_payload.get("live_contradiction_state", {}))
    parts = [
        str(top.get("event_id", "")),
        str(top.get("occurred_at_utc", "")),
        str(live_payload.get("selected_option", "")),
        str(live_payload.get("wave_lane_status", "")),
        str(live_payload.get("active_tranche_id", "")),
        str(gate.get("status", "")),
        str(gate.get("pending_gate_markers", "")),
        str(ctr.get("open_count", "")),
        str(live_payload.get("growth_distribution_status", "")),
        str(((live_payload.get("live_preview_meta", {}) or {}).get("latest_diff_manifest_path", ""))),
        str(((live_payload.get("live_operation_heartbeat", {}) or {}).get("diff_preview_changed_sectors", ""))),
        str(((live_payload.get("live_event_flow_state", {}) or {}).get("latest_event", {}) or {}).get("event_id", "")),
    ]
    return "|".join(parts)


def build_live_tick_payload(
    repo_root: Path,
    state: dict,
    *,
    event_log_path_value: str,
) -> dict:
    live = build_live_state(
        repo_root=repo_root,
        state=state,
        persist_snapshot=False,
        snapshot_path_value=str(state.get("_live_snapshot_path", DEFAULT_LIVE_STATE_SNAPSHOT_PATH)),
        event_log_path_value=event_log_path_value,
    )
    signature = build_live_signature(live)
    return {
        "type": "live_tick",
        "emitted_at_utc": utc_now_iso(),
        "transport": "SSE_EVENTSOURCE_LOCALHOST",
        "signature": signature,
        "truth_class": "DERIVED_CANONICAL",
        "live_event_bus_status": "NOT_YET_IMPLEMENTED",
        "live": live,
        "state_excerpt": {
            "bundle_path": state.get("bundle_path"),
            "bundle_name": state.get("bundle_name"),
            "bundle_binding": state.get("bundle_binding", {}),
            "source_disclosure": state.get("source_disclosure", {}),
        },
    }


def gather_recent_file_changes(repo_root: Path, limit: int = 12) -> list[dict]:
    patterns = [
        "docs/review_artifacts/TIKTOK_AGENT_*.md",
        "docs/review_artifacts/LIVE_*_V1.md",
        "docs/review_artifacts/LIVE_*_V1.json",
        "shared_systems/factory_observation_window_v1/web/*",
        "shared_systems/factory_observation_window_v1/app/*.py",
        "runtime/repo_control_center/*.json",
    ]
    files: list[Path] = []
    seen: set[str] = set()
    for pattern in patterns:
        for path in repo_root.glob(pattern):
            if not path.is_file():
                continue
            key = str(path.resolve())
            if key in seen:
                continue
            seen.add(key)
            files.append(path)
    files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    results: list[dict] = []
    for idx, path in enumerate(files[:limit], start=1):
        rel = normalize_rel(str(path.relative_to(repo_root)))
        event_type = "task_completed"
        if rel.startswith("runtime/repo_control_center/"):
            event_type = "verification_changed"
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            event_type = "preview_updated"
        results.append(
            {
                "event_id": f"live_evt_{idx}",
                "event_type": event_type,
                "occurred_at_utc": file_mtime_iso(path),
                "severity": "info",
                "source_path": rel,
                "summary": f"source updated: {path.name}",
                "truth_class": "SOURCE_EXACT",
            }
        )
    return results


def load_jsonl_live_events(repo_root: Path, log_path_value: str, limit: int = 32) -> tuple[list[dict], dict]:
    path = resolve_path(repo_root, log_path_value)
    rel_or_raw = str(path)
    try:
        rel_or_raw = normalize_rel(str(path.relative_to(repo_root)))
    except ValueError:
        rel_or_raw = str(path)
    meta = {
        "path": rel_or_raw,
        "exists": path.exists(),
        "loaded": False,
        "count": 0,
        "source": "jsonl_log",
    }
    if not path.exists() or not path.is_file():
        meta["reason"] = "not_found"
        return [], meta

    events: list[dict] = []
    try:
        with path.open("r", encoding="utf-8") as fh:
            for idx, raw in enumerate(fh, start=1):
                line = raw.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(payload, dict):
                    continue
                events.append(
                    {
                        "event_id": str(payload.get("event_id", f"log_evt_{idx}")).strip() or f"log_evt_{idx}",
                        "event_type": str(payload.get("event_type", "event")).strip() or "event",
                        "occurred_at_utc": str(payload.get("occurred_at_utc", utc_now_iso())).strip() or utc_now_iso(),
                        "severity": str(payload.get("severity", "info")).strip() or "info",
                        "source_path": normalize_rel(str(payload.get("source_path", "")).strip()),
                        "summary": str(payload.get("summary", "live event")).strip() or "live event",
                        "truth_class": str(payload.get("truth_class", "SOURCE_EXACT")).strip() or "SOURCE_EXACT",
                    }
                )
    except OSError:
        meta["reason"] = "read_error"
        return [], meta

    if not events:
        meta["reason"] = "no_events"
        return [], meta

    meta["loaded"] = True
    meta["count"] = len(events[-limit:])
    return events[-limit:], meta


def persist_live_snapshot(repo_root: Path, snapshot_path_value: str, payload: dict) -> dict:
    path = resolve_path(repo_root, snapshot_path_value)
    rel_or_raw = str(path)
    try:
        rel_or_raw = normalize_rel(str(path.relative_to(repo_root)))
    except ValueError:
        rel_or_raw = str(path)
    result = {
        "enabled": True,
        "path": rel_or_raw,
        "written": False,
        "written_at_utc": utc_now_iso(),
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        result["written"] = True
    except OSError as exc:
        result["error"] = str(exc)
    return result


def gather_visual_audit_runs(repo_root: Path, limit: int = 6) -> list[dict]:
    root = resolve_path(repo_root, DEFAULT_VISUAL_EVIDENCE_ROOT)
    if not root.exists():
        return []
    dirs = [p for p in root.glob("imperial_dashboard_visual_audit_loop_*") if p.is_dir()]
    dirs.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    rows: list[dict] = []
    for path in dirs[:limit]:
        capture_meta_path = path / "capture_meta.json"
        capture_meta = load_json_file_if_exists(capture_meta_path)
        run_id = str(capture_meta.get("run_id") or path.name.replace("imperial_dashboard_visual_audit_loop_", ""))
        modes = capture_meta.get("modes", []) if isinstance(capture_meta.get("modes"), list) else []
        fullvision_zones = 0
        command_zones = 0
        for mode in modes:
            if not isinstance(mode, dict):
                continue
            if str(mode.get("mode", "")).lower() == "fullvision":
                fullvision_zones = len(mode.get("zones", []) or [])
            if str(mode.get("mode", "")).lower() == "command":
                command_zones = len(mode.get("zones", []) or [])
        rows.append(
            {
                "run_id": run_id,
                "path": rel_or_abs(path, repo_root),
                "updated_at_utc": file_mtime_iso(path),
                "capture_meta_path": rel_or_abs(capture_meta_path, repo_root),
                "fullvision_zone_count": fullvision_zones,
                "command_zone_count": command_zones,
                "truth_class": "SOURCE_EXACT",
            }
        )
    return rows


def gather_diff_preview_packs(repo_root: Path, limit: int = 6) -> list[dict]:
    root = resolve_path(repo_root, DEFAULT_VISUAL_EVIDENCE_ROOT)
    if not root.exists():
        return []
    dirs = [p for p in root.glob("imperium_diff_preview_pack_*") if p.is_dir()]
    dirs.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    packs: list[dict] = []
    for path in dirs[:limit]:
        manifest_path = path / "diff_manifest.json"
        manifest = load_json_file_if_exists(manifest_path)
        if not manifest:
            continue
        before_run = str(manifest.get("before_run_id", "unknown"))
        after_run = str(manifest.get("after_run_id", "unknown"))
        changed = int(manifest.get("changed_count", 0) or 0)
        compared = int(manifest.get("compared_count", 0) or 0)
        contact_sheet_html = str(manifest.get("contact_sheet_html", ""))
        packs.append(
            {
                "pack_id": str(manifest.get("pack_id", path.name)),
                "path": rel_or_abs(path, repo_root),
                "updated_at_utc": file_mtime_iso(path),
                "before_run_id": before_run,
                "after_run_id": after_run,
                "changed_count": changed,
                "compared_count": compared,
                "diff_manifest_path": rel_or_abs(manifest_path, repo_root),
                "contact_sheet_html": contact_sheet_html,
                "truth_class": "SOURCE_EXACT",
            }
        )
    return packs


def gather_preview_registry(repo_root: Path, limit: int = 12) -> list[dict]:
    items: list[dict] = []
    diff_packs = gather_diff_preview_packs(repo_root=repo_root, limit=limit)
    visual_runs = gather_visual_audit_runs(repo_root=repo_root, limit=limit)

    for idx, pack in enumerate(diff_packs, start=1):
        items.append(
            {
                "preview_id": f"diff_pack_{idx}",
                "kind": "diff_pack",
                "path": str(pack.get("path", "")),
                "updated_at_utc": str(pack.get("updated_at_utc", "")),
                "related_product": "imperium_dashboard",
                "trust_class": "SOURCE_EXACT",
                "changed_count": int(pack.get("changed_count", 0) or 0),
                "compared_count": int(pack.get("compared_count", 0) or 0),
                "before_run_id": str(pack.get("before_run_id", "")),
                "after_run_id": str(pack.get("after_run_id", "")),
                "diff_manifest_path": str(pack.get("diff_manifest_path", "")),
                "contact_sheet_html": str(pack.get("contact_sheet_html", "")),
            }
        )

    start_idx = len(items)
    for idx, run in enumerate(visual_runs, start=1):
        items.append(
            {
                "preview_id": f"visual_run_{start_idx + idx}",
                "kind": "visual_audit_run",
                "path": str(run.get("path", "")),
                "updated_at_utc": str(run.get("updated_at_utc", "")),
                "related_product": "imperium_dashboard",
                "trust_class": "SOURCE_EXACT",
                "run_id": str(run.get("run_id", "")),
                "fullvision_zone_count": int(run.get("fullvision_zone_count", 0) or 0),
                "command_zone_count": int(run.get("command_zone_count", 0) or 0),
                "capture_meta_path": str(run.get("capture_meta_path", "")),
            }
        )

    # Legacy fallback preview assets from runtime projects.
    patterns = [
        "runtime/projects/**/*.png",
        "runtime/projects/**/*.jpg",
        "runtime/projects/**/*.jpeg",
        "runtime/projects/**/*.webp",
    ]
    files: list[Path] = []
    seen: set[str] = set()
    for pattern in patterns:
        for path in repo_root.glob(pattern):
            if not path.is_file():
                continue
            key = str(path.resolve())
            if key in seen:
                continue
            seen.add(key)
            files.append(path)
    files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    for idx, path in enumerate(files[: max(0, limit - len(items))], start=1):
        rel = normalize_rel(str(path.relative_to(repo_root)))
        items.append(
            {
                "preview_id": f"preview_asset_{idx}",
                "kind": path.suffix.lower().lstrip(".") or "file",
                "path": rel,
                "updated_at_utc": file_mtime_iso(path),
                "related_product": "tiktok_agent_platform",
                "trust_class": "SOURCE_EXACT",
            }
        )
    return items[:limit]


def build_event_flow_state(
    *,
    event_flow_surface: dict,
    live_changes: list[dict],
    preview_registry: list[dict],
) -> dict:
    classes = list((event_flow_surface.get("event_classes", []) or []))
    source_paths = list((event_flow_surface.get("event_sources", []) or []))
    flow_chain = list((event_flow_surface.get("flow_chain", []) or []))
    route_defs = list((event_flow_surface.get("changed_sector_routes", []) or []))
    bloodflow_profile = dict((event_flow_surface.get("living_bloodflow_profile", {}) or {}))
    signal_vessels = list((event_flow_surface.get("signal_vessels", []) or []))
    transition_schema = dict((event_flow_surface.get("transition_markers", {}) or {}))
    class_counts: dict[str, int] = {str(item.get("event_class_id", "")): 0 for item in classes if str(item.get("event_class_id", ""))}
    sector_counts: dict[str, int] = {}
    route_counts: dict[str, int] = {str(item.get("route_id", "")): 0 for item in route_defs if str(item.get("route_id", ""))}
    state_counters = {"active": 0, "waiting": 0, "blocked": 0, "proven": 0}
    event_tail = sort_events_latest(live_changes)[:16]

    def route_sector(node_id: str) -> str:
        normalized = str(node_id or "").strip().lower()
        if normalized in {"analytics_department", "engineering_department", "verification_department", "release_integration_department"}:
            return "factory"
        if normalized in {"growth_distribution_department"}:
            return "owner_queue"
        if normalized in {"tooling_infrastructure_department"}:
            return "dashboard"
        if normalized in {"product_intelligence_research_department"}:
            return "evolution"
        return "dashboard"

    def classify_event_class(item: dict) -> str:
        event_type = str((item or {}).get("event_type", "")).upper()
        summary = str((item or {}).get("summary", "")).lower()
        if "HERESY_CASE" in event_type or "heresy" in summary:
            return "HERESY_CASE"
        if "INQUISITION" in event_type or "contradiction" in summary or "drift" in summary:
            return "INQUISITION_ALERT"
        if "EVOLUTION" in event_type or "insight" in summary or "candidate" in summary:
            return "EVOLUTION_SIGNAL"
        if "CONTINUITY" in event_type or "mutable_tracker" in summary or "ladder" in summary:
            return "CONTINUITY_UPDATE"
        if "PREVIEW" in event_type or "DIFF" in event_type or "preview" in summary or "diff" in summary:
            return "DIFF_PREVIEW_TRIGGER"
        if "RUNTIME" in event_type or "FACTORY" in event_type or "stage" in summary or "assembly" in summary:
            return "FACTORY_STAGE_TRANSITION"
        if "TASK_COMPLETED" in event_type or "STEP" in event_type or "bundle_checkpoint" in event_type or "checkpoint" in summary:
            return "STEP_TRANSITION"
        return "DASHBOARD_REFRESH_TRIGGER"

    def classify_target_sector(event_class: str) -> str:
        if event_class in {"INQUISITION_ALERT", "HERESY_CASE"}:
            return "inquisition"
        if event_class == "EVOLUTION_SIGNAL":
            return "evolution"
        if event_class == "DIFF_PREVIEW_TRIGGER":
            return "owner_review"
        if event_class in {"STEP_TRANSITION", "CONTINUITY_UPDATE"}:
            return "owner_queue"
        return "dashboard"

    def classify_state_bucket(item: dict, event_class: str) -> str:
        summary = str((item or {}).get("summary", "")).lower()
        severity = str((item or {}).get("severity", "")).lower()
        event_type = str((item or {}).get("event_type", "")).lower()
        if event_class in {"HERESY_CASE"} or "critical" in severity or "block" in summary or "error" in summary:
            return "blocked"
        if "wait" in summary or "pending" in summary:
            return "waiting"
        if "proof" in summary or "validated" in summary or "resolved" in summary or "completed" in summary or event_type == "task_completed":
            return "proven"
        return "active"

    for item in event_tail:
        event_class = classify_event_class(item)
        class_counts[event_class] = class_counts.get(event_class, 0) + 1
        state_key = classify_state_bucket(item, event_class)
        state_counters[state_key] = state_counters.get(state_key, 0) + 1
        node_id = infer_route_node_from_source(str((item or {}).get("source_path", "")), default_node="analytics_department")
        sector_counts[node_id] = sector_counts.get(node_id, 0) + 1
        from_sector = route_sector(node_id)
        to_sector = classify_target_sector(event_class)
        for route in route_defs:
            route_id = str(route.get("route_id", "")).strip()
            if not route_id:
                continue
            if str(route.get("from_sector", "")).strip() == from_sector and str(route.get("to_sector", "")).strip() == to_sector:
                route_counts[route_id] = route_counts.get(route_id, 0) + 1

    latest_event = event_tail[0] if event_tail else {}
    diff_triggers = len([item for item in preview_registry if str(item.get("kind", "")) == "diff_pack"])
    latest_proof = pick_latest_event(
        event_tail,
        lambda item: "proof" in str(item.get("summary", "")).lower()
        or "validated" in str(item.get("summary", "")).lower()
        or str(item.get("event_type", "")).lower() == "task_completed",
    )
    latest_risk = pick_latest_event(
        event_tail,
        lambda item: "risk" in str(item.get("summary", "")).lower()
        or str(item.get("event_type", "")).lower() == "contradiction_opened",
    )
    latest_waiting = pick_latest_event(
        event_tail,
        lambda item: "wait" in str(item.get("summary", "")).lower()
        or "pending" in str(item.get("summary", "")).lower(),
    )
    latest_blocker = pick_latest_event(
        event_tail,
        lambda item: "blocker" in str(item.get("summary", "")).lower()
        or "error" in str(item.get("summary", "")).lower()
        or str(item.get("event_type", "")).lower() == "blocker_detected",
    )
    owner_review_trigger_count = (
        class_counts.get("HERESY_CASE", 0)
        + class_counts.get("INQUISITION_ALERT", 0)
        + class_counts.get("CONTINUITY_UPDATE", 0)
    )
    flow_chain_states: list[dict] = []
    for step in flow_chain:
        step_id = str(step.get("step_id", "")).strip()
        default_state = str(step.get("default_state", "WAIT")).strip().upper() or "WAIT"
        dynamic_state = default_state
        if step_id == "event_capture":
            dynamic_state = "ACTIVE" if event_tail else "WAIT"
        elif step_id == "assessment":
            dynamic_state = "ACTIVE" if sum(class_counts.values()) > 0 else "WAIT"
        elif step_id == "case_or_insight":
            if class_counts.get("HERESY_CASE", 0) + class_counts.get("INQUISITION_ALERT", 0) + class_counts.get("EVOLUTION_SIGNAL", 0) > 0:
                dynamic_state = "ACTIVE"
            elif default_state == "PARTIALLY_IMPLEMENTED":
                dynamic_state = "PARTIALLY_IMPLEMENTED"
            else:
                dynamic_state = "WAIT"
        elif step_id == "stage_movement":
            dynamic_state = "ACTIVE" if class_counts.get("FACTORY_STAGE_TRANSITION", 0) + class_counts.get("STEP_TRANSITION", 0) > 0 else "WAIT"
        elif step_id == "owner_review":
            if state_counters.get("blocked", 0) > 0:
                dynamic_state = "BLOCKED"
            elif owner_review_trigger_count > 0:
                dynamic_state = "ACTIVE"
            else:
                dynamic_state = "WAIT"
        flow_chain_states.append(
            {
                **dict(step),
                "state": dynamic_state,
            }
        )

    changed_sector_routes: list[dict] = []
    for route in route_defs:
        route_id = str(route.get("route_id", "")).strip()
        hits = route_counts.get(route_id, 0)
        status = str(route.get("default_state", "WAIT"))
        if hits > 0:
            if state_counters.get("blocked", 0) > 0 and route_id in {"factory_to_inquisition", "inquisition_to_owner_queue"}:
                status = "BLOCKED"
            elif state_counters.get("proven", 0) > 0 and route_id in {"factory_to_dashboard", "factory_to_evolution"}:
                status = "PROVEN"
            else:
                status = "ACTIVE"
        changed_sector_routes.append(
            {
                **dict(route),
                "event_count": hits,
                "status": status,
            }
        )

    vessel_states: list[dict] = []
    for vessel in signal_vessels:
        trigger_classes = list((vessel.get("route_sequence", []) or []))
        hits = sum(class_counts.get(str(item), 0) for item in trigger_classes)
        status = str(vessel.get("status", "WAIT"))
        if hits > 0:
            if state_counters.get("blocked", 0) > 0 and any(item in {"HERESY_CASE", "INQUISITION_ALERT"} for item in trigger_classes):
                status = "BLOCKED"
            elif state_counters.get("proven", 0) > 0 and any(item in {"STEP_TRANSITION", "FACTORY_STAGE_TRANSITION"} for item in trigger_classes):
                status = "PROVEN"
            else:
                status = "ACTIVE"
        vessel_states.append(
            {
                **dict(vessel),
                "event_count": hits,
                "status": status,
            }
        )

    if state_counters.get("blocked", 0) > 0:
        flow_posture = "BLOCKED"
    elif state_counters.get("active", 0) > 0:
        flow_posture = "ACTIVE"
    elif state_counters.get("waiting", 0) > 0:
        flow_posture = "WAIT"
    elif state_counters.get("proven", 0) > 0:
        flow_posture = "PROVEN"
    else:
        flow_posture = "WAIT"

    route_focus = ""
    for route in changed_sector_routes:
        if str((route or {}).get("status", "")).upper() in {"BLOCKED", "ACTIVE", "PROVEN"}:
            route_focus = str(route.get("route_id", ""))
            break

    transition_markers = {
        **transition_schema,
        "latest_event_id": str(latest_event.get("event_id", "")),
        "latest_proof_event_id": str(latest_proof.get("event_id", "")),
        "latest_risk_event_id": str(latest_risk.get("event_id", "")),
        "latest_waiting_event_id": str(latest_waiting.get("event_id", "")),
        "latest_blocker_event_id": str(latest_blocker.get("event_id", "")),
        "active_now": str(latest_event.get("summary", "")) or "no_active_event",
        "waiting_on": str(latest_waiting.get("summary", "")) or "no_waiting_event",
        "blocked_by": str(latest_blocker.get("summary", "")) or "no_blocker",
        "proven_now": str(latest_proof.get("summary", "")) or "no_proof_event",
        "route_focus": route_focus,
    }

    return {
        "surface_id": str(event_flow_surface.get("surface_id", "IMPERIUM_EVENT_FLOW_SPINE_SURFACE_V1")),
        "version": str(event_flow_surface.get("version", "")),
        "status": str(event_flow_surface.get("status", "UNKNOWN")),
        "channel_profile": dict(event_flow_surface.get("channel_profile", {}) or {}),
        "living_bloodflow_profile": bloodflow_profile,
        "event_classes": classes,
        "event_sources": source_paths,
        "class_counts": class_counts,
        "sector_counts": sector_counts,
        "flow_chain": flow_chain,
        "flow_chain_states": flow_chain_states,
        "changed_sector_routes": changed_sector_routes,
        "signal_vessels": vessel_states,
        "state_counters": state_counters,
        "flow_posture": flow_posture,
        "owner_review_trigger_count": owner_review_trigger_count,
        "transition_markers": transition_markers,
        "latest_event": latest_event,
        "event_tail": event_tail,
        "diff_preview_trigger_count": diff_triggers,
        "active_signal_summary": (
            f"active={state_counters.get('active', 0)};"
            f"waiting={state_counters.get('waiting', 0)};"
            f"blocked={state_counters.get('blocked', 0)};"
            f"proven={state_counters.get('proven', 0)}"
        ),
        "known_gaps": list((event_flow_surface.get("known_gaps", []) or [])),
        "truth_class": str(event_flow_surface.get("truth_class", "DERIVED_CANONICAL")),
    }


def build_diff_preview_state(
    *,
    repo_root: Path,
    pipeline_surface: dict,
    preview_registry: list[dict],
) -> dict:
    diff_packs = [item for item in preview_registry if str(item.get("kind", "")) == "diff_pack"]
    latest_pack = diff_packs[0] if diff_packs else {}
    latest_pack_path = str(latest_pack.get("path", "")).strip()
    latest_manifest_path = str(latest_pack.get("diff_manifest_path", "")).strip()
    manifest_payload = load_json_file_if_exists(resolve_path(repo_root, latest_manifest_path)) if latest_manifest_path else {}
    return {
        "surface_id": str(pipeline_surface.get("surface_id", "IMPERIUM_DIFF_PREVIEW_PIPELINE_SURFACE_V1")),
        "version": str(pipeline_surface.get("version", "")),
        "status": str(pipeline_surface.get("status", "UNKNOWN")),
        "pipeline_profile": dict(pipeline_surface.get("pipeline_profile", {}) or {}),
        "stages": list(pipeline_surface.get("stages", []) or []),
        "entrypoints": dict(pipeline_surface.get("entrypoints", {}) or {}),
        "latest_diff_pack_path": latest_pack_path,
        "latest_diff_manifest_path": latest_manifest_path,
        "latest_contact_sheet_html": str(latest_pack.get("contact_sheet_html", "")),
        "latest_before_run_id": str(latest_pack.get("before_run_id", "")),
        "latest_after_run_id": str(latest_pack.get("after_run_id", "")),
        "changed_count": int(manifest_payload.get("changed_count", latest_pack.get("changed_count", 0)) or 0),
        "compared_count": int(manifest_payload.get("compared_count", latest_pack.get("compared_count", 0)) or 0),
        "missing_count": int(manifest_payload.get("missing_count", 0) or 0),
        "known_gaps": list((pipeline_surface.get("known_gaps", []) or [])),
        "truth_class": str(pipeline_surface.get("truth_class", "DERIVED_CANONICAL")),
    }


def build_golden_throne_discoverability_state(*, repo_root: Path, surface: dict) -> dict:
    primary_paths = list((surface.get("primary_surrogate_paths", []) or surface.get("surrogate_paths", []) or []))
    mapped: list[dict] = []
    existing_count = 0

    pre_mapped = list((surface.get("mapped_paths", []) or []))
    if pre_mapped:
        for item in pre_mapped:
            path_value = str((item or {}).get("path", "")).strip()
            if not path_value:
                continue
            has_explicit_exists = isinstance(item, dict) and ("exists" in item)
            exists = bool(item.get("exists")) if has_explicit_exists else source_path_exists(repo_root, path_value)
            if exists:
                existing_count += 1
            mapped.append({"path": path_value, "exists": exists})
    else:
        for path_value in primary_paths:
            exists = source_path_exists(repo_root, str(path_value))
            if exists:
                existing_count += 1
            mapped.append({"path": str(path_value), "exists": exists})
    dedicated_named_bundle_exists = bool(surface.get("dedicated_named_bundle_exists", False))
    if dedicated_named_bundle_exists:
        discoverability_status = "DIRECT"
    elif existing_count > 0:
        discoverability_status = "SURROGATE"
    else:
        discoverability_status = "MISSING"
    return {
        "surface_id": str(surface.get("surface_id", "IMPERIUM_GOLDEN_THRONE_DISCOVERABILITY_SURFACE_V1")),
        "version": str(surface.get("version", "")),
        "status": str(surface.get("status", "UNKNOWN")),
        "discoverability_status": discoverability_status,
        "dedicated_named_bundle_exists": dedicated_named_bundle_exists,
        "mapped_paths": mapped,
        "existing_path_count": existing_count,
        "confirmation_role": str(surface.get("confirmation_role", "machine_imperial_identity_confirmation_surface")),
        "discovery_route": list((surface.get("discovery_route", []) or [])),
        "authority_boundary": dict(
            (surface.get("authority_boundary", {}) or {})
            or {
                "discoverability_is_non_authority_source": True,
                "authority_source_path": DEFAULT_GOLDEN_THRONE_AUTHORITY_ANCHOR_PATH,
                "constitution_rank_is_non_authority_source": True,
            }
        ),
        "truth_boundary": dict((surface.get("truth_boundary", {}) or {})),
        "truth_class": str(surface.get("truth_class", "DERIVED_CANONICAL")),
    }


def build_live_state(
    repo_root: Path,
    state: dict,
    *,
    persist_snapshot: bool = False,
    snapshot_path_value: str = DEFAULT_LIVE_STATE_SNAPSHOT_PATH,
    event_log_path_value: str = DEFAULT_LIVE_EVENT_LOG_PATH,
) -> dict:
    now = utc_now_iso()
    one_screen_path = resolve_path(repo_root, "runtime/repo_control_center/one_screen_status.json")
    constitution_path = resolve_path(repo_root, "runtime/repo_control_center/constitution_status.json")
    gate_doc_path = resolve_path(repo_root, "docs/review_artifacts/TIKTOK_WAVE1_OWNER_GATE_CHECKPOINT_SURFACE_V1.md")
    wave_doc_path = resolve_path(repo_root, "docs/review_artifacts/TIKTOK_WAVE1_STATUS_SURFACE_V1.md")

    one_screen = load_json_file_if_exists(one_screen_path)
    constitution = load_json_file_if_exists(constitution_path)
    live_state_model = load_json_file_if_exists(resolve_path(repo_root, DEFAULT_LIVE_STATE_MODEL_PATH))
    live_event_model = load_json_file_if_exists(resolve_path(repo_root, DEFAULT_LIVE_EVENT_MODEL_PATH))
    canon_sync = state.get("canon_state_sync", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_CANON_STATE_SYNC_PATH)
    )
    canon_truth = extract_canon_truth(canon_sync)
    wave1_control = state.get("wave1_control_surfaces", {}) or load_json_file_if_exists(resolve_path(repo_root, DEFAULT_WAVE1_CONTROL_SURFACES_PATH))
    production_history_seed = state.get("production_history_seed", {}) or {}
    repo_worktree_hygiene = state.get("repo_worktree_hygiene", {}) or collect_repo_worktree_hygiene(repo_root)
    code_bank_state = state.get("imperium_code_bank_state", {}) or build_code_bank_state(
        repo_root,
        load_json_file_if_exists(resolve_path(repo_root, DEFAULT_IMPERIUM_CODE_BANK_SURFACE_PATH)),
    )
    live_work_state = state.get("imperium_live_work_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_LIVE_WORK_VISIBILITY_SURFACE_PATH)
    )
    doctrine_integrity_state = state.get("imperium_doctrine_integrity_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_DOCTRINE_INTEGRITY_SURFACE_PATH)
    )
    truth_spine_state = state.get("imperium_truth_spine_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_TRUTH_SPINE_SURFACE_PATH)
    )
    dashboard_truth_engine_state = state.get("imperium_dashboard_truth_engine_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_DASHBOARD_TRUTH_ENGINE_SURFACE_PATH)
    )
    bundle_truth_chamber_state = state.get("imperium_bundle_truth_chamber_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_BUNDLE_TRUTH_CHAMBER_SURFACE_PATH)
    )
    worktree_purity_gate_state = state.get("imperium_worktree_purity_gate_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_WORKTREE_PURITY_GATE_SURFACE_PATH)
    )
    address_lattice_state = state.get("imperium_address_lattice_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_ADDRESS_LATTICE_SURFACE_PATH)
    )
    anti_lie_model_state = state.get("imperium_anti_lie_model_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_ANTI_LIE_MODEL_SURFACE_PATH)
    )
    live_truth_support_loop_state = state.get("imperium_live_truth_support_loop_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_LIVE_TRUTH_SUPPORT_LOOP_SURFACE_PATH)
    )
    dashboard_coverage_state = state.get("imperium_dashboard_coverage_state", {}) or build_dashboard_coverage_state(
        repo_root,
        load_json_file_if_exists(resolve_path(repo_root, DEFAULT_IMPERIUM_DASHBOARD_COVERAGE_SURFACE_PATH)),
    )
    truth_dominance_state = state.get("imperium_truth_dominance_state", {}) or build_truth_dominance_state(
        repo_root,
        load_json_file_if_exists(resolve_path(repo_root, DEFAULT_IMPERIUM_TRUTH_DOMINANCE_SURFACE_PATH)),
    )
    throne_authority_state = build_throne_authority_state(repo_root)
    system_brain_state = state.get("system_brain_state", {}) or build_system_brain_state(
        repo_root,
        repo_worktree_hygiene=repo_worktree_hygiene,
        code_bank_state=code_bank_state,
        dashboard_coverage_state=dashboard_coverage_state,
        truth_dominance_state=truth_dominance_state,
        throne_authority_state=throne_authority_state,
    )
    custodes_surface = state.get("imperium_custodes_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_CUSTODES_SURFACE_PATH)
    )
    custodes_state = build_custodes_state(
        surface=custodes_surface,
        system_brain_state=system_brain_state,
        coverage_state=dashboard_coverage_state,
        truth_dominance_state=truth_dominance_state,
    )
    system_brain_state["custodes"] = custodes_state
    system_brain_state["throne_authority"] = throne_authority_state
    storage_health_surface = state.get("imperium_storage_health_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_STORAGE_HEALTH_SURFACE_PATH)
    )
    mechanicus_surface = state.get("imperium_mechanicus_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_MECHANICUS_SURFACE_PATH)
    )
    administratum_surface = state.get("imperium_administratum_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_ADMINISTRATUM_SURFACE_PATH)
    )
    force_surface = state.get("imperium_force_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_FORCE_DOCTRINE_SURFACE_PATH)
    )
    palace_archive_surface = state.get("imperium_palace_archive_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_PALACE_ARCHIVE_SURFACE_PATH)
    )
    control_gates_surface = state.get("imperium_control_gates_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_CONTROL_GATES_SURFACE_PATH)
    )
    machine_capability_manifest = state.get("imperium_machine_capability_manifest", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_MACHINE_CAPABILITY_MANIFEST_PATH)
    )
    organ_strength_surface = state.get("imperium_organ_strength_surface", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_ORGAN_STRENGTH_SURFACE_PATH)
    )
    active_mission_contract = state.get("imperium_active_mission_contract", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_ACTIVE_MISSION_CONTRACT_PATH)
    )
    prompt_lineage_state = state.get("prompt_lineage_state", {}) or build_prompt_lineage_state(repo_root)
    tiktok_runtime_state = state.get("tiktok_agent_runtime_observability", {}) or build_tiktok_runtime_observability_state(repo_root)
    runtime_truth_foundation_state = {
        **dict(tiktok_runtime_state or {}),
        "truth_spine_status": str((truth_spine_state or {}).get("status", "UNKNOWN")),
        "dashboard_truth_engine_status": str((dashboard_truth_engine_state or {}).get("status", "UNKNOWN")),
        "bundle_truth_chamber_status": str((bundle_truth_chamber_state or {}).get("status", "UNKNOWN")),
        "worktree_purity_gate_status": str((worktree_purity_gate_state or {}).get("status", "UNKNOWN")),
        "address_lattice_status": str((address_lattice_state or {}).get("status", "UNKNOWN")),
        "anti_lie_model_status": str((anti_lie_model_state or {}).get("status", "UNKNOWN")),
        "live_truth_support_loop_status": str((live_truth_support_loop_state or {}).get("status", "UNKNOWN")),
        "inquisition_truth_guard_status": str((state.get("imperium_inquisition_state", {}) or {}).get("status", "UNKNOWN")),
    }
    mechanicus_state = build_mechanicus_state(
        surface=mechanicus_surface,
        machine_manifest=machine_capability_manifest,
        organ_strength_surface=organ_strength_surface,
        code_bank_state=code_bank_state,
        repo_worktree_hygiene=repo_worktree_hygiene,
    )
    administratum_state = build_administratum_state(
        surface=administratum_surface,
        active_contract=active_mission_contract,
    )
    force_state = build_force_state(
        surface=force_surface,
        machine_manifest=machine_capability_manifest,
        organ_strength_surface=organ_strength_surface,
        administratum_state=administratum_state,
        mechanicus_state=mechanicus_state,
    )
    palace_archive_state = build_palace_archive_state(
        surface=palace_archive_surface,
        storage_health=storage_health_surface,
        throne_authority_state=throne_authority_state,
    )
    control_gates_state = build_control_gates_state(
        surface=control_gates_surface,
        throne_authority_state=throne_authority_state,
        truth_dominance_state=truth_dominance_state,
        dashboard_coverage_state=dashboard_coverage_state,
        evolution_state={},
        runtime_state=runtime_truth_foundation_state,
        administratum_state=administratum_state,
    )
    system_brain_state["mechanicus"] = mechanicus_state
    system_brain_state["administratum"] = administratum_state
    system_brain_state["force"] = force_state
    system_brain_state["palace_archive"] = palace_archive_state
    system_brain_state["control_gates"] = control_gates_state
    semantic_state = state.get("system_semantic_state_surfaces", {}) or build_system_semantic_state_surfaces(
        repo_root=repo_root,
        canon_truth=canon_truth,
        system_brain_state=system_brain_state,
        prompt_lineage_state=prompt_lineage_state,
        tiktok_runtime_state=tiktok_runtime_state,
        wave1_control=wave1_control,
        production_history_seed=production_history_seed,
        semantic_model=load_json_file_if_exists(resolve_path(repo_root, DEFAULT_SYSTEM_SEMANTIC_STATE_MODEL_PATH)),
    )
    evolution_surface = state.get("imperium_evolution_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_EVOLUTION_SURFACE_PATH)
    )
    inquisition_surface = state.get("imperium_inquisition_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_INQUISITION_SURFACE_PATH)
    )
    factory_surface = state.get("imperium_factory_production_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_FACTORY_PRODUCTION_SURFACE_PATH)
    )
    product_map_surface = state.get("imperium_product_evolution_map", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_PRODUCT_EVOLUTION_MAP_PATH)
    )
    event_flow_surface = state.get("imperium_event_flow_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_EVENT_FLOW_SPINE_SURFACE_PATH)
    )
    diff_preview_surface = state.get("imperium_diff_preview_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_DIFF_PREVIEW_PIPELINE_SURFACE_PATH)
    )
    golden_throne_surface = state.get("imperium_golden_throne_discoverability", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_GOLDEN_THRONE_DISCOVERABILITY_SURFACE_PATH)
    )
    true_form_surface = state.get("imperium_true_form_state", {}) or load_json_file_if_exists(
        resolve_path(repo_root, DEFAULT_IMPERIUM_TRUE_FORM_MATRYOSHKA_SURFACE_PATH)
    )
    control_gates_state = build_control_gates_state(
        surface=control_gates_surface,
        throne_authority_state=throne_authority_state,
        truth_dominance_state=truth_dominance_state,
        dashboard_coverage_state=dashboard_coverage_state,
        evolution_state=evolution_surface,
        runtime_state=runtime_truth_foundation_state,
        administratum_state=administratum_state,
    )
    brain_v2_layers = build_brain_v2_layers(
        system_brain_state=system_brain_state,
        throne_authority_state=throne_authority_state,
        custodes_state=custodes_state,
        inquisition_state=inquisition_surface,
        mechanicus_state=mechanicus_state,
        administratum_state=administratum_state,
        force_state=force_state,
        palace_state=palace_archive_state,
        control_gates_state=control_gates_state,
    )
    system_brain_state["brain_v2_layers"] = brain_v2_layers
    parallel_channels = state.get("imperium_parallel_channels", {}) or build_imperium_parallel_channels(
        evolution_surface=evolution_surface,
        inquisition_surface=inquisition_surface,
        custodes_surface=custodes_state,
        mechanicus_surface=mechanicus_state,
        administratum_surface=administratum_state,
        force_surface=force_state,
        palace_archive_surface=palace_archive_state,
        control_gates_surface=control_gates_state,
        factory_surface=factory_surface,
        product_map_surface=product_map_surface,
        canon_truth=canon_truth,
        wave1_control=wave1_control,
        system_semantic_state=semantic_state,
    )

    near_realtime_window_sec = int(
        ((live_state_model.get("cadence_defaults", {}) or {}).get("near_realtime_window_sec", 15))
    )
    owner_gates = (canon_truth.get("owner_gates", {}) or {})
    pending_gate_ids = [k for k, v in owner_gates.items() if "NEXT" in str(v).upper() or "PENDING" in str(v).upper()]
    resolved_gate_ids = [k for k, v in owner_gates.items() if "RESOLVED" in str(v).upper()]
    pending_gates = len(pending_gate_ids)
    wave_count = count_wave_markers(wave_doc_path)
    log_events, log_meta = load_jsonl_live_events(repo_root=repo_root, log_path_value=event_log_path_value, limit=16)
    file_events = gather_recent_file_changes(repo_root=repo_root, limit=12)
    if log_events:
        seen_ids = {str(item.get("event_id", "")) for item in log_events}
        merged_tail = [item for item in file_events if str(item.get("event_id", "")) not in seen_ids]
        live_changes = (log_events + merged_tail)[:16]
    else:
        live_changes = file_events
    runtime_events = []
    for item in tiktok_runtime_state.get("recent_events", []) or []:
        if not isinstance(item, dict):
            continue
        runtime_events.append(
            {
                "event_id": str(item.get("event_id", "")),
                "event_type": str(item.get("event_type", "runtime_activity")),
                "occurred_at_utc": str(item.get("occurred_at_utc", now)),
                "severity": str(item.get("severity", "info")),
                "summary": str(item.get("summary", "")),
                "source_path": str(item.get("source_path", "")),
                "product_id": "tiktok_agent_platform",
                "truth_class": str(item.get("truth_class", "SOURCE_EXACT")),
                "producer": "tiktok_runtime_observability",
            }
        )
    if runtime_events:
        seen = {str(item.get("event_id", "")) for item in live_changes}
        for event in runtime_events:
            if str(event.get("event_id", "")) not in seen:
                live_changes.append(event)
                seen.add(str(event.get("event_id", "")))
    live_changes = sort_events_latest(live_changes)
    preview_registry = gather_preview_registry(repo_root=repo_root, limit=12)
    event_flow_state = build_event_flow_state(
        event_flow_surface=event_flow_surface,
        live_changes=live_changes,
        preview_registry=preview_registry,
    )
    diff_preview_state = build_diff_preview_state(
        repo_root=repo_root,
        pipeline_surface=diff_preview_surface,
        preview_registry=preview_registry,
    )
    golden_throne_discoverability_state = build_golden_throne_discoverability_state(
        repo_root=repo_root,
        surface=golden_throne_surface,
    )
    diff_pack_present = bool(str(diff_preview_state.get("latest_diff_pack_path", "")).strip())
    if diff_pack_present:
        preview_meta_status = "SOURCE_EXACT"
        preview_meta_label = "ACTIVE"
        preview_meta_note = "diff/preview pack is available with before/after manifest and contact sheet"
    elif preview_registry:
        preview_meta_status = "DERIVED_CANONICAL"
        preview_meta_label = "PARTIALLY_IMPLEMENTED"
        preview_meta_note = "preview registry is available; latest diff pack is not generated yet"
    else:
        preview_meta_status = "PLACEHOLDER"
        preview_meta_label = "SCAFFOLDED"
        preview_meta_note = "preview registry is placeholder until capture and diff runs are generated"

    products = state.get("product_lanes", [])
    first_product = products[0] if products else {}
    factory_overview_surface = state.get("factory_overview", {}) or {}
    factory_owner_gate_rows = list((factory_overview_surface.get("owner_gates_waiting", []) or []))
    factory_owner_gate_ids: list[str] = []
    for row in factory_owner_gate_rows:
        if isinstance(row, dict):
            marker = str(row.get("gate_id") or row.get("id") or row.get("gate") or "").strip()
            if marker:
                factory_owner_gate_ids.append(marker)
    if len(factory_owner_gate_rows) > pending_gates:
        pending_gates = len(factory_owner_gate_rows)
    if factory_owner_gate_ids:
        for marker in factory_owner_gate_ids:
            if marker not in pending_gate_ids:
                pending_gate_ids.append(marker)
    if pending_gates > 0 and len(pending_gate_ids) == 0:
        pending_gate_ids = ["factory_owner_gate_waiting"]
    if pending_gates > len(pending_gate_ids):
        pending_gate_ids.append("factory_owner_gate_waiting")
    current_stage = first_product.get("pipeline_stage", "analysis")
    product_id = first_product.get("product_id", "tiktok_agent_platform")
    last_change = live_changes[0] if live_changes else {}
    contradiction_ledger = wave1_control.get("contradiction_ledger", {}) or {}
    contradiction_open_items = contradiction_ledger.get("open", []) or []
    critical_contradictions = len(
        [x for x in contradiction_open_items if str((x or {}).get("severity", "")).lower() in {"critical", "high"}]
    )
    major_contradictions = len(
        [x for x in contradiction_open_items if str((x or {}).get("severity", "")).lower() in {"medium", "low"}]
    )

    throne_status = str(throne_authority_state.get("status", "EMPEROR_STATUS_BLOCKED")).upper()
    if throne_status == "VALID":
        execution_rank = "EMPEROR"
        machine_mode = "emperor"
    else:
        execution_rank = str(
            throne_authority_state.get("detected_rank")
            or one_screen.get("detected_rank")
            or "UNKNOWN"
        )
        machine_mode = str(throne_authority_state.get("machine_mode") or one_screen.get("machine_mode", "unknown"))
    governance_state = str(one_screen.get("governance_acceptance_verdict", "unknown"))
    sync_state = str(one_screen.get("sync_verdict", "unknown"))
    trust_state = str(one_screen.get("trust_verdict", "unknown"))
    admission_state = str(one_screen.get("admission_verdict", "unknown"))
    operator_action_required = parse_bool(one_screen.get("operator_action_required", False), default=False)

    wave_surface = wave1_control.get("wave_status_surface", {}) or {}
    checkpoint_surface = wave1_control.get("owner_gate_checkpoint_surface", {}) or {}
    tranche_surface = wave1_control.get("first_tranche_execution", {}) or {}
    visual_doctrine = (canon_truth.get("visual_doctrine", {}) or {})
    tiktok_truth = (canon_truth.get("tiktok_agent", {}) or {})
    post_wave_stage = (tiktok_truth.get("post_wave1_stage", {}) or {})
    growth_truth = (canon_truth.get("growth_distribution", {}) or {})
    live_layer_truth = (canon_truth.get("live_layer", {}) or {})
    visual_pack = visual_doctrine.get(
        "active_pack", "NEBULA_METALLIC_COMMAND_STYLE_V1"
    )
    selected_option = tiktok_truth.get(
        "selected_option", "UNKNOWN"
    )
    wave_lane_status = tiktok_truth.get(
        "wave_1_status", "UNKNOWN"
    )
    gate_c_status = str(owner_gates.get("gate_c", "UNKNOWN"))
    growth_distribution_status = str(growth_truth.get("department_status", "UNKNOWN"))
    live_layer_front_status = str(live_layer_truth.get("front_status", "UNKNOWN"))
    live_layer_impl_status = str(live_layer_truth.get("implementation_status", "UNKNOWN"))
    canon_field_source_exists = source_path_exists(repo_root, DEFAULT_CANON_STATE_SYNC_PATH)
    selected_option_classification = classify_field_state_with_reason(
        selected_option,
        source_exists=canon_field_source_exists,
        mapped="selected_option" in tiktok_truth,
    )
    wave_lane_classification = classify_field_state_with_reason(
        wave_lane_status,
        source_exists=canon_field_source_exists,
        mapped="wave_1_status" in tiktok_truth,
    )
    gate_c_classification = classify_field_state_with_reason(
        gate_c_status,
        source_exists=canon_field_source_exists,
        mapped="gate_c" in owner_gates,
        owner_decision_pending="PENDING" in gate_c_status.upper(),
    )
    growth_distribution_classification = classify_field_state_with_reason(
        growth_distribution_status,
        source_exists=canon_field_source_exists,
        mapped="department_status" in growth_truth,
    )
    live_layer_front_classification = classify_field_state_with_reason(
        live_layer_front_status,
        source_exists=canon_field_source_exists,
        mapped="front_status" in live_layer_truth,
    )
    live_layer_implementation_classification = classify_field_state_with_reason(
        live_layer_impl_status,
        source_exists=canon_field_source_exists,
        mapped="implementation_status" in live_layer_truth,
    )
    active_department = str(first_product.get("current_department", "analytics_department"))
    active_workset = {}
    for item in tranche_surface.get("active_workset", []) or []:
        if "ACTIVE" in str((item or {}).get("status", "")).upper():
            active_workset = item or {}
            break
    if not active_workset:
        active_workset = (tranche_surface.get("active_workset", []) or [{}])[0] or {}
    product_execution_state = str(first_product.get("execution_state", tranche_surface.get("status", "UNKNOWN")))
    runtime_process_state = str(tiktok_runtime_state.get("process_state", "")).upper()
    if runtime_process_state in {"PROCESSING", "WAIT", "ERROR", "BLOCKED"}:
        process_state = runtime_process_state
    elif "ERROR" in product_execution_state.upper() or critical_contradictions > 0:
        process_state = "ERROR"
    elif "BLOCK" in product_execution_state.upper():
        process_state = "BLOCKED"
    elif "ACTIVE" in product_execution_state.upper() or "IN_PROGRESS" in product_execution_state.upper():
        process_state = "PROCESSING"
    elif "WAIT" in product_execution_state.upper() or "PENDING" in product_execution_state.upper():
        process_state = "WAIT"
    else:
        process_state = "PROCESSING" if str(active_workset.get("work_id", "")).strip() else "WAIT"

    latest_milestone = pick_latest_event(
        live_changes,
        lambda item: str(item.get("event_type", "")).lower()
        in {"wave_started", "wave_completed", "bundle_checkpoint_emitted", "gate_opened", "gate_resolved", "task_completed"},
    )
    latest_proof = pick_latest_event(
        live_changes,
        lambda item: str(item.get("event_type", "")).lower() in {"verification_changed", "task_completed"}
        or "proof" in str(item.get("summary", "")).lower()
        or "validated" in str(item.get("summary", "")).lower(),
    )
    latest_risk = pick_latest_event(
        live_changes,
        lambda item: str(item.get("event_type", "")).lower() in {"contradiction_opened"}
        or "risk" in str(item.get("summary", "")).lower(),
    )
    latest_blocker_event = pick_latest_event(
        live_changes,
        lambda item: str(item.get("event_type", "")).lower() in {"blocker_detected"}
        or "blocker" in str(item.get("summary", "")).lower(),
    )
    if not latest_risk and contradiction_open_items:
        top_ctr = contradiction_open_items[0] or {}
        latest_risk = {
            "event_id": str(top_ctr.get("id", "risk_open_from_contradiction")),
            "event_type": "contradiction_opened",
            "occurred_at_utc": last_change.get("occurred_at_utc", now),
            "severity": str(top_ctr.get("severity", "warning")),
            "summary": str(top_ctr.get("title", "open contradiction risk")),
            "source_path": str((wave1_control.get("truth_links", {}) or {}).get("contradiction_ledger_doc", "")),
            "truth_class": "DERIVED_CANONICAL",
        }
    blocker_node_id = infer_route_node_from_source(
        str(latest_blocker_event.get("source_path", "")),
        default_node=active_department,
    ) if latest_blocker_event else ""
    active_route_node_id = infer_route_node_from_source(
        str(latest_milestone.get("source_path", "")) or str(last_change.get("source_path", "")),
        default_node=active_department,
    )
    latest_changed_node_id = infer_route_node_from_source(
        str(last_change.get("source_path", "")),
        default_node=active_route_node_id,
    )
    runtime_operation_code = str(tiktok_runtime_state.get("current_operation_code", "")).strip()
    runtime_latest_summary = str(tiktok_runtime_state.get("latest_change_summary", "")).strip()
    runtime_failure_reason = str(tiktok_runtime_state.get("failure_reason", "none")).strip() or "none"
    runtime_recovery_signal = str(tiktok_runtime_state.get("recovery_signal", "none")).strip() or "none"
    tiktok_line = next(
        (
            line
            for line in (product_map_surface.get("lines", []) or [])
            if str((line or {}).get("product_id", "")).strip().lower() == "tiktok_agent_platform"
        ),
        {},
    )
    tiktok_ascent_track = dict((tiktok_line.get("ascent_track", {}) or {}))
    tiktok_ascent_status = str(tiktok_ascent_track.get("activation_status", "WAIT"))
    tiktok_ascent_boundary = str(tiktok_ascent_track.get("activation_boundary", "release_readiness_proof_required"))
    tiktok_ascent_future = str(tiktok_line.get("target_point", "VOICE_OF_IMPERIUM_ADVERTISING_DEPARTMENT"))

    history_nodes = list((production_history_seed.get("nodes", []) or []))
    history_times = [parse_utc(str(item.get("occurred_at_utc", ""))) for item in history_nodes if str(item.get("occurred_at_utc", "")).strip()]
    history_times = [value for value in history_times if value > datetime.fromtimestamp(0, tz=timezone.utc)]
    system_started_at = min(history_times).isoformat() if history_times else ""
    system_age_minutes = human_age_minutes(system_started_at)
    regime_started_at = str(post_wave_stage.get("started_at_utc", "")).strip()
    regime_age_minutes = human_age_minutes(regime_started_at)
    one_screen_generated_at = str((system_brain_state.get("one_screen", {}) or {}).get("generated_at", ""))
    one_screen_sync = str((system_brain_state.get("one_screen", {}) or {}).get("sync_verdict", "UNKNOWN"))
    one_screen_trust = str((system_brain_state.get("one_screen", {}) or {}).get("trust_verdict", "UNKNOWN"))
    repo_control_generated_at = str((system_brain_state.get("repo_control", {}) or {}).get("generated_at", ""))
    repo_control_health = str((system_brain_state.get("repo_control", {}) or {}).get("repo_health", "UNKNOWN"))
    last_stable_point_at = ""
    if one_screen_generated_at and one_screen_sync.upper() == "IN_SYNC" and one_screen_trust.upper() in {"TRUSTED", "PASS"}:
        last_stable_point_at = one_screen_generated_at
    elif repo_control_generated_at and repo_control_health.upper() == "PASS":
        last_stable_point_at = repo_control_generated_at
    last_stable_point_age_minutes = human_age_minutes(last_stable_point_at)
    owner_decision_triggers: list[str] = []
    if pending_gates > 0:
        owner_decision_triggers.append("pending_owner_gate_checkpoint")
    if critical_contradictions > 0:
        owner_decision_triggers.append("critical_contradiction_open")
    if parse_bool((system_brain_state.get("limits", {}) or {}).get("operator_action_required"), False):
        owner_decision_triggers.append("operator_action_required")
    if str(checkpoint_surface.get("next_checkpoint", "")).strip():
        owner_decision_triggers.append("checkpoint_transition_review")
    owner_decision_triggers = list(dict.fromkeys(owner_decision_triggers))

    semantic_constitution = dict(semantic_state.get("constitution_state", {}) or {})
    semantic_brain = dict(semantic_state.get("brain_reason_control_state", {}) or {})
    semantic_memory = dict(semantic_state.get("memory_chronology_knowledge_state", {}) or {})
    semantic_product = dict(semantic_state.get("product_state_integration", {}) or {})
    semantic_security = dict(semantic_state.get("security_sovereignty_posture_state", {}) or {})
    semantic_truth = dict(semantic_state.get("exact_derived_gap_disclosure", {}) or {})
    semantic_memory["age_axis"] = {
        **dict(semantic_memory.get("age_axis", {}) or {}),
        "system_started_at_utc": system_started_at,
        "system_age_minutes": system_age_minutes,
        "regime_started_at_utc": regime_started_at,
        "regime_age_minutes": regime_age_minutes,
        "last_stable_point_at_utc": last_stable_point_at,
        "last_stable_point_age_minutes": last_stable_point_age_minutes,
        "truth_class": "DERIVED_CANONICAL",
    }
    semantic_brain["owner_decision_trigger_state"] = owner_decision_triggers
    semantic_brain["owner_decision_trigger_count"] = len(owner_decision_triggers)
    semantic_brain["contradiction_state"] = str(system_brain_state.get("conflict_state", semantic_brain.get("contradiction_state", "UNKNOWN")))
    semantic_brain["trust_state"] = str(system_brain_state.get("trust_state", semantic_brain.get("trust_state", "UNKNOWN")))
    semantic_brain["truth_class"] = "DERIVED_CANONICAL"
    semantic_product["runtime_process_state"] = process_state
    semantic_product["runtime_failure_reason"] = runtime_failure_reason
    semantic_product["runtime_recovery_signal"] = runtime_recovery_signal
    semantic_product["truth_class"] = "DERIVED_CANONICAL"
    semantic_security["local_runtime_boundary"] = live_mode = str(live_layer_truth.get("mode", live_layer_truth.get("front_status", "UNKNOWN")))
    semantic_security["truth_class"] = "DERIVED_CANONICAL"
    known_gaps = list(semantic_truth.get("known_gaps", []) or [])
    semantic_truth["known_gaps"] = known_gaps
    unknown_registry = list(semantic_truth.get("unknown_reason_registry", []) or [])
    semantic_truth["unknown_reason_registry"] = unknown_registry
    if not isinstance(semantic_truth.get("unknown_reason_breakdown"), dict):
        semantic_truth["unknown_reason_breakdown"] = unknown_reason_breakdown(unknown_registry + known_gaps)
    semantic_truth["gap_count"] = max(int(semantic_truth.get("gap_count", 0) or 0), len(known_gaps))
    semantic_truth["stale_source_count"] = int(
        semantic_truth.get("stale_source_count", 0)
        or len([item for item in known_gaps if str((item or {}).get("unknown_reason", "")) == "stale_source"])
    )
    semantic_truth["truth_class"] = "DERIVED_CANONICAL"

    live_semantic_state = {
        "state_id": str(semantic_state.get("state_id", "system_semantic_state_surfaces_v1")),
        "generated_at_utc": now,
        "truth_class": "DERIVED_CANONICAL",
        "constitution_state": semantic_constitution,
        "brain_reason_control_state": semantic_brain,
        "memory_chronology_knowledge_state": semantic_memory,
        "product_state_integration": semantic_product,
        "security_sovereignty_posture_state": semantic_security,
        "exact_derived_gap_disclosure": semantic_truth,
        "source_paths": dict(semantic_state.get("source_paths", {}) or {}),
        "surface_model_path": str(semantic_state.get("surface_model_path", DEFAULT_SYSTEM_SEMANTIC_STATE_MODEL_PATH)),
        "surface_model_loaded": bool(semantic_state.get("surface_model_loaded", False)),
        "implementation_label": "ACTIVE",
    }

    parallel_evolution = dict((parallel_channels.get("evolution", {}) or {}))
    parallel_inquisition = dict((parallel_channels.get("inquisition", {}) or {}))
    parallel_custodes = dict((parallel_channels.get("custodes", {}) or {}))
    parallel_mechanicus = dict((parallel_channels.get("mechanicus", {}) or {}))
    parallel_administratum = dict((parallel_channels.get("administratum", {}) or {}))
    parallel_force = dict((parallel_channels.get("force", {}) or {}))
    parallel_palace_archive = dict((parallel_channels.get("palace_archive", {}) or {}))
    parallel_control_gates = dict((parallel_channels.get("control_gates", {}) or {}))
    parallel_factory = dict((parallel_channels.get("factory", {}) or {}))
    parallel_evolution["generated_at_utc"] = now
    parallel_evolution["truth_class"] = str(parallel_evolution.get("truth_class", "DERIVED_CANONICAL"))
    parallel_evolution["implementation_label"] = "ACTIVE"
    parallel_inquisition["generated_at_utc"] = now
    parallel_inquisition["truth_class"] = str(parallel_inquisition.get("truth_class", "DERIVED_CANONICAL"))
    parallel_inquisition["implementation_label"] = "ACTIVE"
    parallel_custodes["generated_at_utc"] = now
    parallel_custodes["truth_class"] = str(parallel_custodes.get("truth_class", "DERIVED_CANONICAL"))
    parallel_custodes["implementation_label"] = "ACTIVE"
    parallel_mechanicus["generated_at_utc"] = now
    parallel_mechanicus["truth_class"] = str(parallel_mechanicus.get("truth_class", "DERIVED_CANONICAL"))
    parallel_mechanicus["implementation_label"] = "ACTIVE"
    parallel_administratum["generated_at_utc"] = now
    parallel_administratum["truth_class"] = str(parallel_administratum.get("truth_class", "DERIVED_CANONICAL"))
    parallel_administratum["implementation_label"] = "ACTIVE"
    parallel_force["generated_at_utc"] = now
    parallel_force["truth_class"] = str(parallel_force.get("truth_class", "DERIVED_CANONICAL"))
    parallel_force["implementation_label"] = "ACTIVE"
    parallel_palace_archive["generated_at_utc"] = now
    parallel_palace_archive["truth_class"] = str(parallel_palace_archive.get("truth_class", "DERIVED_CANONICAL"))
    parallel_palace_archive["implementation_label"] = "ACTIVE"
    parallel_control_gates["generated_at_utc"] = now
    parallel_control_gates["truth_class"] = str(parallel_control_gates.get("truth_class", "DERIVED_CANONICAL"))
    parallel_control_gates["implementation_label"] = "ACTIVE"
    parallel_factory["generated_at_utc"] = now
    parallel_factory["truth_class"] = str(parallel_factory.get("truth_class", "DERIVED_CANONICAL"))
    parallel_factory["implementation_label"] = "ACTIVE"

    live_health = [
        {
            "metric_id": "verification",
            "value": governance_state,
            "state": verdict_to_live_state(governance_state),
            "trend": "stable",
            "provisional": False,
            "evidence_link": "runtime/repo_control_center/one_screen_status.json",
            "implementation_label": "ACTIVE",
        },
        {
            "metric_id": "operability",
            "value": f"sync={sync_state};trust={trust_state}",
            "state": verdict_to_live_state("PASS" if sync_state == "IN_SYNC" and trust_state == "TRUSTED" else trust_state),
            "trend": "stable",
            "provisional": True,
            "evidence_link": "runtime/repo_control_center/one_screen_status.json",
            "implementation_label": "PARTIALLY_IMPLEMENTED",
        },
        {
            "metric_id": "release_readiness",
            "value": admission_state,
            "state": verdict_to_live_state(admission_state),
            "trend": "stable",
            "provisional": True,
            "evidence_link": "runtime/repo_control_center/one_screen_status.json",
            "implementation_label": "PARTIALLY_IMPLEMENTED",
        },
        {
            "metric_id": "wave_1_readiness",
            "value": wave_lane_status,
            "state": "warning" if "PRELAUNCH" in str(wave_lane_status).upper() else "stable",
            "trend": "improving",
            "provisional": True,
            "evidence_link": "shared_systems/factory_observation_window_v1/adapters/TIKTOK_WAVE1_CONTROL_SURFACES_V1.json",
            "implementation_label": "ACTIVE",
        },
    ]

    live_wave_state = {
        "wave_id": str(wave1_control.get("wave_id", "wave_1_must_fix_foundation")),
        "status": str(wave_surface.get("status", "planned")).lower(),
        "started_at_utc": str(tranche_surface.get("started_at_utc", now)),
        "tasks_total": wave_count,
        "tasks_done": max(0, min(wave_count, len([e for e in live_changes if e.get("event_type") == "task_completed"]))),
        "blocking_issues": int(critical_contradictions > 0),
        "selected_option": selected_option,
        "claim": str(wave_surface.get("claim", "WAVE_NOT_CLAIMED")),
        "implementation_label": "ACTIVE",
        "truth_class": "DERIVED_CANONICAL",
    }

    live_gate_state = {
        "gate_id": "owner_wave_checkpoint",
        "status": "pending_checkpoint" if pending_gates > 0 else "stable",
        "owner_required": pending_gates > 0,
        "opened_at_utc": now,
        "blocking_reason": (
            "waiting owner checkpoint before wave transition"
            if pending_gates > 0
            else "no pending checkpoint gate"
        ),
        "source_path": normalize_rel(str(gate_doc_path.relative_to(repo_root))) if gate_doc_path.exists() else "",
        "truth_class": "DERIVED_CANONICAL",
        "pending_gate_markers": pending_gates,
        "pending_gate_ids": pending_gate_ids,
        "resolved_gate_ids": resolved_gate_ids,
        "next_checkpoint": str(checkpoint_surface.get("next_checkpoint", "UNKNOWN")),
        "implementation_label": "ACTIVE",
    }

    live = {
        "generated_at_utc": now,
        "near_realtime_window_sec": near_realtime_window_sec,
        "mode_scope": "EMPEROR_ONLY",
        "visual_pack": visual_pack,
        # Compatibility projection for legacy/top-level consumers:
        # keep canonical values available without requiring deep object traversal.
        "selected_option": selected_option,
        "selected_option_state": selected_option_classification["state"],
        "selected_option_unknown_reason": selected_option_classification["unknown_reason"],
        "wave_lane_status": wave_lane_status,
        "wave_lane_state": wave_lane_classification["state"],
        "wave_lane_unknown_reason": wave_lane_classification["unknown_reason"],
        "gate_c_status": gate_c_status,
        "gate_c_state": gate_c_classification["state"],
        "gate_c_unknown_reason": gate_c_classification["unknown_reason"],
        "growth_distribution_status": growth_distribution_status,
        "growth_distribution_state": growth_distribution_classification["state"],
        "growth_distribution_unknown_reason": growth_distribution_classification["unknown_reason"],
        "live_layer_front_status": live_layer_front_status,
        "live_layer_front_state": live_layer_front_classification["state"],
        "live_layer_front_unknown_reason": live_layer_front_classification["unknown_reason"],
        "live_layer_implementation_status": live_layer_impl_status,
        "live_layer_implementation_state": live_layer_implementation_classification["state"],
        "live_layer_implementation_unknown_reason": live_layer_implementation_classification["unknown_reason"],
        "active_tranche_id": str(
            ((wave1_control.get("first_tranche_execution", {}) or {}).get("tranche_id"))
            or wave_surface.get("active_tranche_id", "UNKNOWN")
        ),
        "live_update_channel": {
            "primary": "SSE_EVENTSOURCE_LOCALHOST",
            "fallback": "INCREMENTAL_POLLING",
            "event_bus": "NOT_YET_IMPLEMENTED",
            "truth_class": "DERIVED_CANONICAL",
            "implementation_label": "PARTIALLY_IMPLEMENTED",
        },
        "compat_projection_truth_class": "DERIVED_CANONICAL",
        "live_factory_state": {
            "factory_id": "factory_v1",
            "generated_at_utc": now,
            "near_realtime_window_sec": near_realtime_window_sec,
            "active_products_count": len(products),
            "active_departments_count": len(state.get("department_floor", [])),
            "pending_owner_gates_count": pending_gates,
            "open_blockers_count": critical_contradictions + major_contradictions,
            "truth_class": "DERIVED_CANONICAL",
            "selected_option": selected_option,
            "selected_option_state": selected_option_classification["state"],
            "selected_option_unknown_reason": selected_option_classification["unknown_reason"],
            "gate_c_status": gate_c_status,
            "gate_c_state": gate_c_classification["state"],
            "gate_c_unknown_reason": gate_c_classification["unknown_reason"],
            "visual_doctrine_pack": visual_pack,
            "growth_distribution_status": growth_distribution_status,
            "growth_distribution_state": growth_distribution_classification["state"],
            "growth_distribution_unknown_reason": growth_distribution_classification["unknown_reason"],
            "live_layer_front_status": live_layer_front_status,
            "live_layer_front_state": live_layer_front_classification["state"],
            "live_layer_front_unknown_reason": live_layer_front_classification["unknown_reason"],
            "live_layer_implementation_status": live_layer_impl_status,
            "live_layer_implementation_state": live_layer_implementation_classification["state"],
            "live_layer_implementation_unknown_reason": live_layer_implementation_classification["unknown_reason"],
            "system_started_at_utc": system_started_at,
            "system_age_minutes": system_age_minutes,
            "regime_started_at_utc": regime_started_at,
            "regime_age_minutes": regime_age_minutes,
            "last_stable_point_at_utc": last_stable_point_at,
            "last_stable_point_age_minutes": last_stable_point_age_minutes,
            "implementation_label": "ACTIVE",
        },
        "live_product_state": {
            "product_id": product_id,
            "current_stage": current_stage,
            "current_wave": str(wave1_control.get("wave_id", f"wave_{1 if wave_count else 0}")),
            "process_state": process_state,
            "execution_state": product_execution_state,
            "last_change_at_utc": last_change.get("occurred_at_utc", now),
            "last_change_source": last_change.get("source_path", ""),
            "owner_attention_required": operator_action_required or pending_gates > 0,
            "runtime_observability_source": str(tiktok_runtime_state.get("source_mode", "DERIVED_RUNTIME_LOG")),
            "runtime_failure_reason": runtime_failure_reason,
            "runtime_recovery_signal": runtime_recovery_signal,
            "truth_class": "SOURCE_EXACT",
            "selected_option": selected_option,
            "wave_lane_status": wave_lane_status,
            "selected_option_state": selected_option_classification["state"],
            "selected_option_unknown_reason": selected_option_classification["unknown_reason"],
            "wave_lane_state": wave_lane_classification["state"],
            "wave_lane_unknown_reason": wave_lane_classification["unknown_reason"],
            "gate_c_status": gate_c_status,
            "gate_c_state": gate_c_classification["state"],
            "gate_c_unknown_reason": gate_c_classification["unknown_reason"],
            "implementation_label": "ACTIVE",
        },
        "live_wave_state": live_wave_state,
        "live_gate_state": live_gate_state,
        "live_health_state": live_health,
        "live_change_feed": live_changes,
        "live_preview_registry": preview_registry,
        "live_preview_meta": {
            "status": preview_meta_status,
            "implementation_label": preview_meta_label,
            "note": preview_meta_note,
            "latest_diff_pack_path": str(diff_preview_state.get("latest_diff_pack_path", "")),
            "latest_diff_manifest_path": str(diff_preview_state.get("latest_diff_manifest_path", "")),
            "latest_contact_sheet_html": str(diff_preview_state.get("latest_contact_sheet_html", "")),
            "changed_count": int(diff_preview_state.get("changed_count", 0) or 0),
            "compared_count": int(diff_preview_state.get("compared_count", 0) or 0),
        },
        "live_contradiction_state": {
            "open_count": critical_contradictions + major_contradictions,
            "critical_count": critical_contradictions,
            "last_opened_at_utc": last_change.get("occurred_at_utc", now),
            "last_closed_at_utc": "",
            "truth_class": "DERIVED_CANONICAL",
            "implementation_label": "ACTIVE",
        },
        "live_task_state": {
            "active_tasks_count": 0,
            "completed_tasks_count": len([e for e in live_changes if e.get("event_type") == "task_completed"]),
            "blocked_tasks_count": 1 if operator_action_required else 0,
            "last_task_event_at_utc": last_change.get("occurred_at_utc", now),
            "truth_class": "DERIVED_CANONICAL",
            "implementation_label": "SCAFFOLDED",
        },
        "live_execution_state": {
            "execution_mode": "local_live_observation_v1",
            "rank": execution_rank,
            "machine_mode": machine_mode,
            "emperor_proof": str(throne_authority_state.get("emperor_status", "UNKNOWN")),
            "throne_anchor_state": str(throne_authority_state.get("status", "UNKNOWN")),
            "last_verification_state": governance_state,
            "sync_state": sync_state,
            "trust_state": trust_state,
            "governance_blocker_count": int(((system_brain_state.get("blocker_counts", {}) or {}).get("governance_blockers", 0)) or 0),
            "trust_blocker_count": int(((system_brain_state.get("blocker_counts", {}) or {}).get("trust_blockers", 0)) or 0),
            "sync_blocker_count": int(((system_brain_state.get("blocker_counts", {}) or {}).get("sync_blockers", 0)) or 0),
            "truth_class": "SOURCE_EXACT",
            "implementation_label": "PARTIALLY_IMPLEMENTED",
        },
        "live_brain_state": {
            "conflict_state": str(system_brain_state.get("conflict_state", "UNKNOWN")),
            "trust_state": str(system_brain_state.get("trust_state", "UNKNOWN")),
            "one_screen": system_brain_state.get("one_screen", {}),
            "repo_control": system_brain_state.get("repo_control", {}),
            "constitution": system_brain_state.get("constitution", {}),
            "limits": system_brain_state.get("limits", {}),
            "age_axis": system_brain_state.get("age_axis", {}),
            "mission_consistency": system_brain_state.get("mission_consistency", {}),
            "task_program_consistency": system_brain_state.get("task_program_consistency", {}),
            "command_surface": system_brain_state.get("command_surface", {}),
            "conflicts": system_brain_state.get("conflicts", []),
            "owner_decision_triggers": owner_decision_triggers,
            "repo_worktree_hygiene": repo_worktree_hygiene,
            "code_bank": code_bank_state,
            "live_work_visibility": live_work_state,
            "doctrine_integrity": doctrine_integrity_state,
            "dashboard_coverage": dashboard_coverage_state,
            "truth_dominance": truth_dominance_state,
            "throne_authority": throne_authority_state,
            "custodes": custodes_state,
            "mechanicus": mechanicus_state,
            "administratum": administratum_state,
            "force": force_state,
            "palace_archive": palace_archive_state,
            "control_gates": control_gates_state,
            "brain_v2_layers": brain_v2_layers,
            "blocker_classes": system_brain_state.get("blocker_classes", {}),
            "blocker_counts": system_brain_state.get("blocker_counts", {}),
            "truth_class": "DERIVED_CANONICAL",
            "implementation_label": "ACTIVE",
        },
        "live_prompt_state": {
            "active_prompt_state": str(prompt_lineage_state.get("active_prompt_state", "UNKNOWN")),
            "lineage_id": str(prompt_lineage_state.get("lineage_id", "UNKNOWN")),
            "trusted_boundary": str(prompt_lineage_state.get("trusted_boundary", "UNKNOWN")),
            "runtime_observability": prompt_lineage_state.get("runtime_observability", {}),
            "text_boundary": prompt_lineage_state.get("text_boundary", {}),
            "source_paths": prompt_lineage_state.get("source_paths", {}),
            "truth_class": "DERIVED_CANONICAL",
            "implementation_label": "PARTIALLY_IMPLEMENTED",
        },
        "live_semantic_state": live_semantic_state,
        "live_evolution_state": parallel_evolution,
        "live_inquisition_state": parallel_inquisition,
        "live_custodes_state": parallel_custodes or custodes_state,
        "live_mechanicus_state": parallel_mechanicus or mechanicus_state,
        "live_administratum_state": parallel_administratum or administratum_state,
        "live_force_state": parallel_force or force_state,
        "live_palace_archive_state": parallel_palace_archive or palace_archive_state,
        "live_control_gates_state": parallel_control_gates or control_gates_state,
        "live_brain_v2_layers": brain_v2_layers,
        "live_machine_capability_manifest": machine_capability_manifest,
        "live_organ_strength_surface": organ_strength_surface,
        "live_active_mission_contract": active_mission_contract,
        "live_throne_authority_state": throne_authority_state,
        "live_factory_production_state": parallel_factory,
        "live_storage_health_state": storage_health_surface,
        "live_code_bank_state": code_bank_state,
        "live_work_state": live_work_state,
        "live_doctrine_integrity_state": doctrine_integrity_state,
        "live_truth_spine_state": truth_spine_state,
        "live_dashboard_truth_engine_state": dashboard_truth_engine_state,
        "live_bundle_truth_chamber_state": bundle_truth_chamber_state,
        "live_worktree_purity_gate_state": worktree_purity_gate_state,
        "live_address_lattice_state": address_lattice_state,
        "live_anti_lie_model_state": anti_lie_model_state,
        "live_truth_support_loop_state": live_truth_support_loop_state,
        "live_dashboard_coverage_state": dashboard_coverage_state,
        "live_truth_dominance_state": truth_dominance_state,
        "live_event_flow_state": {
            **event_flow_state,
            "generated_at_utc": now,
            "implementation_label": "ACTIVE",
            "truth_class": str(event_flow_state.get("truth_class", "DERIVED_CANONICAL")),
        },
        "live_diff_preview_state": {
            **diff_preview_state,
            "generated_at_utc": now,
            "implementation_label": "PARTIALLY_IMPLEMENTED",
            "truth_class": str(diff_preview_state.get("truth_class", "DERIVED_CANONICAL")),
        },
        "live_golden_throne_discoverability": {
            **golden_throne_discoverability_state,
            "generated_at_utc": now,
            "implementation_label": "ACTIVE",
            "truth_class": str(golden_throne_discoverability_state.get("truth_class", "DERIVED_CANONICAL")),
        },
        "live_agent_runtime_state": {
            "state_id": str(tiktok_runtime_state.get("state_id", "tiktok_runtime_observability_v1")),
            "source_mode": str(tiktok_runtime_state.get("source_mode", "DERIVED_RUNTIME_LOG")),
            "process_state": process_state,
            "current_operation_code": runtime_operation_code or str(wave_surface.get("objective", "must_fix_foundation")),
            "latest_change_summary": runtime_latest_summary or str(last_change.get("summary", "")),
            "failure_reason": runtime_failure_reason,
            "recovery_signal": runtime_recovery_signal,
            "latest_event_at_utc": str(tiktok_runtime_state.get("latest_event_at_utc", "")),
            "truth_class": str(tiktok_runtime_state.get("truth_class", "DERIVED_CANONICAL")),
            "implementation_label": "ACTIVE",
            "source_paths": tiktok_runtime_state.get("source_paths", {}),
        },
        "live_operation_heartbeat": {
            "current_operation_code": runtime_operation_code or str(wave_surface.get("objective", "must_fix_foundation")),
            "current_operation_ru": "Идет активная операция текущего tranche/workset в Wave 1",
            "active_tranche_id": str(tranche_surface.get("tranche_id", "UNKNOWN")),
            "active_workset_id": str(active_workset.get("work_id", "UNKNOWN")),
            "active_workset_title": str(active_workset.get("title", "active workset")),
            "active_route_node_id": active_route_node_id,
            "latest_changed_node_id": latest_changed_node_id,
            "blocker_node_id": blocker_node_id,
            "latest_milestone_event_id": str(latest_milestone.get("event_id", "")),
            "latest_milestone_summary": str(latest_milestone.get("summary", "")) or runtime_latest_summary,
            "latest_milestone_at_utc": str(latest_milestone.get("occurred_at_utc", "")),
            "latest_proof_event_id": str(latest_proof.get("event_id", "")),
            "latest_proof_summary": str(latest_proof.get("summary", "")),
            "latest_proof_at_utc": str(latest_proof.get("occurred_at_utc", "")),
            "latest_risk_event_id": str(latest_risk.get("event_id", "")),
            "latest_risk_summary": str(latest_risk.get("summary", "")),
            "latest_risk_at_utc": str(latest_risk.get("occurred_at_utc", "")),
            "latest_blocker_event_id": str(latest_blocker_event.get("event_id", "")),
            "latest_blocker_summary": str(latest_blocker_event.get("summary", "")) or (
                runtime_failure_reason if process_state == "ERROR" else ""
            ),
            "latest_blocker_at_utc": str(latest_blocker_event.get("occurred_at_utc", "")),
            "runtime_failure_reason": runtime_failure_reason,
            "runtime_recovery_signal": runtime_recovery_signal,
            "event_flow_posture": str(event_flow_state.get("flow_posture", "WAIT")),
            "event_flow_active_signal_summary": str(event_flow_state.get("active_signal_summary", "")),
            "event_flow_route_focus": str(
                next(
                    (
                        route.get("route_id")
                        for route in (event_flow_state.get("changed_sector_routes", []) or [])
                        if str((route or {}).get("status", "")).upper() in {"ACTIVE", "BLOCKED", "PROVEN"}
                    ),
                    "",
                )
            ),
            "event_flow_transition_markers": dict(event_flow_state.get("transition_markers", {})),
            "event_flow_signal_vessels": list(event_flow_state.get("signal_vessels", [])),
            "event_flow_route_states": list(event_flow_state.get("changed_sector_routes", [])),
            "coverage_verdict": str(dashboard_coverage_state.get("coverage_verdict", "UNKNOWN")),
            "code_bank_status": str(code_bank_state.get("status", "UNKNOWN")),
            "code_bank_monolith_count": int(code_bank_state.get("monolith_count", 0) or 0),
            "truth_dominance_status": str(truth_dominance_state.get("status", "UNKNOWN")),
            "truth_dominance_stale_rules_count": int(truth_dominance_state.get("stale_rules_count", 0) or 0),
            "throne_authority_status": str(throne_authority_state.get("status", "UNKNOWN")),
            "throne_breach": bool(throne_authority_state.get("throne_breach", False)),
            "emperor_status_blocked": bool(throne_authority_state.get("emperor_status_blocked", False)),
            "custodes_vigilance_state": str(custodes_state.get("vigilance_state", "UNKNOWN")),
            "custodes_lock_mode": str(custodes_state.get("foundation_lock_mode", "UNKNOWN")),
            "checkpoint_posture": str(checkpoint_surface.get("current_checkpoint", "UNKNOWN")),
            "checkpoint_next": str(checkpoint_surface.get("next_checkpoint", "UNKNOWN")),
            "tiktok_ascent_status": tiktok_ascent_status,
            "tiktok_ascent_boundary": tiktok_ascent_boundary,
            "tiktok_ascent_target": tiktok_ascent_future,
            "tiktok_ascent_lane": list(tiktok_ascent_track.get("ascent_lane", [])),
            "update_mechanism": "DERIVED_FROM_LOCAL_EVENT_LOG_AND_CANONICAL_STATE",
            "event_flow_class_counts": dict(event_flow_state.get("class_counts", {})),
            "diff_preview_changed_sectors": int(diff_preview_state.get("changed_count", 0) or 0),
            "live_bus_status": "NOT_YET_IMPLEMENTED",
            "truth_class": "DERIVED_CANONICAL",
            "implementation_label": "PARTIALLY_IMPLEMENTED",
        },
        "contracts": {
            "state_model_loaded": bool(live_state_model),
            "event_model_loaded": bool(live_event_model),
            "state_model_path": DEFAULT_LIVE_STATE_MODEL_PATH,
            "event_model_path": DEFAULT_LIVE_EVENT_MODEL_PATH,
            "canon_state_sync_loaded": bool(canon_sync),
            "canon_state_sync_path": DEFAULT_CANON_STATE_SYNC_PATH,
            "wave1_control_loaded": bool(wave1_control),
            "wave1_control_path": DEFAULT_WAVE1_CONTROL_SURFACES_PATH,
            "imperium_evolution_surface_loaded": bool(evolution_surface),
            "imperium_evolution_surface_path": DEFAULT_IMPERIUM_EVOLUTION_SURFACE_PATH,
            "imperium_inquisition_surface_loaded": bool(inquisition_surface),
            "imperium_inquisition_surface_path": DEFAULT_IMPERIUM_INQUISITION_SURFACE_PATH,
            "imperium_factory_surface_loaded": bool(factory_surface),
            "imperium_factory_surface_path": DEFAULT_IMPERIUM_FACTORY_PRODUCTION_SURFACE_PATH,
            "imperium_event_flow_surface_loaded": bool(event_flow_surface),
            "imperium_event_flow_surface_path": DEFAULT_IMPERIUM_EVENT_FLOW_SPINE_SURFACE_PATH,
            "imperium_diff_preview_surface_loaded": bool(diff_preview_surface),
            "imperium_diff_preview_surface_path": DEFAULT_IMPERIUM_DIFF_PREVIEW_PIPELINE_SURFACE_PATH,
            "imperium_golden_throne_surface_loaded": bool(golden_throne_surface),
            "imperium_golden_throne_surface_path": DEFAULT_IMPERIUM_GOLDEN_THRONE_DISCOVERABILITY_SURFACE_PATH,
            "golden_throne_authority_anchor_exists": bool(throne_authority_state.get("anchor_exists", False)),
            "golden_throne_authority_anchor_path": DEFAULT_GOLDEN_THRONE_AUTHORITY_ANCHOR_PATH,
            "imperium_true_form_surface_loaded": bool(true_form_surface),
            "imperium_true_form_surface_path": DEFAULT_IMPERIUM_TRUE_FORM_MATRYOSHKA_SURFACE_PATH,
            "imperium_storage_health_surface_loaded": bool(storage_health_surface),
            "imperium_storage_health_surface_path": DEFAULT_IMPERIUM_STORAGE_HEALTH_SURFACE_PATH,
            "imperium_code_bank_surface_loaded": bool(code_bank_state),
            "imperium_code_bank_surface_path": DEFAULT_IMPERIUM_CODE_BANK_SURFACE_PATH,
            "imperium_live_work_surface_loaded": bool(live_work_state),
            "imperium_live_work_surface_path": DEFAULT_IMPERIUM_LIVE_WORK_VISIBILITY_SURFACE_PATH,
            "imperium_doctrine_integrity_surface_loaded": bool(doctrine_integrity_state),
            "imperium_doctrine_integrity_surface_path": DEFAULT_IMPERIUM_DOCTRINE_INTEGRITY_SURFACE_PATH,
            "imperium_dashboard_coverage_surface_loaded": bool(dashboard_coverage_state),
            "imperium_dashboard_coverage_surface_path": DEFAULT_IMPERIUM_DASHBOARD_COVERAGE_SURFACE_PATH,
            "imperium_truth_dominance_surface_loaded": bool(truth_dominance_state),
            "imperium_truth_dominance_surface_path": DEFAULT_IMPERIUM_TRUTH_DOMINANCE_SURFACE_PATH,
            "imperium_custodes_surface_loaded": bool(custodes_surface),
            "imperium_custodes_surface_path": DEFAULT_IMPERIUM_CUSTODES_SURFACE_PATH,
            "imperium_mechanicus_surface_loaded": bool(mechanicus_surface),
            "imperium_mechanicus_surface_path": DEFAULT_IMPERIUM_MECHANICUS_SURFACE_PATH,
            "imperium_administratum_surface_loaded": bool(administratum_surface),
            "imperium_administratum_surface_path": DEFAULT_IMPERIUM_ADMINISTRATUM_SURFACE_PATH,
            "imperium_force_surface_loaded": bool(force_surface),
            "imperium_force_surface_path": DEFAULT_IMPERIUM_FORCE_DOCTRINE_SURFACE_PATH,
            "imperium_palace_archive_surface_loaded": bool(palace_archive_surface),
            "imperium_palace_archive_surface_path": DEFAULT_IMPERIUM_PALACE_ARCHIVE_SURFACE_PATH,
            "imperium_control_gates_surface_loaded": bool(control_gates_surface),
            "imperium_control_gates_surface_path": DEFAULT_IMPERIUM_CONTROL_GATES_SURFACE_PATH,
            "imperium_machine_capability_manifest_loaded": bool(machine_capability_manifest),
            "imperium_machine_capability_manifest_path": DEFAULT_IMPERIUM_MACHINE_CAPABILITY_MANIFEST_PATH,
            "imperium_organ_strength_surface_loaded": bool(organ_strength_surface),
            "imperium_organ_strength_surface_path": DEFAULT_IMPERIUM_ORGAN_STRENGTH_SURFACE_PATH,
            "imperium_active_mission_contract_loaded": bool(active_mission_contract),
            "imperium_active_mission_contract_path": DEFAULT_IMPERIUM_ACTIVE_MISSION_CONTRACT_PATH,
            "live_event_log_loaded": bool(log_meta.get("loaded", False)),
            "live_event_log_path": str(log_meta.get("path", event_log_path_value)),
        },
        "observational_boundary": {
            "live_layer_non_canonical": True,
            "checkpoint_bundle_required_for_completion_claims": True,
            "provisional_metrics_labeled": True,
        },
        "canon_projection": {
            "selected_option": selected_option,
            "selected_option_state": selected_option_classification["state"],
            "selected_option_unknown_reason": selected_option_classification["unknown_reason"],
            "wave_lane_status": wave_lane_status,
            "wave_lane_state": wave_lane_classification["state"],
            "wave_lane_unknown_reason": wave_lane_classification["unknown_reason"],
            "gate_c_status": gate_c_status,
            "gate_c_state": gate_c_classification["state"],
            "gate_c_unknown_reason": gate_c_classification["unknown_reason"],
            "visual_pack": visual_pack,
            "growth_distribution_status": growth_distribution_status,
            "growth_distribution_state": growth_distribution_classification["state"],
            "growth_distribution_unknown_reason": growth_distribution_classification["unknown_reason"],
            "live_layer_front_status": live_layer_front_status,
            "live_layer_front_state": live_layer_front_classification["state"],
            "live_layer_front_unknown_reason": live_layer_front_classification["unknown_reason"],
            "live_layer_implementation_status": live_layer_impl_status,
            "live_layer_implementation_state": live_layer_implementation_classification["state"],
            "live_layer_implementation_unknown_reason": live_layer_implementation_classification["unknown_reason"],
            "truth_class": "DERIVED_CANONICAL",
        },
        "notes": [
            "SCAFFOLDED: live observation snapshot derived from local files.",
            "NOT AUTHORITATIVE: canonical completion claims require checkpoint bundle.",
        ],
        "live_event_log_meta": log_meta,
    }
    if persist_snapshot:
        live["snapshot_persistence"] = persist_live_snapshot(
            repo_root=repo_root,
            snapshot_path_value=snapshot_path_value,
            payload=live,
        )
    else:
        live["snapshot_persistence"] = {
            "enabled": False,
            "path": normalize_rel(snapshot_path_value),
            "written": False,
        }
    return live


def load_optional_model(repo_root: Path, path_value: str) -> tuple[dict | None, dict]:
    model_path = resolve_path(repo_root, path_value)
    meta: dict = {
        "path": str(model_path),
        "loaded": False,
    }
    if not model_path.exists():
        meta["error"] = "model_file_missing"
        return None, meta
    try:
        data = load_json_file(model_path)
        meta["loaded"] = True
        meta["model_version"] = data.get("model_version", "unknown")
        return data, meta
    except Exception as exc:  # pragma: no cover
        meta["error"] = f"model_parse_error:{exc}"
        return None, meta


def resolve_path(repo_root: Path, path_value: str) -> Path:
    p = Path(path_value).expanduser()
    if p.is_absolute():
        return p
    return (repo_root / p).resolve()


def rel_or_abs(path: Path, repo_root: Path) -> str:
    try:
        return normalize_rel(str(path.relative_to(repo_root)))
    except ValueError:
        return str(path)


def resolve_bundle_binding(repo_root: Path, requested_bundle_value: str) -> dict:
    requested_value = str(requested_bundle_value or "").strip()
    active_alias_path = resolve_path(repo_root, DEFAULT_ACTIVE_EVIDENCE_BUNDLE_PATH)
    fallback_alias_path = resolve_path(repo_root, DEFAULT_FALLBACK_BUNDLE_PATH)
    companion_path = resolve_path(repo_root, DEFAULT_COMPANION_BUNDLE_PATH)
    kickoff_alias_rel = normalize_rel(DEFAULT_FALLBACK_BUNDLE_PATH)

    if requested_value:
        requested_path = resolve_path(repo_root, requested_value)
    else:
        requested_path = active_alias_path

    requested_rel = rel_or_abs(requested_path, repo_root)
    active_alias_rel = rel_or_abs(active_alias_path, repo_root)
    fallback_alias_rel = rel_or_abs(fallback_alias_path, repo_root)

    selected_path = requested_path
    selection_mode = "explicit_bundle_path"
    selection_reason = "explicit --bundle path selected"

    if requested_rel == kickoff_alias_rel and active_alias_path.exists():
        # Historical kickoff alias should not silently dominate once ongoing tranche evidence exists.
        selected_path = active_alias_path
        selection_mode = "legacy_kickoff_alias_redirected_to_active_ongoing"
        selection_reason = "kickoff alias received, active ongoing alias exists and is promoted to primary source"
    elif selected_path.exists():
        selection_mode = "explicit_bundle_path"
        selection_reason = "explicit --bundle path exists and is used"
    elif active_alias_path.exists():
        selected_path = active_alias_path
        selection_mode = "active_ongoing_alias_autoselect"
        selection_reason = "requested bundle missing; active ongoing alias used"
    elif fallback_alias_path.exists():
        selected_path = fallback_alias_path
        selection_mode = "fallback_kickoff_alias"
        selection_reason = "active ongoing alias unavailable; kickoff fallback used"
    else:
        selection_mode = "missing_active_and_fallback_bundle"
        selection_reason = "requested, active, and fallback bundle paths are all missing"

    return {
        "selection_mode": selection_mode,
        "selection_reason": selection_reason,
        "active_bundle": {
            "role": "active_evidence_bundle",
            "path": str(selected_path),
            "repo_relative_path": rel_or_abs(selected_path, repo_root),
            "bundle_name": selected_path.name,
            "exists": selected_path.exists(),
        },
        "presentation_bundle": {
            "role": "presentation_bundle",
            "path": str(requested_path),
            "repo_relative_path": requested_rel,
            "bundle_name": requested_path.name,
            "exists": requested_path.exists(),
        },
        "fallback_bundle": {
            "role": "fallback_bundle",
            "path": str(fallback_alias_path),
            "repo_relative_path": fallback_alias_rel,
            "bundle_name": fallback_alias_path.name,
            "exists": fallback_alias_path.exists(),
        },
        "active_alias_bundle": {
            "role": "active_alias_bundle",
            "path": str(active_alias_path),
            "repo_relative_path": active_alias_rel,
            "bundle_name": active_alias_path.name,
            "exists": active_alias_path.exists(),
        },
        "companion_dependency": {
            "role": "companion_dependency",
            "required": True,
            "model": "PATH_B_EXPLICIT_COMPANION_DEPENDENT_CHECKPOINT",
            "path": str(companion_path),
            "repo_relative_path": rel_or_abs(companion_path, repo_root),
            "bundle_name": companion_path.name,
            "exists": companion_path.exists(),
        },
        "disclosure": {
            "active_source": "active_evidence_bundle",
            "presentation_source": "presentation_bundle",
            "fallback_source": "fallback_bundle",
            "selection_mode": selection_mode,
            "selection_reason": selection_reason,
            "legacy_kickoff_requested": requested_rel == kickoff_alias_rel,
            "truth_class": "SOURCE_EXACT",
        },
    }


def parity_status(present: int, total: int) -> str:
    if total <= 0:
        return "MISSING"
    if present >= total:
        return "FULL"
    if present > 0:
        return "PARTIAL"
    return "MISSING"


def build_panels_from_viewpack(names: list[str], viewpack: dict) -> list[dict]:
    panels: list[dict] = []
    for panel in viewpack.get("panels", []):
        source_checks = []
        present_count = 0
        source_paths = panel.get("source_paths", [])
        for source in source_paths:
            member = find_member_by_suffix(names, source)
            present = member is not None
            if present:
                present_count += 1
            source_checks.append(
                {
                    "source_path": source,
                    "source_section_or_member": "whole_document",
                    "data_class": panel.get("truth_class", "SOURCE_EXACT"),
                    "present_in_bundle": present,
                    "bundle_member": member,
                }
            )

        panels.append(
            {
                "panel_id": panel.get("panel_id"),
                "title": panel.get("title"),
                "truth_class": panel.get("truth_class"),
                "parity_status": parity_status(present_count, len(source_paths)),
                "source_checks": source_checks,
            }
        )
    return panels


def load_panel_registry(repo_root: Path, adapter: dict) -> tuple[dict | None, str | None]:
    registry_path_value = str(adapter.get("panel_registry_path", "")).strip()
    if not registry_path_value:
        return None, "panel_registry_path_missing"
    registry_path = resolve_path(repo_root, registry_path_value)
    if not registry_path.exists():
        return None, f"panel_registry_not_found:{registry_path}"
    try:
        return load_json_file(registry_path), None
    except Exception as exc:  # pragma: no cover
        return None, f"panel_registry_parse_error:{exc}"


def build_panels_from_adapter(names: list[str], adapter: dict) -> list[dict]:
    panels: list[dict] = []
    for panel in adapter.get("panels", []):
        source_checks = []
        present_count = 0
        sources = panel.get("sources", [])
        for source in sources:
            source_path = str(source.get("source_path", "")).strip()
            member = find_member_by_suffix(names, source_path)
            present = member is not None
            if present:
                present_count += 1
            source_checks.append(
                {
                    "source_path": source_path,
                    "source_section_or_member": source.get("source_section", "whole_document"),
                    "data_class": source.get("data_class", panel.get("panel_data_class", "SOURCE_EXACT")),
                    "present_in_bundle": present,
                    "bundle_member": member,
                }
            )

        panels.append(
            {
                "panel_id": panel.get("panel_id"),
                "title": panel.get("title"),
                "truth_class": panel.get("panel_data_class", "SOURCE_EXACT"),
                "parity_status": parity_status(present_count, len(sources)),
                "source_checks": source_checks,
            }
        )
    return panels


def build_parity_summary(
    *,
    panels: list[dict],
    required_panel_ids: list[str],
    source_kind: str,
) -> dict:
    by_id = {p.get("panel_id"): p for p in panels}
    statuses: list[str] = []
    for panel_id in required_panel_ids:
        panel = by_id.get(panel_id)
        if panel is None:
            statuses.append("MISSING")
            continue
        statuses.append(str(panel.get("parity_status", "MISSING")))

    full = sum(1 for s in statuses if s == "FULL")
    partial = sum(1 for s in statuses if s == "PARTIAL")
    missing = sum(1 for s in statuses if s == "MISSING")

    overall = "FULL"
    if missing > 0:
        overall = "PARTIAL"
    elif partial > 0:
        overall = "PARTIAL"

    return {
        "source_kind": source_kind,
        "required_panels_count": len(required_panel_ids),
        "full_panels_count": full,
        "partial_panels_count": partial,
        "missing_panels_count": missing,
        "overall": overall,
    }


def build_state(
    repo_root: Path,
    bundle_path: Path,
    adapter_path: Path,
    *,
    bundle_binding: dict | None = None,
    persist_live_snapshot_enabled: bool = False,
    live_snapshot_path_value: str = DEFAULT_LIVE_STATE_SNAPSHOT_PATH,
    live_event_log_path_value: str = DEFAULT_LIVE_EVENT_LOG_PATH,
) -> dict:
    factory_model, factory_model_meta = load_optional_model(repo_root, DEFAULT_FACTORY_STATE_MODEL_PATH)
    floor_model, floor_model_meta = load_optional_model(repo_root, DEFAULT_DEPARTMENT_FLOOR_MODEL_PATH)
    lane_model, lane_model_meta = load_optional_model(repo_root, DEFAULT_PRODUCT_LANE_MODEL_PATH)
    queue_model, queue_model_meta = load_optional_model(repo_root, DEFAULT_QUEUE_MONITOR_MODEL_PATH)
    force_model, force_model_meta = load_optional_model(repo_root, DEFAULT_FORCE_MAP_MODEL_PATH)
    history_seed_model, history_seed_model_meta = load_optional_model(repo_root, DEFAULT_PRODUCTION_HISTORY_SEED_PATH)
    canon_sync_model, canon_sync_model_meta = load_optional_model(repo_root, DEFAULT_CANON_STATE_SYNC_PATH)
    wave1_control_model, wave1_control_model_meta = load_optional_model(repo_root, DEFAULT_WAVE1_CONTROL_SURFACES_PATH)
    semantic_state_model, semantic_state_model_meta = load_optional_model(repo_root, DEFAULT_SYSTEM_SEMANTIC_STATE_MODEL_PATH)
    evolution_surface_model, evolution_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_EVOLUTION_SURFACE_PATH,
    )
    inquisition_surface_model, inquisition_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_INQUISITION_SURFACE_PATH,
    )
    factory_production_surface_model, factory_production_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_FACTORY_PRODUCTION_SURFACE_PATH,
    )
    product_evolution_map_model, product_evolution_map_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_PRODUCT_EVOLUTION_MAP_PATH,
    )
    event_flow_spine_surface_model, event_flow_spine_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_EVENT_FLOW_SPINE_SURFACE_PATH,
    )
    diff_preview_pipeline_surface_model, diff_preview_pipeline_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_DIFF_PREVIEW_PIPELINE_SURFACE_PATH,
    )
    golden_throne_discoverability_surface_model, golden_throne_discoverability_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_GOLDEN_THRONE_DISCOVERABILITY_SURFACE_PATH,
    )
    true_form_matryoshka_surface_model, true_form_matryoshka_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_TRUE_FORM_MATRYOSHKA_SURFACE_PATH,
    )
    storage_health_surface_model, storage_health_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_STORAGE_HEALTH_SURFACE_PATH,
    )
    code_bank_surface_model, code_bank_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_CODE_BANK_SURFACE_PATH,
    )
    dashboard_coverage_surface_model, dashboard_coverage_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_DASHBOARD_COVERAGE_SURFACE_PATH,
    )
    live_work_surface_model, live_work_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_LIVE_WORK_VISIBILITY_SURFACE_PATH,
    )
    doctrine_integrity_surface_model, doctrine_integrity_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_DOCTRINE_INTEGRITY_SURFACE_PATH,
    )
    truth_spine_surface_model, truth_spine_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_TRUTH_SPINE_SURFACE_PATH,
    )
    dashboard_truth_engine_surface_model, dashboard_truth_engine_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_DASHBOARD_TRUTH_ENGINE_SURFACE_PATH,
    )
    bundle_truth_chamber_surface_model, bundle_truth_chamber_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_BUNDLE_TRUTH_CHAMBER_SURFACE_PATH,
    )
    worktree_purity_gate_surface_model, worktree_purity_gate_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_WORKTREE_PURITY_GATE_SURFACE_PATH,
    )
    address_lattice_surface_model, address_lattice_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_ADDRESS_LATTICE_SURFACE_PATH,
    )
    anti_lie_model_surface_model, anti_lie_model_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_ANTI_LIE_MODEL_SURFACE_PATH,
    )
    live_truth_support_loop_surface_model, live_truth_support_loop_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_LIVE_TRUTH_SUPPORT_LOOP_SURFACE_PATH,
    )
    truth_dominance_surface_model, truth_dominance_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_TRUTH_DOMINANCE_SURFACE_PATH,
    )
    custodes_surface_model, custodes_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_CUSTODES_SURFACE_PATH,
    )
    mechanicus_surface_model, mechanicus_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_MECHANICUS_SURFACE_PATH,
    )
    administratum_surface_model, administratum_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_ADMINISTRATUM_SURFACE_PATH,
    )
    force_doctrine_surface_model, force_doctrine_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_FORCE_DOCTRINE_SURFACE_PATH,
    )
    palace_archive_surface_model, palace_archive_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_PALACE_ARCHIVE_SURFACE_PATH,
    )
    control_gates_surface_model, control_gates_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_CONTROL_GATES_SURFACE_PATH,
    )
    machine_capability_manifest_model, machine_capability_manifest_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_MACHINE_CAPABILITY_MANIFEST_PATH,
    )
    organ_strength_surface_model, organ_strength_surface_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_ORGAN_STRENGTH_SURFACE_PATH,
    )
    active_mission_contract_model, active_mission_contract_model_meta = load_optional_model(
        repo_root,
        DEFAULT_IMPERIUM_ACTIVE_MISSION_CONTRACT_PATH,
    )
    repo_worktree_hygiene = collect_repo_worktree_hygiene(repo_root)
    code_bank_state = build_code_bank_state(repo_root, code_bank_surface_model or {})
    dashboard_coverage_state = build_dashboard_coverage_state(repo_root, dashboard_coverage_surface_model or {})
    truth_dominance_state = build_truth_dominance_state(repo_root, truth_dominance_surface_model or {})
    throne_authority_state = build_throne_authority_state(repo_root)
    system_brain_state = build_system_brain_state(
        repo_root,
        repo_worktree_hygiene=repo_worktree_hygiene,
        code_bank_state=code_bank_state,
        dashboard_coverage_state=dashboard_coverage_state,
        truth_dominance_state=truth_dominance_state,
        throne_authority_state=throne_authority_state,
    )
    custodes_state = build_custodes_state(
        surface=custodes_surface_model or {},
        system_brain_state=system_brain_state,
        coverage_state=dashboard_coverage_state,
        truth_dominance_state=truth_dominance_state,
    )
    active_mission_contract = active_mission_contract_model or {}
    mechanicus_state = build_mechanicus_state(
        surface=mechanicus_surface_model or {},
        machine_manifest=machine_capability_manifest_model or {},
        organ_strength_surface=organ_strength_surface_model or {},
        code_bank_state=code_bank_state,
        repo_worktree_hygiene=repo_worktree_hygiene,
    )
    administratum_state = build_administratum_state(
        surface=administratum_surface_model or {},
        active_contract=active_mission_contract,
    )
    force_state = build_force_state(
        surface=force_doctrine_surface_model or {},
        machine_manifest=machine_capability_manifest_model or {},
        organ_strength_surface=organ_strength_surface_model or {},
        administratum_state=administratum_state,
        mechanicus_state=mechanicus_state,
    )
    palace_archive_state = build_palace_archive_state(
        surface=palace_archive_surface_model or {},
        storage_health=storage_health_surface_model or {},
        throne_authority_state=throne_authority_state,
    )
    def status_from_surface(surface_model: dict) -> str:
        payload = dict((surface_model or {}).get("payload", {}) or {})
        return str(payload.get("status", (surface_model or {}).get("status", "UNKNOWN")))

    runtime_truth_foundation_state = {
        "truth_spine_status": status_from_surface(truth_spine_surface_model or {}),
        "dashboard_truth_engine_status": status_from_surface(dashboard_truth_engine_surface_model or {}),
        "bundle_truth_chamber_status": status_from_surface(bundle_truth_chamber_surface_model or {}),
        "worktree_purity_gate_status": status_from_surface(worktree_purity_gate_surface_model or {}),
        "address_lattice_status": status_from_surface(address_lattice_surface_model or {}),
        "anti_lie_model_status": status_from_surface(anti_lie_model_surface_model or {}),
        "live_truth_support_loop_status": status_from_surface(live_truth_support_loop_surface_model or {}),
        "inquisition_truth_guard_status": str((inquisition_surface_model or {}).get("status", "UNKNOWN")),
    }
    control_gates_state = build_control_gates_state(
        surface=control_gates_surface_model or {},
        throne_authority_state=throne_authority_state,
        truth_dominance_state=truth_dominance_state,
        dashboard_coverage_state=dashboard_coverage_state,
        evolution_state=evolution_surface_model or {},
        runtime_state=runtime_truth_foundation_state,
        administratum_state=administratum_state,
    )
    brain_v2_layers = build_brain_v2_layers(
        system_brain_state=system_brain_state,
        throne_authority_state=throne_authority_state,
        custodes_state=custodes_state,
        inquisition_state=inquisition_surface_model or {},
        mechanicus_state=mechanicus_state,
        administratum_state=administratum_state,
        force_state=force_state,
        palace_state=palace_archive_state,
        control_gates_state=control_gates_state,
    )
    system_brain_state["custodes"] = custodes_state
    system_brain_state["mechanicus"] = mechanicus_state
    system_brain_state["administratum"] = administratum_state
    system_brain_state["force"] = force_state
    system_brain_state["palace_archive"] = palace_archive_state
    system_brain_state["control_gates"] = control_gates_state
    system_brain_state["brain_v2_layers"] = brain_v2_layers
    system_brain_state["throne_authority"] = throne_authority_state
    prompt_lineage_state = build_prompt_lineage_state(repo_root)
    tiktok_runtime_observability = build_tiktok_runtime_observability_state(repo_root)
    canon_sync_truth = extract_canon_truth(canon_sync_model or {})
    wave1_control_state = wave1_control_model or {}
    production_history_seed_state = history_seed_model or {}
    system_semantic_state_surfaces = build_system_semantic_state_surfaces(
        repo_root=repo_root,
        canon_truth=canon_sync_truth,
        system_brain_state=system_brain_state,
        prompt_lineage_state=prompt_lineage_state,
        tiktok_runtime_state=tiktok_runtime_observability,
        wave1_control=wave1_control_state,
        production_history_seed=production_history_seed_state,
        semantic_model=semantic_state_model,
    )
    imperium_parallel_channels = build_imperium_parallel_channels(
        evolution_surface=evolution_surface_model or {},
        inquisition_surface=inquisition_surface_model or {},
        custodes_surface=custodes_state,
        mechanicus_surface=mechanicus_state,
        administratum_surface=administratum_state,
        force_surface=force_state,
        palace_archive_surface=palace_archive_state,
        control_gates_surface=control_gates_state,
        factory_surface=factory_production_surface_model or {},
        product_map_surface=product_evolution_map_model or {},
        canon_truth=canon_sync_truth,
        wave1_control=wave1_control_state,
        system_semantic_state=system_semantic_state_surfaces,
    )
    preview_registry_seed = gather_preview_registry(repo_root=repo_root, limit=12)
    event_flow_state = build_event_flow_state(
        event_flow_surface=event_flow_spine_surface_model or {},
        live_changes=gather_recent_file_changes(repo_root=repo_root, limit=24),
        preview_registry=preview_registry_seed,
    )
    diff_preview_state = build_diff_preview_state(
        repo_root=repo_root,
        pipeline_surface=diff_preview_pipeline_surface_model or {},
        preview_registry=preview_registry_seed,
    )
    golden_throne_discoverability_state = build_golden_throne_discoverability_state(
        repo_root=repo_root,
        surface=golden_throne_discoverability_surface_model or {},
    )

    multi_department_meta = {
        "factory_state_model": factory_model_meta,
        "department_floor_model": floor_model_meta,
        "product_lane_model": lane_model_meta,
        "queue_monitor_model": queue_model_meta,
        "force_map_model": force_model_meta,
        "production_history_seed_model": history_seed_model_meta,
        "canon_state_sync_model": canon_sync_model_meta,
        "wave1_control_model": wave1_control_model_meta,
        "system_semantic_state_model": semantic_state_model_meta,
        "imperium_evolution_surface_model": evolution_surface_model_meta,
        "imperium_inquisition_surface_model": inquisition_surface_model_meta,
        "imperium_factory_production_surface_model": factory_production_surface_model_meta,
        "imperium_product_evolution_map_model": product_evolution_map_model_meta,
        "imperium_event_flow_spine_surface_model": event_flow_spine_surface_model_meta,
        "imperium_diff_preview_pipeline_surface_model": diff_preview_pipeline_surface_model_meta,
        "imperium_golden_throne_discoverability_surface_model": golden_throne_discoverability_surface_model_meta,
        "imperium_true_form_matryoshka_surface_model": true_form_matryoshka_surface_model_meta,
        "imperium_storage_health_surface_model": storage_health_surface_model_meta,
        "imperium_code_bank_surface_model": code_bank_surface_model_meta,
        "imperium_dashboard_coverage_surface_model": dashboard_coverage_surface_model_meta,
        "imperium_live_work_surface_model": live_work_surface_model_meta,
        "imperium_doctrine_integrity_surface_model": doctrine_integrity_surface_model_meta,
        "imperium_truth_spine_surface_model": truth_spine_surface_model_meta,
        "imperium_dashboard_truth_engine_surface_model": dashboard_truth_engine_surface_model_meta,
        "imperium_bundle_truth_chamber_surface_model": bundle_truth_chamber_surface_model_meta,
        "imperium_worktree_purity_gate_surface_model": worktree_purity_gate_surface_model_meta,
        "imperium_address_lattice_surface_model": address_lattice_surface_model_meta,
        "imperium_anti_lie_model_surface_model": anti_lie_model_surface_model_meta,
        "imperium_live_truth_support_loop_surface_model": live_truth_support_loop_surface_model_meta,
        "imperium_truth_dominance_surface_model": truth_dominance_surface_model_meta,
        "imperium_custodes_surface_model": custodes_surface_model_meta,
        "imperium_mechanicus_surface_model": mechanicus_surface_model_meta,
        "imperium_administratum_surface_model": administratum_surface_model_meta,
        "imperium_force_doctrine_surface_model": force_doctrine_surface_model_meta,
        "imperium_palace_archive_surface_model": palace_archive_surface_model_meta,
        "imperium_control_gates_surface_model": control_gates_surface_model_meta,
        "imperium_machine_capability_manifest_model": machine_capability_manifest_model_meta,
        "imperium_organ_strength_surface_model": organ_strength_surface_model_meta,
        "imperium_active_mission_contract_model": active_mission_contract_model_meta,
        "system_brain_state": {"loaded": True, "state_id": system_brain_state.get("state_id")},
        "system_semantic_state_surfaces": {
            "loaded": True,
            "state_id": system_semantic_state_surfaces.get("state_id"),
            "surface_model_loaded": bool(system_semantic_state_surfaces.get("surface_model_loaded", False)),
        },
        "prompt_lineage_state": {"loaded": True, "state_id": prompt_lineage_state.get("state_id")},
        "tiktok_runtime_observability": {
            "loaded": True,
            "state_id": tiktok_runtime_observability.get("state_id"),
            "source_mode": tiktok_runtime_observability.get("source_mode"),
        },
    }
    binding = bundle_binding or {}

    if not bundle_path.exists():
        base = {
            "status": "missing_bundle",
            "bundle_path": str(bundle_path),
            "bundle_name": bundle_path.name,
            "adapter_path": str(adapter_path),
            "generated_at": utc_now_iso(),
            "panels": [],
            "files": [],
            "factory_overview": {},
            "department_floor": [],
            "product_lanes": [],
            "queue_monitor": [],
            "force_map": {},
            "production_history_seed": production_history_seed_state,
            "canon_state_sync": canon_sync_truth,
            "wave1_control_surfaces": wave1_control_state,
            "system_brain_state": system_brain_state,
            "system_semantic_state_surfaces": system_semantic_state_surfaces,
            "prompt_lineage_state": prompt_lineage_state,
            "tiktok_agent_runtime_observability": tiktok_runtime_observability,
            "repo_worktree_hygiene": repo_worktree_hygiene,
            "imperium_evolution_state": imperium_parallel_channels.get("evolution", {}),
            "imperium_inquisition_state": imperium_parallel_channels.get("inquisition", {}),
            "imperium_custodes_state": imperium_parallel_channels.get("custodes", custodes_state),
            "imperium_mechanicus_state": imperium_parallel_channels.get("mechanicus", mechanicus_state),
            "imperium_administratum_state": imperium_parallel_channels.get("administratum", administratum_state),
            "imperium_force_state": imperium_parallel_channels.get("force", force_state),
            "imperium_palace_archive_state": imperium_parallel_channels.get("palace_archive", palace_archive_state),
            "imperium_control_gates_state": imperium_parallel_channels.get("control_gates", control_gates_state),
            "imperium_factory_production_state": imperium_parallel_channels.get("factory", {}),
            "imperium_product_evolution_map": product_evolution_map_model or {},
            "imperium_event_flow_state": event_flow_state,
            "imperium_diff_preview_state": diff_preview_state,
            "imperium_throne_authority_state": system_brain_state.get("throne_authority", {}),
            "imperium_brain_v2_layers": brain_v2_layers,
            "imperium_machine_capability_manifest": machine_capability_manifest_model or {},
            "imperium_organ_strength_surface": organ_strength_surface_model or {},
            "imperium_active_mission_contract": active_mission_contract,
            "imperium_golden_throne_discoverability": golden_throne_discoverability_state,
            "imperium_true_form_state": true_form_matryoshka_surface_model or {},
            "imperium_storage_health_state": storage_health_surface_model or {},
            "imperium_code_bank_state": code_bank_state,
            "imperium_live_work_state": live_work_surface_model or {},
            "imperium_doctrine_integrity_state": doctrine_integrity_surface_model or {},
            "imperium_truth_spine_state": (truth_spine_surface_model or {}).get("payload", truth_spine_surface_model or {}),
            "imperium_dashboard_truth_engine_state": (dashboard_truth_engine_surface_model or {}).get(
                "payload", dashboard_truth_engine_surface_model or {}
            ),
            "imperium_bundle_truth_chamber_state": (bundle_truth_chamber_surface_model or {}).get(
                "payload", bundle_truth_chamber_surface_model or {}
            ),
            "imperium_worktree_purity_gate_state": (worktree_purity_gate_surface_model or {}).get(
                "payload", worktree_purity_gate_surface_model or {}
            ),
            "imperium_address_lattice_state": (address_lattice_surface_model or {}).get(
                "payload", address_lattice_surface_model or {}
            ),
            "imperium_anti_lie_model_state": (anti_lie_model_surface_model or {}).get(
                "payload", anti_lie_model_surface_model or {}
            ),
            "imperium_live_truth_support_loop_state": (live_truth_support_loop_surface_model or {}).get(
                "payload", live_truth_support_loop_surface_model or {}
            ),
            "imperium_dashboard_coverage_state": dashboard_coverage_state,
            "imperium_truth_dominance_state": truth_dominance_state,
            "imperium_repo_hygiene_classification_state": system_brain_state.get("repo_hygiene_classification", {}),
            "imperium_parallel_channels": imperium_parallel_channels,
            "multi_department_models": multi_department_meta,
            "bundle_binding": binding,
            "source_disclosure": binding.get("disclosure", {}),
        }
        base["live"] = build_live_state(
            repo_root=repo_root,
            state=base,
            persist_snapshot=persist_live_snapshot_enabled,
            snapshot_path_value=live_snapshot_path_value,
            event_log_path_value=live_event_log_path_value,
        )
        return base

    with zipfile.ZipFile(bundle_path, "r") as zf:
        names = sorted(zf.namelist())
        md_files = [n for n in names if n.lower().endswith(".md")]
        json_files = [n for n in names if n.lower().endswith(".json")]

        viewpack_member = find_member_by_suffix(names, "docs/review_artifacts/TIKTOK_AGENT_DASHBOARD_VIEWPACK_V1.json")
        panels = []
        parity = {
            "source_kind": "none",
            "required_panels_count": 0,
            "full_panels_count": 0,
            "partial_panels_count": 0,
            "missing_panels_count": 0,
            "overall": "PARTIAL",
        }
        adapter_info: dict = {
            "adapter_path": str(adapter_path),
            "adapter_loaded": False,
            "panel_registry_loaded": False,
        }

        if adapter_path.exists():
            try:
                adapter = load_json_file(adapter_path)
                panels = build_panels_from_adapter(names, adapter)
                adapter_info["adapter_loaded"] = True
                adapter_info["adapter_id"] = adapter.get("adapter_id")
                adapter_info["adapter_version"] = adapter.get("adapter_version")
                panel_registry, panel_registry_error = load_panel_registry(repo_root, adapter)
                if panel_registry_error:
                    adapter_info["panel_registry_error"] = panel_registry_error
                    required_ids = [str(p.get("panel_id", "")).strip() for p in adapter.get("panels", [])]
                else:
                    adapter_info["panel_registry_loaded"] = True
                    required_ids = [str(p.get("id", "")).strip() for p in panel_registry.get("required_panels", [])]
                required_ids = [pid for pid in required_ids if pid]
                parity = build_parity_summary(panels=panels, required_panel_ids=required_ids, source_kind="repo_adapter_primary")
            except Exception as exc:  # pragma: no cover
                adapter_info["adapter_error"] = str(exc)
        else:
            adapter_info["adapter_error"] = "adapter_file_missing"

        if not panels and viewpack_member:
            try:
                viewpack = json.loads(read_zip_text(zf, viewpack_member))
                panels = build_panels_from_viewpack(names, viewpack)
                required_ids = [str(p.get("panel_id", "")).strip() for p in viewpack.get("panels", [])]
                required_ids = [pid for pid in required_ids if pid]
                parity = build_parity_summary(
                    panels=panels,
                    required_panel_ids=required_ids,
                    source_kind="bundle_viewpack_fallback",
                )
                adapter_info["viewpack_fallback_used"] = True
            except Exception as exc:  # pragma: no cover
                panels = [
                    {
                        "panel_id": "panel_source_parse_error",
                        "title": "Panel source parse error",
                        "truth_class": "VIEW_ONLY",
                        "parity_status": "MISSING",
                        "error": str(exc),
                        "source_checks": [],
                    }
                ]
                parity = build_parity_summary(
                    panels=panels,
                    required_panel_ids=["panel_source_parse_error"],
                    source_kind="panel_source_parse_error",
                )

        if not panels:
            parity = build_parity_summary(
                panels=[],
                required_panel_ids=[],
                source_kind="no_panel_source",
            )

        base = {
            "status": "ok",
            "generated_at": utc_now_iso(),
            "bundle_path": str(bundle_path),
            "bundle_name": bundle_path.name,
            "file_counts": {
                "total": len(names),
                "markdown": len(md_files),
                "json": len(json_files),
            },
            "files": names,
            "panels": panels,
            "parity": parity,
            "adapter": adapter_info,
            "factory_overview": (factory_model or {}).get("factory_overview", {}),
            "department_floor": (floor_model or {}).get("departments", []),
            "product_lanes": (lane_model or {}).get("products", []),
            "queue_monitor": (queue_model or {}).get("queues", []),
            "force_map": (force_model or {}).get("force_map", {}),
            "production_history_seed": production_history_seed_state,
            "canon_state_sync": canon_sync_truth,
            "wave1_control_surfaces": wave1_control_state,
            "system_brain_state": system_brain_state,
            "system_semantic_state_surfaces": system_semantic_state_surfaces,
            "prompt_lineage_state": prompt_lineage_state,
            "tiktok_agent_runtime_observability": tiktok_runtime_observability,
            "repo_worktree_hygiene": repo_worktree_hygiene,
            "imperium_evolution_state": imperium_parallel_channels.get("evolution", {}),
            "imperium_inquisition_state": imperium_parallel_channels.get("inquisition", {}),
            "imperium_custodes_state": imperium_parallel_channels.get("custodes", custodes_state),
            "imperium_mechanicus_state": imperium_parallel_channels.get("mechanicus", mechanicus_state),
            "imperium_administratum_state": imperium_parallel_channels.get("administratum", administratum_state),
            "imperium_force_state": imperium_parallel_channels.get("force", force_state),
            "imperium_palace_archive_state": imperium_parallel_channels.get("palace_archive", palace_archive_state),
            "imperium_control_gates_state": imperium_parallel_channels.get("control_gates", control_gates_state),
            "imperium_factory_production_state": imperium_parallel_channels.get("factory", {}),
            "imperium_product_evolution_map": product_evolution_map_model or {},
            "imperium_event_flow_state": event_flow_state,
            "imperium_diff_preview_state": diff_preview_state,
            "imperium_throne_authority_state": system_brain_state.get("throne_authority", {}),
            "imperium_brain_v2_layers": brain_v2_layers,
            "imperium_machine_capability_manifest": machine_capability_manifest_model or {},
            "imperium_organ_strength_surface": organ_strength_surface_model or {},
            "imperium_active_mission_contract": active_mission_contract,
            "imperium_golden_throne_discoverability": golden_throne_discoverability_state,
            "imperium_true_form_state": true_form_matryoshka_surface_model or {},
            "imperium_storage_health_state": storage_health_surface_model or {},
            "imperium_code_bank_state": code_bank_state,
            "imperium_live_work_state": live_work_surface_model or {},
            "imperium_doctrine_integrity_state": doctrine_integrity_surface_model or {},
            "imperium_truth_spine_state": (truth_spine_surface_model or {}).get("payload", truth_spine_surface_model or {}),
            "imperium_dashboard_truth_engine_state": (dashboard_truth_engine_surface_model or {}).get(
                "payload", dashboard_truth_engine_surface_model or {}
            ),
            "imperium_bundle_truth_chamber_state": (bundle_truth_chamber_surface_model or {}).get(
                "payload", bundle_truth_chamber_surface_model or {}
            ),
            "imperium_worktree_purity_gate_state": (worktree_purity_gate_surface_model or {}).get(
                "payload", worktree_purity_gate_surface_model or {}
            ),
            "imperium_address_lattice_state": (address_lattice_surface_model or {}).get(
                "payload", address_lattice_surface_model or {}
            ),
            "imperium_anti_lie_model_state": (anti_lie_model_surface_model or {}).get(
                "payload", anti_lie_model_surface_model or {}
            ),
            "imperium_live_truth_support_loop_state": (live_truth_support_loop_surface_model or {}).get(
                "payload", live_truth_support_loop_surface_model or {}
            ),
            "imperium_dashboard_coverage_state": dashboard_coverage_state,
            "imperium_truth_dominance_state": truth_dominance_state,
            "imperium_repo_hygiene_classification_state": system_brain_state.get("repo_hygiene_classification", {}),
            "imperium_parallel_channels": imperium_parallel_channels,
            "multi_department_models": multi_department_meta,
            "bundle_binding": binding,
            "source_disclosure": binding.get("disclosure", {}),
            "notes": [
                "SCAFFOLDED: local-only bootstrap",
                "PARTIALLY IMPLEMENTED: bundle truth and source trace rendering",
                "REPO ADAPTER PRIMARY: local canonical panel mapping is preferred over bundled stale viewpack",
                "SCAFFOLDED: multi-department skeleton cards from local JSON models",
                "ACTIVE: evolution/inquisition/factory parallel channel surfaces",
            ],
            "repo_root": str(repo_root),
        }
        base["live"] = build_live_state(
            repo_root=repo_root,
            state=base,
            persist_snapshot=persist_live_snapshot_enabled,
            snapshot_path_value=live_snapshot_path_value,
            event_log_path_value=live_event_log_path_value,
        )
        return base


class Handler(SimpleHTTPRequestHandler):
    state: dict = {}
    web_root: Path
    repo_root: Path
    bundle_request_value: str = DEFAULT_ACTIVE_EVIDENCE_BUNDLE_PATH
    adapter_path_value: str = DEFAULT_ADAPTER_PATH
    persist_live_snapshot_enabled: bool = False
    live_snapshot_path_value: str = DEFAULT_LIVE_STATE_SNAPSHOT_PATH
    live_event_log_path_value: str = DEFAULT_LIVE_EVENT_LOG_PATH

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(self.web_root), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _rebuild_state(self) -> dict:
        try:
            bundle_binding = resolve_bundle_binding(
                repo_root=self.repo_root,
                requested_bundle_value=str(self.bundle_request_value or ""),
            )
            bundle_path = Path(bundle_binding.get("active_bundle", {}).get("path", "")).expanduser()
            if not bundle_path.is_absolute():
                bundle_path = (self.repo_root / bundle_path).resolve()
            adapter_path = resolve_path(self.repo_root, str(self.adapter_path_value or DEFAULT_ADAPTER_PATH))
            fresh_state = build_state(
                repo_root=self.repo_root,
                bundle_path=bundle_path,
                adapter_path=adapter_path,
                bundle_binding=bundle_binding,
                persist_live_snapshot_enabled=bool(self.persist_live_snapshot_enabled),
                live_snapshot_path_value=str(self.live_snapshot_path_value or DEFAULT_LIVE_STATE_SNAPSHOT_PATH),
                live_event_log_path_value=str(self.live_event_log_path_value or DEFAULT_LIVE_EVENT_LOG_PATH),
            )
            fresh_state["_persist_live_snapshot"] = bool(self.persist_live_snapshot_enabled)
            fresh_state["_live_snapshot_path"] = str(self.live_snapshot_path_value or DEFAULT_LIVE_STATE_SNAPSHOT_PATH)
            fresh_state["_live_event_log_path"] = str(self.live_event_log_path_value or DEFAULT_LIVE_EVENT_LOG_PATH)
            self.__class__.state = fresh_state
            return fresh_state
        except Exception as exc:  # pragma: no cover
            stale_state = dict(self.state or {})
            stale_state["_state_refresh_error"] = str(exc)
            self.__class__.state = stale_state
            return stale_state

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._send_json({"status": "ok", "time": utc_now_iso()})
            return
        if parsed.path == "/api/state":
            self._send_json(self._rebuild_state())
            return
        if parsed.path == "/api/live_state":
            state = self._rebuild_state()
            self._send_json(
                build_live_state(
                    repo_root=self.repo_root,
                    state=state,
                    persist_snapshot=bool(state.get("_persist_live_snapshot", False)),
                    snapshot_path_value=str(state.get("_live_snapshot_path", DEFAULT_LIVE_STATE_SNAPSHOT_PATH)),
                    event_log_path_value=str(state.get("_live_event_log_path", DEFAULT_LIVE_EVENT_LOG_PATH)),
                )
            )
            return
        if parsed.path == "/api/live_stream":
            self._handle_live_stream(parsed.query)
            return
        if parsed.path == "/api/source":
            self._handle_source(parsed.query)
            return
        super().do_GET()

    def _handle_source(self, query: str) -> None:
        self._rebuild_state()
        params = parse_qs(query)
        member = params.get("member", [""])[0]
        member = posixpath.normpath(member).replace("\\", "/").lstrip("/")
        files = set(self.state.get("files", []))
        if not member or member not in files:
            self._send_json({"status": "not_found", "member": member}, status=HTTPStatus.NOT_FOUND)
            return

        bundle_path = Path(self.state.get("bundle_path", ""))
        if not bundle_path.exists():
            self._send_json({"status": "bundle_missing"}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            with zipfile.ZipFile(bundle_path, "r") as zf:
                text = read_zip_text(zf, member)
            preview = text[:4000]
            self._send_json({"status": "ok", "member": member, "preview": preview})
        except Exception as exc:  # pragma: no cover
            self._send_json({"status": "error", "error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            return

    def _handle_live_stream(self, query: str) -> None:
        params = parse_qs(query)
        try:
            interval_ms = int((params.get("interval_ms", ["1800"]) or ["1800"])[0])
        except (TypeError, ValueError):
            interval_ms = 1800
        interval_ms = max(800, min(interval_ms, 10_000))

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        last_signature = ""
        try:
            while True:
                state = self._rebuild_state()
                tick = build_live_tick_payload(
                    repo_root=self.repo_root,
                    state=state,
                    event_log_path_value=str(state.get("_live_event_log_path", DEFAULT_LIVE_EVENT_LOG_PATH)),
                )
                signature = str(tick.get("signature", ""))
                if signature != last_signature:
                    payload = json.dumps(tick, ensure_ascii=False)
                    chunk = f"event: live_tick\nid: {signature}\ndata: {payload}\n\n"
                    self.wfile.write(chunk.encode("utf-8"))
                    self.wfile.flush()
                    last_signature = signature
                else:
                    self.wfile.write(f": keepalive {utc_now_iso()}\n\n".encode("utf-8"))
                    self.wfile.flush()
                time.sleep(interval_ms / 1000.0)
        except (BrokenPipeError, ConnectionResetError, OSError):
            return


class QuietThreadingHTTPServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):  # pragma: no cover
        _, exc_value, _ = sys.exc_info()
        if isinstance(exc_value, (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError)):
            return
        super().handle_error(request, client_address)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Local-only Factory Observation Window V1 scaffold server.")
    p.add_argument(
        "--bundle",
        default=DEFAULT_ACTIVE_EVIDENCE_BUNDLE_PATH,
        help="Primary bundle path (repo-relative or absolute). Active ongoing alias is default.",
    )
    p.add_argument("--host", default="127.0.0.1", help="Bind host. Default is localhost-only.")
    p.add_argument("--port", type=int, default=8777, help="Bind port.")
    p.add_argument(
        "--adapter",
        default=DEFAULT_ADAPTER_PATH,
        help="Adapter JSON for bundle-to-panel mapping when viewpack is absent in bundle.",
    )
    p.add_argument(
        "--live-event-log",
        default=DEFAULT_LIVE_EVENT_LOG_PATH,
        help="Optional JSONL log path for local live events.",
    )
    p.add_argument(
        "--live-snapshot-path",
        default=DEFAULT_LIVE_STATE_SNAPSHOT_PATH,
        help="Path for optional persisted live snapshot JSON.",
    )
    p.add_argument(
        "--persist-live-snapshot",
        action="store_true",
        help="Persist generated /api/live_state snapshots to --live-snapshot-path.",
    )
    p.add_argument("--dry-run", action="store_true", help="Only parse bundle and print state summary.")
    return p


def main() -> int:
    args = build_parser().parse_args()
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]
    bundle_binding = resolve_bundle_binding(repo_root=repo_root, requested_bundle_value=args.bundle)
    bundle_path = Path(bundle_binding.get("active_bundle", {}).get("path", "")).expanduser()
    if not bundle_path.is_absolute():
        bundle_path = (repo_root / bundle_path).resolve()
    adapter_path = resolve_path(repo_root, args.adapter)

    state = build_state(
        repo_root=repo_root,
        bundle_path=bundle_path,
        adapter_path=adapter_path,
        bundle_binding=bundle_binding,
        persist_live_snapshot_enabled=bool(args.persist_live_snapshot),
        live_snapshot_path_value=args.live_snapshot_path,
        live_event_log_path_value=args.live_event_log,
    )
    state["_persist_live_snapshot"] = bool(args.persist_live_snapshot)
    state["_live_snapshot_path"] = args.live_snapshot_path
    state["_live_event_log_path"] = args.live_event_log
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": state.get("status"),
                    "bundle_path": state.get("bundle_path"),
                    "bundle_name": state.get("bundle_name"),
                    "bundle_binding": state.get("bundle_binding"),
                    "file_counts": state.get("file_counts"),
                    "panels_count": len(state.get("panels", [])),
                    "department_floor_count": len(state.get("department_floor", [])),
                    "product_lanes_count": len(state.get("product_lanes", [])),
                    "queue_count": len(state.get("queue_monitor", [])),
                    "parity": state.get("parity", {}),
                    "adapter": state.get("adapter", {}),
                    "multi_department_models": state.get("multi_department_models", {}),
                    "live_snapshot_generated": bool(state.get("live")),
                    "live_change_feed_count": len((state.get("live", {}) or {}).get("live_change_feed", [])),
                    "live_preview_count": len((state.get("live", {}) or {}).get("live_preview_registry", [])),
                    "canon_state_sync_loaded": bool(state.get("canon_state_sync", {})),
                    "wave1_control_surfaces_loaded": bool(state.get("wave1_control_surfaces", {})),
                    "live_event_log_loaded": bool(((state.get("live", {}) or {}).get("live_event_log_meta", {}) or {}).get("loaded", False)),
                    "live_snapshot_persist_enabled": bool(args.persist_live_snapshot),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    web_root = script_path.parents[1] / "web"
    Handler.state = state
    Handler.web_root = web_root
    Handler.repo_root = repo_root
    Handler.bundle_request_value = args.bundle
    Handler.adapter_path_value = args.adapter
    Handler.persist_live_snapshot_enabled = bool(args.persist_live_snapshot)
    Handler.live_snapshot_path_value = args.live_snapshot_path
    Handler.live_event_log_path_value = args.live_event_log
    server = QuietThreadingHTTPServer((args.host, args.port), Handler)
    print(f"[factory-observation-v1] serving on http://{args.host}:{args.port}")
    print(f"[factory-observation-v1] active bundle: {bundle_path}")
    print(
        "[factory-observation-v1] selection mode: "
        + str((state.get("bundle_binding", {}) or {}).get("selection_mode", "unknown"))
    )
    print(
        "[factory-observation-v1] fallback bundle: "
        + str(
            (
                (state.get("bundle_binding", {}) or {}).get("fallback_bundle", {}) or {}
            ).get("path", "")
        )
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

