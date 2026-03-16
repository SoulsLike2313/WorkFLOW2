#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
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
    missing_core = missing_paths(CORE_DOCS)

    weak_docs: list[str] = []
    for rel in GOVERNANCE_BRAIN_STACK + EVOLUTION_LAYER_DOCS:
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

    bootstrap = cm.get("bootstrap_read_order", [])
    missing_bootstrap = [rel for rel in BOOTSTRAP_REQUIRED if rel not in bootstrap]

    blockers = [
        *[f"missing governance doc: {p}" for p in missing_stack],
        *[f"missing evolution doc: {p}" for p in missing_evolution],
        *[f"missing core doc: {p}" for p in missing_core],
        *governance_refs_missing,
        *[f"bootstrap missing: {p}" for p in missing_bootstrap],
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
            "missing_core": missing_core,
            "missing_bootstrap": missing_bootstrap,
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
    evidence: dict[str, Any] = {"required_files": SAFE_STATE_FILES, "missing": missing}

    if missing:
        blockers.extend([f"missing safe-state artifact: {p}" for p in missing])

    if exists("workspace_config/SAFE_MIRROR_MANIFEST.json"):
        safe_manifest = load_json("workspace_config/SAFE_MIRROR_MANIFEST.json")
        manifest_head = safe_manifest.get("head_sha")
        evidence["manifest_head"] = manifest_head
        evidence["current_head"] = git_state.head
        evidence["manifest_head_matches_current"] = manifest_head == git_state.head

    if exists("docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md"):
        report_text = read_text("docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md")
        evidence["report_mentions_current_head"] = git_state.head in report_text

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
        for token in ["context", "files", "paths", "project", "request"]:
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


def trust_checks(sync: dict[str, Any], governance: dict[str, Any], contradictions: dict[str, Any], mirror: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
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

    if bundle["verdict"] != "READY":
        blockers.append("bundle readiness blocked")

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
            "bundle_verdict": bundle["verdict"],
        },
        "blockers": blockers,
        "warnings": warnings,
        "next_step": "Resolve blockers, then rerun full-check." if blockers else "Maintain trust baseline.",
    }


def admission_checks(trust: dict[str, Any], sync: dict[str, Any], governance: dict[str, Any], contradictions: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if trust["verdict"] == "NOT_TRUSTED":
        blockers.append("trust verdict is NOT_TRUSTED")
    if sync["verdict"] != "IN_SYNC":
        blockers.append("sync not IN_SYNC")
    if governance["verdict"] == "NON_COMPLIANT":
        blockers.append("governance NON_COMPLIANT")
    if contradictions["critical_count"] > 0:
        blockers.append("critical contradictions unresolved")

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
        },
        "blockers": blockers,
        "next_step": "Clear blockers to reach ADMISSIBLE." if blockers else "Admission gate is clear.",
    }


def parse_current_level() -> str:
    path = REPO_ROOT / "docs/governance/NEXT_EVOLUTION_CANDIDATE.md"
    if not path.exists():
        return "V1_STABLE"
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.lower().startswith("- current_level:"):
            return line.split(":", 1)[1].strip().strip("`")
    return "V1_STABLE"


def evolution_checks(sync: dict[str, Any], governance: dict[str, Any], contradictions: dict[str, Any], trust: dict[str, Any], admission: dict[str, Any], mirror: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    current_level = parse_current_level()

    positive_signals = [
        ("sync_in_sync", sync["verdict"] == "IN_SYNC", 15),
        ("worktree_clean", sync["evidence"]["worktree_clean"], 10),
        ("governance_compliant", governance["verdict"] == "COMPLIANT", 15),
        ("brain_stack_complete", len(governance["evidence"]["missing_stack"]) == 0, 10),
        ("evolution_layer_present", len(governance["evidence"]["missing_evolution"]) == 0, 10),
        ("critical_contradictions_zero", contradictions["critical_count"] == 0, 10),
        ("admission_gate_green", admission["verdict"] == "ADMISSIBLE", 10),
        ("bundle_ready", bundle["verdict"] == "READY", 10),
        ("safe_mirror_not_blocked", mirror["verdict"] != "BLOCKED", 5),
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

    if blocking_signals:
        candidate_level = current_level
        readiness = "BLOCKED"
        evolution_verdict = "BLOCKED"
    elif score >= 90:
        candidate_level = "V2_READY"
        readiness = "HIGH"
        evolution_verdict = "PROMOTE"
    elif score >= 75:
        candidate_level = "V2_CANDIDATE"
        readiness = "MEDIUM_HIGH"
        evolution_verdict = "V2_CANDIDATE"
    elif score >= 55:
        candidate_level = "V1_EVOLVING"
        readiness = "MEDIUM"
        evolution_verdict = "PREPARE"
    else:
        candidate_level = "V1_PLUS"
        readiness = "LOW"
        evolution_verdict = "HOLD"

    policy_changes_proposed: list[str] = []
    if governance["verdict"] != "COMPLIANT":
        policy_changes_proposed.append("Close governance compliance gaps listed in governance blockers.")
    if mirror["verdict"] == "WARNING":
        policy_changes_proposed.append("Refresh SAFE_MIRROR_MANIFEST and SAFE_MIRROR_BUILD_REPORT to current HEAD.")
    if contradictions["major_count"] > 0:
        policy_changes_proposed.append("Resolve major contradiction items before promotion.")

    recommendation = evolution_verdict if evolution_verdict in {"HOLD", "PREPARE", "PROMOTE"} else "PREPARE"

    return {
        "verdict": evolution_verdict,
        "basis": "evidence-weighted maturity signal model",
        "evidence": {
            "score": score,
            "positive_signals": positive_signals,
            "current_level": current_level,
            "candidate_level": candidate_level,
            "readiness": readiness,
        },
        "blockers": blocking_signals,
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
    governance = governance_checks()
    sync = sync_checks(git_state)
    mirror = mirror_checks(git_state)
    bundle = bundle_checks()
    trust = trust_checks(sync, governance, contradictions, mirror, bundle)
    admission = admission_checks(trust, sync, governance, contradictions)
    evolution = evolution_checks(sync, governance, contradictions, trust, admission, mirror, bundle)

    repo_health = "PASS"
    if trust["verdict"] == "NOT_TRUSTED" or admission["verdict"] == "REJECTED":
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
            "mirror": mirror,
            "bundle": bundle,
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
        "## Safe Mirror Health",
        f"- verdict: `{result['checks']['mirror']['verdict']}`",
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
            "admission": v["admission"]["verdict"],
            "evolution": v["evolution"]["verdict"],
        }
    elif mode == "trust":
        base["trust"] = v["trust"]
        base["governance"] = v["governance"]
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
    if mode == "sync":
        return 0 if v["sync"]["verdict"] == "IN_SYNC" else 1
    if mode == "trust":
        return 0 if v["trust"]["verdict"] == "TRUSTED" else 1
    if mode == "evolution":
        return 0 if v["evolution"]["verdict"] not in {"BLOCKED"} else 1
    if mode in {"audit", "full-check"}:
        return 0 if v["admission"]["verdict"] in {"ADMISSIBLE", "CONDITIONAL"} and v["sync"]["verdict"] == "IN_SYNC" else 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Repo Control Center V1 (CLI-first)")
    parser.add_argument("mode", choices=["status", "audit", "trust", "sync", "mirror", "bundle", "evolution", "full-check"])
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
