#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
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

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = REPO_ROOT / "runtime" / "repo_control_center"

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


def load_json(rel: str) -> dict[str, Any]:
    return json.loads(read_text(rel))


def exists(rel: str) -> bool:
    return (REPO_ROOT / rel).exists()


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
    if not detection_contract.exists():
        blockers.append("missing workspace_config/creator_mode_detection_contract.json")
    if not federation_contract.exists():
        blockers.append("missing workspace_config/federation_mode_contract.json")

    if detection_contract.exists():
        text = detection_contract.read_text(encoding="utf-8-sig")
        if re.search(r"[A-Za-z]:\\\\", text):
            blockers.append("creator detection contract leaks local absolute path")

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
        evidence["authority_present"] = payload.get("authority", {}).get("authority_present")
        evidence["detection_state"] = payload.get("authority", {}).get("detection_state")
        evidence["env_var_name"] = payload.get("authority", {}).get("env_var_name")
        evidence["marker_filename"] = payload.get("authority", {}).get("marker_filename")
        evidence["allowed_operations"] = payload.get("operations", {}).get("allowed", [])
        evidence["forbidden_operations"] = payload.get("operations", {}).get("forbidden", [])
        evidence["warnings"] = payload.get("warnings", [])

        mode = str(payload.get("machine_mode", "helper"))
        if mode == "helper":
            warnings.append("machine is in helper mode (creator authority absent)")

    if blockers:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "WARNING"
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "basis": "federation machine-mode detection via external creator authority contract",
        "evidence": evidence,
        "blockers": blockers,
        "warnings": warnings,
        "next_step": "Establish creator authority marker for canonical creator operations." if warnings else "Machine mode detection is valid.",
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
    missing_core = missing_paths(CORE_DOCS)
    missing_acceptance = missing_paths([GOVERNANCE_ACCEPTANCE_DOC])

    weak_docs: list[str] = []
    for rel in GOVERNANCE_BRAIN_STACK + EVOLUTION_LAYER_DOCS + FEDERATION_LAYER_DOCS:
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

    blockers = [
        *[f"missing governance doc: {p}" for p in missing_stack],
        *[f"missing evolution doc: {p}" for p in missing_evolution],
        *[f"missing hardening doc: {p}" for p in missing_hardening],
        *[f"missing federation doc: {p}" for p in missing_federation],
        *[f"missing federation contract: {p}" for p in missing_federation_contracts],
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
            "missing_acceptance": missing_acceptance,
            "missing_core": missing_core,
            "weak_docs": weak_docs,
        },
    }


def sync_checks(git_state: GitState) -> dict[str, Any]:
    blockers: list[str] = []
    if git_state.branch != CANONICAL_BRANCH:
        blockers.append(f"branch mismatch: {git_state.branch}")
    if git_state.head != git_state.remote_head:
        blockers.append("HEAD != safe_mirror/main")
    if git_state.ahead != 0 or git_state.behind != 0:
        blockers.append(f"divergence {git_state.ahead}/{git_state.behind}")
    if not git_state.worktree_clean:
        blockers.append("worktree dirty")

    if not blockers:
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
        },
        "blockers": blockers,
        "next_step": "Run git add/commit/push and resolve divergence/worktree blockers." if blockers else "Maintain parity discipline.",
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
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if sync["verdict"] != "IN_SYNC":
        blockers.append(f"sync verdict {sync['verdict']}")
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
        warnings.append("machine mode is helper-only (creator authority absent)")

    if integration_inbox["verdict"] == "BLOCKED":
        blockers.append("integration inbox flow blocked")
    elif integration_inbox["verdict"] == "WARNING":
        warnings.append("integration inbox flow warning")

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
    if trust["verdict"] == "NOT_TRUSTED":
        blockers.append("trust verdict is NOT_TRUSTED")
    if sync["verdict"] != "IN_SYNC":
        blockers.append("sync not IN_SYNC")
    if governance["verdict"] == "NON_COMPLIANT":
        blockers.append("governance NON_COMPLIANT")
    if contradictions["critical_count"] > 0:
        blockers.append("critical contradictions unresolved")
    if governance_acceptance["verdict"] != "PASS":
        blockers.append("governance acceptance gate not PASS")
    if machine_mode.get("evidence", {}).get("machine_mode") != "creator":
        blockers.append("machine mode is not creator")

    if blockers:
        verdict = "REJECTED"
    elif trust["verdict"] == "WARNING" or governance["verdict"] == "PARTIAL" or contradictions["major_count"] > 0:
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
        },
        "blockers": blockers,
        "next_step": "Clear blockers to reach ADMISSIBLE." if blockers else "Admission gate is clear.",
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
    git_state: GitState,
) -> dict[str, Any]:
    blockers: list[str] = []
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
    has_valid_route = has_governance_closure or has_federation_transition
    evidence["next_step_has_governance_acceptance_closure"] = has_governance_closure
    evidence["next_step_has_federation_transition"] = has_federation_transition
    evidence["next_step_has_valid_post_acceptance_route"] = has_valid_route
    if not has_valid_route:
        blockers.append("NEXT_CANONICAL_STEP missing governance-accepted canonical route")

    if sync["verdict"] != "IN_SYNC":
        blockers.append("sync gate not IN_SYNC")
    if trust["verdict"] != "TRUSTED":
        blockers.append("trust gate not TRUSTED")
    if governance["verdict"] != "COMPLIANT":
        blockers.append("governance gate not COMPLIANT")
    if bootstrap["verdict"] != "PASS":
        blockers.append("bootstrap enforcement not PASS")
    if mirror["verdict"] != "PASS":
        blockers.append("safe mirror evidence gate not PASS")
    if bundle["verdict"] != "READY":
        blockers.append("bundle gate not READY")
    if machine_mode["verdict"] == "BLOCKED":
        blockers.append("machine mode detection blocked")
    if machine_mode.get("evidence", {}).get("machine_mode") != "creator":
        blockers.append("creator authority required for governance acceptance PASS")
    if contradictions["critical_count"] > 0:
        blockers.append("critical contradictions unresolved")
    if not git_state.worktree_clean:
        blockers.append("worktree is dirty")
    if git_state.ahead != 0 or git_state.behind != 0:
        blockers.append(f"divergence is not zero: {git_state.ahead}/{git_state.behind}")

    verdict = "PASS" if not blockers else "FAIL"
    return {
        "verdict": verdict,
        "basis": "formal governance acceptance gate for transition readiness",
        "evidence": evidence,
        "blockers": blockers,
        "next_step": "Governance foundation accepted for next-stage consideration." if verdict == "PASS" else "Close governance acceptance blockers.",
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


def evolution_checks(sync: dict[str, Any], governance: dict[str, Any], contradictions: dict[str, Any], trust: dict[str, Any], admission: dict[str, Any], mirror: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    candidate_context = parse_candidate_context()
    current_level = candidate_context["current_level"]
    threshold_policy = parse_promotion_threshold_policy()
    policy_log_text = read_text("docs/governance/POLICY_EVOLUTION_LOG.md") if exists("docs/governance/POLICY_EVOLUTION_LOG.md") else ""
    next_candidate_text = read_text("docs/governance/NEXT_EVOLUTION_CANDIDATE.md") if exists("docs/governance/NEXT_EVOLUTION_CANDIDATE.md") else ""

    positive_signals = [
        ("sync_in_sync", sync["verdict"] == "IN_SYNC", 15),
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
    if sync["verdict"] != "IN_SYNC":
        blocking_signals.append("broken_sync_discipline")
    if contradictions["critical_count"] > 0:
        blocking_signals.append("unresolved_critical_contradiction")
    if trust["verdict"] == "NOT_TRUSTED":
        blocking_signals.append("hidden_blocker_or_failed_trust")

    current_cycle_clean = (
        sync["verdict"] == "IN_SYNC"
        and sync["evidence"]["worktree_clean"]
        and sync["evidence"]["ahead"] == 0
        and sync["evidence"]["behind"] == 0
        and contradictions["critical_count"] == 0
        and trust["verdict"] != "NOT_TRUSTED"
    )
    observed_clean_cycles = 1 if current_cycle_clean else 0

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


def build_results(fetch: bool) -> dict[str, Any]:
    git_state = build_git_state(fetch=fetch)
    contradictions = contradiction_checks(git_state)
    bootstrap = bootstrap_enforcement_checks()
    machine_mode = machine_mode_checks()
    integration_inbox = integration_inbox_checks()
    governance = governance_checks()
    sync = sync_checks(git_state)
    mirror = mirror_checks(git_state)
    bundle = bundle_checks()
    trust = trust_checks(sync, governance, contradictions, mirror, bundle, bootstrap, machine_mode, integration_inbox)
    governance_acceptance = governance_acceptance_checks(
        sync=sync,
        trust=trust,
        governance=governance,
        contradictions=contradictions,
        mirror=mirror,
        bundle=bundle,
        bootstrap=bootstrap,
        machine_mode=machine_mode,
        git_state=git_state,
    )
    admission = admission_checks(trust, sync, governance, contradictions, governance_acceptance, machine_mode)
    evolution = evolution_checks(sync, governance, contradictions, trust, admission, mirror, bundle)

    repo_health = "PASS"
    if trust["verdict"] == "NOT_TRUSTED" or admission["verdict"] == "REJECTED" or governance_acceptance["verdict"] != "PASS":
        repo_health = "FAIL"
    elif trust["verdict"] == "WARNING" or admission["verdict"] == "CONDITIONAL":
        repo_health = "WARNING"

    drift_status = {
        "critical": contradictions["critical_count"] > 0 or sync["verdict"] != "IN_SYNC",
        "major": contradictions["major_count"] > 0 or governance["verdict"] == "PARTIAL",
        "status": "CRITICAL" if contradictions["critical_count"] > 0 or sync["verdict"] != "IN_SYNC" else "LOW",
    }

    return {
        "run_id": f"rcc-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
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
        },
        "checks": {
            "contradictions": contradictions,
            "drift": drift_status,
            "bootstrap": bootstrap,
            "machine_mode": machine_mode,
            "integration_inbox": integration_inbox,
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
        "",
        "## Verdicts",
        f"- TRUST VERDICT: `{v['trust']['verdict']}`",
        f"- SYNC VERDICT: `{v['sync']['verdict']}`",
        f"- GOVERNANCE VERDICT: `{v['governance']['verdict']}`",
        f"- ADMISSION VERDICT: `{v['admission']['verdict']}`",
        f"- EVOLUTION VERDICT: `{v['evolution']['verdict']}`",
        f"- MACHINE MODE VERDICT: `{v['machine_mode']['verdict']}`",
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
            "trust": v["trust"]["verdict"],
            "sync": v["sync"]["verdict"],
            "governance": v["governance"]["verdict"],
            "governance_acceptance": v["governance_acceptance"]["verdict"],
            "machine_mode": v["machine_mode"]["verdict"],
            "integration_inbox": v["integration_inbox"]["verdict"],
            "admission": v["admission"]["verdict"],
            "evolution": v["evolution"]["verdict"],
        }
    elif mode == "mode":
        base["machine_mode"] = v["machine_mode"]
    elif mode == "integration":
        base["integration_inbox"] = v["integration_inbox"]
    elif mode == "trust":
        base["trust"] = v["trust"]
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
        return 0 if v["sync"]["verdict"] == "IN_SYNC" else 1
    if mode == "trust":
        return 0 if v["trust"]["verdict"] == "TRUSTED" and v["governance_acceptance"]["verdict"] == "PASS" else 1
    if mode == "evolution":
        return 0 if v["evolution"]["verdict"] not in {"BLOCKED"} else 1
    if mode in {"audit", "full-check"}:
        return 0 if v["admission"]["verdict"] in {"ADMISSIBLE", "CONDITIONAL"} and v["sync"]["verdict"] == "IN_SYNC" else 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Repo Control Center V1 (CLI-first)")
    parser.add_argument("mode", choices=["status", "mode", "integration", "audit", "trust", "sync", "mirror", "bundle", "evolution", "full-check"])
    parser.add_argument("--no-fetch", action="store_true", help="Skip git fetch --all --prune before checks.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = build_results(fetch=not args.no_fetch)
    write_runtime_reports(result)
    payload = summarize_for_mode(result, args.mode)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code_for_mode(result, args.mode)


if __name__ == "__main__":
    raise SystemExit(main())
