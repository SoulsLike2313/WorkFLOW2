#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CANONICAL_LOCAL_ROOT = r"E:\CVVCODEX"
CANONICAL_REMOTE = "safe_mirror"
CANONICAL_BRANCH = "main"
CANONICAL_REMOTE_REF = f"{CANONICAL_REMOTE}/{CANONICAL_BRANCH}"
CANONICAL_SAFE_REPO = "WorkFLOW2"
ACTIVE_PROJECT_SLUG = "platform_test_agent"
GOLDEN_THRONE_AUTHORITY_ANCHOR_RELATIVE_PATH = "docs/governance/GOLDEN_THRONE_AUTHORITY_ANCHOR_V1.json"
IMPERIUM_REPO_HYGIENE_SURFACE_RELATIVE_PATH = (
    "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_REPO_HYGIENE_CLASSIFICATION_SURFACE_V1.json"
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = REPO_ROOT / "runtime" / "repo_control_center"
OBSERVATION_CYCLE_STATE_PATH = RUNTIME_DIR / "promotion_observation_cycles.json"
ADMIN_RUNTIME_DIR = REPO_ROOT / "runtime" / "administratum"

GATE_POLICY_REL = "runtime/administratum/IMPERIUM_GATE_POLICY_V1.json"
OWNER_OVERRIDE_REL = "runtime/administratum/IMPERIUM_OWNER_OVERRIDE_GATE_V1.json"
ENTITY_REGISTRY_REL = "runtime/administratum/IMPERIUM_ENTITY_REGISTRY_V1.json"
ZONE_CLASS_POLICY_REL = "runtime/administratum/IMPERIUM_ZONE_CLASS_POLICY_V1.json"
ZONE_TRANSITION_POLICY_REL = "runtime/administratum/IMPERIUM_ZONE_TRANSITION_POLICY_V1.json"
ZONE_TRANSITION_LEDGER_REL = "runtime/administratum/IMPERIUM_ZONE_TRANSITION_LEDGER_V1.json"
DASHBOARD_SIGNAL_REGISTRY_REL = "runtime/administratum/IMPERIUM_DASHBOARD_SIGNAL_REGISTRY_V1.json"
TOMB_REGISTRY_REL = "runtime/administratum/IMPERIUM_TOMB_REGISTRY_V1.json"
REIMPORT_REQUESTS_REL = "runtime/administratum/IMPERIUM_REIMPORT_REQUESTS_V1.json"

GATE_SUMMARY_REL = "runtime/administratum/IMPERIUM_GATE_EXECUTION_SUMMARY_V1.json"
GATE_AUDIT_LOG_REL = "runtime/administratum/IMPERIUM_GATE_AUDIT_LOG_V1.jsonl"
CANONICAL_WRITE_STATE_REL = "runtime/administratum/IMPERIUM_CANONICAL_WRITE_GATE_STATE_V1.json"
REGISTRY_VALIDATION_STATE_REL = "runtime/administratum/IMPERIUM_REGISTRY_VALIDATION_GATE_STATE_V1.json"
ZONE_TRANSITION_STATE_REL = "runtime/administratum/IMPERIUM_ZONE_TRANSITION_GATE_STATE_V1.json"
DASHBOARD_TRUTH_STATE_REL = "runtime/administratum/IMPERIUM_DASHBOARD_TRUTH_VALIDATOR_STATE_V1.json"
TOMB_REIMPORT_STATE_REL = "runtime/administratum/IMPERIUM_TOMB_REIMPORT_BLOCKER_STATE_V1.json"

LAW_LOCK_CANON_REL = "docs/governance/IMPERIUM_CANONICAL_PATH_UNIFICATION_AND_LAW_LOCK_V1.md"
LAW_LOCK_REGISTRY_REL = "docs/governance/IMPERIUM_FOUNDATION_LAW_LOCK_REGISTRY_V1.json"
OWNER_COMMAND_GATE_CONTRACT_REL = "workspace_config/owner_command_gate_contract.json"
INTEGRATION_PORT_GATE_CONTRACT_REL = "workspace_config/integration_port_gate_contract.json"
OWNER_COMMAND_INBOX_REL = "runtime/administratum/IMPERIUM_OWNER_COMMAND_INBOX_V1.json"
LAW_LOCK_STATUS_REL = "runtime/administratum/IMPERIUM_FOUNDATION_LAW_LOCK_STATUS_V1.json"
DUPLICATE_LAW_SCAN_REL = "runtime/administratum/IMPERIUM_DUPLICATE_LAW_SCAN_V1.json"
AMBIGUOUS_COMMAND_GATE_STATUS_REL = "runtime/administratum/IMPERIUM_AMBIGUOUS_COMMAND_HARD_GATE_STATUS_V1.json"
OWNER_COMMAND_GATE_RUNTIME_STATE_REL = "runtime/administratum/IMPERIUM_OWNER_COMMAND_GATE_RUNTIME_STATE_V1.json"
PORT_INTEGRATION_GATE_STATUS_REL = "runtime/administratum/IMPERIUM_PORT_INTEGRATION_GATE_STATUS_V1.json"

CORE_DOCS = [
    "README.md",
    "REPO_MAP.md",
    "MACHINE_CONTEXT.md",
    "docs/INSTRUCTION_INDEX.md",
    "docs/CHATGPT_BUNDLE_EXPORT.md",
    "docs/repo_publication_policy.md",
    "workspace_config/GITHUB_SYNC_POLICY.md",
    "workspace_config/AGENT_EXECUTION_POLICY.md",
    "workspace_config/MACHINE_REPO_READING_RULES.md",
    "workspace_config/workspace_manifest.json",
    "workspace_config/codex_manifest.json",
]

OPERATOR_QUERY_LAYER_DOCS = [
    "docs/governance/OPERATOR_QUERY_LAYER_BASELINE.md",
    "docs/governance/OPERATOR_QUERY_CATALOG.md",
    "docs/governance/OPERATOR_RESPONSE_CONTRACT.md",
    "docs/governance/OPERATOR_INTENT_ROUTING.md",
]

OPERATOR_COMMAND_LAYER_DOCS = [
    "docs/governance/OPERATOR_COMMAND_EXECUTION_BASELINE.md",
    "docs/governance/OPERATOR_COMMAND_CATALOG.md",
    "docs/governance/OPERATOR_COMMAND_EXECUTION_CONTRACT.md",
    "docs/governance/OPERATOR_COMMAND_INTENT_ROUTING.md",
]

OPERATOR_COMMAND_LAYER_FILES = [
    "workspace_config/operator_command_registry.json",
    "scripts/operator_command_surface.py",
    "docs/review_artifacts/OPERATOR_COMMAND_GOLDEN_PACK.json",
]

OPERATOR_PROGRAM_LAYER_DOCS = [
    "docs/governance/OPERATOR_PROGRAM_EXECUTION_BASELINE.md",
    "docs/governance/OPERATOR_PROGRAM_CATALOG.md",
    "docs/governance/OPERATOR_PROGRAM_EXECUTION_CONTRACT.md",
    "docs/governance/OPERATOR_PROGRAM_INTENT_ROUTING.md",
]

OPERATOR_PROGRAM_LAYER_FILES = [
    "workspace_config/operator_program_registry.json",
    "scripts/operator_program_surface.py",
    "docs/review_artifacts/OPERATOR_PROGRAM_GOLDEN_PACK.json",
]

OPERATOR_MISSION_LAYER_DOCS = [
    "docs/governance/OPERATOR_MISSION_LAYER_BASELINE.md",
    "docs/governance/OPERATOR_MISSION_BASELINE.md",
    "docs/governance/OPERATOR_MISSION_CONTRACT.md",
    "docs/governance/OPERATOR_MISSION_REGISTRY.md",
]

OPERATOR_MISSION_LAYER_FILES = [
    "workspace_config/operator_mission_registry.json",
    "scripts/operator_mission_surface.py",
    "docs/review_artifacts/OPERATOR_MISSION_GOLDEN_PACK_FINAL.json",
    "docs/review_artifacts/OPERATOR_MISSION_CERTIFICATION_REPORT.md",
]

GOVERNANCE_BRAIN_STACK = [
    "docs/governance/FIRST_PRINCIPLES.md",
    "docs/governance/GOVERNANCE_HIERARCHY.md",
    "docs/governance/SELF_VERIFICATION_POLICY.md",
    "docs/governance/CONTRADICTION_CONTROL_POLICY.md",
    "docs/governance/ADMISSION_GATE_POLICY.md",
    "docs/governance/ANTI_DRIFT_POLICY.md",
    "docs/governance/DEVIATION_INTELLIGENCE_POLICY.md",
    "docs/governance/GOVERNANCE_EVOLUTION_POLICY.md",
    "docs/governance/CREATIVE_REASONING_POLICY.md",
    "docs/governance/AGENT_CHARACTER_PROFILE.md",
]

EVOLUTION_LAYER_DOCS = [
    "docs/governance/EVOLUTION_READINESS_POLICY.md",
    "docs/governance/MODEL_MATURITY_MODEL.md",
    "docs/governance/EVOLUTION_SIGNAL_REGISTRY.md",
    "docs/governance/POLICY_EVOLUTION_LOG.md",
    "docs/governance/NEXT_EVOLUTION_CANDIDATE.md",
]

FEDERATION_LAYER_DOCS = [
    "docs/governance/CREATOR_AUTHORITY_POLICY.md",
    "docs/governance/HELPER_NODE_POLICY.md",
    "docs/governance/TASK_ID_EXECUTION_CONTRACT.md",
    "docs/governance/EXTERNAL_BLOCK_HANDOFF_POLICY.md",
    "docs/governance/INTEGRATION_INBOX_POLICY.md",
    "docs/governance/CANONICAL_MACHINE_PROTECTION_POLICY.md",
    "docs/governance/FEDERATION_ARCHITECTURE.md",
]

FEDERATION_CONTRACT_FILES = [
    "workspace_config/federation_mode_contract.json",
    "workspace_config/block_task_schema.json",
    "workspace_config/handoff_package_schema.json",
    "workspace_config/integration_inbox_contract.json",
    "workspace_config/creator_mode_detection_contract.json",
]

INTEGRATION_STRUCTURE_PATHS = [
    "integration/README.md",
    "integration/inbox",
    "integration/review_queue",
    "integration/accepted",
    "integration/rejected",
    "integration/quarantine",
]

TASK_FLOW_FILES = [
    "tasks/README.md",
    "tasks/registry/example_block_task.json",
    "scripts/detect_machine_mode.py",
    "scripts/resolve_task_id.py",
    "scripts/prepare_handoff_package.py",
    "scripts/review_integration_inbox.py",
]

GOVERNANCE_V11_HARDENING_DOCS = [
    "docs/governance/POLICY_CHANGE_AUTHORITY_POLICY.md",
    "docs/governance/INCIDENT_AND_ROLLBACK_POLICY.md",
    "docs/governance/VERIFICATION_DEPTH_POLICY.md",
    "docs/governance/EVIDENCE_RETENTION_POLICY.md",
    "docs/governance/PROMOTION_THRESHOLD_POLICY.md",
    "docs/governance/SECURITY_AND_EXPOSURE_INCIDENT_POLICY.md",
    "docs/governance/DEPRECATION_AND_RETIREMENT_POLICY.md",
    "docs/governance/OPERATIONAL_METRICS_POLICY.md",
    "docs/governance/NOTIFICATION_AND_ESCALATION_POLICY.md",
    "docs/governance/GOVERNANCE_SCHEMA_VERSIONING_POLICY.md",
]

GOVERNANCE_ACCEPTANCE_DOC = "docs/governance/GOVERNANCE_ACCEPTANCE_GATE.md"
MACHINE_BOOTSTRAP_CONTRACT = "docs/governance/MACHINE_BOOTSTRAP_CONTRACT.md"
CANONICAL_SOURCE_PRECEDENCE_DOC = "docs/governance/CANONICAL_SOURCE_PRECEDENCE.md"
ZERO_CONFIG_POLICY_DOC = "docs/governance/ZERO_CONFIG_OPERATION_POLICY.md"
MACHINE_OPERATOR_GUIDE_DOC = "docs/governance/MACHINE_OPERATOR_GUIDE.md"
MACHINE_CAPABILITIES_SUMMARY_DOC = "docs/governance/MACHINE_CAPABILITIES_SUMMARY.md"
POLICY_DIGEST_DOC = "docs/governance/POLICY_DIGEST.md"

SAFE_STATE_FILES = [
    "workspace_config/SAFE_MIRROR_MANIFEST.json",
    "docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md",
]

BOOTSTRAP_REQUIRED = [
    "README.md",
    "workspace_config/workspace_manifest.json",
    "workspace_config/codex_manifest.json",
    "REPO_MAP.md",
    "MACHINE_CONTEXT.md",
    "docs/INSTRUCTION_INDEX.md",
    "docs/CURRENT_PLATFORM_STATE.md",
    "docs/NEXT_CANONICAL_STEP.md",
    *GOVERNANCE_BRAIN_STACK,
    *EVOLUTION_LAYER_DOCS,
    "docs/governance/MACHINE_BOOTSTRAP_CONTRACT.md",
    "docs/governance/CANONICAL_SOURCE_PRECEDENCE.md",
    "docs/governance/ZERO_CONFIG_OPERATION_POLICY.md",
    "docs/governance/GOVERNANCE_ACCEPTANCE_GATE.md",
    *FEDERATION_LAYER_DOCS,
    *OPERATOR_QUERY_LAYER_DOCS,
    *OPERATOR_COMMAND_LAYER_DOCS,
    *OPERATOR_COMMAND_LAYER_FILES,
    *OPERATOR_PROGRAM_LAYER_DOCS,
    *OPERATOR_PROGRAM_LAYER_FILES,
    *OPERATOR_MISSION_LAYER_DOCS,
    *OPERATOR_MISSION_LAYER_FILES,
    "scripts/repo_control_center.py",
    "workspace_config/GITHUB_SYNC_POLICY.md",
    "workspace_config/AGENT_EXECUTION_POLICY.md",
    "workspace_config/MACHINE_REPO_READING_RULES.md",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class GitState:
    branch: str
    head: str
    remote_head: str
    ahead: int
    behind: int
    worktree_clean: bool
    status_short: str


def run_cmd(args: list[str], allow_fail: bool = False) -> str:
    completed = subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0 and not allow_fail:
        raise RuntimeError(f"command failed: {' '.join(args)} :: {completed.stderr.strip()}")
    return completed.stdout.strip()


def read_text(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8-sig")


def read_text_loose(rel: str) -> str:
    raw = (REPO_ROOT / rel).read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1251", "latin-1"):
        try:
            return raw.decode(encoding)
        except Exception:
            continue
    return raw.decode("utf-8", errors="ignore")


def load_json(rel: str) -> dict[str, Any]:
    return json.loads(read_text(rel))


def load_json_if_exists(rel: str) -> dict[str, Any]:
    if not exists(rel):
        return {}
    try:
        return load_json(rel)
    except Exception:
        return {}


def exists(rel: str) -> bool:
    return (REPO_ROOT / rel).exists()


def write_json_rel(rel: str, payload: dict[str, Any]) -> None:
    path = REPO_ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_iso_ts(raw: Any) -> datetime | None:
    text = str(raw or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None


def path_is_git_tracked(rel: str) -> bool:
    if not str(rel).strip():
        return False
    proc = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", rel],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode == 0


def append_jsonl_rel(rel: str, payload: dict[str, Any]) -> None:
    path = REPO_ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def normalize_semantic_token(value: str) -> str:
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def contains_failure_signal(value: Any) -> bool:
    fail_tokens = {"FAIL", "BLOCKED", "NOT_TRUSTED", "REJECTED"}
    if isinstance(value, dict):
        return any(contains_failure_signal(v) for v in value.values())
    if isinstance(value, list):
        return any(contains_failure_signal(v) for v in value)
    return str(value).strip().upper() in fail_tokens


def build_git_state(fetch: bool) -> GitState:
    if fetch:
        run_cmd(["git", "fetch", "--all", "--prune"], allow_fail=True)

    branch = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    head = run_cmd(["git", "rev-parse", "HEAD"])
    remote_head = run_cmd(["git", "rev-parse", CANONICAL_REMOTE_REF])
    status_short = run_cmd(["git", "status", "-sb"])
    worktree_clean = run_cmd(["git", "status", "--porcelain"]) == ""
    counts = run_cmd(["git", "rev-list", "--left-right", "--count", f"HEAD...{CANONICAL_REMOTE_REF}"])
    ahead, behind = [int(x) for x in counts.split()]
    return GitState(
        branch=branch,
        head=head,
        remote_head=remote_head,
        ahead=ahead,
        behind=behind,
        worktree_clean=worktree_clean,
        status_short=status_short,
    )


def missing_paths(paths: list[str]) -> list[str]:
    return [p for p in paths if not exists(p)]


def is_sovereign_mode(mode: str) -> bool:
    return str(mode or "").strip().lower() in {"emperor", "creator"}


def is_sync_aligned(verdict: str) -> bool:
    return str(verdict or "").strip().upper() in {"IN_SYNC", "IN_SYNC_CLASSIFIED"}


def parse_live_worktree_counts() -> dict[str, Any]:
    raw = run_cmd(["git", "status", "--porcelain=v1"], allow_fail=True)
    tracked_dirty_count = 0
    untracked_count = 0
    for line in str(raw or "").splitlines():
        row = str(line or "")
        if row.startswith("?? "):
            untracked_count += 1
            continue
        if len(row) < 2:
            continue
        x = row[0]
        y = row[1]
        if x not in {" ", "?"} or y not in {" ", "?"}:
            tracked_dirty_count += 1
    if tracked_dirty_count == 0 and untracked_count == 0:
        cleanliness_verdict = "CLEAN"
    elif tracked_dirty_count > 0 and untracked_count == 0:
        cleanliness_verdict = "DIRTY_TRACKED_ONLY"
    elif tracked_dirty_count == 0 and untracked_count > 0:
        cleanliness_verdict = "DIRTY_UNTRACKED_ONLY"
    else:
        cleanliness_verdict = "DIRTY_MIXED"
    return {
        "cleanliness_verdict": cleanliness_verdict,
        "tracked_dirty_count": tracked_dirty_count,
        "untracked_count": untracked_count,
    }


def build_hygiene_classification_context(git_state: GitState | None = None) -> dict[str, Any]:
    surface = load_json_if_exists(IMPERIUM_REPO_HYGIENE_SURFACE_RELATIVE_PATH)
    counts = dict(surface.get("classification_counts", {}) or {})
    live = parse_live_worktree_counts()
    live_cleanliness = str(live.get("cleanliness_verdict", "UNKNOWN"))
    live_tracked = int(live.get("tracked_dirty_count", 0) or 0)
    live_untracked = int(live.get("untracked_count", 0) or 0)
    if git_state and bool(git_state.worktree_clean):
        live_cleanliness = "CLEAN"
        live_tracked = 0
        live_untracked = 0

    surface_cleanliness = str(surface.get("cleanliness_verdict", "UNKNOWN"))
    surface_tracked = int(surface.get("tracked_dirty_count", 0) or 0)
    surface_untracked = int(surface.get("untracked_count", 0) or 0)
    surface_stale_against_live = bool(
        surface
        and (
            surface_cleanliness != live_cleanliness
            or surface_tracked != live_tracked
            or surface_untracked != live_untracked
        )
    )

    classification_counts = {
        "CANONICAL_MUST_TRACK": int(counts.get("CANONICAL_MUST_TRACK", 0) or 0),
        "GENERATED_RUNTIME_ONLY": int(counts.get("GENERATED_RUNTIME_ONLY", 0) or 0),
        "REVIEW_ARTIFACT_RETENTION": int(counts.get("REVIEW_ARTIFACT_RETENTION", 0) or 0),
        "JUNK_OR_RESIDUE": int(counts.get("JUNK_OR_RESIDUE", 0) or 0),
        "NEEDS_OWNER_DECISION": int(counts.get("NEEDS_OWNER_DECISION", 0) or 0),
    }
    if live_cleanliness == "CLEAN":
        classification_counts = {
            "CANONICAL_MUST_TRACK": 0,
            "GENERATED_RUNTIME_ONLY": 0,
            "REVIEW_ARTIFACT_RETENTION": 0,
            "JUNK_OR_RESIDUE": 0,
            "NEEDS_OWNER_DECISION": 0,
        }

    return {
        "surface_loaded": bool(surface),
        "source_path": IMPERIUM_REPO_HYGIENE_SURFACE_RELATIVE_PATH,
        "generated_at_utc": str(surface.get("generated_at_utc", "")),
        "cleanliness_verdict": live_cleanliness,
        "tracked_dirty_count": live_tracked,
        "untracked_count": live_untracked,
        "classification_counts": classification_counts,
        "live_git_snapshot": live,
        "surface_stale_against_live": surface_stale_against_live,
        "surface_cleanliness_verdict": surface_cleanliness,
        "surface_tracked_dirty_count": surface_tracked,
        "surface_untracked_count": surface_untracked,
    }


def is_controlled_classified_dirty(hygiene: dict[str, Any]) -> bool:
    counts = dict((hygiene or {}).get("classification_counts", {}) or {})
    return bool(
        (hygiene or {}).get("surface_loaded")
        and str((hygiene or {}).get("cleanliness_verdict", "")).upper() == "DIRTY_TRACKED_ONLY"
        and int((hygiene or {}).get("untracked_count", 0) or 0) == 0
        and counts.get("NEEDS_OWNER_DECISION", 0) == 0
        and counts.get("JUNK_OR_RESIDUE", 0) == 0
        and counts.get("GENERATED_RUNTIME_ONLY", 0) == 0
    )


def load_observation_cycle_state() -> dict[str, Any]:
    if not OBSERVATION_CYCLE_STATE_PATH.exists():
        return {
            "schema_version": "promotion_observation_cycles.v1",
            "generated_at_utc": utc_now(),
            "cycles": [],
            "observed_clean_cycles": 0,
        }
    try:
        payload = json.loads(OBSERVATION_CYCLE_STATE_PATH.read_text(encoding="utf-8-sig"))
    except Exception:
        payload = {}
    cycles = list(payload.get("cycles", []) or [])
    return {
        "schema_version": "promotion_observation_cycles.v1",
        "generated_at_utc": str(payload.get("generated_at_utc", "")),
        "cycles": cycles,
        "observed_clean_cycles": int(payload.get("observed_clean_cycles", 0) or 0),
    }


def persist_observation_cycle_state(
    *,
    run_id: str,
    git_state: GitState,
    sync: dict[str, Any],
    trust: dict[str, Any],
    mirror: dict[str, Any],
    governance_acceptance: dict[str, Any],
    admission: dict[str, Any],
    contradictions: dict[str, Any],
) -> dict[str, Any]:
    current_cycle_clean = (
        sync["verdict"] == "IN_SYNC"
        and git_state.worktree_clean
        and git_state.ahead == 0
        and git_state.behind == 0
        and contradictions["critical_count"] == 0
        and trust["verdict"] == "TRUSTED"
        and mirror["verdict"] == "PASS"
        and governance_acceptance["verdict"] == "PASS"
        and admission["verdict"] == "ADMISSIBLE"
    )

    state = load_observation_cycle_state()
    cycles = list(state.get("cycles", []) or [])
    cycles.append(
        {
            "run_id": run_id,
            "generated_at_utc": utc_now(),
            "head": git_state.head,
            "safe_mirror_main": git_state.remote_head,
            "sync_verdict": sync["verdict"],
            "trust_verdict": trust["verdict"],
            "mirror_verdict": mirror["verdict"],
            "governance_acceptance_verdict": governance_acceptance["verdict"],
            "admission_verdict": admission["verdict"],
            "critical_contradictions": contradictions["critical_count"],
            "worktree_clean": git_state.worktree_clean,
            "clean_cycle": bool(current_cycle_clean),
        }
    )
    cycles = cycles[-200:]

    observed_clean_cycles = 0
    for item in reversed(cycles):
        if bool(item.get("clean_cycle", False)):
            observed_clean_cycles += 1
        else:
            break

    payload = {
        "schema_version": "promotion_observation_cycles.v1",
        "generated_at_utc": utc_now(),
        "cycles": cycles,
        "observed_clean_cycles": observed_clean_cycles,
    }
    OBSERVATION_CYCLE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    OBSERVATION_CYCLE_STATE_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "path": str(OBSERVATION_CYCLE_STATE_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "entries_total": len(cycles),
        "observed_clean_cycles": observed_clean_cycles,
        "current_cycle_clean": bool(current_cycle_clean),
    }


def parse_numbered_markdown_paths(rel: str) -> list[str]:
    if not exists(rel):
        return []
    items: list[str] = []
    for line in read_text(rel).splitlines():
        match = re.match(r"\s*\d+\.\s+`([^`]+)`", line)
        if match:
            items.append(match.group(1).strip())
    return items


def bootstrap_enforcement_checks() -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    evidence: dict[str, Any] = {}

    cm = load_json("workspace_config/codex_manifest.json")
    bootstrap = cm.get("bootstrap_read_order", [])
    evidence["bootstrap_exists"] = isinstance(bootstrap, list)
    if not isinstance(bootstrap, list) or not bootstrap:
        blockers.append("bootstrap_read_order missing or empty in codex_manifest")
        bootstrap = []

    normalized_bootstrap = [str(x).strip() for x in bootstrap if str(x).strip()]
    evidence["bootstrap_count"] = len(normalized_bootstrap)
    evidence["bootstrap_unique_count"] = len(set(normalized_bootstrap))

    if len(set(normalized_bootstrap)) != len(normalized_bootstrap):
        blockers.append("bootstrap_read_order contains duplicate paths")

    missing_from_repo = [p for p in normalized_bootstrap if not exists(p)]
    evidence["bootstrap_missing_paths"] = missing_from_repo
    if missing_from_repo:
        blockers.extend([f"bootstrap path missing in repo: {p}" for p in missing_from_repo])

    missing_required = [p for p in BOOTSTRAP_REQUIRED if p not in normalized_bootstrap]
    evidence["bootstrap_missing_required"] = missing_required
    if missing_required:
        blockers.extend([f"bootstrap missing required path: {p}" for p in missing_required])

    legacy_tokens = [
        p
        for p in normalized_bootstrap
        if "PUBLIC_REPO_SANITIZATION_REPORT.md" in p or "tools/public_mirror" in p
    ]
    evidence["legacy_tokens_in_bootstrap"] = legacy_tokens
    if legacy_tokens:
        blockers.extend([f"legacy/non-canonical bootstrap entry: {p}" for p in legacy_tokens])

    canonical_prefix = [
        "README.md",
        "workspace_config/workspace_manifest.json",
        "workspace_config/codex_manifest.json",
        "REPO_MAP.md",
        "MACHINE_CONTEXT.md",
        "docs/INSTRUCTION_INDEX.md",
    ]
    evidence["canonical_prefix_expected"] = canonical_prefix
    evidence["canonical_prefix_actual"] = normalized_bootstrap[: len(canonical_prefix)]
    if normalized_bootstrap[: len(canonical_prefix)] != canonical_prefix:
        blockers.append("bootstrap canonical prefix mismatch")

    repo_control_entries = [p for p in normalized_bootstrap if p.endswith("repo_control_center.py")]
    evidence["repo_control_entries"] = repo_control_entries
    if len(repo_control_entries) != 1 or repo_control_entries[0] != "scripts/repo_control_center.py":
        blockers.append("conflicting bootstrap entrypoints for repo control center")

    if "docs/governance/FIRST_PRINCIPLES.md" in normalized_bootstrap and "docs/governance/GOVERNANCE_HIERARCHY.md" in normalized_bootstrap:
        if normalized_bootstrap.index("docs/governance/FIRST_PRINCIPLES.md") > normalized_bootstrap.index("docs/governance/GOVERNANCE_HIERARCHY.md"):
            blockers.append("bootstrap precedence violated: FIRST_PRINCIPLES appears after GOVERNANCE_HIERARCHY")

    bootstrap_rules_list = parse_numbered_markdown_paths("workspace_config/MACHINE_REPO_READING_RULES.md")
    machine_context_list = parse_numbered_markdown_paths("MACHINE_CONTEXT.md")
    evidence["rules_list_count"] = len(bootstrap_rules_list)
    evidence["machine_context_list_count"] = len(machine_context_list)
    if bootstrap_rules_list and set(bootstrap_rules_list) != set(normalized_bootstrap):
        warnings.append("MACHINE_REPO_READING_RULES list differs from codex_manifest bootstrap set")
    if machine_context_list and set(machine_context_list) != set(normalized_bootstrap):
        warnings.append("MACHINE_CONTEXT bootstrap list differs from codex_manifest bootstrap set")

    for rel in [MACHINE_BOOTSTRAP_CONTRACT, CANONICAL_SOURCE_PRECEDENCE_DOC, ZERO_CONFIG_POLICY_DOC]:
        if not exists(rel):
            blockers.append(f"missing bootstrap/precedence contract: {rel}")

    if blockers:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "WARNING"
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "basis": "single canonical bootstrap contract enforcement",
        "evidence": evidence,
        "blockers": blockers,
        "warnings": warnings,
        "next_step": "Resolve bootstrap contract blockers/warnings." if (blockers or warnings) else "Bootstrap contract enforced.",
    }


def machine_mode_checks() -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    evidence: dict[str, Any] = {}

    detect_script = REPO_ROOT / "scripts/detect_machine_mode.py"
    detection_contract = REPO_ROOT / "workspace_config/creator_mode_detection_contract.json"
    federation_contract = REPO_ROOT / "workspace_config/federation_mode_contract.json"

    if not detect_script.exists():
        blockers.append("missing scripts/detect_machine_mode.py")
    if not federation_contract.exists():
        blockers.append("missing workspace_config/federation_mode_contract.json")

    if detection_contract.exists():
        text = detection_contract.read_text(encoding="utf-8-sig")
        if re.search(r"[A-Za-z]:\\\\", text):
            warnings.append("legacy creator detection contract contains local absolute path (compatibility surface)")

    payload: dict[str, Any] | None = None
    if not blockers:
        proc = subprocess.run(
            ["python", str(detect_script), "--intent", "auto", "--json-only", "--no-write"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        evidence["detect_exit_code"] = proc.returncode
        if proc.returncode != 0:
            blockers.append("detect_machine_mode.py returned non-zero")
        else:
            try:
                payload = json.loads(proc.stdout)
            except Exception as exc:
                blockers.append(f"detect_machine_mode output is not valid JSON: {exc}")

    if payload:
        evidence["machine_mode"] = payload.get("machine_mode")
        evidence["helper_tier"] = payload.get("helper_tier")
        evidence["detected_rank"] = payload.get("detected_rank")
        evidence["authority_source"] = payload.get("authority_source")
        evidence["authority_present"] = payload.get("authority", {}).get("authority_present")
        evidence["detection_state"] = payload.get("authority", {}).get("detection_state")
        evidence["work_posture"] = payload.get("work_posture")
        evidence["legacy_creator_authority_present"] = payload.get("legacy_creator_authority", {}).get("authority_present")
        evidence["legacy_creator_detection_state"] = payload.get("legacy_creator_authority", {}).get("detection_state")
        evidence["allowed_operations"] = payload.get("operations", {}).get("allowed", [])
        evidence["forbidden_operations"] = payload.get("operations", {}).get("forbidden", [])
        evidence["posture_overlay"] = payload.get("operations", {}).get("posture_overlay", {})
        evidence["warnings"] = payload.get("warnings", [])
        evidence["rank_detection_verification_verdict"] = payload.get("rank_detection", {}).get("verification_verdict")
        evidence["rank_detection"] = payload.get("rank_detection", {})
        evidence["throne_anchor_path"] = payload.get("rank_detection", {}).get("throne_anchor_path")
        evidence["emperor_status"] = payload.get("rank_detection", {}).get("emperor_status")
        evidence["throne_breach"] = payload.get("rank_detection", {}).get("throne_breach")
        evidence["emperor_status_blocked"] = payload.get("rank_detection", {}).get("emperor_status_blocked")

        mode = str(payload.get("machine_mode", "helper"))
        tier = str(payload.get("helper_tier", "") or "")
        detected_rank = str(payload.get("detected_rank", "UNKNOWN"))
        if mode == "helper":
            warnings.append(f"machine is in helper mode (tier={tier or 'unknown'})")
        if is_sovereign_mode(mode) and detected_rank != "EMPEROR":
            blockers.append("sovereign mode derived without EMPEROR rank")
        if mode == "creator":
            warnings.append("legacy creator mode alias detected; canonical sovereign mode is emperor")
        if payload.get("blockers"):
            blockers.extend([f"detect_machine_mode blocker: {x}" for x in payload.get("blockers", [])])

    if blockers:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "WARNING"
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "basis": "federation machine-mode detection derived from status-model-v2 rank (integration posture non-authority)",
        "evidence": evidence,
        "blockers": blockers,
        "warnings": warnings,
        "next_step": "Ensure rank-derived mode mapping and posture overlays are consistent." if warnings else "Machine mode detection is valid.",
    }


def integration_inbox_checks() -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    evidence: dict[str, Any] = {}

    missing_structure = missing_paths(INTEGRATION_STRUCTURE_PATHS)
    missing_contracts = missing_paths(FEDERATION_CONTRACT_FILES)
    missing_task_flow = missing_paths(TASK_FLOW_FILES)
    evidence["missing_structure"] = missing_structure
    evidence["missing_contracts"] = missing_contracts
    evidence["missing_task_flow"] = missing_task_flow

    blockers.extend([f"missing integration structure path: {p}" for p in missing_structure])
    blockers.extend([f"missing federation contract file: {p}" for p in missing_contracts])
    blockers.extend([f"missing task-flow file: {p}" for p in missing_task_flow])

    review_script = REPO_ROOT / "scripts/review_integration_inbox.py"
    if review_script.exists():
        proc = subprocess.run(
            ["python", str(review_script), "--help"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        evidence["review_script_help_exit_code"] = proc.returncode
        if proc.returncode != 0:
            blockers.append("integration inbox review script help failed")
    else:
        blockers.append("missing scripts/review_integration_inbox.py")

    resolve_script = REPO_ROOT / "scripts/resolve_task_id.py"
    if resolve_script.exists():
        proc = subprocess.run(
            ["python", str(resolve_script), "--task-id", "TASK-PLATFORM_TEST_AGENT-001"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        evidence["resolve_example_exit_code"] = proc.returncode
        if proc.returncode != 0:
            blockers.append("resolve_task_id example check failed")
    else:
        blockers.append("missing scripts/resolve_task_id.py")

    if blockers:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "WARNING"
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "basis": "integration inbox structure and review flow readiness",
        "evidence": evidence,
        "blockers": blockers,
        "warnings": warnings,
        "next_step": "Fix integration inbox blockers." if blockers else "Integration inbox flow is ready.",
    }


def contradiction_checks(git_state: GitState) -> dict[str, Any]:
    contradictions: list[dict[str, str]] = []

    wm = load_json("workspace_config/workspace_manifest.json")
    cm = load_json("workspace_config/codex_manifest.json")

    if wm.get("active_project") != ACTIVE_PROJECT_SLUG:
        contradictions.append(
            {
                "severity": "CRITICAL",
                "type": "active_project_mismatch",
                "detail": f"workspace_manifest active_project={wm.get('active_project')} expected={ACTIVE_PROJECT_SLUG}",
            }
        )

    for rel in CORE_DOCS:
        if rel.endswith(".json"):
            continue
        text = read_text(rel)
        if CANONICAL_LOCAL_ROOT not in text:
            contradictions.append(
                {
                    "severity": "MAJOR",
                    "type": "canonical_root_missing",
                    "detail": f"{rel} missing canonical local root token",
                }
            )
        if "WorkFLOW2" not in text:
            contradictions.append(
                {
                    "severity": "MAJOR",
                    "type": "safe_repo_identity_missing",
                    "detail": f"{rel} missing WorkFLOW2 token",
                }
            )

    sanitization_report = read_text("docs/review_artifacts/PUBLIC_REPO_SANITIZATION_REPORT.md")
    if "LEGACY_NON_CANONICAL" not in sanitization_report:
        contradictions.append(
            {
                "severity": "MAJOR",
                "type": "legacy_report_not_marked",
                "detail": "PUBLIC_REPO_SANITIZATION_REPORT.md is not marked LEGACY_NON_CANONICAL",
            }
        )

    wm_arch = wm.get("canonical_architecture", {})
    cm_arch = cm.get("canonical_architecture", {})
    for source, arch in [("workspace_manifest", wm_arch), ("codex_manifest", cm_arch)]:
        if arch.get("working_source_of_truth_root") != CANONICAL_LOCAL_ROOT:
            contradictions.append(
                {
                    "severity": "CRITICAL",
                    "type": "manifest_root_mismatch",
                    "detail": f"{source} canonical_architecture working_source_of_truth_root mismatch",
                }
            )
        if arch.get("public_safe_mirror_repo") != CANONICAL_SAFE_REPO:
            contradictions.append(
                {
                    "severity": "CRITICAL",
                    "type": "manifest_safe_repo_mismatch",
                    "detail": f"{source} canonical_architecture public_safe_mirror_repo mismatch",
                }
            )

    if git_state.branch != CANONICAL_BRANCH:
        contradictions.append(
            {
                "severity": "MAJOR",
                "type": "branch_mismatch",
                "detail": f"current branch {git_state.branch} expected {CANONICAL_BRANCH}",
            }
        )

    critical = [x for x in contradictions if x["severity"] == "CRITICAL"]
    major = [x for x in contradictions if x["severity"] == "MAJOR"]

    return {
        "count": len(contradictions),
        "critical_count": len(critical),
        "major_count": len(major),
        "items": contradictions,
        "status": "PASS" if not contradictions else "FAIL",
    }


def governance_checks() -> dict[str, Any]:
    missing_stack = missing_paths(GOVERNANCE_BRAIN_STACK)
    missing_evolution = missing_paths(EVOLUTION_LAYER_DOCS)
    missing_hardening = missing_paths(GOVERNANCE_V11_HARDENING_DOCS)
    missing_federation = missing_paths(FEDERATION_LAYER_DOCS)
    missing_federation_contracts = missing_paths(FEDERATION_CONTRACT_FILES)
    missing_operator_query = missing_paths(OPERATOR_QUERY_LAYER_DOCS)
    missing_operator_command = missing_paths(OPERATOR_COMMAND_LAYER_DOCS)
    missing_operator_command_files = missing_paths(OPERATOR_COMMAND_LAYER_FILES)
    missing_operator_program = missing_paths(OPERATOR_PROGRAM_LAYER_DOCS)
    missing_operator_program_files = missing_paths(OPERATOR_PROGRAM_LAYER_FILES)
    missing_operator_mission = missing_paths(OPERATOR_MISSION_LAYER_DOCS)
    missing_operator_mission_files = missing_paths(OPERATOR_MISSION_LAYER_FILES)
    missing_core = missing_paths(CORE_DOCS)
    missing_acceptance = missing_paths([GOVERNANCE_ACCEPTANCE_DOC])

    weak_docs: list[str] = []
    for rel in (
        GOVERNANCE_BRAIN_STACK
        + EVOLUTION_LAYER_DOCS
        + FEDERATION_LAYER_DOCS
        + OPERATOR_QUERY_LAYER_DOCS
        + OPERATOR_COMMAND_LAYER_DOCS
        + OPERATOR_PROGRAM_LAYER_DOCS
        + OPERATOR_MISSION_LAYER_DOCS
    ):
        if exists(rel):
            lines = [ln for ln in read_text(rel).splitlines() if ln.strip()]
            if len(lines) < 20:
                weak_docs.append(rel)

    wm = load_json("workspace_config/workspace_manifest.json")
    cm = load_json("workspace_config/codex_manifest.json")

    governance_refs_missing: list[str] = []
    wm_stack = wm.get("governance_brain_stack", {}).get("documents", [])
    cm_stack = cm.get("governance_brain_stack", {}).get("documents", [])
    for rel in GOVERNANCE_BRAIN_STACK:
        if rel not in wm_stack:
            governance_refs_missing.append(f"workspace_manifest missing {rel}")
        if rel not in cm_stack:
            governance_refs_missing.append(f"codex_manifest missing {rel}")
    for rel in FEDERATION_LAYER_DOCS:
        if rel not in wm_stack:
            governance_refs_missing.append(f"workspace_manifest missing federation doc {rel}")
        if rel not in cm_stack:
            governance_refs_missing.append(f"codex_manifest missing federation doc {rel}")
    for rel in OPERATOR_QUERY_LAYER_DOCS:
        if rel not in wm_stack:
            governance_refs_missing.append(f"workspace_manifest missing operator query doc {rel}")
        if rel not in cm_stack:
            governance_refs_missing.append(f"codex_manifest missing operator query doc {rel}")
    for rel in OPERATOR_COMMAND_LAYER_DOCS:
        if rel not in wm_stack:
            governance_refs_missing.append(f"workspace_manifest missing operator command doc {rel}")
        if rel not in cm_stack:
            governance_refs_missing.append(f"codex_manifest missing operator command doc {rel}")
    for rel in OPERATOR_PROGRAM_LAYER_DOCS:
        if rel not in wm_stack:
            governance_refs_missing.append(f"workspace_manifest missing operator program doc {rel}")
        if rel not in cm_stack:
            governance_refs_missing.append(f"codex_manifest missing operator program doc {rel}")
    for rel in OPERATOR_MISSION_LAYER_DOCS:
        if rel not in wm_stack:
            governance_refs_missing.append(f"workspace_manifest missing operator mission doc {rel}")
        if rel not in cm_stack:
            governance_refs_missing.append(f"codex_manifest missing operator mission doc {rel}")

    blockers = [
        *[f"missing governance doc: {p}" for p in missing_stack],
        *[f"missing evolution doc: {p}" for p in missing_evolution],
        *[f"missing hardening doc: {p}" for p in missing_hardening],
        *[f"missing federation doc: {p}" for p in missing_federation],
        *[f"missing federation contract: {p}" for p in missing_federation_contracts],
        *[f"missing operator query doc: {p}" for p in missing_operator_query],
        *[f"missing operator command doc: {p}" for p in missing_operator_command],
        *[f"missing operator command file: {p}" for p in missing_operator_command_files],
        *[f"missing operator program doc: {p}" for p in missing_operator_program],
        *[f"missing operator program file: {p}" for p in missing_operator_program_files],
        *[f"missing operator mission doc: {p}" for p in missing_operator_mission],
        *[f"missing operator mission file: {p}" for p in missing_operator_mission_files],
        *[f"missing governance acceptance gate: {p}" for p in missing_acceptance],
        *[f"missing core doc: {p}" for p in missing_core],
        *governance_refs_missing,
    ]

    warnings = [f"low operational density: {p}" for p in weak_docs]

    if blockers:
        verdict = "NON_COMPLIANT"
    elif warnings:
        verdict = "PARTIAL"
    else:
        verdict = "COMPLIANT"

    return {
        "verdict": verdict,
        "blockers": blockers,
        "warnings": warnings,
        "evidence": {
            "missing_stack": missing_stack,
            "missing_evolution": missing_evolution,
            "missing_hardening": missing_hardening,
            "missing_federation": missing_federation,
            "missing_federation_contracts": missing_federation_contracts,
            "missing_operator_query": missing_operator_query,
            "missing_operator_command": missing_operator_command,
            "missing_operator_command_files": missing_operator_command_files,
            "missing_operator_program": missing_operator_program,
            "missing_operator_program_files": missing_operator_program_files,
            "missing_operator_mission": missing_operator_mission,
            "missing_operator_mission_files": missing_operator_mission_files,
            "missing_acceptance": missing_acceptance,
            "missing_core": missing_core,
            "weak_docs": weak_docs,
        },
    }


def sync_checks(git_state: GitState) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if git_state.branch != CANONICAL_BRANCH:
        blockers.append(f"branch mismatch: {git_state.branch}")
    if git_state.head != git_state.remote_head:
        blockers.append("HEAD != safe_mirror/main")
    if git_state.ahead != 0 or git_state.behind != 0:
        blockers.append(f"divergence {git_state.ahead}/{git_state.behind}")
    if not git_state.worktree_clean:
        blockers.append("worktree dirty")

    hygiene = build_hygiene_classification_context(git_state)
    classified_dirty_allowed = is_controlled_classified_dirty(hygiene)

    if blockers == ["worktree dirty"] and classified_dirty_allowed:
        blockers = []
        warnings.append("worktree dirty but classified under hygiene surface (no owner-decision/junk/runtime blockers)")
        verdict = "IN_SYNC_CLASSIFIED"
    elif not blockers:
        verdict = "IN_SYNC"
    elif "branch mismatch" in " ".join(blockers):
        verdict = "BLOCKED"
    else:
        verdict = "DRIFTED"

    return {
        "verdict": verdict,
        "basis": "git parity against safe_mirror/main",
        "evidence": {
            "branch": git_state.branch,
            "head": git_state.head,
            "safe_mirror_main": git_state.remote_head,
            "ahead": git_state.ahead,
            "behind": git_state.behind,
            "worktree_clean": git_state.worktree_clean,
            "status_short": git_state.status_short,
            "hygiene_classification": hygiene,
            "classified_dirty_allowed": classified_dirty_allowed,
            "classified_dirty_controlled": classified_dirty_allowed,
        },
        "blockers": blockers,
        "warnings": warnings,
        "next_step": (
            "Run git add/commit/push and resolve divergence/worktree blockers."
            if blockers
            else (
                "Track classified canonical deltas to converge from IN_SYNC_CLASSIFIED toward IN_SYNC."
                if verdict == "IN_SYNC_CLASSIFIED"
                else "Maintain parity discipline."
            )
        ),
    }


def gate_runtime_checks(git_state: GitState) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    policy = load_json_if_exists(GATE_POLICY_REL)
    owner_override = load_json_if_exists(OWNER_OVERRIDE_REL)
    registry = load_json_if_exists(ENTITY_REGISTRY_REL)
    zone_class_policy = load_json_if_exists(ZONE_CLASS_POLICY_REL)
    zone_transition_policy = load_json_if_exists(ZONE_TRANSITION_POLICY_REL)
    zone_transition_ledger = load_json_if_exists(ZONE_TRANSITION_LEDGER_REL)
    dashboard_registry = load_json_if_exists(DASHBOARD_SIGNAL_REGISTRY_REL)
    tomb_registry = load_json_if_exists(TOMB_REGISTRY_REL)
    reimport_requests = load_json_if_exists(REIMPORT_REQUESTS_REL)
    integration_port_contract = load_json_if_exists(INTEGRATION_PORT_GATE_CONTRACT_REL)

    status_lines = run_cmd(["git", "status", "--porcelain=v1"], allow_fail=True).splitlines()
    changed_paths: list[str] = []
    for raw in status_lines:
        line = str(raw or "").strip()
        if not line:
            continue
        payload = line[3:].strip() if len(line) >= 3 else line
        if " -> " in payload:
            payload = payload.split(" -> ", 1)[1].strip()
        changed_paths.append(payload.replace("\\", "/"))

    gate_results: list[dict[str, Any]] = []

    canonical_prefixes = list(policy.get("canonical_write_gate", {}).get("protected_prefixes", []) or ["docs/governance/"])
    allowed_canon_paths = set(policy.get("canonical_write_gate", {}).get("allowed_canon_mutation_paths", []) or [])
    canon_changes = [p for p in changed_paths if any(p.startswith(prefix) for prefix in canonical_prefixes)]
    unauthorized_canon_changes = [p for p in canon_changes if p not in allowed_canon_paths]
    canonical_override = bool(owner_override.get("canonical_write_override", False))
    canonical_pass = len(unauthorized_canon_changes) == 0 or canonical_override
    canonical_gate = {
        "gate_id": "canonical_write_gate",
        "status": "PASS" if canonical_pass else "FAIL",
        "pass": canonical_pass,
        "implemented": True,
        "summary": "No unauthorized canonical write path detected." if canonical_pass else "Unauthorized canonical write detected.",
        "evidence": {
            "changed_paths_count": len(changed_paths),
            "canon_changes": canon_changes,
            "unauthorized_canon_changes": unauthorized_canon_changes,
            "owner_override": canonical_override,
        },
        "audit_path": GATE_AUDIT_LOG_REL,
    }
    gate_results.append(canonical_gate)

    records = list(registry.get("records", []) or [])
    allowed_zone_by_class = dict(zone_class_policy.get("allowed_zone_by_class", {}) or {})
    required_fields = [
        "entity_id",
        "canonical_name",
        "address",
        "class",
        "zone",
        "order",
        "owner",
        "mandate",
        "state",
        "birth_basis",
        "change_basis",
        "provenance_link",
        "last_review",
        "visibility_class",
        "dashboard_exposure_class",
    ]
    registry_failures: list[dict[str, Any]] = []
    registry_warnings: list[dict[str, Any]] = []
    integration_failures: list[dict[str, Any]] = []
    seen_entity: set[str] = set()
    seen_address: set[str] = set()
    seen_semantic_name: dict[str, str] = {}
    integration_required_fields = list(integration_port_contract.get("required_integration_fields", []) or [])
    integration_apply_to_classes = set(integration_port_contract.get("apply_to_classes", []) or [])
    integration_hard_gate = bool(integration_port_contract.get("deny_without_port", False))
    for record in records:
        entity_id = str(record.get("entity_id", "")).strip() or "UNKNOWN"
        address = str(record.get("address", "")).strip()
        canonical_name = str(record.get("canonical_name", "")).strip()
        for field in required_fields:
            if str(record.get(field, "")).strip() == "":
                registry_failures.append({"entity_id": entity_id, "issue": f"missing_field:{field}"})
        if entity_id in seen_entity:
            registry_failures.append({"entity_id": entity_id, "issue": "duplicate_entity_id"})
        seen_entity.add(entity_id)
        if address:
            if address in seen_address:
                registry_failures.append({"entity_id": entity_id, "issue": "duplicate_address"})
            seen_address.add(address)
        semantic_name = normalize_semantic_token(canonical_name)
        if semantic_name:
            prior = seen_semantic_name.get(semantic_name)
            if prior and prior != entity_id:
                registry_failures.append(
                    {
                        "entity_id": entity_id,
                        "issue": f"semantic_name_collision:{canonical_name}",
                        "with_entity": prior,
                    }
                )
            seen_semantic_name[semantic_name] = entity_id
        class_name = str(record.get("class", "")).strip()
        zone_name = str(record.get("zone", "")).strip()
        if class_name not in allowed_zone_by_class:
            registry_failures.append({"entity_id": entity_id, "issue": f"class_policy_missing:{class_name}"})
        elif zone_name not in list(allowed_zone_by_class.get(class_name, []) or []):
            registry_failures.append({"entity_id": entity_id, "issue": f"class_zone_mismatch:{class_name}->{zone_name}"})
        provenance_rel = str(record.get("provenance_link", "")).strip().replace("\\", "/")
        if provenance_rel:
            provenance_path = REPO_ROOT / provenance_rel
            if not provenance_path.exists():
                registry_failures.append({"entity_id": entity_id, "issue": "missing_provenance_path"})
            elif not path_is_git_tracked(provenance_rel):
                if provenance_rel.startswith("runtime/") or provenance_rel.startswith("docs/review_artifacts/"):
                    registry_warnings.append({"entity_id": entity_id, "issue": "untracked_provenance_generated_zone"})
                else:
                    registry_failures.append({"entity_id": entity_id, "issue": "untracked_provenance_path"})
        if integration_hard_gate and (not integration_apply_to_classes or class_name in integration_apply_to_classes):
            for field in integration_required_fields:
                value = record.get(field)
                missing_value = False
                if isinstance(value, list):
                    missing_value = len(value) == 0
                elif isinstance(value, dict):
                    missing_value = len(value.keys()) == 0
                else:
                    missing_value = str(value if value is not None else "").strip() == ""
                if missing_value:
                    integration_failures.append({"entity_id": entity_id, "issue": f"integration_port_missing_field:{field}"})
    if integration_failures:
        registry_failures.extend(integration_failures)
    registry_pass = len(registry_failures) == 0
    registry_gate = {
        "gate_id": "registry_validation_gate",
        "status": "PASS" if registry_pass else "FAIL",
        "pass": registry_pass,
        "implemented": True,
        "summary": "Registry records satisfy required schema and class-zone policy." if registry_pass else "Registry validation failures detected.",
        "evidence": {
            "records_total": len(records),
            "failures": registry_failures,
            "warnings": registry_warnings,
            "schema_fields_required": required_fields,
            "policy_path": ZONE_CLASS_POLICY_REL,
            "integration_hard_gate": integration_hard_gate,
            "integration_required_fields": integration_required_fields,
            "integration_apply_to_classes": sorted(integration_apply_to_classes),
        },
        "audit_path": GATE_AUDIT_LOG_REL,
    }
    gate_results.append(registry_gate)

    allowed_transitions = {
        (str(x.get("from_zone", "")).strip(), str(x.get("to_zone", "")).strip())
        for x in list(zone_transition_policy.get("allowed_transitions", []) or [])
    }
    transition_entries = list(zone_transition_ledger.get("entries", []) or [])
    transition_failures: list[dict[str, Any]] = []
    for entry in transition_entries:
        entry_id = str(entry.get("entry_id", "UNKNOWN")).strip()
        from_zone = str(entry.get("from_zone", "")).strip()
        to_zone = str(entry.get("to_zone", "")).strip()
        for field in ["subject_id", "from_zone", "to_zone", "authority_basis", "evidence_ref"]:
            if str(entry.get(field, "")).strip() == "":
                transition_failures.append({"entry_id": entry_id, "issue": f"missing_field:{field}"})
        if (from_zone, to_zone) not in allowed_transitions:
            transition_failures.append({"entry_id": entry_id, "issue": f"forbidden_transition:{from_zone}->{to_zone}"})
        if from_zone == "Officium Runtime Nodorum" and to_zone == "Sanctum Canonis":
            transition_failures.append({"entry_id": entry_id, "issue": "runtime_direct_to_canon_forbidden"})
    transition_pass = len(transition_failures) == 0
    transition_gate = {
        "gate_id": "zone_transition_gate",
        "status": "PASS" if transition_pass else "FAIL",
        "pass": transition_pass,
        "implemented": True,
        "summary": "Zone transitions comply with allowed movement policy." if transition_pass else "Zone transition policy violations detected.",
        "evidence": {
            "entries_total": len(transition_entries),
            "allowed_transitions_total": len(allowed_transitions),
            "failures": transition_failures,
        },
        "audit_path": GATE_AUDIT_LOG_REL,
    }
    gate_results.append(transition_gate)

    signal_entries = list(dashboard_registry.get("signals", []) or [])
    signal_failures: list[dict[str, Any]] = []
    required_signal_fields = [
        "signal_id",
        "source_path",
        "owner",
        "freshness_max_minutes",
        "last_observed_utc",
        "evidence_link",
        "provenance_link",
        "status",
    ]
    allowed_statuses = {"GREEN", "YELLOW", "RED", "UNKNOWN", "ERROR", "BLOCKED"}
    for signal in signal_entries:
        signal_id = str(signal.get("signal_id", "UNKNOWN"))
        for field in required_signal_fields:
            if str(signal.get(field, "")).strip() == "":
                signal_failures.append({"signal_id": signal_id, "issue": f"missing_field:{field}"})
        source_rel = str(signal.get("source_path", "")).replace("\\", "/").strip()
        source_path = REPO_ROOT / source_rel
        if not source_path.exists():
            signal_failures.append({"signal_id": signal_id, "issue": "missing_source_path"})
            continue
        obs_ts = parse_iso_ts(signal.get("last_observed_utc"))
        age_minutes = (now - obs_ts).total_seconds() / 60.0 if obs_ts else 10**9
        freshness_limit = float(signal.get("freshness_max_minutes", 0) or 0)
        if age_minutes > freshness_limit:
            signal_failures.append({"signal_id": signal_id, "issue": f"stale_signal:{int(age_minutes)}m>{int(freshness_limit)}m"})
        source_data = load_json_if_exists(source_rel)
        source_ts = (
            parse_iso_ts(source_data.get("generated_at_utc"))
            or parse_iso_ts(source_data.get("generated_at"))
            or parse_iso_ts(source_data.get("timestamp_utc"))
        )
        if source_ts:
            source_age = (now - source_ts).total_seconds() / 60.0
            if source_age > freshness_limit:
                signal_failures.append({"signal_id": signal_id, "issue": f"stale_source:{int(source_age)}m>{int(freshness_limit)}m"})
        status = str(signal.get("status", "")).strip().upper()
        if status not in allowed_statuses:
            signal_failures.append({"signal_id": signal_id, "issue": f"invalid_signal_status:{status or 'EMPTY'}"})
        if status == "GREEN" and contains_failure_signal(source_data):
            signal_failures.append({"signal_id": signal_id, "issue": "green_with_failure_source"})
    dashboard_pass = len(signal_failures) == 0
    dashboard_gate = {
        "gate_id": "dashboard_truth_validator",
        "status": "PASS" if dashboard_pass else "FAIL",
        "pass": dashboard_pass,
        "implemented": True,
        "summary": "Dashboard signal metadata and truth-state validation passed." if dashboard_pass else "Dashboard signal validation failures detected.",
        "evidence": {
            "signals_total": len(signal_entries),
            "failures": signal_failures,
            "registry_path": DASHBOARD_SIGNAL_REGISTRY_REL,
        },
        "audit_path": GATE_AUDIT_LOG_REL,
    }
    gate_results.append(dashboard_gate)

    tomb_entries = {
        str(x.get("subject_id", "")).strip(): str(x.get("status", "")).strip().upper()
        for x in list(tomb_registry.get("entries", []) or [])
    }
    requests = list(reimport_requests.get("requests", []) or [])
    reimport_blocked: list[dict[str, Any]] = []
    for req in requests:
        req_id = str(req.get("request_id", "UNKNOWN"))
        subject_id = str(req.get("subject_id", "")).strip()
        subject_status = tomb_entries.get(subject_id, "")
        if subject_status in {"TOMBED", "QUARANTINED"}:
            if str(req.get("restoration_act_id", "")).strip() == "" or not bool(req.get("owner_approved", False)):
                reimport_blocked.append(
                    {
                        "request_id": req_id,
                        "subject_id": subject_id,
                        "issue": "reimport_blocked_missing_restoration_or_owner_approval",
                    }
                )
    tomb_pass = len(reimport_blocked) == 0
    tomb_gate = {
        "gate_id": "tomb_reimport_blocker",
        "status": "PASS" if tomb_pass else "FAIL",
        "pass": tomb_pass,
        "implemented": True,
        "summary": "Tomb reimport attempts are lawfully controlled." if tomb_pass else "Blocked/illegal tomb reimport attempt detected.",
        "evidence": {
            "requests_total": len(requests),
            "blocked_attempts": reimport_blocked,
            "tomb_entries_total": len(tomb_entries),
        },
        "audit_path": GATE_AUDIT_LOG_REL,
    }
    gate_results.append(tomb_gate)

    for gate in gate_results:
        event = {
            "timestamp_utc": utc_now(),
            "gate_id": gate.get("gate_id", "unknown"),
            "status": gate.get("status", "UNKNOWN"),
            "pass": bool(gate.get("pass", False)),
            "summary": gate.get("summary", ""),
        }
        append_jsonl_rel(GATE_AUDIT_LOG_REL, event)

    write_json_rel(CANONICAL_WRITE_STATE_REL, canonical_gate)
    write_json_rel(REGISTRY_VALIDATION_STATE_REL, registry_gate)
    write_json_rel(ZONE_TRANSITION_STATE_REL, transition_gate)
    write_json_rel(DASHBOARD_TRUTH_STATE_REL, dashboard_gate)
    write_json_rel(TOMB_REIMPORT_STATE_REL, tomb_gate)

    overall_pass = all(bool(g.get("pass", False)) for g in gate_results)
    summary = {
        "surface_id": "IMPERIUM_GATE_EXECUTION_SUMMARY_V1",
        "generated_at_utc": utc_now(),
        "overall_status": "PASS" if overall_pass else "FAIL",
        "overall_pass": overall_pass,
        "gates": gate_results,
    }
    write_json_rel(GATE_SUMMARY_REL, summary)

    blockers = [f"gate_fail:{g['gate_id']}" for g in gate_results if not g.get("pass", False)]
    warnings = []
    if registry_warnings:
        warnings.append("registry_generated_zone_provenance_warnings")
    return {
        "verdict": "PASS" if overall_pass else "FAIL",
        "basis": "canonical tracked gate runtime checks via repo_control_center",
        "evidence": summary,
        "blockers": blockers,
        "warnings": warnings,
        "next_step": "Resolve gate_fail blockers." if blockers else "Maintain gate runtime integrity.",
    }


def foundation_law_lock_checks() -> dict[str, Any]:
    required_law_ids = [
        "LAW-FOUNDATION-NO-DUPLICATE-LAWS",
        "LAW-FOUNDATION-IMPERIUM-COMMIT-PHRASE",
        "LAW-FOUNDATION-SINGLE-THREAD-COMPLETION",
        "LAW-FOUNDATION-FULL-EXECUTION-DUTY",
        "LAW-FOUNDATION-SERVITOR-FIDELITY",
        "LAW-FOUNDATION-PORT-GATED-INTEGRATION",
        "LAW-FOUNDATION-ONE-TRUTH-CENTER",
        "LAW-FOUNDATION-AMBIGUOUS-OWNER-COMMAND-HARD-GATE",
        "LAW-FOUNDATION-CODEX-RESPONSE-FORMAT",
    ]

    blockers: list[str] = []
    warnings: list[str] = []

    law_doc_exists = exists(LAW_LOCK_CANON_REL)
    law_registry = load_json_if_exists(LAW_LOCK_REGISTRY_REL)
    law_doc_text = read_text(LAW_LOCK_CANON_REL) if law_doc_exists else ""
    registry_laws = list(law_registry.get("laws", []) or [])
    registry_ids = [str(x.get("law_id", "")).strip() for x in registry_laws if str(x.get("law_id", "")).strip()]
    missing_in_registry = [law_id for law_id in required_law_ids if law_id not in registry_ids]
    if not law_doc_exists:
        blockers.append("missing_law_lock_canon_doc")
    if missing_in_registry:
        blockers.append("missing_required_foundation_laws")

    for law_id in required_law_ids:
        if law_doc_text and law_id not in law_doc_text:
            blockers.append(f"law_id_missing_in_doc:{law_id}")

    duplicate_id_map: dict[str, list[str]] = {}
    for row in registry_laws:
        law_id = str(row.get("law_id", "")).strip()
        if law_id:
            duplicate_id_map.setdefault(law_id, []).append(str(row.get("title", "")).strip())
    duplicate_law_ids = sorted([law_id for law_id, titles in duplicate_id_map.items() if len(titles) > 1])

    semantic_index: dict[str, str] = {}
    semantic_collisions: list[dict[str, str]] = []
    for row in registry_laws:
        law_id = str(row.get("law_id", "")).strip()
        title = str(row.get("title", "")).strip()
        token = normalize_semantic_token(title)
        if not token:
            continue
        prior = semantic_index.get(token)
        if prior and prior != law_id:
            semantic_collisions.append({"law_id": law_id, "collides_with": prior, "title": title})
        semantic_index[token] = law_id
    if duplicate_law_ids:
        blockers.append("duplicate_law_id_detected")
    if semantic_collisions:
        blockers.append("semantic_duplicate_law_detected")

    governance_files = run_cmd(["git", "ls-files", "docs/governance/*.md"], allow_fail=True).splitlines()
    law_occurrence_map: dict[str, list[str]] = {law_id: [] for law_id in required_law_ids}
    for rel in governance_files:
        rel_clean = str(rel).strip()
        if not rel_clean:
            continue
        text = read_text_loose(rel_clean)
        for law_id in required_law_ids:
            if law_id in text:
                law_occurrence_map[law_id].append(rel_clean)
    cross_file_duplicates = {
        law_id: files
        for law_id, files in law_occurrence_map.items()
        if len(files) > 1 and any(x != LAW_LOCK_CANON_REL for x in files)
    }
    if cross_file_duplicates:
        blockers.append("cross_file_law_duplication_detected")
        warnings.append("cross_file_law_duplication_detected")

    one_truth_center_ok = not exists("scripts/imperium_gate_implementation.py")
    if not one_truth_center_ok:
        blockers.append("second_enforcement_path_detected")

    owner_command_contract = load_json_if_exists(OWNER_COMMAND_GATE_CONTRACT_REL)
    command_required_fields = list(owner_command_contract.get("required_fields", []) or [])
    reject_policy = bool(owner_command_contract.get("reject_on_ambiguity", False))
    owner_phrase = str(owner_command_contract.get("owner_commit_phrase", "")).strip()
    command_collection_key = str(owner_command_contract.get("command_collection_key", "commands")).strip() or "commands"
    denied_ambiguity_statuses = {
        str(x).strip().upper() for x in list(owner_command_contract.get("ambiguity_status_denied", []) or [])
    }
    command_contract_ok = bool(command_required_fields) and reject_policy and owner_phrase == "Закрепи в Империуме"
    if not command_contract_ok:
        blockers.append("ambiguous_command_hard_gate_contract_invalid")

    owner_command_inbox = load_json_if_exists(OWNER_COMMAND_INBOX_REL)
    owner_commands = list(owner_command_inbox.get(command_collection_key, []) or [])
    ambiguous_command_failures: list[dict[str, Any]] = []
    for row in owner_commands:
        command_id = str(row.get("command_id", "")).strip() or "UNKNOWN"
        missing_fields = [
            field for field in command_required_fields if str(row.get(field, "")).strip() == ""
        ]
        if missing_fields:
            ambiguous_command_failures.append(
                {
                    "command_id": command_id,
                    "issue": "missing_required_fields",
                    "fields": missing_fields,
                }
            )
        ambiguity_status = str(row.get("ambiguity_status", "")).strip().upper()
        owner_clarified = bool(row.get("owner_clarified", False))
        if reject_policy and ambiguity_status in denied_ambiguity_statuses and not owner_clarified:
            ambiguous_command_failures.append(
                {
                    "command_id": command_id,
                    "issue": "ambiguous_status_rejected",
                    "ambiguity_status": ambiguity_status or "EMPTY",
                }
            )
    if ambiguous_command_failures:
        blockers.append("ambiguous_owner_command_detected")

    port_contract = load_json_if_exists(INTEGRATION_PORT_GATE_CONTRACT_REL)
    port_required = list(port_contract.get("required_integration_fields", []) or [])
    port_policy_ok = bool(port_required) and bool(port_contract.get("deny_without_port", False))
    if not port_policy_ok:
        blockers.append("port_gated_integration_contract_invalid")

    codex_format_law_ok = "LAW-FOUNDATION-CODEX-RESPONSE-FORMAT" in law_doc_text and "3-4" in law_doc_text
    if not codex_format_law_ok:
        blockers.append("codex_response_format_law_not_enforced")

    duplicate_scan_payload = {
        "surface_id": "IMPERIUM_DUPLICATE_LAW_SCAN_V1",
        "generated_at_utc": utc_now(),
        "required_law_ids": required_law_ids,
        "registry_ids": sorted(set(registry_ids)),
        "missing_in_registry": missing_in_registry,
        "duplicate_law_ids": duplicate_law_ids,
        "semantic_collisions": semantic_collisions,
        "cross_file_duplicates": cross_file_duplicates,
    }
    write_json_rel(DUPLICATE_LAW_SCAN_REL, duplicate_scan_payload)

    ambiguous_gate_payload = {
        "surface_id": "IMPERIUM_AMBIGUOUS_COMMAND_HARD_GATE_STATUS_V1",
        "generated_at_utc": utc_now(),
        "status": "PASS" if command_contract_ok and not ambiguous_command_failures else "FAIL",
        "owner_commit_phrase": owner_phrase,
        "required_fields": command_required_fields,
        "reject_on_ambiguity": reject_policy,
        "command_collection_key": command_collection_key,
        "commands_total": len(owner_commands),
        "ambiguity_status_denied": sorted(denied_ambiguity_statuses),
        "ambiguity_failures": ambiguous_command_failures,
        "source_path": OWNER_COMMAND_INBOX_REL,
    }
    write_json_rel(AMBIGUOUS_COMMAND_GATE_STATUS_REL, ambiguous_gate_payload)
    write_json_rel(OWNER_COMMAND_GATE_RUNTIME_STATE_REL, ambiguous_gate_payload)

    port_gate_payload = {
        "surface_id": "IMPERIUM_PORT_INTEGRATION_GATE_STATUS_V1",
        "generated_at_utc": utc_now(),
        "status": "PASS" if port_policy_ok else "FAIL",
        "deny_without_port": bool(port_contract.get("deny_without_port", False)),
        "required_integration_fields": port_required,
        "port_name": str(port_contract.get("port_name", "")).strip(),
    }
    write_json_rel(PORT_INTEGRATION_GATE_STATUS_REL, port_gate_payload)

    law_lock_payload = {
        "surface_id": "IMPERIUM_FOUNDATION_LAW_LOCK_STATUS_V1",
        "generated_at_utc": utc_now(),
        "status": "PASS" if not blockers else "FAIL",
        "required_law_ids": required_law_ids,
        "blockers": blockers,
        "warnings": warnings,
        "one_truth_center_ok": one_truth_center_ok,
        "law_doc_exists": law_doc_exists,
        "law_registry_path": LAW_LOCK_REGISTRY_REL,
        "law_doc_path": LAW_LOCK_CANON_REL,
    }
    write_json_rel(LAW_LOCK_STATUS_REL, law_lock_payload)

    return {
        "verdict": "PASS" if not blockers else "FAIL",
        "basis": "foundation law lock, duplicate-law control, command ambiguity gate, and integration port gate",
        "evidence": {
            "law_lock": law_lock_payload,
            "duplicate_scan": duplicate_scan_payload,
            "ambiguous_command_gate": ambiguous_gate_payload,
            "port_integration_gate": port_gate_payload,
        },
        "blockers": blockers,
        "warnings": warnings,
        "next_step": "Resolve law lock blockers." if blockers else "Maintain law lock and duplicate-law hygiene.",
    }


def mirror_checks(git_state: GitState) -> dict[str, Any]:
    missing = missing_paths(SAFE_STATE_FILES)
    blockers: list[str] = []
    warnings: list[str] = []
    evidence: dict[str, Any] = {
        "required_files": SAFE_STATE_FILES,
        "missing": missing,
        "evidence_contract_model": "basis_commit",
    }

    if missing:
        blockers.extend([f"missing safe-state artifact: {p}" for p in missing])

    if exists("workspace_config/SAFE_MIRROR_MANIFEST.json"):
        safe_manifest = load_json("workspace_config/SAFE_MIRROR_MANIFEST.json")
        basis_head = safe_manifest.get("basis_head_sha") or safe_manifest.get("head_sha")
        evidence_mode = safe_manifest.get("evidence_mode", "legacy")
        contract_version = safe_manifest.get("evidence_contract_version")
        evidence_generated_at = safe_manifest.get("evidence_generated_at")
        evidence["basis_head_sha"] = basis_head
        evidence["evidence_mode"] = evidence_mode
        evidence["evidence_contract_version"] = contract_version
        evidence["evidence_generated_at"] = evidence_generated_at
        evidence["current_head"] = git_state.head

        if not basis_head:
            blockers.append("SAFE_MIRROR_MANIFEST missing basis_head_sha")
        if not contract_version:
            blockers.append("SAFE_MIRROR_MANIFEST missing evidence_contract_version")
        if not evidence_generated_at:
            blockers.append("SAFE_MIRROR_MANIFEST missing evidence_generated_at")

        basis_commit_valid = False
        if basis_head:
            commit_check = subprocess.run(
                ["git", "cat-file", "-e", f"{basis_head}^{{commit}}"],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            basis_commit_valid = commit_check.returncode == 0
            evidence["basis_commit_valid"] = basis_commit_valid
            if not basis_commit_valid:
                blockers.append(f"basis_head_sha is not a valid commit: {basis_head}")

        evidence_valid = False
        if basis_head and basis_commit_valid:
            if evidence_mode == "runtime_current_head":
                evidence_valid = git_state.head == basis_head
                evidence["runtime_mode_head_match"] = evidence_valid
                if not evidence_valid:
                    warnings.append(
                        f"runtime_current_head mismatch: basis_head_sha={basis_head} current={git_state.head}"
                    )
            elif evidence_mode == "tracked_evidence_refresh_commit":
                if git_state.head == basis_head:
                    warnings.append("tracked evidence mode expects evidence refresh commit on top of basis_head_sha")
                    evidence["basis_to_current_changed_files"] = []
                    evidence["non_evidence_changes"] = []
                else:
                    ancestor_check = subprocess.run(
                        ["git", "merge-base", "--is-ancestor", basis_head, git_state.head],
                        cwd=REPO_ROOT,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    basis_is_ancestor = ancestor_check.returncode == 0
                    evidence["basis_is_ancestor_of_current"] = basis_is_ancestor
                    if not basis_is_ancestor:
                        warnings.append("basis_head_sha is not ancestor of current HEAD")
                    diff_out = run_cmd(["git", "diff", "--name-only", f"{basis_head}..{git_state.head}"], allow_fail=True)
                    changed_files = [x.strip() for x in diff_out.splitlines() if x.strip()]
                    non_evidence_changes = [x for x in changed_files if x not in SAFE_STATE_FILES]
                    evidence["basis_to_current_changed_files"] = changed_files
                    evidence["non_evidence_changes"] = non_evidence_changes
                    if not changed_files:
                        warnings.append("no changes found between basis_head_sha and current HEAD")
                    if non_evidence_changes:
                        warnings.append(
                            "tracked evidence refresh commit model violated: non-evidence files changed from basis to current"
                        )
                    evidence_valid = basis_is_ancestor and bool(changed_files) and not non_evidence_changes
            else:
                warnings.append(f"unsupported evidence_mode in SAFE_MIRROR_MANIFEST: {evidence_mode}")
                evidence["unsupported_evidence_mode"] = evidence_mode

        evidence["evidence_valid"] = evidence_valid
        evidence["stale_evidence"] = not evidence_valid
        if not evidence_valid and not blockers:
            warnings.append(
                "SAFE_MIRROR_MANIFEST evidence contract not satisfied for current HEAD"
            )

    if exists("docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md"):
        report_text = read_text("docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md")
        basis_head_for_report = evidence.get("basis_head_sha")
        evidence["report_mentions_basis_head"] = bool(basis_head_for_report and basis_head_for_report in report_text)
        evidence["report_mentions_contract_version"] = bool(
            evidence.get("evidence_contract_version") and str(evidence["evidence_contract_version"]) in report_text
        )
        evidence["report_mentions_evidence_mode"] = bool(
            evidence.get("evidence_mode") and str(evidence["evidence_mode"]) in report_text
        )
        if basis_head_for_report and basis_head_for_report not in report_text:
            warnings.append("SAFE_MIRROR_BUILD_REPORT missing basis_head_sha reference")
        if evidence.get("evidence_contract_version") and str(evidence["evidence_contract_version"]) not in report_text:
            warnings.append("SAFE_MIRROR_BUILD_REPORT missing evidence_contract_version reference")
        if evidence.get("evidence_mode") and str(evidence["evidence_mode"]) not in report_text:
            warnings.append("SAFE_MIRROR_BUILD_REPORT missing evidence_mode reference")

    if blockers:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "WARNING"
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "basis": "safe mirror manifest/report freshness and presence",
        "evidence": evidence,
        "warnings": warnings,
        "blockers": blockers,
        "next_step": "Refresh safe mirror manifest/report if warnings exist." if warnings else "Safe mirror artifacts are aligned.",
    }


def bundle_checks() -> dict[str, Any]:
    blockers: list[str] = []
    evidence: dict[str, Any] = {}

    exporter = REPO_ROOT / "scripts/export_chatgpt_bundle.py"
    protocol_doc = REPO_ROOT / "docs/CHATGPT_BUNDLE_EXPORT.md"
    if not exporter.exists():
        blockers.append("missing scripts/export_chatgpt_bundle.py")
    if not protocol_doc.exists():
        blockers.append("missing docs/CHATGPT_BUNDLE_EXPORT.md")

    help_output = ""
    if exporter.exists():
        proc = subprocess.run(
            ["python", str(exporter), "--help"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        evidence["help_exit_code"] = proc.returncode
        help_output = (proc.stdout or "") + (proc.stderr or "")
        for token in ["context", "files", "paths", "project", "request", "audit-runtime"]:
            if token not in help_output:
                blockers.append(f"exporter missing mode in CLI help: {token}")
        if proc.returncode != 0:
            blockers.append("exporter --help failed")

    if blockers:
        verdict = "BLOCKED"
    else:
        verdict = "READY"

    return {
        "verdict": verdict,
        "basis": "targeted bundle exporter availability and mode surface",
        "evidence": evidence,
        "blockers": blockers,
        "next_step": "Fix exporter mode surface blockers." if blockers else "Bundle export path is ready.",
    }


def trust_checks(
    sync: dict[str, Any],
    governance: dict[str, Any],
    contradictions: dict[str, Any],
    mirror: dict[str, Any],
    bundle: dict[str, Any],
    bootstrap: dict[str, Any],
    machine_mode: dict[str, Any],
    integration_inbox: dict[str, Any],
    gate_runtime: dict[str, Any],
    law_lock: dict[str, Any],
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    sync_evidence = dict((sync or {}).get("evidence", {}) or {})
    sync_controlled_classified = bool(sync_evidence.get("classified_dirty_controlled", False))

    if not is_sync_aligned(sync["verdict"]):
        blockers.append(f"sync verdict {sync['verdict']}")
    elif str(sync["verdict"]).upper() == "IN_SYNC_CLASSIFIED" and not sync_controlled_classified:
        warnings.append("sync is IN_SYNC_CLASSIFIED (classified dirty worktree)")
    if governance["verdict"] == "NON_COMPLIANT":
        blockers.append("governance non-compliant")
    elif governance["verdict"] == "PARTIAL":
        warnings.append("governance partial")

    if contradictions["critical_count"] > 0:
        blockers.append("critical contradictions present")
    elif contradictions["major_count"] > 0:
        warnings.append("major contradictions present")

    if mirror["verdict"] == "BLOCKED":
        blockers.append("safe mirror artifacts blocked")
    elif mirror["verdict"] == "WARNING":
        warnings.append("safe mirror artifact freshness warning")

    if bootstrap["verdict"] == "BLOCKED":
        blockers.append("bootstrap contract blocked")
    elif bootstrap["verdict"] == "WARNING":
        warnings.append("bootstrap contract warning")

    if bundle["verdict"] != "READY":
        blockers.append("bundle readiness blocked")

    if machine_mode["verdict"] == "BLOCKED":
        blockers.append("machine mode detection blocked")
    elif machine_mode["verdict"] == "WARNING":
        warnings.append("machine mode is helper-only (rank-derived non-emperor posture)")

    if integration_inbox["verdict"] == "BLOCKED":
        blockers.append("integration inbox flow blocked")
    elif integration_inbox["verdict"] == "WARNING":
        warnings.append("integration inbox flow warning")

    if gate_runtime["verdict"] != "PASS":
        blockers.append("gate runtime checks failed")
    if law_lock["verdict"] != "PASS":
        blockers.append("foundation law lock failed")

    if blockers:
        verdict = "NOT_TRUSTED"
    elif warnings:
        verdict = "WARNING"
    else:
        verdict = "TRUSTED"

    return {
        "verdict": verdict,
        "basis": "combined sync/governance/contradiction/mirror/bundle checks",
        "evidence": {
            "sync_verdict": sync["verdict"],
            "governance_verdict": governance["verdict"],
            "critical_contradictions": contradictions["critical_count"],
            "major_contradictions": contradictions["major_count"],
            "mirror_verdict": mirror["verdict"],
            "bootstrap_verdict": bootstrap["verdict"],
            "bundle_verdict": bundle["verdict"],
            "machine_mode_verdict": machine_mode["verdict"],
            "integration_inbox_verdict": integration_inbox["verdict"],
            "gate_runtime_verdict": gate_runtime["verdict"],
            "law_lock_verdict": law_lock["verdict"],
            "sync_controlled_classified": sync_controlled_classified,
        },
        "blockers": blockers,
        "warnings": warnings,
        "next_step": "Resolve blockers, then rerun full-check." if blockers else "Maintain trust baseline.",
    }


def admission_checks(
    trust: dict[str, Any],
    sync: dict[str, Any],
    governance: dict[str, Any],
    contradictions: dict[str, Any],
    governance_acceptance: dict[str, Any],
    machine_mode: dict[str, Any],
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    sync_evidence = dict((sync or {}).get("evidence", {}) or {})
    sync_controlled_classified = bool(sync_evidence.get("classified_dirty_controlled", False))
    if trust["verdict"] == "NOT_TRUSTED":
        blockers.append("trust verdict is NOT_TRUSTED")
    if not is_sync_aligned(sync["verdict"]):
        blockers.append("sync is not aligned")
    elif str(sync["verdict"]).upper() == "IN_SYNC_CLASSIFIED" and not sync_controlled_classified:
        warnings.append("sync classified as IN_SYNC_CLASSIFIED")
    if governance["verdict"] == "NON_COMPLIANT":
        blockers.append("governance NON_COMPLIANT")
    if contradictions["critical_count"] > 0:
        blockers.append("critical contradictions unresolved")
    if governance_acceptance["verdict"] == "FAIL":
        blockers.append("governance acceptance gate not PASS")
    elif governance_acceptance["verdict"] == "PARTIAL":
        warnings.append("governance acceptance gate PARTIAL")
    if not is_sovereign_mode(str(machine_mode.get("evidence", {}).get("machine_mode", "unknown"))):
        blockers.append("rank-derived machine mode is not sovereign")

    if blockers:
        verdict = "REJECTED"
    elif (
        trust["verdict"] == "WARNING"
        or governance["verdict"] == "PARTIAL"
        or contradictions["major_count"] > 0
        or (str(sync["verdict"]).upper() == "IN_SYNC_CLASSIFIED" and not sync_controlled_classified)
        or governance_acceptance["verdict"] == "PARTIAL"
        or bool(warnings)
    ):
        verdict = "CONDITIONAL"
    else:
        verdict = "ADMISSIBLE"

    return {
        "verdict": verdict,
        "basis": "admission gate based on trust/sync/governance/contradictions",
        "evidence": {
            "trust_verdict": trust["verdict"],
            "sync_verdict": sync["verdict"],
            "governance_verdict": governance["verdict"],
            "critical_contradictions": contradictions["critical_count"],
            "major_contradictions": contradictions["major_count"],
            "governance_acceptance_verdict": governance_acceptance["verdict"],
            "machine_mode": machine_mode.get("evidence", {}).get("machine_mode"),
            "sync_controlled_classified": sync_controlled_classified,
        },
        "blockers": blockers,
        "warnings": warnings,
        "next_step": (
            "Clear blockers to reach ADMISSIBLE."
            if blockers
            else "Admission is conditional; clear warnings for ADMISSIBLE."
            if verdict == "CONDITIONAL"
            else "Admission gate is clear."
        ),
    }


def governance_acceptance_checks(
    *,
    sync: dict[str, Any],
    trust: dict[str, Any],
    governance: dict[str, Any],
    contradictions: dict[str, Any],
    mirror: dict[str, Any],
    bundle: dict[str, Any],
    bootstrap: dict[str, Any],
    machine_mode: dict[str, Any],
    gate_runtime: dict[str, Any],
    law_lock: dict[str, Any],
    git_state: GitState,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    evidence: dict[str, Any] = {
        "acceptance_doc_exists": exists(GOVERNANCE_ACCEPTANCE_DOC),
        "next_step_doc_exists": exists("docs/NEXT_CANONICAL_STEP.md"),
        "sync_verdict": sync["verdict"],
        "trust_verdict": trust["verdict"],
        "governance_verdict": governance["verdict"],
        "bootstrap_verdict": bootstrap["verdict"],
        "mirror_verdict": mirror["verdict"],
        "bundle_verdict": bundle["verdict"],
        "machine_mode_verdict": machine_mode["verdict"],
        "gate_runtime_verdict": gate_runtime["verdict"],
        "law_lock_verdict": law_lock["verdict"],
        "machine_mode": machine_mode.get("evidence", {}).get("machine_mode"),
        "critical_contradictions": contradictions["critical_count"],
        "worktree_clean": git_state.worktree_clean,
        "divergence": f"{git_state.ahead}/{git_state.behind}",
    }

    if not exists(GOVERNANCE_ACCEPTANCE_DOC):
        blockers.append("missing governance acceptance gate document")

    next_step_text = read_text("docs/NEXT_CANONICAL_STEP.md") if exists("docs/NEXT_CANONICAL_STEP.md") else ""
    next_step_lower = next_step_text.lower()
    has_governance_closure = "governance acceptance closure" in next_step_lower
    has_federation_transition = "federation / integration layer v1" in next_step_lower or "next-step-federation-integration-layer-v1" in next_step_lower
    has_operator_command_transition = (
        "operator command execution layer v1" in next_step_lower
        or "next-step-operator-command-execution-layer-v1" in next_step_lower
    )
    has_operator_program_transition = (
        "operator task / program layer v1" in next_step_lower
        or "task / program layer v1" in next_step_lower
        or "next-step-operator-task-program-layer-v1" in next_step_lower
    )
    has_operator_mission_transition = (
        "work package / mission layer v1" in next_step_lower
        or "operator mission layer v1" in next_step_lower
        or "next-step-operator-mission-layer-v1" in next_step_lower
    )
    has_constitution_transition = (
        "constitution-first phase" in next_step_lower
        or "next-step-constitution-first-phase-v0" in next_step_lower
        or "workflow2_constitution_v0" in next_step_lower
    )
    has_valid_route = (
        has_governance_closure
        or has_federation_transition
        or has_operator_command_transition
        or has_operator_program_transition
        or has_operator_mission_transition
        or has_constitution_transition
    )
    evidence["next_step_has_governance_acceptance_closure"] = has_governance_closure
    evidence["next_step_has_federation_transition"] = has_federation_transition
    evidence["next_step_has_operator_command_transition"] = has_operator_command_transition
    evidence["next_step_has_operator_program_transition"] = has_operator_program_transition
    evidence["next_step_has_operator_mission_transition"] = has_operator_mission_transition
    evidence["next_step_has_constitution_transition"] = has_constitution_transition
    evidence["next_step_has_valid_post_acceptance_route"] = has_valid_route
    if not has_valid_route:
        blockers.append("NEXT_CANONICAL_STEP missing governance-accepted canonical route")

    if not is_sync_aligned(sync["verdict"]):
        blockers.append("sync gate not aligned")
    sync_hygiene = dict((sync.get("evidence", {}) or {}).get("hygiene_classification", {}) or {})
    sync_controlled_classified = bool((sync.get("evidence", {}) or {}).get("classified_dirty_controlled", False))
    evidence["sync_controlled_classified"] = sync_controlled_classified
    if str(sync["verdict"]).upper() == "IN_SYNC_CLASSIFIED" and not sync_controlled_classified:
        warnings.append("sync gate is IN_SYNC_CLASSIFIED")
    if trust["verdict"] == "NOT_TRUSTED":
        blockers.append("trust gate not TRUSTED")
    elif trust["verdict"] == "WARNING":
        warnings.append("trust gate WARNING")
    if governance["verdict"] != "COMPLIANT":
        blockers.append("governance gate not COMPLIANT")
    if bootstrap["verdict"] != "PASS":
        blockers.append("bootstrap enforcement not PASS")
    if mirror["verdict"] != "PASS":
        blockers.append("safe mirror evidence gate not PASS")
    if bundle["verdict"] != "READY":
        blockers.append("bundle gate not READY")
    if gate_runtime["verdict"] != "PASS":
        blockers.append("gate runtime not PASS")
    if law_lock["verdict"] != "PASS":
        blockers.append("foundation law lock not PASS")
    if machine_mode["verdict"] == "BLOCKED":
        blockers.append("machine mode detection blocked")
    if not is_sovereign_mode(str(machine_mode.get("evidence", {}).get("machine_mode", "unknown"))):
        blockers.append("rank-derived sovereign mode required for governance acceptance PASS")
    if contradictions["critical_count"] > 0:
        blockers.append("critical contradictions unresolved")
    if not git_state.worktree_clean:
        counts = dict(sync_hygiene.get("classification_counts", {}) or {})
        classified_dirty_safe = bool(
            counts.get("NEEDS_OWNER_DECISION", 0) == 0
            and counts.get("JUNK_OR_RESIDUE", 0) == 0
            and counts.get("GENERATED_RUNTIME_ONLY", 0) == 0
        )
        evidence["classified_dirty_safe"] = classified_dirty_safe
        if sync_controlled_classified and classified_dirty_safe:
            pass
        elif str(sync.get("verdict", "")).upper() == "IN_SYNC_CLASSIFIED" and classified_dirty_safe:
            warnings.append("worktree dirty but classified as safe canonical delta")
        else:
            blockers.append("worktree is dirty")
    if git_state.ahead != 0 or git_state.behind != 0:
        blockers.append(f"divergence is not zero: {git_state.ahead}/{git_state.behind}")

    if blockers:
        verdict = "FAIL"
    elif warnings:
        verdict = "PARTIAL"
    else:
        verdict = "PASS"
    return {
        "verdict": verdict,
        "basis": "formal governance acceptance gate for transition readiness",
        "evidence": evidence,
        "blockers": blockers,
        "warnings": warnings,
        "next_step": (
            "Governance foundation accepted for next-stage consideration."
            if verdict == "PASS"
            else "Governance acceptance is partial; converge classified dirt and warnings."
            if verdict == "PARTIAL"
            else "Close governance acceptance blockers."
        ),
    }


def parse_current_level() -> str:
    path = REPO_ROOT / "docs/governance/NEXT_EVOLUTION_CANDIDATE.md"
    if not path.exists():
        return "V1_STABLE"
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.lower().startswith("- current_level:"):
            return line.split(":", 1)[1].strip().strip("`")
    return "V1_STABLE"


def parse_candidate_context() -> dict[str, str]:
    path = REPO_ROOT / "docs/governance/NEXT_EVOLUTION_CANDIDATE.md"
    context = {
        "current_level": "V1_STABLE",
        "candidate_level": "V1_PLUS",
        "recommendation": "HOLD",
    }
    if not path.exists():
        return context

    for line in path.read_text(encoding="utf-8-sig").splitlines():
        lower = line.lower()
        if lower.startswith("- current_level:"):
            context["current_level"] = line.split(":", 1)[1].strip().strip("`")
        elif lower.startswith("- candidate_level:"):
            context["candidate_level"] = line.split(":", 1)[1].strip().strip("`")
        elif lower.startswith("- readiness:"):
            context["recommendation"] = line.split(":", 1)[1].strip().strip("`").upper()
    return context


def parse_promotion_threshold_policy() -> dict[str, Any]:
    rel = "docs/governance/PROMOTION_THRESHOLD_POLICY.md"
    parsed: dict[str, Any] = {
        "path": rel,
        "exists": exists(rel),
        "observation_window_required": 5,
        "candidate_cycles_required": 3,
        "ready_cycles_required": 5,
        "promote_cycles_required": 5,
    }
    if not parsed["exists"]:
        return parsed

    text = read_text(rel)

    def extract(pattern: str, default: int) -> int:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        return int(match.group(1)) if match else default

    parsed["observation_window_required"] = extract(r"default minimum window:\s*-\s*(\d+)\s+consecutive clean cycles", 5)
    parsed["candidate_cycles_required"] = extract(r"candidate.*?at least\s+(\d+)\s+consecutive clean cycles", 3)
    parsed["ready_cycles_required"] = extract(r"ready.*?at least\s+(\d+)\s+consecutive clean cycles", 5)
    parsed["promote_cycles_required"] = extract(r"promote.*?at least\s+(\d+)\s+clean cycles", parsed["ready_cycles_required"])
    return parsed


def evolution_checks(
    sync: dict[str, Any],
    governance: dict[str, Any],
    contradictions: dict[str, Any],
    trust: dict[str, Any],
    admission: dict[str, Any],
    mirror: dict[str, Any],
    bundle: dict[str, Any],
    observation_cycles: dict[str, Any],
) -> dict[str, Any]:
    candidate_context = parse_candidate_context()
    current_level = candidate_context["current_level"]
    threshold_policy = parse_promotion_threshold_policy()
    policy_log_text = read_text("docs/governance/POLICY_EVOLUTION_LOG.md") if exists("docs/governance/POLICY_EVOLUTION_LOG.md") else ""
    next_candidate_text = read_text("docs/governance/NEXT_EVOLUTION_CANDIDATE.md") if exists("docs/governance/NEXT_EVOLUTION_CANDIDATE.md") else ""

    positive_signals = [
        ("sync_in_sync", is_sync_aligned(sync["verdict"]), 15),
        ("worktree_clean", sync["evidence"]["worktree_clean"], 10),
        ("governance_compliant", governance["verdict"] == "COMPLIANT", 15),
        ("brain_stack_complete", len(governance["evidence"]["missing_stack"]) == 0, 10),
        ("evolution_layer_present", len(governance["evidence"]["missing_evolution"]) == 0, 10),
        ("critical_contradictions_zero", contradictions["critical_count"] == 0, 10),
        ("admission_gate_green", admission["verdict"] == "ADMISSIBLE", 10),
        ("bundle_ready", bundle["verdict"] == "READY", 10),
        ("safe_mirror_fresh", mirror["verdict"] == "PASS", 5),
        ("trust_not_failed", trust["verdict"] != "NOT_TRUSTED", 5),
    ]

    score = sum(weight for _, ok, weight in positive_signals if ok)
    gained = [name for name, ok, _ in positive_signals if ok]

    blocking_signals: list[str] = []
    if not is_sync_aligned(sync["verdict"]):
        blocking_signals.append("broken_sync_discipline")
    if contradictions["critical_count"] > 0:
        blocking_signals.append("unresolved_critical_contradiction")
    if trust["verdict"] == "NOT_TRUSTED":
        blocking_signals.append("hidden_blocker_or_failed_trust")

    current_cycle_clean = bool(observation_cycles.get("current_cycle_clean", False))
    observed_clean_cycles = int(observation_cycles.get("observed_clean_cycles", 0) or 0)

    approved_hardening_events = policy_log_text.count("decision: `APPROVED`")
    governance_hardening_evidence = approved_hardening_events > 0
    repeated_failure_reduction_evidence = bool(
        re.search(r"(drift|failure)\s+reduction", policy_log_text, flags=re.IGNORECASE)
    )

    false_pass_history_entries = len(re.findall(r"false\s+pass", policy_log_text, flags=re.IGNORECASE))
    false_pass_unresolved = bool(re.search(r"false\s+pass.*unresolved", policy_log_text, flags=re.IGNORECASE))
    unresolved_contradiction_history_hits = len(
        re.findall(r"unresolved critical contradiction", policy_log_text, flags=re.IGNORECASE)
    )

    observation_window_required = int(threshold_policy["observation_window_required"])
    candidate_cycles_required = int(threshold_policy["candidate_cycles_required"])
    ready_cycles_required = int(threshold_policy["ready_cycles_required"])
    promote_cycles_required = int(threshold_policy["promote_cycles_required"])

    observation_window_complete = observed_clean_cycles >= observation_window_required
    candidate_cycles_complete = observed_clean_cycles >= candidate_cycles_required
    ready_cycles_complete = observed_clean_cycles >= ready_cycles_required
    promote_cycles_complete = observed_clean_cycles >= promote_cycles_required
    blocking_signals_zero = len(blocking_signals) == 0
    mirror_evidence_fresh = mirror["verdict"] == "PASS"
    false_pass_history_zero = false_pass_history_entries == 0 and not false_pass_unresolved
    contradiction_history_clean = unresolved_contradiction_history_hits == 0 and contradictions["critical_count"] == 0
    evidence_completeness = (
        threshold_policy["exists"]
        and exists("docs/governance/POLICY_EVOLUTION_LOG.md")
        and exists("docs/governance/NEXT_EVOLUTION_CANDIDATE.md")
    )

    promotion_requirements_missing: list[str] = []
    if not threshold_policy["exists"]:
        promotion_requirements_missing.append("missing PROMOTION_THRESHOLD_POLICY baseline")
    if not observation_window_complete:
        promotion_requirements_missing.append(
            f"required observation window incomplete: {observed_clean_cycles}/{observation_window_required} clean cycles"
        )
    if not blocking_signals_zero:
        promotion_requirements_missing.append("blocking signals present")
    if not false_pass_history_zero:
        promotion_requirements_missing.append("false PASS history not clean")
    if not contradiction_history_clean:
        promotion_requirements_missing.append("contradiction history not clean")
    if not governance_hardening_evidence:
        promotion_requirements_missing.append("governance hardening evidence missing")
    if not repeated_failure_reduction_evidence:
        promotion_requirements_missing.append("repeated failure reduction evidence missing")
    if not mirror_evidence_fresh:
        promotion_requirements_missing.append("safe mirror evidence stale")
    if not evidence_completeness:
        promotion_requirements_missing.append("promotion evidence package incomplete")

    formal_promotion_thresholds_confirmed = len(promotion_requirements_missing) == 0

    explicit_promote_approval = (
        bool(re.search(r"-\s*recommendation:\s*`?\s*PROMOTE\s*`?", next_candidate_text, flags=re.IGNORECASE))
        or candidate_context["recommendation"] == "PROMOTE"
    )

    if blocking_signals:
        candidate_level = current_level
        readiness = "BLOCKED"
        evolution_verdict = "BLOCKED"
    elif score >= 90 and formal_promotion_thresholds_confirmed:
        candidate_level = "V2_READY"
        readiness = "HIGH"
        evolution_verdict = "PROMOTE" if explicit_promote_approval and promote_cycles_complete else "V2_READY"
    elif score >= 75:
        candidate_level = "V2_CANDIDATE"
        readiness = "MEDIUM_HIGH"
        evolution_verdict = "V2_CANDIDATE" if candidate_cycles_complete else "PREPARE"
    elif score >= 55:
        candidate_level = "V1_EVOLVING"
        readiness = "MEDIUM"
        evolution_verdict = "PREPARE"
    else:
        candidate_level = "V1_PLUS"
        readiness = "LOW"
        evolution_verdict = "HOLD"

    # Hard guard: never allow V2_READY/PROMOTE without formal promotion threshold confirmation.
    if evolution_verdict in {"V2_READY", "PROMOTE"} and not formal_promotion_thresholds_confirmed:
        evolution_verdict = "V2_CANDIDATE" if score >= 75 else "PREPARE"
        candidate_level = "V2_CANDIDATE" if score >= 75 else "V1_EVOLVING"
        readiness = "MEDIUM_HIGH" if score >= 75 else "MEDIUM"

    policy_changes_proposed: list[str] = []
    if governance["verdict"] != "COMPLIANT":
        policy_changes_proposed.append("Close governance compliance gaps listed in governance blockers.")
    if mirror["verdict"] == "WARNING":
        policy_changes_proposed.append("Refresh SAFE_MIRROR_MANIFEST and SAFE_MIRROR_BUILD_REPORT to current HEAD.")
    if contradictions["major_count"] > 0:
        policy_changes_proposed.append("Resolve major contradiction items before promotion.")
    if not repeated_failure_reduction_evidence:
        policy_changes_proposed.append("Record measurable repeated-failure reduction evidence in POLICY_EVOLUTION_LOG.")
    if not observation_window_complete:
        policy_changes_proposed.append(
            f"Accumulate {observation_window_required} consecutive clean full-check cycles with evidence linkage."
        )

    recommendation = evolution_verdict if evolution_verdict in {"HOLD", "PREPARE", "PROMOTE"} else "PREPARE"

    return {
        "verdict": evolution_verdict,
        "basis": "evidence-weighted maturity model gated by PROMOTION_THRESHOLD_POLICY",
        "evidence": {
            "score": score,
            "positive_signals": positive_signals,
            "current_level": current_level,
            "candidate_level": candidate_level,
            "readiness": readiness,
            "current_cycle_clean": current_cycle_clean,
            "observation_cycle_source_path": str(observation_cycles.get("path", "")),
            "observation_cycle_entries_total": int(observation_cycles.get("entries_total", 0) or 0),
            "threshold_policy": threshold_policy,
            "observed_clean_cycles": observed_clean_cycles,
            "observation_window_complete": observation_window_complete,
            "candidate_cycles_complete": candidate_cycles_complete,
            "ready_cycles_complete": ready_cycles_complete,
            "promote_cycles_complete": promote_cycles_complete,
            "false_pass_history_entries": false_pass_history_entries,
            "false_pass_unresolved": false_pass_unresolved,
            "unresolved_contradiction_history_hits": unresolved_contradiction_history_hits,
            "governance_hardening_evidence": governance_hardening_evidence,
            "repeated_failure_reduction_evidence": repeated_failure_reduction_evidence,
            "formal_promotion_thresholds_confirmed": formal_promotion_thresholds_confirmed,
            "promotion_requirements_missing": promotion_requirements_missing,
            "explicit_promote_approval": explicit_promote_approval,
        },
        "blockers": [*blocking_signals, *promotion_requirements_missing],
        "next_step": "Clear blocking signals." if blocking_signals else "Execute proposed validations for next maturity step.",
        "evolution_block": {
            "current_level": current_level,
            "candidate_level": candidate_level,
            "readiness": readiness,
            "signals_gained": gained,
            "blocking_signals": blocking_signals,
            "policy_changes_proposed": policy_changes_proposed,
            "recommendation": recommendation,
        },
    }


def parse_next_canonical_step() -> str:
    rel = "docs/NEXT_CANONICAL_STEP.md"
    if not exists(rel):
        return "unknown-next-step"
    text = read_text(rel)
    match = re.search(r"-\s*step_id:\s*`([^`]+)`", text, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    for line in text.splitlines():
        value = line.strip()
        if value and not value.startswith("#") and not value.startswith("-"):
            return value[:120]
    return "next-step-defined-in-doc"


def classify_blocking_reason(
    *,
    sync: dict[str, Any],
    governance: dict[str, Any],
    governance_acceptance: dict[str, Any],
    admission: dict[str, Any],
    trust: dict[str, Any],
    machine_mode: dict[str, Any],
) -> tuple[str, str]:
    if not is_sync_aligned(sync["verdict"]):
        detail = "; ".join(sync.get("blockers", [])) or "sync is not aligned"
        return "SYNC", detail

    if machine_mode["verdict"] == "BLOCKED":
        detail = "; ".join(machine_mode.get("blockers", [])) or "machine mode detection blocked"
        return "AUTHORITY", detail

    mode = machine_mode.get("evidence", {}).get("machine_mode", "unknown")
    if governance_acceptance["verdict"] != "PASS" and not is_sovereign_mode(str(mode)):
        detail = "sovereign governance acceptance unavailable in current rank-derived machine mode"
        return "ROLE_AUTHORITY", detail

    if governance["verdict"] == "NON_COMPLIANT":
        detail = "; ".join(governance.get("blockers", [])) or "governance non-compliant"
        return "GOVERNANCE_POLICY", detail

    if admission["verdict"] == "REJECTED":
        detail = "; ".join(admission.get("blockers", [])) or "admission rejected"
        return "ADMISSION_GATE", detail

    if trust["verdict"] == "NOT_TRUSTED":
        detail = "; ".join(trust.get("blockers", [])) or "trust verdict is NOT_TRUSTED"
        return "TRUST", detail

    if trust["verdict"] == "WARNING":
        detail = "; ".join(trust.get("warnings", [])) or "trust has warnings"
        return "WARNING", detail

    return "NONE", "no blocking reason"


def compute_status_layers(
    *,
    sync: dict[str, Any],
    governance: dict[str, Any],
    contradictions: dict[str, Any],
    bootstrap: dict[str, Any],
    mirror: dict[str, Any],
    bundle: dict[str, Any],
    governance_acceptance: dict[str, Any],
    admission: dict[str, Any],
    machine_mode: dict[str, Any],
) -> dict[str, Any]:
    workspace_blockers: list[str] = []
    workspace_warnings: list[str] = []

    if not is_sync_aligned(sync["verdict"]):
        workspace_blockers.append("sync_not_in_sync")
    elif str(sync["verdict"]).upper() == "IN_SYNC_CLASSIFIED":
        workspace_warnings.append("sync_classified_dirty")
    if contradictions["critical_count"] > 0:
        workspace_blockers.append("critical_contradictions_present")
    if governance["verdict"] == "NON_COMPLIANT":
        workspace_blockers.append("governance_non_compliant")
    if bootstrap["verdict"] == "BLOCKED":
        workspace_blockers.append("bootstrap_blocked")
    if bundle["verdict"] != "READY":
        workspace_blockers.append("bundle_not_ready")
    if mirror["verdict"] == "BLOCKED":
        workspace_blockers.append("safe_mirror_blocked")

    if contradictions["major_count"] > 0:
        workspace_warnings.append("major_contradictions_present")
    if governance["verdict"] == "PARTIAL":
        workspace_warnings.append("governance_partial")
    if bootstrap["verdict"] == "WARNING":
        workspace_warnings.append("bootstrap_warning")
    if mirror["verdict"] == "WARNING":
        workspace_warnings.append("safe_mirror_warning")

    if workspace_blockers:
        workspace_health = "FAIL"
    elif workspace_warnings:
        workspace_health = "WARNING"
    else:
        workspace_health = "PASS"

    mode = machine_mode.get("evidence", {}).get("machine_mode", "unknown")
    helper_tier = str(machine_mode.get("evidence", {}).get("helper_tier", "") or "")
    detected_rank = str(machine_mode.get("evidence", {}).get("detected_rank", "UNKNOWN"))
    if machine_mode["verdict"] == "BLOCKED":
        authority_status = "BLOCKED"
    elif is_sovereign_mode(str(mode)) and detected_rank == "EMPEROR":
        authority_status = "EMPEROR_FROM_THRONE_ANCHOR"
    elif mode == "helper" and helper_tier == "high" and detected_rank == "PRIMARCH":
        authority_status = "HELPER_HIGH_FROM_PRIMARCH_RANK"
    elif mode == "helper" and helper_tier == "low" and detected_rank == "ASTARTES":
        authority_status = "HELPER_LOW_FROM_ASTARTES_RANK"
    else:
        authority_status = "LIMITED_OR_UNKNOWN"

    if governance["verdict"] == "NON_COMPLIANT":
        governance_status = "NON_COMPLIANT"
    elif governance_acceptance["verdict"] == "PASS":
        governance_status = "ACCEPTED"
    elif not is_sovereign_mode(str(mode)):
        governance_status = "ROLE_LIMITED_ACCEPTANCE"
    else:
        governance_status = "GATE_BLOCKED"

    admission_verdict = admission["verdict"]
    if admission_verdict == "ADMISSIBLE":
        admission_status = "ADMISSION_GATE_OPEN"
    elif admission_verdict == "CONDITIONAL":
        admission_status = "ADMISSION_GATE_CONDITIONAL"
    else:
        admission_status = "ADMISSION_GATE_BLOCKED"

    explainability_missing = missing_paths(
        [
            MACHINE_OPERATOR_GUIDE_DOC,
            MACHINE_CAPABILITIES_SUMMARY_DOC,
            POLICY_DIGEST_DOC,
            "docs/NEXT_CANONICAL_STEP.md",
            "MACHINE_CONTEXT.md",
        ]
    )
    explainability_status = "READY" if not explainability_missing else "MISSING_EXPLAINABILITY_DOCS"

    return {
        "workspace_health": workspace_health,
        "workspace_blockers": workspace_blockers,
        "workspace_warnings": workspace_warnings,
        "authority_status": authority_status,
        "governance_status": governance_status,
        "admission_status": admission_status,
        "explainability_status": explainability_status,
        "explainability_missing": explainability_missing,
    }


def one_screen_status_payload(result: dict[str, Any]) -> dict[str, Any]:
    v = result["verdicts"]
    checks = result["checks"]
    machine_mode_evidence = dict(v["machine_mode"].get("evidence", {}) or {})
    rank_detection = dict(machine_mode_evidence.get("rank_detection", {}) or {})
    authority_path = str(
        rank_detection.get("throne_anchor_path")
        or machine_mode_evidence.get("throne_anchor_path")
        or GOLDEN_THRONE_AUTHORITY_ANCHOR_RELATIVE_PATH
    )
    legacy_substrate_env_present = bool(os.getenv("CVVCODEX_EMPEROR_PROOF_DIR", ""))
    legacy_creator_env_present = bool(os.getenv("CVVCODEX_CREATOR_AUTHORITY_DIR", ""))
    block_category, block_detail = classify_blocking_reason(
        sync=v["sync"],
        governance=v["governance"],
        governance_acceptance=v["governance_acceptance"],
        admission=v["admission"],
        trust=v["trust"],
        machine_mode=v["machine_mode"],
    )
    payload = {
        "schema_version": "one_screen_status.v1.2.0",
        "run_id": result["run_id"],
        "generated_at": result["generated_at"],
        "branch": result["repo"]["branch"],
        "head": result["repo"]["head"],
        "safe_mirror_main": result["repo"]["safe_mirror_main"],
        "machine_mode": machine_mode_evidence.get("machine_mode", "unknown"),
        "machine_mode_verdict": v["machine_mode"]["verdict"],
        "authority_present": bool(machine_mode_evidence.get("authority_present", False)),
        "authority_path": authority_path,
        "throne_breach": bool(rank_detection.get("throne_breach", False)),
        "emperor_status_blocked": bool(rank_detection.get("emperor_status_blocked", False)),
        "emperor_status": str(rank_detection.get("emperor_status", "UNKNOWN")),
        "legacy_substrate_env_present": legacy_substrate_env_present,
        "legacy_creator_env_present": legacy_creator_env_present,
        "legacy_envs_ignored_for_authority": True,
        "trust_verdict": v["trust"]["verdict"],
        "sync_verdict": v["sync"]["verdict"],
        "governance_verdict": v["governance"]["verdict"],
        "governance_acceptance_verdict": v["governance_acceptance"]["verdict"],
        "admission_verdict": v["admission"]["verdict"],
        "evolution_verdict": v["evolution"]["verdict"],
        "workspace_health": result.get("status_layers", {}).get("workspace_health", "UNKNOWN"),
        "authority_status": result.get("status_layers", {}).get("authority_status", "UNKNOWN"),
        "governance_status": result.get("status_layers", {}).get("governance_status", "UNKNOWN"),
        "admission_status": result.get("status_layers", {}).get("admission_status", "UNKNOWN"),
        "explainability_status": result.get("status_layers", {}).get("explainability_status", "UNKNOWN"),
        "next_canonical_step": result.get("next_canonical_step", "unknown-next-step"),
        "blocking_reason_category": block_category,
        "blocking_reason_detail": block_detail,
        "operator_action_required": block_category != "NONE",
        "critical_contradictions": checks["contradictions"]["critical_count"],
        "major_contradictions": checks["contradictions"]["major_count"],
    }
    return payload


def plain_status_markdown(result: dict[str, Any], one_screen: dict[str, Any]) -> str:
    notes: list[str] = []
    if one_screen["blocking_reason_category"] == "NONE":
        notes.append("no_blocking_factors_detected")
    else:
        notes.append("blocking_factors_present")
    if one_screen["operator_action_required"]:
        notes.append("operator_action_required=true")
    else:
        notes.append("operator_action_required=false")

    lines = [
        "# Runtime Status (Engineering One-Screen)",
        "",
        "## Runtime Identity",
        f"- schema_version: `{one_screen['schema_version']}`",
        f"- run_id: `{one_screen['run_id']}`",
        f"- generated_at_utc: `{one_screen['generated_at']}`",
        f"- branch: `{one_screen['branch']}`",
        f"- head: `{one_screen['head']}`",
        f"- safe_mirror_main: `{one_screen['safe_mirror_main']}`",
        f"- machine_mode: `{one_screen['machine_mode']}`",
        f"- machine_mode_verdict: `{one_screen['machine_mode_verdict']}`",
        "",
        "## Authority State",
        f"- authority_present: `{one_screen['authority_present']}`",
        f"- authority_status: `{one_screen['authority_status']}`",
        f"- authority_path: `{one_screen['authority_path'] or 'not-set-in-environment'}`",
        f"- emperor_status: `{one_screen.get('emperor_status', 'UNKNOWN')}`",
        f"- emperor_status_blocked: `{one_screen.get('emperor_status_blocked', False)}`",
        f"- throne_breach: `{one_screen.get('throne_breach', False)}`",
        f"- legacy_substrate_env_present: `{one_screen['legacy_substrate_env_present']}`",
        f"- legacy_creator_env_present: `{one_screen['legacy_creator_env_present']}`",
        f"- legacy_envs_ignored_for_authority: `{one_screen['legacy_envs_ignored_for_authority']}`",
        "",
        "## Trust / Sync / Governance Chain",
        f"- trust_verdict: `{one_screen['trust_verdict']}`",
        f"- sync_verdict: `{one_screen['sync_verdict']}`",
        f"- governance_verdict: `{one_screen['governance_verdict']}`",
        f"- governance_acceptance_verdict: `{one_screen['governance_acceptance_verdict']}`",
        f"- evolution_verdict: `{one_screen['evolution_verdict']}`",
        "",
        "## Acceptance / Admission State",
        f"- workspace_health: `{one_screen['workspace_health']}`",
        f"- governance_status: `{one_screen['governance_status']}`",
        f"- admission_verdict: `{one_screen['admission_verdict']}`",
        f"- admission_status: `{one_screen['admission_status']}`",
        f"- explainability_status: `{one_screen['explainability_status']}`",
        "",
        "## Blocking Factors",
        f"- blocking_reason_category: `{one_screen['blocking_reason_category']}`",
        f"- blocking_reason_detail: `{one_screen['blocking_reason_detail']}`",
        f"- contradictions: critical=`{one_screen['critical_contradictions']}` major=`{one_screen['major_contradictions']}`",
        "",
        "## Canonical Next Step",
        f"- next_canonical_step: `{one_screen['next_canonical_step']}`",
        "",
        "## Notes / Exceptions",
    ]
    lines.extend([f"- {item}" for item in notes])
    return "\n".join(lines) + "\n"


def build_results(fetch: bool, mode_for_cycles: str = "") -> dict[str, Any]:
    run_id = f"rcc-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    git_state = build_git_state(fetch=fetch)
    contradictions = contradiction_checks(git_state)
    bootstrap = bootstrap_enforcement_checks()
    machine_mode = machine_mode_checks()
    integration_inbox = integration_inbox_checks()
    governance = governance_checks()
    sync = sync_checks(git_state)
    gate_runtime = gate_runtime_checks(git_state)
    law_lock = foundation_law_lock_checks()
    mirror = mirror_checks(git_state)
    bundle = bundle_checks()
    trust = trust_checks(sync, governance, contradictions, mirror, bundle, bootstrap, machine_mode, integration_inbox, gate_runtime, law_lock)
    governance_acceptance = governance_acceptance_checks(
        sync=sync,
        trust=trust,
        governance=governance,
        contradictions=contradictions,
        mirror=mirror,
        bundle=bundle,
        bootstrap=bootstrap,
        machine_mode=machine_mode,
        gate_runtime=gate_runtime,
        law_lock=law_lock,
        git_state=git_state,
    )
    admission = admission_checks(trust, sync, governance, contradictions, governance_acceptance, machine_mode)
    if str(mode_for_cycles).strip().lower() in {"full-check", "audit"}:
        observation_cycles = persist_observation_cycle_state(
            run_id=run_id,
            git_state=git_state,
            sync=sync,
            trust=trust,
            mirror=mirror,
            governance_acceptance=governance_acceptance,
            admission=admission,
            contradictions=contradictions,
        )
    else:
        state = load_observation_cycle_state()
        cycles = list(state.get("cycles", []) or [])
        observation_cycles = {
            "path": str(OBSERVATION_CYCLE_STATE_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "entries_total": len(cycles),
            "observed_clean_cycles": int(state.get("observed_clean_cycles", 0) or 0),
            "current_cycle_clean": bool(cycles[-1].get("clean_cycle", False)) if cycles else False,
        }
    evolution = evolution_checks(
        sync,
        governance,
        contradictions,
        trust,
        admission,
        mirror,
        bundle,
        observation_cycles,
    )

    status_layers = compute_status_layers(
        sync=sync,
        governance=governance,
        contradictions=contradictions,
        bootstrap=bootstrap,
        mirror=mirror,
        bundle=bundle,
        governance_acceptance=governance_acceptance,
        admission=admission,
        machine_mode=machine_mode,
    )
    repo_health = status_layers["workspace_health"]
    next_canonical_step = parse_next_canonical_step()

    drift_status = {
        "critical": contradictions["critical_count"] > 0 or str(sync["verdict"]).upper() in {"DRIFTED", "BLOCKED"},
        "major": contradictions["major_count"] > 0 or governance["verdict"] == "PARTIAL" or str(sync["verdict"]).upper() == "IN_SYNC_CLASSIFIED",
        "status": (
            "CRITICAL"
            if contradictions["critical_count"] > 0 or str(sync["verdict"]).upper() in {"DRIFTED", "BLOCKED"}
            else "MAJOR"
            if contradictions["major_count"] > 0 or governance["verdict"] == "PARTIAL" or str(sync["verdict"]).upper() == "IN_SYNC_CLASSIFIED"
            else "LOW"
        ),
    }

    return {
        "run_id": run_id,
        "generated_at": utc_now(),
        "canonical": {
            "local_root": CANONICAL_LOCAL_ROOT,
            "safe_mirror_repo": CANONICAL_SAFE_REPO,
            "safe_mirror_ref": CANONICAL_REMOTE_REF,
            "targeted_bundle_export": "scripts/export_chatgpt_bundle.py",
        },
        "repo": {
            "branch": git_state.branch,
            "head": git_state.head,
            "safe_mirror_main": git_state.remote_head,
            "ahead": git_state.ahead,
            "behind": git_state.behind,
            "worktree_clean": git_state.worktree_clean,
            "status_short": git_state.status_short,
            "repo_health": repo_health,
            "workspace_health": status_layers["workspace_health"],
        },
        "next_canonical_step": next_canonical_step,
        "status_layers": status_layers,
        "checks": {
            "contradictions": contradictions,
            "drift": drift_status,
            "bootstrap": bootstrap,
            "machine_mode": machine_mode,
            "integration_inbox": integration_inbox,
            "gate_runtime": gate_runtime,
            "law_lock": law_lock,
            "mirror": mirror,
            "bundle": bundle,
            "governance_acceptance": governance_acceptance,
        },
        "verdicts": {
            "trust": trust,
            "sync": sync,
            "governance": {
                "verdict": governance["verdict"],
                "basis": "governance brain stack + evolution layer completeness and manifest linkage",
                "evidence": governance["evidence"],
                "blockers": governance["blockers"],
                "next_step": "Resolve governance blockers." if governance["blockers"] else "Maintain governance parity.",
            },
            "governance_acceptance": governance_acceptance,
            "machine_mode": {
                "verdict": machine_mode["verdict"],
                "basis": machine_mode["basis"],
                "evidence": machine_mode["evidence"],
                "blockers": machine_mode["blockers"],
                "warnings": machine_mode["warnings"],
                "next_step": machine_mode["next_step"],
            },
            "gate_runtime": gate_runtime,
            "law_lock": law_lock,
            "integration_inbox": {
                "verdict": integration_inbox["verdict"],
                "basis": integration_inbox["basis"],
                "evidence": integration_inbox["evidence"],
                "blockers": integration_inbox["blockers"],
                "warnings": integration_inbox["warnings"],
                "next_step": integration_inbox["next_step"],
            },
            "admission": admission,
            "evolution": evolution,
        },
    }


def markdown_report(result: dict[str, Any]) -> str:
    v = result["verdicts"]
    lines = [
        "# Repo Control Center Report",
        "",
        f"- run_id: `{result['run_id']}`",
        f"- generated_at: `{result['generated_at']}`",
        "",
        "## Repo",
        f"- branch: `{result['repo']['branch']}`",
        f"- head: `{result['repo']['head']}`",
        f"- safe_mirror/main: `{result['repo']['safe_mirror_main']}`",
        f"- ahead/behind: `{result['repo']['ahead']}/{result['repo']['behind']}`",
        f"- worktree_clean: `{result['repo']['worktree_clean']}`",
        f"- repo_health: `{result['repo']['repo_health']}`",
        f"- workspace_health: `{result['repo'].get('workspace_health', 'UNKNOWN')}`",
        f"- authority_status: `{result.get('status_layers', {}).get('authority_status', 'UNKNOWN')}`",
        f"- governance_status: `{result.get('status_layers', {}).get('governance_status', 'UNKNOWN')}`",
        f"- admission_status: `{result.get('status_layers', {}).get('admission_status', 'UNKNOWN')}`",
        f"- explainability_status: `{result.get('status_layers', {}).get('explainability_status', 'UNKNOWN')}`",
        "",
        "## Verdicts",
        f"- TRUST VERDICT: `{v['trust']['verdict']}`",
        f"- SYNC VERDICT: `{v['sync']['verdict']}`",
        f"- GOVERNANCE VERDICT: `{v['governance']['verdict']}`",
        f"- ADMISSION VERDICT: `{v['admission']['verdict']}`",
        f"- EVOLUTION VERDICT: `{v['evolution']['verdict']}`",
        f"- MACHINE MODE VERDICT: `{v['machine_mode']['verdict']}`",
        f"- GATE RUNTIME VERDICT: `{v['gate_runtime']['verdict']}`",
        f"- LAW LOCK VERDICT: `{v['law_lock']['verdict']}`",
        f"- INTEGRATION INBOX VERDICT: `{v['integration_inbox']['verdict']}`",
        "",
        "## Contradictions",
        f"- critical: `{result['checks']['contradictions']['critical_count']}`",
        f"- major: `{result['checks']['contradictions']['major_count']}`",
        f"- total: `{result['checks']['contradictions']['count']}`",
        "",
        "## Drift",
        f"- status: `{result['checks']['drift']['status']}`",
        f"- critical: `{result['checks']['drift']['critical']}`",
        f"- major: `{result['checks']['drift']['major']}`",
        "",
        "## Bundle Readiness",
        f"- verdict: `{result['checks']['bundle']['verdict']}`",
        "",
        "## Bootstrap Enforcement",
        f"- verdict: `{result['checks']['bootstrap']['verdict']}`",
        "",
        "## Machine Mode",
        f"- verdict: `{result['checks']['machine_mode']['verdict']}`",
        f"- detected_mode: `{result['checks']['machine_mode']['evidence'].get('machine_mode', 'unknown')}`",
        "",
        "## Integration Inbox",
        f"- verdict: `{result['checks']['integration_inbox']['verdict']}`",
        "",
        "## Safe Mirror Health",
        f"- verdict: `{result['checks']['mirror']['verdict']}`",
        "",
        "## Governance Acceptance Gate",
        f"- verdict: `{result['checks']['governance_acceptance']['verdict']}`",
        "",
        "## Next Canonical Step",
        f"- `{result.get('next_canonical_step', 'unknown-next-step')}`",
        "",
        "## EVOLUTION",
        f"- current_level: `{v['evolution']['evolution_block']['current_level']}`",
        f"- candidate_level: `{v['evolution']['evolution_block']['candidate_level']}`",
        f"- readiness: `{v['evolution']['evolution_block']['readiness']}`",
        "- signals_gained:",
    ]
    for item in v["evolution"]["evolution_block"]["signals_gained"]:
        lines.append(f"  - {item}")
    lines.append("- blocking_signals:")
    for item in v["evolution"]["evolution_block"]["blocking_signals"] or ["none"]:
        lines.append(f"  - {item}")
    lines.append("- policy_changes_proposed:")
    for item in v["evolution"]["evolution_block"]["policy_changes_proposed"] or ["none"]:
        lines.append(f"  - {item}")
    lines.append("- recommendation:")
    lines.append(f"  - {v['evolution']['evolution_block']['recommendation']}")
    return "\n".join(lines) + "\n"


def evolution_markdown(result: dict[str, Any]) -> str:
    e = result["verdicts"]["evolution"]["evolution_block"]
    lines = [
        "# Evolution Readiness Report",
        "",
        f"- run_id: `{result['run_id']}`",
        f"- generated_at: `{result['generated_at']}`",
        f"- current_level: `{e['current_level']}`",
        f"- candidate_level: `{e['candidate_level']}`",
        f"- readiness: `{e['readiness']}`",
        f"- evolution_verdict: `{result['verdicts']['evolution']['verdict']}`",
        "",
        "## Signals Gained",
    ]
    lines.extend([f"- {x}" for x in e["signals_gained"]] or ["- none"])
    lines += [
        "",
        "## Blocking Signals",
    ]
    lines.extend([f"- {x}" for x in e["blocking_signals"]] or ["- none"])
    lines += [
        "",
        "## Policy Changes Proposed",
    ]
    lines.extend([f"- {x}" for x in e["policy_changes_proposed"]] or ["- none"])
    lines += [
        "",
        "## Recommendation",
        f"- {e['recommendation']}",
    ]
    return "\n".join(lines) + "\n"


def write_runtime_reports(result: dict[str, Any]) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    (RUNTIME_DIR / "repo_control_status.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (RUNTIME_DIR / "repo_control_report.md").write_text(markdown_report(result), encoding="utf-8")

    evolution_status = {
        "run_id": result["run_id"],
        "generated_at": result["generated_at"],
        "evolution": result["verdicts"]["evolution"],
    }
    (RUNTIME_DIR / "evolution_status.json").write_text(
        json.dumps(evolution_status, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (RUNTIME_DIR / "evolution_report.md").write_text(evolution_markdown(result), encoding="utf-8")

    machine_mode_status = {
        "run_id": result["run_id"],
        "generated_at": result["generated_at"],
        "machine_mode": result["checks"]["machine_mode"],
    }
    (RUNTIME_DIR / "machine_mode_status.json").write_text(
        json.dumps(machine_mode_status, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    mm = result["checks"]["machine_mode"]
    mm_lines = [
        "# Machine Mode Report",
        "",
        f"- run_id: `{result['run_id']}`",
        f"- generated_at: `{result['generated_at']}`",
        f"- verdict: `{mm['verdict']}`",
        f"- machine_mode: `{mm['evidence'].get('machine_mode', 'unknown')}`",
        f"- detection_state: `{mm['evidence'].get('detection_state', 'unknown')}`",
        "",
        "## Allowed Operations",
    ]
    mm_lines.extend([f"- {x}" for x in mm["evidence"].get("allowed_operations", [])] or ["- none"])
    mm_lines += ["", "## Forbidden Operations"]
    mm_lines.extend([f"- {x}" for x in mm["evidence"].get("forbidden_operations", [])] or ["- none"])
    if mm.get("warnings"):
        mm_lines += ["", "## Warnings"]
        mm_lines.extend([f"- {x}" for x in mm["warnings"]])
    if mm.get("blockers"):
        mm_lines += ["", "## Blockers"]
        mm_lines.extend([f"- {x}" for x in mm["blockers"]])
    (RUNTIME_DIR / "machine_mode_report.md").write_text("\n".join(mm_lines) + "\n", encoding="utf-8")

    one_screen = one_screen_status_payload(result)
    (RUNTIME_DIR / "one_screen_status.json").write_text(
        json.dumps(one_screen, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (RUNTIME_DIR / "plain_status.md").write_text(
        plain_status_markdown(result, one_screen),
        encoding="utf-8",
    )


def summarize_for_mode(result: dict[str, Any], mode: str) -> dict[str, Any]:
    v = result["verdicts"]
    base = {
        "run_id": result["run_id"],
        "mode": mode,
        "repo": result["repo"],
    }
    if mode == "status":
        base["summary"] = {
            "repo_health": result["repo"]["repo_health"],
            "workspace_health": result["repo"].get("workspace_health", "UNKNOWN"),
            "authority_status": result.get("status_layers", {}).get("authority_status", "UNKNOWN"),
            "governance_status": result.get("status_layers", {}).get("governance_status", "UNKNOWN"),
            "admission_status": result.get("status_layers", {}).get("admission_status", "UNKNOWN"),
            "explainability_status": result.get("status_layers", {}).get("explainability_status", "UNKNOWN"),
            "trust_verdict": v["trust"]["verdict"],
            "sync_verdict": v["sync"]["verdict"],
            "governance_verdict": v["governance"]["verdict"],
            "governance_acceptance_verdict": v["governance_acceptance"]["verdict"],
            "machine_mode_verdict": v["machine_mode"]["verdict"],
            "gate_runtime_verdict": v["gate_runtime"]["verdict"],
            "law_lock_verdict": v["law_lock"]["verdict"],
            "integration_inbox_verdict": v["integration_inbox"]["verdict"],
            "admission_verdict": v["admission"]["verdict"],
            "evolution_verdict": v["evolution"]["verdict"],
            "next_canonical_step": result.get("next_canonical_step", "unknown-next-step"),
        }
    elif mode == "mode":
        base["machine_mode"] = v["machine_mode"]
    elif mode == "integration":
        base["integration_inbox"] = v["integration_inbox"]
    elif mode == "trust":
        base["trust"] = v["trust"]
        base["gate_runtime"] = v["gate_runtime"]
        base["law_lock"] = v["law_lock"]
        base["governance"] = v["governance"]
        base["governance_acceptance"] = v["governance_acceptance"]
        base["admission"] = v["admission"]
    elif mode == "sync":
        base["sync"] = v["sync"]
    elif mode == "mirror":
        base["mirror"] = result["checks"]["mirror"]
    elif mode == "bundle":
        base["bundle"] = result["checks"]["bundle"]
    elif mode == "evolution":
        base["evolution"] = v["evolution"]
    elif mode in {"audit", "full-check"}:
        base["full"] = result
    return base


def exit_code_for_mode(result: dict[str, Any], mode: str) -> int:
    v = result["verdicts"]
    if mode == "mode":
        return 0 if v["machine_mode"]["verdict"] in {"PASS", "WARNING"} else 1
    if mode == "integration":
        return 0 if v["integration_inbox"]["verdict"] in {"PASS", "WARNING"} else 1
    if mode == "sync":
        return 0 if is_sync_aligned(v["sync"]["verdict"]) else 1
    if mode == "trust":
        return 0 if v["trust"]["verdict"] == "TRUSTED" and v["governance_acceptance"]["verdict"] == "PASS" else 1
    if mode == "evolution":
        return 0 if v["evolution"]["verdict"] not in {"BLOCKED"} else 1
    if mode in {"audit", "full-check"}:
        return 0 if v["admission"]["verdict"] in {"ADMISSIBLE", "CONDITIONAL"} and is_sync_aligned(v["sync"]["verdict"]) else 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Repo Control Center V1 (CLI-first)")
    parser.add_argument("mode", choices=["status", "mode", "integration", "audit", "trust", "sync", "mirror", "bundle", "evolution", "full-check"])
    parser.add_argument("--no-fetch", action="store_true", help="Skip git fetch --all --prune before checks.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = build_results(fetch=not args.no_fetch, mode_for_cycles=args.mode)
    write_runtime_reports(result)
    payload = summarize_for_mode(result, args.mode)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code_for_mode(result, args.mode)


if __name__ == "__main__":
    raise SystemExit(main())

