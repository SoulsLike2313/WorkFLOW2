#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from detect_machine_mode import build_mode_payload

CANONICAL_LOCAL_ROOT = r"E:\CVVCODEX"
REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = REPO_ROOT / "runtime" / "operator_command_layer"
OUTPUTS_DIR = RUNTIME_DIR / "outputs"
LAST_EXECUTION_PATH = RUNTIME_DIR / "last_execution.json"
LOG_PATH = RUNTIME_DIR / "command_execution_log.jsonl"
STATUS_PATH = RUNTIME_DIR / "command_surface_status.json"
REPORT_PATH = RUNTIME_DIR / "command_surface_report.md"
CONSISTENCY_PATH = RUNTIME_DIR / "operator_command_consistency_check.json"
REGISTRY_PATH = REPO_ROOT / "workspace_config" / "operator_command_registry.json"
ONE_SCREEN_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "one_screen_status.json"
POLICY_DIGEST_PATH = REPO_ROOT / "docs" / "governance" / "POLICY_DIGEST.md"

EXECUTION_CONTRACT_VERSION = "operator_command_execution_contract.v1.0.0"
STATUS_SCHEMA_VERSION = "operator_command_surface_status.v1.0.0"

OPERATOR_EVIDENCE_ALLOWLIST = [
    "runtime/repo_control_center/repo_control_status.json",
    "runtime/repo_control_center/repo_control_report.md",
    "runtime/repo_control_center/evolution_status.json",
    "runtime/repo_control_center/evolution_report.md",
    "runtime/repo_control_center/one_screen_status.json",
    "runtime/repo_control_center/plain_status.md",
    "runtime/repo_control_center/machine_mode_status.json",
    "runtime/repo_control_center/machine_mode_report.md",
    "runtime/operator_command_layer/command_surface_status.json",
    "runtime/operator_command_layer/command_surface_report.md",
    "runtime/operator_command_layer/last_execution.json",
]


@dataclass(frozen=True)
class RouteRule:
    command_class: str
    resolved_action: str
    tokens: tuple[str, ...]


@dataclass
class ActionPolicy:
    command_class: str
    resolved_action: str
    wave: str
    mutability_level: str
    allowed_modes: list[str]
    creator_authority_required: bool
    requires_in_sync: bool
    requires_clean_worktree: bool
    dry_run_supported: bool
    review_requirement: str
    policy_basis: list[str]
    execution_scope: str


@dataclass
class ActionOutcome:
    execution_result: dict[str, Any]
    artifacts_produced: list[str]
    blocking_factors: list[str]
    notes: list[str]


ROUTING_PRECEDENCE: tuple[RouteRule, ...] = (
    RouteRule("install_remove_controlled_command", "remove_system", ("remove system", "uninstall system", "detach system")),
    RouteRule("install_remove_controlled_command", "install_system", ("install system", "add system", "attach system", "provision system")),
    RouteRule("creator_only_execution_command", "creator_acceptance_precheck", ("creator only execution", "creator precheck", "creator acceptance precheck", "creator full check")),
    RouteRule("guarded_state_change_command", "refresh_safe_mirror_evidence", ("guarded state change", "refresh safe mirror evidence", "refresh safe mirror manifest")),
    RouteRule("governance_maintenance_command", "governance_maintenance_check", ("governance maintenance", "policy maintenance", "governance integrity check")),
    RouteRule("handoff_command", "handoff_prepare", ("handoff command", "prepare handoff", "handoff package", "integration handoff")),
    RouteRule("inbox_review_command", "inbox_review", ("inbox review", "review integration inbox", "integration inbox review")),
    RouteRule("evidence_routing_command", "evidence_routing", ("evidence routing", "route evidence", "route runtime evidence")),
    RouteRule("policy_reference_command", "policy_reference_execute", ("policy reference command", "policy reference execution", "policy reference", "policy lookup")),
    RouteRule("validation_command", "validation_run", ("validation command", "run validation", "workspace validation", "validation sweep")),
    RouteRule("evidence_bundle_command", "evidence_bundle_context", ("evidence bundle command", "build evidence bundle", "bundle evidence", "export context bundle")),
    RouteRule("report_generation_command", "report_generation", ("report generation command", "generate execution report", "build execution report", "status report generation")),
    RouteRule("status_refresh_command", "status_refresh", ("status refresh command", "status refresh", "refresh status", "refresh runtime status")),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_rel(path: str) -> str:
    value = path.replace("\\", "/").strip()
    while value.startswith("./"):
        value = value[2:]
    return value.strip("/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def run_cmd(args: list[str], *, allow_fail: bool = False) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    if completed.returncode != 0 and not allow_fail:
        raise RuntimeError(f"command failed: {' '.join(args)} :: {completed.stderr.strip() or completed.stdout.strip()}")
    return completed


def safe_parse_json(raw: str) -> dict[str, Any] | None:
    text = raw.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except Exception:
        return None
    return parsed if isinstance(parsed, dict) else {"value": parsed}


def parse_git_status_files() -> set[str]:
    out = run_cmd(["git", "status", "--porcelain"], allow_fail=True).stdout
    files: set[str] = set()
    for line in out.splitlines():
        if len(line) >= 4:
            rel = normalize_rel(line[3:].strip())
            if rel:
                files.add(rel)
    return files


def git_head() -> str:
    return run_cmd(["git", "rev-parse", "HEAD"], allow_fail=True).stdout.strip()


def load_one_screen() -> dict[str, Any]:
    if not ONE_SCREEN_PATH.exists():
        return {
            "sync_verdict": "UNKNOWN",
            "workspace_health": "UNKNOWN",
            "trust_verdict": "UNKNOWN",
            "governance_verdict": "UNKNOWN",
            "governance_acceptance_verdict": "UNKNOWN",
            "admission_verdict": "UNKNOWN",
            "machine_mode": "unknown",
            "authority_present": False,
            "blocking_reason_category": "UNKNOWN",
            "blocking_reason_detail": "one_screen_status_missing",
            "next_canonical_step": "run repo_control_center status",
        }
    return load_json(ONE_SCREEN_PATH)


def load_registry() -> tuple[dict[str, Any], dict[str, ActionPolicy]]:
    if not REGISTRY_PATH.exists():
        raise RuntimeError(f"operator command registry missing: {REGISTRY_PATH}")
    payload = load_json(REGISTRY_PATH)
    action_index: dict[str, ActionPolicy] = {}
    for cls in payload.get("command_classes", []):
        base = {
            "command_class": str(cls.get("command_class", "")).strip(),
            "wave": str(cls.get("wave", "unknown")).strip(),
            "mutability_level": str(cls.get("mutability_level", "read_only")).strip(),
            "allowed_modes": [str(x).strip() for x in cls.get("allowed_modes", []) if str(x).strip()],
            "creator_authority_required": bool(cls.get("creator_authority_required", False)),
            "requires_in_sync": bool(cls.get("requires_in_sync", False)),
            "requires_clean_worktree": bool(cls.get("requires_clean_worktree", False)),
            "dry_run_supported": bool(cls.get("dry_run_supported", True)),
            "review_requirement": str(cls.get("review_requirement", "none")).strip(),
            "policy_basis": [str(x).strip() for x in cls.get("policy_basis", []) if str(x).strip()],
            "execution_scope": str(cls.get("execution_scope", cls.get("command_class", "unknown"))).strip(),
        }
        for action_cfg in cls.get("actions", []):
            action = str(action_cfg.get("resolved_action", "")).strip()
            if not action:
                continue
            action_index[action] = ActionPolicy(resolved_action=action, **base)
    if not action_index:
        raise RuntimeError("operator command registry contains no actions")
    return payload, action_index


def route_command(raw_command: str, action_index: dict[str, ActionPolicy], *, command_class_override: str = "", action_override: str = "") -> tuple[str, str, str]:
    if action_override and action_override.strip() in action_index:
        policy = action_index[action_override.strip()]
        return policy.command_class, policy.resolved_action, "explicit_action_override"
    if command_class_override:
        requested_class = command_class_override.strip()
        for action, policy in action_index.items():
            if policy.command_class == requested_class:
                return requested_class, action, "explicit_class_override"

    direct = raw_command.strip()
    if direct in action_index:
        policy = action_index[direct]
        return policy.command_class, policy.resolved_action, "direct_action_match"

    normalized = f" {' '.join(raw_command.lower().split())} "
    for rule in ROUTING_PRECEDENCE:
        if any(token in normalized for token in rule.tokens) and rule.resolved_action in action_index:
            return rule.command_class, rule.resolved_action, "token_match"

    fallback = "status_refresh" if "status_refresh" in action_index else next(iter(action_index))
    policy = action_index[fallback]
    return policy.command_class, policy.resolved_action, "fallback_status_refresh"


def determine_execution_mode(policy: ActionPolicy, args: argparse.Namespace) -> str:
    if policy.mutability_level == "read_only":
        return "read_only"
    if args.dry_run:
        return "dry_run"
    if args.allow_mutation:
        return "live_mutation"
    return "dry_run"


def validate_preconditions(policy: ActionPolicy, one_screen: dict[str, Any], mode_payload: dict[str, Any], git_state: dict[str, Any], args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[str]]:
    machine_mode = str(mode_payload.get("machine_mode", "unknown"))
    authority = mode_payload.get("authority", {})
    authority_present = bool(authority.get("authority_present", False))

    authority_failures: list[str] = []
    if policy.allowed_modes and machine_mode not in policy.allowed_modes:
        authority_failures.append(f"machine_mode '{machine_mode}' not allowed for action '{policy.resolved_action}'")
    if policy.creator_authority_required and not authority_present:
        authority_failures.append("creator authority required but not present")

    authority_check = {
        "required_modes": policy.allowed_modes,
        "creator_authority_required": policy.creator_authority_required,
        "machine_mode": machine_mode,
        "authority_present": authority_present,
        "detection_state": authority.get("detection_state", "unknown"),
        "verdict": "PASS" if not authority_failures else "BLOCKED",
        "details": authority_failures or ["authority contract satisfied"],
    }

    missing_policy_files = [p for p in policy.policy_basis if not (REPO_ROOT / p).exists()]
    policy_check = {
        "policy_basis": policy.policy_basis,
        "missing_policy_files": missing_policy_files,
        "verdict": "PASS" if not missing_policy_files else "BLOCKED",
    }

    items: list[dict[str, Any]] = []
    failed: list[str] = []
    repo_root_ok = str(REPO_ROOT).lower() == CANONICAL_LOCAL_ROOT.lower()
    items.append({"name": "repo_root_is_canonical", "ok": repo_root_ok})
    if not repo_root_ok:
        failed.append("repo_root_is_canonical")

    in_sync = str(one_screen.get("sync_verdict", "UNKNOWN")) == "IN_SYNC"
    items.append({"name": "sync_in_sync", "ok": in_sync, "required": policy.requires_in_sync})
    if policy.requires_in_sync and not in_sync:
        failed.append("sync_in_sync")

    clean = bool(git_state.get("worktree_clean", False))
    items.append({"name": "worktree_clean", "ok": clean, "required": policy.requires_clean_worktree})
    if policy.requires_clean_worktree and not clean:
        failed.append("worktree_clean")

    if policy.resolved_action == "handoff_prepare":
        has_task = bool((args.task_id or "").strip())
        has_node = bool((args.node_id or "").strip())
        items.extend([
            {"name": "task_id_provided", "ok": has_task, "required": True},
            {"name": "node_id_provided", "ok": has_node, "required": True},
        ])
        if not has_task:
            failed.append("task_id_provided")
        if not has_node:
            failed.append("node_id_provided")

    if policy.resolved_action in {"install_system", "remove_system"}:
        has_project = bool((args.project_slug or "").strip())
        has_system = bool((args.system_slug or "").strip())
        items.extend([
            {"name": "project_slug_provided", "ok": has_project, "required": True},
            {"name": "system_slug_provided", "ok": has_system, "required": True},
        ])
        if not has_project:
            failed.append("project_slug_provided")
        if not has_system:
            failed.append("system_slug_provided")

    preconditions = {"items": items, "failed": failed, "verdict": "PASS" if not failed else "BLOCKED"}

    blocking = [*authority_failures]
    blocking.extend([f"missing policy file: {p}" for p in missing_policy_files])
    blocking.extend([f"failed precondition: {x}" for x in failed])
    return authority_check, policy_check, preconditions, blocking

def write_command_output(run_id: str, action: str, command: list[str], completed: subprocess.CompletedProcess[str], parsed_json: dict[str, Any] | None) -> str:
    path = OUTPUTS_DIR / run_id / f"{action}_output.json"
    payload = {
        "run_id": run_id,
        "action": action,
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "stdout_json": parsed_json,
        "generated_at": utc_now(),
    }
    write_json(path, payload)
    return normalize_rel(str(path.relative_to(REPO_ROOT)))


def run_command_action(run_id: str, action: str, cmd: list[str]) -> tuple[ActionOutcome, dict[str, Any]]:
    completed = run_cmd(cmd, allow_fail=True)
    parsed = safe_parse_json(completed.stdout)
    output_rel = write_command_output(run_id, action, cmd, completed, parsed)
    verdict = "SUCCESS" if completed.returncode == 0 else "FAILED"
    outcome = ActionOutcome(
        execution_result={"verdict": verdict, "summary": f"command return code {completed.returncode}", "exit_code": completed.returncode},
        artifacts_produced=[output_rel],
        blocking_factors=[] if completed.returncode == 0 else [f"command_return_code={completed.returncode}"],
        notes=[],
    )
    return outcome, parsed or {}


def action_status_refresh(run_id: str) -> ActionOutcome:
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "repo_control_center.py"), "status"]
    outcome, _ = run_command_action(run_id, "status_refresh", cmd)
    outcome.artifacts_produced.extend([
        "runtime/repo_control_center/repo_control_status.json",
        "runtime/repo_control_center/repo_control_report.md",
        "runtime/repo_control_center/one_screen_status.json",
        "runtime/repo_control_center/plain_status.md",
    ])
    return outcome


def action_validation_run(run_id: str) -> ActionOutcome:
    commands = [
        [sys.executable, str(REPO_ROOT / "scripts" / "validate_workspace.py")],
        [sys.executable, str(REPO_ROOT / "scripts" / "check_repo_sync.py"), "--remote", "safe_mirror", "--branch", "main"],
        [sys.executable, str(REPO_ROOT / "scripts" / "repo_control_center.py"), "trust"],
    ]
    artifacts: list[str] = []
    failures: list[str] = []
    for idx, cmd in enumerate(commands, start=1):
        completed = run_cmd(cmd, allow_fail=True)
        rel = write_command_output(run_id, f"validation_step_{idx}", cmd, completed, safe_parse_json(completed.stdout))
        artifacts.append(rel)
        if completed.returncode != 0:
            failures.append(f"validation_step_{idx}_rc={completed.returncode}")
    return ActionOutcome(
        execution_result={"verdict": "SUCCESS" if not failures else "FAILED", "summary": "validation sweep passed" if not failures else "; ".join(failures), "exit_code": 0 if not failures else 1},
        artifacts_produced=artifacts,
        blocking_factors=failures,
        notes=[],
    )


def action_evidence_bundle_context(run_id: str) -> ActionOutcome:
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "export_chatgpt_bundle.py"), "context"]
    completed = run_cmd(cmd, allow_fail=True)
    parsed = safe_parse_json(completed.stdout)
    output_rel = write_command_output(run_id, "evidence_bundle_context", cmd, completed, parsed)
    artifacts = [output_rel]
    blocking: list[str] = []
    summary = "context bundle exported"
    verdict = "SUCCESS"

    if parsed:
        bundle_zip = str(parsed.get("bundle_zip_path", "")).strip()
        safe_share = str(parsed.get("safe_share_verdict", "UNKNOWN"))
        if bundle_zip:
            artifacts.append(bundle_zip)
        if safe_share != "SAFE TO SHARE":
            verdict = "FAILED"
            blocking.append(f"safe_share_verdict={safe_share}")
            summary = f"bundle exported with non-safe verdict: {safe_share}"

    if completed.returncode != 0:
        verdict = "FAILED"
        blocking.append(f"command_return_code={completed.returncode}")

    return ActionOutcome(
        execution_result={"verdict": verdict, "summary": summary, "exit_code": completed.returncode},
        artifacts_produced=artifacts,
        blocking_factors=blocking,
        notes=[],
    )


def action_report_generation(run_id: str) -> ActionOutcome:
    one_screen = load_one_screen()
    repo_control = {}
    path = REPO_ROOT / "runtime" / "repo_control_center" / "repo_control_status.json"
    if path.exists():
        repo_control = load_json(path)

    report_rel = normalize_rel(str((RUNTIME_DIR / f"operator_execution_report_{run_id}.md").relative_to(REPO_ROOT)))
    lines = [
        "# Operator Command Execution Report",
        "",
        f"- run_id: `{run_id}`",
        f"- generated_at: `{utc_now()}`",
        f"- machine_mode: `{one_screen.get('machine_mode', 'unknown')}`",
        f"- authority_present: `{one_screen.get('authority_present', False)}`",
        f"- trust_verdict: `{one_screen.get('trust_verdict', 'UNKNOWN')}`",
        f"- sync_verdict: `{one_screen.get('sync_verdict', 'UNKNOWN')}`",
        f"- governance_verdict: `{one_screen.get('governance_verdict', 'UNKNOWN')}`",
        f"- governance_acceptance_verdict: `{one_screen.get('governance_acceptance_verdict', 'UNKNOWN')}`",
        f"- admission_verdict: `{one_screen.get('admission_verdict', 'UNKNOWN')}`",
        f"- next_canonical_step: `{one_screen.get('next_canonical_step', 'unknown-next-step')}`",
        "",
        "## Repo Control Summary",
    ]
    verdicts = repo_control.get("verdicts", {})
    if verdicts:
        for key in ["trust", "sync", "governance", "governance_acceptance", "admission", "evolution"]:
            lines.append(f"- `{key}`: `{verdicts.get(key, {}).get('verdict', 'UNKNOWN')}`")
    else:
        lines.append("- repo_control_status.json not available")

    write_markdown(REPO_ROOT / report_rel, "\n".join(lines))
    return ActionOutcome(
        execution_result={"verdict": "SUCCESS", "summary": "execution report generated", "exit_code": 0},
        artifacts_produced=[report_rel],
        blocking_factors=[],
        notes=[],
    )


def action_handoff_prepare(run_id: str, args: argparse.Namespace, execution_mode: str) -> ActionOutcome:
    output_dir = args.output_dir.strip() if args.output_dir else ""
    if not output_dir:
        output_dir = str(REPO_ROOT / "integration" / "inbox") if execution_mode == "live_mutation" else str(REPO_ROOT / "runtime" / "operator_command_layer" / "handoff_preview")

    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "prepare_handoff_package.py"),
        "--task-id", args.task_id,
        "--node-id", args.node_id,
        "--mode", "auto",
        "--verdict", "PASS_WITH_WARNINGS",
        "--output-dir", output_dir,
        "--package-id", f"{run_id}_{args.task_id.replace('/', '_')}",
    ]
    for item in args.changed_file:
        cmd.extend(["--changed-file", item])
    for item in args.check:
        cmd.extend(["--check", item])
    for item in args.risk:
        cmd.extend(["--risk", item])
    for item in args.blocker:
        cmd.extend(["--blocker", item])
    for item in args.attachment:
        cmd.extend(["--attachment", item])

    completed = run_cmd(cmd, allow_fail=True)
    parsed = safe_parse_json(completed.stdout)
    output_rel = write_command_output(run_id, "handoff_prepare", cmd, completed, parsed)
    artifacts = [output_rel]
    if parsed:
        package_dir = str(parsed.get("package_dir", "")).strip()
        if package_dir:
            artifacts.append(package_dir)

    verdict = "SUCCESS" if completed.returncode == 0 else "FAILED"
    return ActionOutcome(
        execution_result={"verdict": verdict, "summary": "handoff package prepared" if verdict == "SUCCESS" else f"handoff command failed rc={completed.returncode}", "exit_code": completed.returncode},
        artifacts_produced=artifacts,
        blocking_factors=[] if verdict == "SUCCESS" else [f"command_return_code={completed.returncode}"],
        notes=[f"execution_mode={execution_mode}"] if execution_mode != "live_mutation" else [],
    )


def action_inbox_review(run_id: str, args: argparse.Namespace, execution_mode: str) -> ActionOutcome:
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "review_integration_inbox.py")]
    if args.route and execution_mode == "live_mutation":
        cmd.append("--route")

    completed = run_cmd(cmd, allow_fail=True)
    output_rel = write_command_output(run_id, "inbox_review", cmd, completed, safe_parse_json(completed.stdout))
    notes: list[str] = []
    if args.route and execution_mode != "live_mutation":
        notes.append("route requested but execution mode is dry_run/read_only; route suppressed")

    return ActionOutcome(
        execution_result={"verdict": "SUCCESS" if completed.returncode == 0 else "FAILED", "summary": "integration inbox review completed" if completed.returncode == 0 else f"inbox review failed rc={completed.returncode}", "exit_code": completed.returncode},
        artifacts_produced=[output_rel],
        blocking_factors=[] if completed.returncode == 0 else [f"command_return_code={completed.returncode}"],
        notes=notes,
    )

def action_evidence_routing(run_id: str, execution_mode: str) -> ActionOutcome:
    target_root = (REPO_ROOT / "integration" / "inbox") if execution_mode == "live_mutation" else (REPO_ROOT / "runtime" / "operator_command_layer" / "evidence_routes")
    package_dir = target_root / f"evidence_route_{run_id}"
    evidence_dir = package_dir / "evidence"
    package_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    skipped: list[dict[str, str]] = []
    for rel in OPERATOR_EVIDENCE_ALLOWLIST:
        src = REPO_ROOT / rel
        if not src.exists() or not src.is_file():
            skipped.append({"path": rel, "reason": "source_missing"})
            continue
        dst = evidence_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(rel)

    manifest_path = package_dir / "evidence_routing_manifest.json"
    report_path = package_dir / "EVIDENCE_ROUTING_REPORT.md"
    write_json(manifest_path, {
        "schema_version": "operator_evidence_routing.v1.0.0",
        "run_id": run_id,
        "generated_at": utc_now(),
        "execution_mode": execution_mode,
        "target_root": normalize_rel(str(target_root.relative_to(REPO_ROOT))),
        "copied_files": copied,
        "skipped_files": skipped,
    })

    lines = [
        "# Evidence Routing Report",
        "",
        f"- run_id: `{run_id}`",
        f"- execution_mode: `{execution_mode}`",
        f"- copied_files_count: `{len(copied)}`",
        f"- skipped_files_count: `{len(skipped)}`",
        "",
        "## Copied Files",
    ]
    lines.extend([f"- `{x}`" for x in copied] or ["- none"])
    lines += ["", "## Skipped Files"]
    lines.extend([f"- `{x['path']}` ({x['reason']})" for x in skipped] or ["- none"])
    write_markdown(report_path, "\n".join(lines))

    artifacts = [normalize_rel(str(manifest_path.relative_to(REPO_ROOT))), normalize_rel(str(report_path.relative_to(REPO_ROOT)))]
    if copied:
        return ActionOutcome(
            execution_result={"verdict": "SUCCESS", "summary": "evidence package routed", "exit_code": 0},
            artifacts_produced=artifacts,
            blocking_factors=[],
            notes=[],
        )
    return ActionOutcome(
        execution_result={"verdict": "FAILED", "summary": "no allowlisted evidence files available", "exit_code": 1},
        artifacts_produced=artifacts,
        blocking_factors=["no_evidence_files_available"],
        notes=[],
    )


def action_policy_reference_execute(run_id: str, args: argparse.Namespace, raw_command: str) -> ActionOutcome:
    topic = (args.policy_topic or "").strip() or raw_command
    digest_lines = POLICY_DIGEST_PATH.read_text(encoding="utf-8-sig").splitlines() if POLICY_DIGEST_PATH.exists() else []
    tokens = [tok for tok in topic.lower().replace("_", " ").split() if tok]

    matches: list[str] = []
    for line in digest_lines:
        lowered = line.lower()
        if tokens and all(tok in lowered for tok in tokens[:2]):
            matches.append(line)
        elif tokens and any(tok in lowered for tok in tokens):
            matches.append(line)

    report_path = RUNTIME_DIR / f"policy_reference_{run_id}.md"
    lines = [
        "# Policy Reference Execution",
        "",
        f"- run_id: `{run_id}`",
        f"- topic: `{topic}`",
        f"- generated_at: `{utc_now()}`",
        "",
        "## Matching Digest Lines",
    ]
    lines.extend([f"- {x}" for x in matches[:60]] or ["- no direct digest match; use POLICY_DIGEST.md full scan"])
    write_markdown(report_path, "\n".join(lines))

    return ActionOutcome(
        execution_result={"verdict": "SUCCESS", "summary": "policy reference generated", "exit_code": 0},
        artifacts_produced=[normalize_rel(str(report_path.relative_to(REPO_ROOT)))],
        blocking_factors=[],
        notes=[],
    )


def action_refresh_safe_mirror_evidence(run_id: str, execution_mode: str) -> ActionOutcome:
    if execution_mode != "live_mutation":
        plan_path = RUNTIME_DIR / f"guarded_state_change_plan_{run_id}.md"
        write_markdown(plan_path, "\n".join([
            "# Guarded State Change Plan",
            "",
            f"- run_id: `{run_id}`",
            "- action: `refresh_safe_mirror_evidence`",
            "- execution_mode: `dry_run`",
            "- mutation skipped by guard",
        ]))
        return ActionOutcome(
            execution_result={"verdict": "SUCCESS", "summary": "dry-run plan generated", "exit_code": 0},
            artifacts_produced=[normalize_rel(str(plan_path.relative_to(REPO_ROOT)))],
            blocking_factors=[],
            notes=["live mutation not enabled; no state change executed"],
        )

    artifacts: list[str] = []
    failures: list[str] = []

    cmd1 = [sys.executable, str(REPO_ROOT / "scripts" / "build_safe_mirror_manifest.py"), "--repo-root", CANONICAL_LOCAL_ROOT]
    c1 = run_cmd(cmd1, allow_fail=True)
    artifacts.append(write_command_output(run_id, "refresh_safe_mirror_manifest", cmd1, c1, safe_parse_json(c1.stdout)))
    if c1.returncode != 0:
        failures.append(f"build_safe_mirror_manifest_rc={c1.returncode}")

    cmd2 = [sys.executable, str(REPO_ROOT / "scripts" / "repo_control_center.py"), "mirror"]
    c2 = run_cmd(cmd2, allow_fail=True)
    artifacts.append(write_command_output(run_id, "mirror_recheck", cmd2, c2, safe_parse_json(c2.stdout)))
    if c2.returncode != 0:
        failures.append(f"repo_control_mirror_rc={c2.returncode}")

    artifacts.append("workspace_config/SAFE_MIRROR_MANIFEST.json")
    return ActionOutcome(
        execution_result={"verdict": "SUCCESS" if not failures else "FAILED", "summary": "safe mirror evidence refreshed" if not failures else "; ".join(failures), "exit_code": 0 if not failures else 1},
        artifacts_produced=artifacts,
        blocking_factors=failures,
        notes=[],
    )


def action_creator_acceptance_precheck(run_id: str) -> ActionOutcome:
    commands = [
        [sys.executable, str(REPO_ROOT / "scripts" / "detect_machine_mode.py"), "--intent", "creator", "--strict-intent"],
        [sys.executable, str(REPO_ROOT / "scripts" / "repo_control_center.py"), "full-check"],
    ]
    artifacts: list[str] = []
    failures: list[str] = []
    for idx, cmd in enumerate(commands, start=1):
        c = run_cmd(cmd, allow_fail=True)
        artifacts.append(write_command_output(run_id, f"creator_precheck_step_{idx}", cmd, c, safe_parse_json(c.stdout)))
        if c.returncode != 0:
            failures.append(f"creator_precheck_step_{idx}_rc={c.returncode}")

    artifacts.extend([
        "runtime/repo_control_center/one_screen_status.json",
        "runtime/repo_control_center/repo_control_status.json",
        "runtime/repo_control_center/repo_control_report.md",
    ])
    return ActionOutcome(
        execution_result={"verdict": "SUCCESS" if not failures else "FAILED", "summary": "creator acceptance precheck passed" if not failures else "; ".join(failures), "exit_code": 0 if not failures else 1},
        artifacts_produced=artifacts,
        blocking_factors=failures,
        notes=[],
    )


def action_governance_maintenance_check(run_id: str) -> ActionOutcome:
    workspace_manifest = load_json(REPO_ROOT / "workspace_config" / "workspace_manifest.json")
    required = list(workspace_manifest.get("task_governance", {}).get("governance_brain_stack_paths", []))
    required.extend([
        "docs/governance/OPERATOR_QUERY_LAYER_BASELINE.md",
        "docs/governance/OPERATOR_QUERY_CATALOG.md",
        "docs/governance/OPERATOR_RESPONSE_CONTRACT.md",
        "docs/governance/OPERATOR_INTENT_ROUTING.md",
        "docs/governance/OPERATOR_COMMAND_EXECUTION_BASELINE.md",
        "docs/governance/OPERATOR_COMMAND_CATALOG.md",
        "docs/governance/OPERATOR_COMMAND_EXECUTION_CONTRACT.md",
        "docs/governance/OPERATOR_COMMAND_INTENT_ROUTING.md",
    ])
    required = sorted({normalize_rel(str(x)) for x in required if str(x).strip()})
    missing = [p for p in required if not (REPO_ROOT / p).exists()]

    json_rel = normalize_rel(str((RUNTIME_DIR / f"governance_maintenance_{run_id}.json").relative_to(REPO_ROOT)))
    md_rel = normalize_rel(str((RUNTIME_DIR / f"governance_maintenance_{run_id}.md").relative_to(REPO_ROOT)))
    write_json(REPO_ROOT / json_rel, {
        "schema_version": "governance_maintenance_check.v1.0.0",
        "run_id": run_id,
        "generated_at": utc_now(),
        "required_count": len(required),
        "missing_count": len(missing),
        "missing": missing,
    })
    write_markdown(REPO_ROOT / md_rel, "\n".join([
        "# Governance Maintenance Check",
        "",
        f"- run_id: `{run_id}`",
        f"- generated_at: `{utc_now()}`",
        f"- required_count: `{len(required)}`",
        f"- missing_count: `{len(missing)}`",
        "",
        "## Missing",
        *([f"- `{x}`" for x in missing] or ["- none"]),
    ]))

    return ActionOutcome(
        execution_result={"verdict": "SUCCESS" if not missing else "FAILED", "summary": "governance maintenance check clean" if not missing else "missing governance files detected", "exit_code": 0 if not missing else 1},
        artifacts_produced=[json_rel, md_rel],
        blocking_factors=[f"missing_governance_file={x}" for x in missing],
        notes=[],
    )


def action_install_remove_controlled(run_id: str, action: str, args: argparse.Namespace, execution_mode: str) -> ActionOutcome:
    script_rel = "scripts/install_system.py" if action == "install_system" else "scripts/remove_system.py"
    cmd = [sys.executable, str(REPO_ROOT / script_rel), "--project-slug", args.project_slug, "--system-slug", args.system_slug]
    if execution_mode != "live_mutation":
        cmd.append("--dry-run")

    completed = run_cmd(cmd, allow_fail=True)
    output_rel = write_command_output(run_id, action, cmd, completed, safe_parse_json(completed.stdout))
    notes = ["dry-run enforced for install/remove command"] if execution_mode != "live_mutation" else []

    return ActionOutcome(
        execution_result={"verdict": "SUCCESS" if completed.returncode == 0 else "FAILED", "summary": f"{action} completed" if completed.returncode == 0 else f"{action} failed rc={completed.returncode}", "exit_code": completed.returncode},
        artifacts_produced=[output_rel],
        blocking_factors=[] if completed.returncode == 0 else [f"command_return_code={completed.returncode}"],
        notes=notes,
    )


def execute_action(run_id: str, policy: ActionPolicy, action: str, args: argparse.Namespace, execution_mode: str) -> ActionOutcome:
    if action == "status_refresh":
        return action_status_refresh(run_id)
    if action == "validation_run":
        return action_validation_run(run_id)
    if action == "evidence_bundle_context":
        return action_evidence_bundle_context(run_id)
    if action == "report_generation":
        return action_report_generation(run_id)
    if action == "handoff_prepare":
        return action_handoff_prepare(run_id, args, execution_mode)
    if action == "inbox_review":
        return action_inbox_review(run_id, args, execution_mode)
    if action == "evidence_routing":
        return action_evidence_routing(run_id, execution_mode)
    if action == "policy_reference_execute":
        return action_policy_reference_execute(run_id, args, args.command)
    if action == "refresh_safe_mirror_evidence":
        return action_refresh_safe_mirror_evidence(run_id, execution_mode)
    if action == "creator_acceptance_precheck":
        return action_creator_acceptance_precheck(run_id)
    if action == "governance_maintenance_check":
        return action_governance_maintenance_check(run_id)
    if action in {"install_system", "remove_system"}:
        return action_install_remove_controlled(run_id, action, args, execution_mode)
    return ActionOutcome(
        execution_result={"verdict": "FAILED", "summary": f"unsupported action '{action}'", "exit_code": 1},
        artifacts_produced=[],
        blocking_factors=[f"unsupported_action={action}"],
        notes=[],
    )


def build_state_change(policy: ActionPolicy, execution_mode: str, status_before: set[str], status_after: set[str]) -> dict[str, Any]:
    changed = sorted(status_after.symmetric_difference(status_before))
    return {
        "mutability_level": policy.mutability_level,
        "execution_mode": execution_mode,
        "state_change_detected": bool(changed),
        "changed_files": changed,
        "git_status_before_count": len(status_before),
        "git_status_after_count": len(status_after),
    }


def determine_next_step(execution_result: dict[str, Any], blocking_factors: list[str], action: str) -> str:
    if execution_result.get("verdict") == "SUCCESS" and not blocking_factors:
        return "Run repo_control_center full-check if command changed state."
    if any("creator authority" in item.lower() for item in blocking_factors):
        return "Activate creator authority marker or switch to allowed helper command scope."
    if any("missing policy file" in item.lower() for item in blocking_factors):
        return "Restore missing policy files before execution retry."
    if any("failed precondition" in item.lower() for item in blocking_factors):
        return "Satisfy preconditions and rerun the same command."
    return f"Inspect command output artifacts for action '{action}' and resolve blockers."

def build_contract_payload(
    *,
    run_id: str,
    command_id: str,
    raw_command: str,
    policy: ActionPolicy,
    resolved_action: str,
    route_basis: str,
    authority_check: dict[str, Any],
    policy_check: dict[str, Any],
    preconditions: dict[str, Any],
    execution_result: dict[str, Any],
    artifacts_produced: list[str],
    state_change: dict[str, Any],
    blocking_factors: list[str],
    next_step: str,
    evidence_source: list[str],
    notes: list[str],
    mode_payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "execution_contract_version": EXECUTION_CONTRACT_VERSION,
        "run_id": run_id,
        "generated_at": utc_now(),
        "command_id": command_id,
        "raw_command": raw_command,
        "command_class": policy.command_class,
        "resolved_action": resolved_action,
        "execution_scope": policy.execution_scope,
        "authority_check": authority_check,
        "policy_check": policy_check,
        "preconditions": preconditions,
        "execution_result": execution_result,
        "artifacts_produced": artifacts_produced,
        "state_change": state_change,
        "blocking_factors": blocking_factors,
        "next_step": next_step,
        "evidence_source": evidence_source,
        "escalation_requirement": bool(blocking_factors),
        "execution_mode": state_change.get("execution_mode", "read_only"),
        "dry_run_supported": policy.dry_run_supported,
        "mutability_level": policy.mutability_level,
        "review_requirement": policy.review_requirement,
        "notes": notes,
        "route_basis": route_basis,
        "wave": policy.wave,
        "machine_mode": mode_payload.get("machine_mode", "unknown"),
    }


def summarize_status(last_payload: dict[str, Any]) -> dict[str, Any]:
    log_count = 0
    success_count = 0
    blocked_count = 0
    failed_count = 0
    if LOG_PATH.exists():
        for raw in LOG_PATH.read_text(encoding="utf-8-sig").splitlines():
            if not raw.strip():
                continue
            log_count += 1
            try:
                item = json.loads(raw)
            except Exception:
                continue
            verdict = item.get("execution_result", {}).get("verdict")
            if verdict == "SUCCESS":
                success_count += 1
            elif verdict == "BLOCKED":
                blocked_count += 1
            else:
                failed_count += 1

    return {
        "schema_version": STATUS_SCHEMA_VERSION,
        "generated_at": utc_now(),
        "latest_run_id": last_payload.get("run_id"),
        "latest_command_id": last_payload.get("command_id"),
        "latest_command_class": last_payload.get("command_class"),
        "latest_resolved_action": last_payload.get("resolved_action"),
        "latest_execution_mode": last_payload.get("execution_mode"),
        "latest_execution_verdict": last_payload.get("execution_result", {}).get("verdict"),
        "latest_state_change_detected": last_payload.get("state_change", {}).get("state_change_detected", False),
        "latest_next_step": last_payload.get("next_step"),
        "authority_check_verdict": last_payload.get("authority_check", {}).get("verdict"),
        "policy_check_verdict": last_payload.get("policy_check", {}).get("verdict"),
        "preconditions_verdict": last_payload.get("preconditions", {}).get("verdict"),
        "blocking_factors": last_payload.get("blocking_factors", []),
        "log_stats": {
            "total_runs": log_count,
            "success_runs": success_count,
            "blocked_runs": blocked_count,
            "failed_runs": failed_count,
        },
    }


def status_report_markdown(status: dict[str, Any], last_payload: dict[str, Any]) -> str:
    lines = [
        "# Operator Command Surface Report",
        "",
        f"- generated_at: `{status['generated_at']}`",
        f"- latest_run_id: `{status['latest_run_id']}`",
        f"- latest_command_id: `{status['latest_command_id']}`",
        f"- latest_command_class: `{status['latest_command_class']}`",
        f"- latest_resolved_action: `{status['latest_resolved_action']}`",
        f"- latest_execution_mode: `{status['latest_execution_mode']}`",
        f"- latest_execution_verdict: `{status['latest_execution_verdict']}`",
        f"- authority_check_verdict: `{status['authority_check_verdict']}`",
        f"- policy_check_verdict: `{status['policy_check_verdict']}`",
        f"- preconditions_verdict: `{status['preconditions_verdict']}`",
        "",
        "## Log Stats",
        f"- total_runs: `{status['log_stats']['total_runs']}`",
        f"- success_runs: `{status['log_stats']['success_runs']}`",
        f"- blocked_runs: `{status['log_stats']['blocked_runs']}`",
        f"- failed_runs: `{status['log_stats']['failed_runs']}`",
        "",
        "## Blocking Factors",
    ]
    lines.extend([f"- {x}" for x in status.get("blocking_factors", [])] or ["- none"])
    lines += ["", "## Next Step", f"- {status.get('latest_next_step', 'n/a')}"]
    lines += ["", "## Last Execution Evidence Sources"]
    lines.extend([f"- `{x}`" for x in last_payload.get("evidence_source", [])] or ["- none"])
    return "\n".join(lines) + "\n"


def persist_execution(payload: dict[str, Any]) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    write_json(LAST_EXECUTION_PATH, payload)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    status = summarize_status(payload)
    write_json(STATUS_PATH, status)
    write_markdown(REPORT_PATH, status_report_markdown(status, payload))


def command_registry_snapshot(registry_payload: dict[str, Any]) -> dict[str, Any]:
    classes = []
    for item in registry_payload.get("command_classes", []):
        classes.append(
            {
                "wave": item.get("wave"),
                "command_class": item.get("command_class"),
                "mutability_level": item.get("mutability_level"),
                "allowed_modes": item.get("allowed_modes", []),
                "actions": [a.get("resolved_action") for a in item.get("actions", [])],
            }
        )
    return {
        "schema_version": "operator_command_registry_snapshot.v1.0.0",
        "generated_at": utc_now(),
        "registry_path": normalize_rel(str(REGISTRY_PATH.relative_to(REPO_ROOT))),
        "registry_schema_version": registry_payload.get("schema_version", "unknown"),
        "execution_contract_version": registry_payload.get("execution_contract_version", "unknown"),
        "classes": classes,
    }


def run_golden_consistency(action_index: dict[str, ActionPolicy], golden_path: Path) -> dict[str, Any]:
    payload = load_json(golden_path)
    checked = 0
    matched = 0
    mismatches: list[dict[str, Any]] = []
    for item in payload.get("items", []):
        checked += 1
        raw_command = str(item.get("raw_command", "")).strip()
        expected_class = str(item.get("command_class", "")).strip()
        expected_action = str(item.get("resolved_action", "")).strip()
        got_class, got_action, route_basis = route_command(raw_command, action_index)
        if got_class == expected_class and got_action == expected_action:
            matched += 1
        else:
            mismatches.append(
                {
                    "id": item.get("id"),
                    "raw_command": raw_command,
                    "expected_command_class": expected_class,
                    "expected_resolved_action": expected_action,
                    "got_command_class": got_class,
                    "got_resolved_action": got_action,
                    "route_basis": route_basis,
                }
            )

    result = {
        "schema_version": "operator_command_consistency_check.v1.0.0",
        "generated_at": utc_now(),
        "golden_pack": normalize_rel(str(golden_path.relative_to(REPO_ROOT))),
        "checked": checked,
        "matched": matched,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "consistency_verdict": "PASS" if not mismatches else "FAIL",
    }
    write_json(CONSISTENCY_PATH, result)
    return result


def execute_mode(args: argparse.Namespace) -> int:
    _, action_index = load_registry()
    mode_payload = build_mode_payload(intent="auto")
    one_screen = load_one_screen()
    command_class, resolved_action, route_basis = route_command(
        args.command,
        action_index,
        command_class_override=args.command_class,
        action_override=args.action,
    )
    policy = action_index[resolved_action]
    if command_class != policy.command_class:
        command_class = policy.command_class

    execution_mode = determine_execution_mode(policy, args)
    run_id = f"operator-cmd-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    command_id = args.command_id.strip() or f"{policy.wave}-{resolved_action}-{run_id}"

    status_before = parse_git_status_files()
    git_state = {"head": git_head(), "worktree_clean": len(status_before) == 0}

    authority_check, policy_check, preconditions, early_blocking = validate_preconditions(policy, one_screen, mode_payload, git_state, args)

    execution_mode_note = ""
    if policy.mutability_level != "read_only" and execution_mode == "dry_run":
        execution_mode_note = "mutable action executed in dry_run mode unless --allow-mutation is provided"

    if early_blocking:
        notes = [execution_mode_note] if execution_mode_note else []
        outcome = ActionOutcome(
            execution_result={"verdict": "BLOCKED", "summary": "pre-execution checks failed", "exit_code": 2},
            artifacts_produced=[],
            blocking_factors=early_blocking,
            notes=notes,
        )
    else:
        outcome = execute_action(run_id, policy, resolved_action, args, execution_mode)
        if execution_mode_note:
            outcome.notes.append(execution_mode_note)

    status_after = parse_git_status_files()
    state_change = build_state_change(policy, execution_mode, status_before, status_after)
    blocking_factors = [*outcome.blocking_factors]
    next_step = determine_next_step(outcome.execution_result, blocking_factors, resolved_action)

    payload = build_contract_payload(
        run_id=run_id,
        command_id=command_id,
        raw_command=args.command,
        policy=policy,
        resolved_action=resolved_action,
        route_basis=route_basis,
        authority_check=authority_check,
        policy_check=policy_check,
        preconditions=preconditions,
        execution_result=outcome.execution_result,
        artifacts_produced=sorted(dict.fromkeys(outcome.artifacts_produced)),
        state_change=state_change,
        blocking_factors=sorted(dict.fromkeys(blocking_factors)),
        next_step=next_step,
        evidence_source=[
            "workspace_config/operator_command_registry.json",
            "runtime/repo_control_center/one_screen_status.json",
            "runtime/repo_control_center/repo_control_status.json",
        ],
        notes=outcome.notes,
        mode_payload=mode_payload,
    )
    persist_execution(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["execution_result"]["verdict"] == "SUCCESS" else 1


def classify_mode(args: argparse.Namespace) -> int:
    _, action_index = load_registry()
    command_class, resolved_action, route_basis = route_command(
        args.command,
        action_index,
        command_class_override=args.command_class,
        action_override=args.action,
    )
    print(json.dumps({"command": args.command, "command_class": command_class, "resolved_action": resolved_action, "route_basis": route_basis}, ensure_ascii=False, indent=2))
    return 0


def status_mode() -> int:
    if not STATUS_PATH.exists():
        print(json.dumps({"schema_version": STATUS_SCHEMA_VERSION, "generated_at": utc_now(), "status": "NO_RUNS_YET", "next_step": "Run operator_command_surface.py execute --command 'status refresh'"}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(load_json(STATUS_PATH), ensure_ascii=False, indent=2))
    return 0


def registry_mode() -> int:
    registry_payload, _ = load_registry()
    snapshot = command_registry_snapshot(registry_payload)
    write_json(RUNTIME_DIR / "operator_command_registry_snapshot.json", snapshot)
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return 0


def consistency_mode(args: argparse.Namespace) -> int:
    _, action_index = load_registry()
    golden_path = Path(args.golden_pack)
    if not golden_path.is_absolute():
        golden_path = (REPO_ROOT / golden_path).resolve()
    if not golden_path.exists():
        raise RuntimeError(f"golden pack not found: {golden_path}")
    result = run_golden_consistency(action_index, golden_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["consistency_verdict"] == "PASS" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Operator Command Execution Layer (policy-bound command surface).")
    sub = parser.add_subparsers(dest="mode", required=True)

    execute = sub.add_parser("execute", help="Execute one operator command with contract checks.")
    execute.add_argument("--command", required=True)
    execute.add_argument("--command-id", default="")
    execute.add_argument("--command-class", default="")
    execute.add_argument("--action", default="")
    execute.add_argument("--dry-run", action="store_true")
    execute.add_argument("--allow-mutation", action="store_true")
    execute.add_argument("--task-id", default="")
    execute.add_argument("--node-id", default="")
    execute.add_argument("--project-slug", default="")
    execute.add_argument("--system-slug", default="")
    execute.add_argument("--policy-topic", default="")
    execute.add_argument("--output-dir", default="")
    execute.add_argument("--route", action="store_true")
    execute.add_argument("--changed-file", action="append", default=[])
    execute.add_argument("--check", action="append", default=[])
    execute.add_argument("--risk", action="append", default=[])
    execute.add_argument("--blocker", action="append", default=[])
    execute.add_argument("--attachment", action="append", default=[])

    classify = sub.add_parser("classify", help="Classify command without execution.")
    classify.add_argument("--command", required=True)
    classify.add_argument("--command-class", default="")
    classify.add_argument("--action", default="")

    sub.add_parser("status", help="Print latest command surface status.")
    sub.add_parser("registry", help="Print command registry snapshot.")

    consistency = sub.add_parser("consistency-check", help="Replay golden command pack and verify routing consistency.")
    consistency.add_argument("--golden-pack", default="docs/review_artifacts/OPERATOR_COMMAND_GOLDEN_PACK.json")

    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.mode == "execute":
        return execute_mode(args)
    if args.mode == "classify":
        return classify_mode(args)
    if args.mode == "status":
        return status_mode()
    if args.mode == "registry":
        return registry_mode()
    if args.mode == "consistency-check":
        return consistency_mode(args)
    raise RuntimeError(f"unsupported mode: {args.mode}")


if __name__ == "__main__":
    raise SystemExit(main())
