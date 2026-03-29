#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from detect_machine_mode import build_mode_payload
from operator_surface_common import (
    normalize_rel as common_normalize_rel,
    read_json as common_read_json,
    run_command as common_run_command,
    utc_now_iso as common_utc_now_iso,
    write_json as common_write_json,
    write_markdown as common_write_markdown,
)

CANONICAL_LOCAL_ROOT = r"E:\CVVCODEX"
REPO_ROOT = Path(__file__).resolve().parents[1]

RUNTIME_DIR = REPO_ROOT / "runtime" / "operator_program_layer"
OUTPUTS_DIR = RUNTIME_DIR / "outputs"
LAST_EXECUTION_PATH = RUNTIME_DIR / "last_execution.json"
LOG_PATH = RUNTIME_DIR / "program_execution_log.jsonl"
STATUS_PATH = RUNTIME_DIR / "program_surface_status.json"
REPORT_PATH = RUNTIME_DIR / "program_surface_report.md"
CONSISTENCY_PATH = RUNTIME_DIR / "operator_program_consistency_check.json"
REGISTRY_PATH = REPO_ROOT / "workspace_config" / "operator_program_registry.json"
ONE_SCREEN_PATH = REPO_ROOT / "runtime" / "repo_control_center" / "one_screen_status.json"

EXECUTION_CONTRACT_VERSION = "operator_program_execution_contract.v1.0.0"
STATUS_SCHEMA_VERSION = "operator_program_surface_status.v1.0.0"
PROGRAM_SNAPSHOT_SCHEMA = "operator_program_registry_snapshot.v1.0.0"
CONSISTENCY_SCHEMA = "operator_program_consistency_check.v1.0.0"

ROUTING_PRECEDENCE: tuple[str, ...] = (
    "creator_guarded_program",
    "operational_handoff_review_program",
    "operational_task_routing_program",
    "safe_read_validate_report_program",
)


@dataclass
class ProgramPolicy:
    wave: str
    program_class: str
    program_id: str
    resolved_goal: str
    execution_scope: str
    mutability_level: str
    allowed_modes: list[str]
    creator_authority_required: bool
    requires_in_sync: bool
    requires_clean_worktree: bool
    resume_supported: bool
    rollback_supported: bool
    failure_policy: str
    operator_confirmation_required: bool
    policy_basis: list[str]
    route_tokens: tuple[str, ...]
    required_inputs: list[str]
    stop_conditions: list[str]
    step_plan: list[dict[str, Any]]
    rollback_plan: list[dict[str, Any]]


def utc_now() -> str:
    return common_utc_now_iso()


def normalize_rel(path: str) -> str:
    return common_normalize_rel(path)


def load_json(path: Path) -> dict[str, Any]:
    return common_read_json(path)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    common_write_json(path, payload)


def write_markdown(path: Path, content: str) -> None:
    common_write_markdown(path, content)


def run_cmd(args: list[str], *, allow_fail: bool = False) -> subprocess.CompletedProcess[str]:
    return common_run_command(args, cwd=REPO_ROOT, allow_fail=allow_fail)


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


def load_registry() -> tuple[dict[str, Any], dict[str, ProgramPolicy], dict[str, list[str]]]:
    if not REGISTRY_PATH.exists():
        raise RuntimeError(f"operator program registry missing: {REGISTRY_PATH}")
    payload = load_json(REGISTRY_PATH)
    program_index: dict[str, ProgramPolicy] = {}
    class_to_programs: dict[str, list[str]] = {}

    for cls in payload.get("program_classes", []):
        wave = str(cls.get("wave", "unknown")).strip()
        program_class = str(cls.get("program_class", "")).strip()
        if not program_class:
            continue
        class_to_programs.setdefault(program_class, [])

        base = {
            "wave": wave,
            "program_class": program_class,
            "execution_scope": str(cls.get("execution_scope", program_class)).strip(),
            "mutability_level": str(cls.get("mutability_level", "read_only")).strip(),
            "allowed_modes": [str(x).strip() for x in cls.get("allowed_modes", []) if str(x).strip()],
            "creator_authority_required": bool(cls.get("creator_authority_required", False)),
            "requires_in_sync": bool(cls.get("requires_in_sync", False)),
            "requires_clean_worktree": bool(cls.get("requires_clean_worktree", False)),
            "resume_supported": bool(cls.get("resume_supported", False)),
            "rollback_supported": bool(cls.get("rollback_supported", False)),
            "failure_policy": str(cls.get("failure_policy", "stop_on_failure")).strip(),
            "operator_confirmation_required": bool(cls.get("operator_confirmation_required", False)),
            "policy_basis": [str(x).strip() for x in cls.get("policy_basis", []) if str(x).strip()],
        }

        for program_cfg in cls.get("programs", []):
            program_id = str(program_cfg.get("program_id", "")).strip()
            if not program_id:
                continue
            route_tokens = tuple(
                str(x).lower().strip()
                for x in program_cfg.get("route_tokens", [])
                if str(x).strip()
            )
            policy = ProgramPolicy(
                program_id=program_id,
                resolved_goal=str(program_cfg.get("resolved_goal", "")).strip() or f"Execute {program_id}",
                route_tokens=route_tokens,
                required_inputs=[str(x).strip() for x in program_cfg.get("required_inputs", []) if str(x).strip()],
                stop_conditions=[str(x).strip() for x in program_cfg.get("stop_conditions", []) if str(x).strip()],
                step_plan=program_cfg.get("step_plan", []),
                rollback_plan=program_cfg.get("rollback_plan", []),
                **base,
            )
            program_index[program_id] = policy
            class_to_programs[program_class].append(program_id)

    for program_list in class_to_programs.values():
        program_list.sort()

    if not program_index:
        raise RuntimeError("operator program registry contains no programs")
    return payload, program_index, class_to_programs


def route_program(
    request_text: str,
    program_index: dict[str, ProgramPolicy],
    class_to_programs: dict[str, list[str]],
    *,
    program_id_override: str = "",
    class_override: str = "",
) -> tuple[ProgramPolicy, str]:
    if program_id_override.strip():
        key = program_id_override.strip()
        if key in program_index:
            return program_index[key], "explicit_program_id_override"

    if class_override.strip():
        requested_class = class_override.strip()
        candidates = class_to_programs.get(requested_class, [])
        if candidates:
            return program_index[candidates[0]], "explicit_program_class_override"

    direct = request_text.strip()
    if direct in program_index:
        return program_index[direct], "direct_program_id_match"

    normalized = f" {' '.join(request_text.lower().split())} "
    for class_name in ROUTING_PRECEDENCE:
        for program_id in class_to_programs.get(class_name, []):
            policy = program_index[program_id]
            for token in policy.route_tokens:
                if token and token in normalized:
                    return policy, "token_match"

    fallback = "program.safe_status_validation_report.v1"
    if fallback in program_index:
        return program_index[fallback], "fallback_safe_status_validation"
    first = sorted(program_index.keys())[0]
    return program_index[first], "fallback_first_program"


def determine_execution_mode(policy: ProgramPolicy, args: argparse.Namespace) -> str:
    if policy.mutability_level == "read_only":
        return "read_only"
    if args.allow_mutation:
        return "live_mutation"
    return "dry_run"


def build_program_context(args: argparse.Namespace, policy: ProgramPolicy) -> dict[str, Any]:
    context = {
        "task_id": (args.task_id or "").strip(),
        "node_id": (args.node_id or "").strip(),
        "project_slug": (args.project_slug or "").strip(),
        "system_slug": (args.system_slug or "").strip(),
        "policy_topic": (args.policy_topic or "").strip(),
        "output_dir": (args.output_dir or "").strip(),
        "route": bool(args.route),
        "changed_file": list(args.changed_file or []),
        "check": list(args.check or []),
        "risk": list(args.risk or []),
        "blocker": list(args.blocker or []),
        "attachment": list(args.attachment or []),
        "program_id": policy.program_id,
        "request_text": args.request.strip() if args.request else policy.program_id,
        "request_file": (args.request_file or "").strip(),
    }
    return context


def validate_preconditions(
    policy: ProgramPolicy,
    one_screen: dict[str, Any],
    mode_payload: dict[str, Any],
    git_state: dict[str, Any],
    context: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[str]]:
    machine_mode = str(mode_payload.get("machine_mode", "unknown"))
    authority = mode_payload.get("authority", {})
    authority_present = bool(authority.get("authority_present", False))

    authority_failures: list[str] = []
    creator_alias_allowed = machine_mode == "emperor" and ("creator" in policy.allowed_modes)
    if policy.allowed_modes and machine_mode not in policy.allowed_modes and not creator_alias_allowed:
        authority_failures.append(f"machine_mode '{machine_mode}' not allowed for program '{policy.program_id}'")
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

    for name in policy.required_inputs:
        value = context.get(name)
        has_value = bool(value)
        items.append({"name": f"{name}_provided", "ok": has_value, "required": True})
        if not has_value:
            failed.append(f"{name}_provided")

    total_steps = len(policy.step_plan)
    resume_ok = 1 <= args.resume_from_step <= max(total_steps, 1)
    items.append({"name": "resume_step_in_range", "ok": resume_ok, "required": True})
    if not resume_ok:
        failed.append("resume_step_in_range")

    if args.resume_from_step > 1 and not policy.resume_supported:
        items.append({"name": "resume_supported", "ok": False, "required": True})
        failed.append("resume_supported")
    else:
        items.append({"name": "resume_supported", "ok": True, "required": args.resume_from_step > 1})

    live_mutation = args.allow_mutation and policy.mutability_level != "read_only"
    if live_mutation and policy.operator_confirmation_required and not args.confirm_mutation:
        items.append({"name": "operator_confirmation_required", "ok": False, "required": True})
        failed.append("operator_confirmation_required")
    else:
        items.append(
            {
                "name": "operator_confirmation_required",
                "ok": True,
                "required": bool(live_mutation and policy.operator_confirmation_required),
            }
        )

    if args.attempt_rollback and not policy.rollback_supported:
        items.append({"name": "rollback_supported", "ok": False, "required": True})
        failed.append("rollback_supported")
    else:
        items.append({"name": "rollback_supported", "ok": True, "required": bool(args.attempt_rollback)})

    preconditions = {"items": items, "failed": failed, "verdict": "PASS" if not failed else "BLOCKED"}

    blockers = [*authority_failures]
    blockers.extend([f"missing policy file: {p}" for p in missing_policy_files])
    blockers.extend([f"failed precondition: {item}" for item in failed])
    return authority_check, policy_check, preconditions, blockers


def add_cli_arg(cmd: list[str], key: str, value: Any) -> None:
    if value is None:
        return
    flag = "--" + key.replace("_", "-")
    if isinstance(value, bool):
        if value:
            cmd.append(flag)
        return
    if isinstance(value, list):
        for item in value:
            if str(item).strip():
                cmd.extend([flag, str(item)])
        return
    text = str(value).strip()
    if text:
        cmd.extend([flag, text])


def merge_step_args(step: dict[str, Any], context: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    merged: dict[str, Any] = {}
    missing: list[str] = []

    static_args = step.get("static_args", {})
    if isinstance(static_args, dict):
        for key, value in static_args.items():
            merged[str(key)] = value

    for key in step.get("pass_args", []) or []:
        name = str(key).strip()
        if not name:
            continue
        value = context.get(name)
        if value is None or (isinstance(value, str) and not value.strip()):
            if name not in merged:
                missing.append(name)
        else:
            merged[name] = value

    return merged, missing


def write_step_output(
    run_id: str,
    step_id: str,
    command: list[str],
    completed: subprocess.CompletedProcess[str],
    parsed_json: dict[str, Any] | None,
    *,
    step_type: str,
) -> str:
    output_path = OUTPUTS_DIR / run_id / f"{step_id}_output.json"
    payload = {
        "run_id": run_id,
        "step_id": step_id,
        "step_type": step_type,
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "stdout_json": parsed_json,
        "generated_at": utc_now(),
    }
    write_json(output_path, payload)
    return normalize_rel(str(output_path.relative_to(REPO_ROOT)))

def execute_command_step(
    run_id: str,
    policy: ProgramPolicy,
    step: dict[str, Any],
    context: dict[str, Any],
    execution_mode: str,
) -> tuple[dict[str, Any], list[str], list[str]]:
    step_id = str(step.get("step_id", "STEP")).strip()
    merged_args, missing = merge_step_args(step, context)
    if missing:
        return (
            {
                "step_id": step_id,
                "step_type": "command_execute",
                "execution_result": "BLOCKED",
                "summary": f"missing required step inputs: {', '.join(missing)}",
                "exit_code": 2,
                "blocking_factors": [f"missing_step_input={x}" for x in missing],
                "command": [],
                "output_artifact": "",
                "artifacts_produced": [],
            },
            [],
            [f"step {step_id}: missing step inputs {', '.join(missing)}"],
        )

    command_text = str(step.get("command", "")).strip() or f"program_step_{step_id}"
    resolved_action = str(step.get("action", "")).strip()

    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "operator_command_surface.py"),
        "execute",
        "--command",
        command_text,
        "--command-id",
        f"{policy.program_id}:{step_id}:{run_id}",
    ]
    if resolved_action:
        cmd.extend(["--action", resolved_action])

    allow_mutation_for_step = bool(step.get("allow_mutation", False))
    if execution_mode == "live_mutation" and allow_mutation_for_step:
        cmd.append("--allow-mutation")
    else:
        cmd.append("--dry-run")

    for key, value in merged_args.items():
        add_cli_arg(cmd, key, value)

    completed = run_cmd(cmd, allow_fail=True)
    parsed = safe_parse_json(completed.stdout)
    output_rel = write_step_output(
        run_id,
        step_id,
        cmd,
        completed,
        parsed,
        step_type="command_execute",
    )

    artifacts = [output_rel]
    blocking: list[str] = []
    execution_result = "SUCCESS"
    summary = f"command step return code {completed.returncode}"
    exit_code = completed.returncode

    if parsed and isinstance(parsed, dict):
        result = parsed.get("execution_result", {})
        verdict = str(result.get("verdict", "")).upper()
        if verdict in {"SUCCESS", "FAILED", "BLOCKED"}:
            execution_result = verdict
        if "summary" in result and str(result.get("summary", "")).strip():
            summary = str(result.get("summary", "")).strip()
        if isinstance(result.get("exit_code"), int):
            exit_code = int(result["exit_code"])
        for artifact in parsed.get("artifacts_produced", []) or []:
            text = str(artifact).strip()
            if text:
                artifacts.append(text)
        for item in parsed.get("blocking_factors", []) or []:
            text = str(item).strip()
            if text:
                blocking.append(text)

    if completed.returncode != 0 and execution_result == "SUCCESS":
        execution_result = "FAILED"
    if completed.returncode != 0 and not blocking:
        blocking.append(f"command_return_code={completed.returncode}")

    step_result = {
        "step_id": step_id,
        "step_type": "command_execute",
        "command": cmd,
        "resolved_action": resolved_action or "unknown",
        "execution_result": execution_result,
        "summary": summary,
        "exit_code": exit_code,
        "blocking_factors": blocking,
        "output_artifact": output_rel,
        "artifacts_produced": sorted(dict.fromkeys(artifacts)),
    }
    return step_result, artifacts, [f"step {step_id}: {x}" for x in blocking]


def execute_script_step(
    run_id: str,
    step: dict[str, Any],
    context: dict[str, Any],
) -> tuple[dict[str, Any], list[str], list[str]]:
    step_id = str(step.get("step_id", "STEP")).strip()
    template = step.get("command", [])
    if not isinstance(template, list) or not template:
        return (
            {
                "step_id": step_id,
                "step_type": "script_run",
                "execution_result": "FAILED",
                "summary": "invalid script command template",
                "exit_code": 1,
                "blocking_factors": ["invalid_script_template"],
                "command": [],
                "output_artifact": "",
                "artifacts_produced": [],
            },
            [],
            [f"step {step_id}: invalid script command template"],
        )

    missing_keys: list[str] = []
    command: list[str] = []
    for raw_part in template:
        part = str(raw_part)
        keys = re.findall(r"\{([^{}]+)\}", part)
        for key in keys:
            if not context.get(key):
                missing_keys.append(key)
        for key in keys:
            part = part.replace("{" + key + "}", str(context.get(key, "")))
        command.append(part)

    if missing_keys:
        unique_missing = sorted(dict.fromkeys(missing_keys))
        return (
            {
                "step_id": step_id,
                "step_type": "script_run",
                "execution_result": "BLOCKED",
                "summary": f"missing required script placeholders: {', '.join(unique_missing)}",
                "exit_code": 2,
                "blocking_factors": [f"missing_script_input={x}" for x in unique_missing],
                "command": command,
                "output_artifact": "",
                "artifacts_produced": [],
            },
            [],
            [f"step {step_id}: missing script inputs {', '.join(unique_missing)}"],
        )

    if command and command[0].lower() == "python":
        command[0] = sys.executable

    completed = run_cmd(command, allow_fail=True)
    parsed = safe_parse_json(completed.stdout)
    output_rel = write_step_output(
        run_id,
        step_id,
        command,
        completed,
        parsed,
        step_type="script_run",
    )

    blocking: list[str] = []
    if completed.returncode != 0:
        blocking.append(f"command_return_code={completed.returncode}")

    step_result = {
        "step_id": step_id,
        "step_type": "script_run",
        "command": command,
        "execution_result": "SUCCESS" if completed.returncode == 0 else "FAILED",
        "summary": "script step completed" if completed.returncode == 0 else f"script step failed rc={completed.returncode}",
        "exit_code": completed.returncode,
        "blocking_factors": blocking,
        "output_artifact": output_rel,
        "artifacts_produced": [output_rel],
    }
    return step_result, [output_rel], [f"step {step_id}: {x}" for x in blocking]


def execute_steps(
    run_id: str,
    policy: ProgramPolicy,
    context: dict[str, Any],
    execution_mode: str,
    start_step: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str], list[str], dict[str, Any]]:
    step_results: list[dict[str, Any]] = []
    artifacts: list[str] = []
    blocking: list[str] = []
    completed_steps: list[str] = []
    failed_step = ""
    failed_index = 0
    current_step_id = ""

    for index in range(start_step - 1, len(policy.step_plan)):
        step = policy.step_plan[index]
        step_id = str(step.get("step_id", f"S{index + 1}")).strip()
        current_step_id = step_id
        step_type = str(step.get("step_type", "command_execute")).strip()

        if step_type == "command_execute":
            result, step_artifacts, step_blocking = execute_command_step(run_id, policy, step, context, execution_mode)
        elif step_type == "script_run":
            result, step_artifacts, step_blocking = execute_script_step(run_id, step, context)
        else:
            result = {
                "step_id": step_id,
                "step_type": step_type,
                "execution_result": "FAILED",
                "summary": f"unsupported step_type '{step_type}'",
                "exit_code": 1,
                "blocking_factors": [f"unsupported_step_type={step_type}"],
                "command": [],
                "output_artifact": "",
                "artifacts_produced": [],
            }
            step_artifacts = []
            step_blocking = [f"step {step_id}: unsupported step_type={step_type}"]

        step_results.append(result)
        artifacts.extend(step_artifacts)

        verdict = str(result.get("execution_result", "FAILED")).upper()
        if verdict == "SUCCESS":
            completed_steps.append(step_id)
            continue

        blocking.extend(step_blocking)
        failed_step = step_id
        failed_index = index + 1
        if policy.failure_policy == "stop_on_failure":
            break

    if failed_step:
        if any("BLOCKED" == str(x.get("execution_result", "")).upper() for x in step_results):
            execution_verdict = "BLOCKED"
            summary = f"blocked at step {failed_step}"
            exit_code = 2
        else:
            execution_verdict = "FAILED"
            summary = f"failed at step {failed_step}"
            exit_code = 1
    else:
        execution_verdict = "SUCCESS"
        summary = "program completed successfully"
        exit_code = 0

    total_steps = len(policy.step_plan)
    next_index = failed_index + 1 if failed_step else total_steps + 1
    if next_index < 1:
        next_index = 1

    checkpoint_state = {
        "total_steps": total_steps,
        "start_step": start_step,
        "completed_steps": completed_steps,
        "current_step": current_step_id or "",
        "failed_step": failed_step,
        "resume_pointer": next_index if failed_step else total_steps + 1,
        "resume_supported": policy.resume_supported,
        "can_resume": bool(failed_step and policy.resume_supported and next_index <= total_steps),
        "failure_policy": policy.failure_policy,
    }
    execution_result = {"verdict": execution_verdict, "summary": summary, "exit_code": exit_code}
    return execution_result, step_results, artifacts, blocking, checkpoint_state


def execute_rollback_if_requested(
    run_id: str,
    policy: ProgramPolicy,
    context: dict[str, Any],
    execution_mode: str,
    args: argparse.Namespace,
    *,
    trigger_failed: bool,
) -> tuple[dict[str, Any], list[str], list[str]]:
    if not trigger_failed or not args.attempt_rollback:
        return {"attempted": False, "verdict": "SKIPPED", "steps": []}, [], []
    if not policy.rollback_plan:
        return {"attempted": True, "verdict": "SKIPPED", "reason": "rollback_plan_missing", "steps": []}, [], ["rollback_plan_missing"]

    steps_out: list[dict[str, Any]] = []
    artifacts: list[str] = []
    blocking: list[str] = []
    verdict = "SUCCESS"

    for step in policy.rollback_plan:
        step_id = str(step.get("step_id", "RB")).strip()
        step_type = str(step.get("step_type", "command_execute")).strip()
        if step_type == "command_execute":
            result, step_artifacts, step_blocking = execute_command_step(
                run_id,
                policy,
                step,
                context,
                execution_mode,
            )
        elif step_type == "script_run":
            result, step_artifacts, step_blocking = execute_script_step(run_id, step, context)
        else:
            result = {
                "step_id": step_id,
                "step_type": step_type,
                "execution_result": "FAILED",
                "summary": f"unsupported rollback step_type '{step_type}'",
                "exit_code": 1,
                "blocking_factors": [f"unsupported_rollback_step_type={step_type}"],
                "command": [],
                "output_artifact": "",
                "artifacts_produced": [],
            }
            step_artifacts = []
            step_blocking = [f"rollback step {step_id}: unsupported step_type={step_type}"]

        steps_out.append(result)
        artifacts.extend(step_artifacts)
        if str(result.get("execution_result", "")).upper() != "SUCCESS":
            verdict = "FAILED"
            blocking.extend(step_blocking)
            if policy.failure_policy == "stop_on_failure":
                break

    return {"attempted": True, "verdict": verdict, "steps": steps_out}, artifacts, blocking


def build_state_change(policy: ProgramPolicy, execution_mode: str, status_before: set[str], status_after: set[str]) -> dict[str, Any]:
    changed = sorted(status_after.symmetric_difference(status_before))
    return {
        "mutability_level": policy.mutability_level,
        "execution_mode": execution_mode,
        "state_change_detected": bool(changed),
        "changed_files": changed,
        "git_status_before_count": len(status_before),
        "git_status_after_count": len(status_after),
    }


def determine_next_step(
    execution_result: dict[str, Any],
    blocking_factors: list[str],
    checkpoint_state: dict[str, Any],
    args: argparse.Namespace,
) -> str:
    verdict = str(execution_result.get("verdict", "FAILED")).upper()
    if verdict == "SUCCESS" and not blocking_factors:
        return "Run python scripts/repo_control_center.py full-check and sync if state changed."
    if any("creator authority" in item.lower() for item in blocking_factors):
        return "Enable creator authority marker or use non-creator program scope."
    if any("failed precondition" in item.lower() for item in blocking_factors):
        return "Provide required inputs/flags and rerun the same program."
    if checkpoint_state.get("can_resume"):
        return f"Resume with --resume-from-step {checkpoint_state.get('resume_pointer')}."
    if args.attempt_rollback:
        return "Inspect rollback step outputs and clear blockers before rerun."
    return "Inspect step output artifacts and resolve blockers before retry."


def build_contract_payload(
    *,
    run_id: str,
    command_id: str,
    request_text: str,
    policy: ProgramPolicy,
    route_basis: str,
    authority_check: dict[str, Any],
    policy_check: dict[str, Any],
    preconditions: dict[str, Any],
    step_plan: list[dict[str, Any]],
    step_results: list[dict[str, Any]],
    checkpoint_state: dict[str, Any],
    execution_result: dict[str, Any],
    artifacts_produced: list[str],
    state_change: dict[str, Any],
    blocking_factors: list[str],
    next_step: str,
    evidence_source: list[str],
    mode_payload: dict[str, Any],
    rollback_result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "execution_contract_version": EXECUTION_CONTRACT_VERSION,
        "run_id": run_id,
        "generated_at": utc_now(),
        "command_id": command_id,
        "request_text": request_text,
        "program_class": policy.program_class,
        "task_id_or_program_id": policy.program_id,
        "resolved_goal": policy.resolved_goal,
        "execution_scope": policy.execution_scope,
        "authority_check": authority_check,
        "policy_check": policy_check,
        "preconditions": preconditions,
        "step_plan": step_plan,
        "current_step": checkpoint_state.get("current_step", ""),
        "step_results": step_results,
        "checkpoint_state": checkpoint_state,
        "execution_result": execution_result,
        "artifacts_produced": artifacts_produced,
        "state_change": state_change,
        "blocking_factors": blocking_factors,
        "next_step": next_step,
        "evidence_source": evidence_source,
        "resume_supported": policy.resume_supported,
        "rollback_supported": policy.rollback_supported,
        "escalation_requirement": bool(blocking_factors),
        "mutability_level": policy.mutability_level,
        "failure_policy": policy.failure_policy,
        "stop_conditions": policy.stop_conditions,
        "operator_confirmation_required": policy.operator_confirmation_required,
        "execution_mode": state_change.get("execution_mode", "read_only"),
        "route_basis": route_basis,
        "wave": policy.wave,
        "machine_mode": mode_payload.get("machine_mode", "unknown"),
        "rollback_result": rollback_result,
        "notes": [],
    }

def summarize_status(last_payload: dict[str, Any]) -> dict[str, Any]:
    total = 0
    success = 0
    blocked = 0
    failed = 0

    if LOG_PATH.exists():
        for raw in LOG_PATH.read_text(encoding="utf-8-sig").splitlines():
            text = raw.strip()
            if not text:
                continue
            total += 1
            try:
                item = json.loads(text)
            except Exception:
                continue
            verdict = str(item.get("execution_result", {}).get("verdict", "FAILED")).upper()
            if verdict == "SUCCESS":
                success += 1
            elif verdict == "BLOCKED":
                blocked += 1
            else:
                failed += 1

    return {
        "schema_version": STATUS_SCHEMA_VERSION,
        "generated_at": utc_now(),
        "latest_run_id": last_payload.get("run_id"),
        "latest_program_id": last_payload.get("task_id_or_program_id"),
        "latest_program_class": last_payload.get("program_class"),
        "latest_execution_mode": last_payload.get("execution_mode"),
        "latest_execution_verdict": last_payload.get("execution_result", {}).get("verdict"),
        "latest_current_step": last_payload.get("current_step", ""),
        "latest_state_change_detected": last_payload.get("state_change", {}).get("state_change_detected", False),
        "latest_next_step": last_payload.get("next_step"),
        "authority_check_verdict": last_payload.get("authority_check", {}).get("verdict"),
        "policy_check_verdict": last_payload.get("policy_check", {}).get("verdict"),
        "preconditions_verdict": last_payload.get("preconditions", {}).get("verdict"),
        "blocking_factors": last_payload.get("blocking_factors", []),
        "log_stats": {
            "total_runs": total,
            "success_runs": success,
            "blocked_runs": blocked,
            "failed_runs": failed,
        },
    }


def status_report_markdown(status: dict[str, Any], last_payload: dict[str, Any]) -> str:
    lines = [
        "# Operator Program Surface Report",
        "",
        f"- generated_at: `{status['generated_at']}`",
        f"- latest_run_id: `{status['latest_run_id']}`",
        f"- latest_program_id: `{status['latest_program_id']}`",
        f"- latest_program_class: `{status['latest_program_class']}`",
        f"- latest_execution_mode: `{status['latest_execution_mode']}`",
        f"- latest_execution_verdict: `{status['latest_execution_verdict']}`",
        f"- latest_current_step: `{status['latest_current_step']}`",
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
    lines.extend([f"- {item}" for item in status.get("blocking_factors", [])] or ["- none"])
    lines += ["", "## Next Step", f"- {status.get('latest_next_step', 'n/a')}"]
    lines += ["", "## Last Execution Evidence Sources"]
    lines.extend([f"- `{item}`" for item in last_payload.get("evidence_source", [])] or ["- none"])
    return "\n".join(lines) + "\n"


def persist_execution(payload: dict[str, Any]) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    write_json(LAST_EXECUTION_PATH, payload)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    status = summarize_status(payload)
    write_json(STATUS_PATH, status)
    write_markdown(REPORT_PATH, status_report_markdown(status, payload))


def registry_snapshot(registry_payload: dict[str, Any], class_to_programs: dict[str, list[str]]) -> dict[str, Any]:
    classes: list[dict[str, Any]] = []
    for cls in registry_payload.get("program_classes", []):
        class_name = str(cls.get("program_class", "")).strip()
        classes.append(
            {
                "wave": cls.get("wave"),
                "program_class": class_name,
                "mutability_level": cls.get("mutability_level"),
                "allowed_modes": cls.get("allowed_modes", []),
                "programs": class_to_programs.get(class_name, []),
            }
        )
    return {
        "schema_version": PROGRAM_SNAPSHOT_SCHEMA,
        "generated_at": utc_now(),
        "registry_path": normalize_rel(str(REGISTRY_PATH.relative_to(REPO_ROOT))),
        "registry_schema_version": registry_payload.get("schema_version", "unknown"),
        "execution_contract_version": registry_payload.get("execution_contract_version", "unknown"),
        "classes": classes,
    }


def run_golden_consistency(
    program_index: dict[str, ProgramPolicy],
    class_to_programs: dict[str, list[str]],
    golden_pack: Path,
) -> dict[str, Any]:
    payload = load_json(golden_pack)
    checked = 0
    matched = 0
    mismatches: list[dict[str, Any]] = []

    for item in payload.get("items", []):
        checked += 1
        raw = str(item.get("raw_request", "")).strip()
        expected_class = str(item.get("program_class", "")).strip()
        expected_id = str(item.get("program_id", "")).strip()
        got_policy, route_basis = route_program(raw, program_index, class_to_programs)
        if got_policy.program_class == expected_class and got_policy.program_id == expected_id:
            matched += 1
        else:
            mismatches.append(
                {
                    "id": item.get("id"),
                    "raw_request": raw,
                    "expected_program_class": expected_class,
                    "expected_program_id": expected_id,
                    "got_program_class": got_policy.program_class,
                    "got_program_id": got_policy.program_id,
                    "route_basis": route_basis,
                }
            )

    result = {
        "schema_version": CONSISTENCY_SCHEMA,
        "generated_at": utc_now(),
        "golden_pack": normalize_rel(str(golden_pack.relative_to(REPO_ROOT))),
        "checked": checked,
        "matched": matched,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "consistency_verdict": "PASS" if not mismatches else "FAIL",
    }
    write_json(CONSISTENCY_PATH, result)
    return result


def execute_mode(args: argparse.Namespace) -> int:
    _, program_index, class_to_programs = load_registry()
    mode_payload = build_mode_payload(intent="auto")
    one_screen = load_one_screen()

    request_text = (args.request or "").strip()
    if not request_text and args.program_id:
        request_text = args.program_id.strip()
    if not request_text and args.program_class:
        request_text = args.program_class.strip()
    if not request_text:
        request_text = "safe status validation report"

    policy, route_basis = route_program(
        request_text,
        program_index,
        class_to_programs,
        program_id_override=args.program_id,
        class_override=args.program_class,
    )

    execution_mode = determine_execution_mode(policy, args)
    run_id = f"operator-program-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    command_id = (args.command_id or "").strip() or f"{policy.wave}-{policy.program_id}-{run_id}"
    context = build_program_context(args, policy)

    status_before = parse_git_status_files()
    git_state = {"head": git_head(), "worktree_clean": len(status_before) == 0}

    authority_check, policy_check, preconditions, early_blocking = validate_preconditions(
        policy,
        one_screen,
        mode_payload,
        git_state,
        context,
        args,
    )

    if early_blocking:
        step_results: list[dict[str, Any]] = []
        artifacts: list[str] = []
        blocking_factors = early_blocking
        checkpoint_state = {
            "total_steps": len(policy.step_plan),
            "start_step": args.resume_from_step,
            "completed_steps": [],
            "current_step": "",
            "failed_step": "",
            "resume_pointer": args.resume_from_step,
            "resume_supported": policy.resume_supported,
            "can_resume": False,
            "failure_policy": policy.failure_policy,
        }
        execution_result = {"verdict": "BLOCKED", "summary": "pre-execution checks failed", "exit_code": 2}
        rollback_result = {"attempted": False, "verdict": "SKIPPED", "steps": []}
    else:
        execution_result, step_results, artifacts, step_blocking, checkpoint_state = execute_steps(
            run_id,
            policy,
            context,
            execution_mode,
            args.resume_from_step,
        )
        rollback_result, rollback_artifacts, rollback_blocking = execute_rollback_if_requested(
            run_id,
            policy,
            context,
            execution_mode,
            args,
            trigger_failed=execution_result["verdict"] in {"FAILED", "BLOCKED"},
        )
        artifacts.extend(rollback_artifacts)
        blocking_factors = [*step_blocking, *rollback_blocking]

    status_after = parse_git_status_files()
    state_change = build_state_change(policy, execution_mode, status_before, status_after)
    next_step = determine_next_step(execution_result, blocking_factors, checkpoint_state, args)

    payload = build_contract_payload(
        run_id=run_id,
        command_id=command_id,
        request_text=request_text,
        policy=policy,
        route_basis=route_basis,
        authority_check=authority_check,
        policy_check=policy_check,
        preconditions=preconditions,
        step_plan=policy.step_plan,
        step_results=step_results,
        checkpoint_state=checkpoint_state,
        execution_result=execution_result,
        artifacts_produced=sorted(dict.fromkeys(artifacts)),
        state_change=state_change,
        blocking_factors=sorted(dict.fromkeys(blocking_factors)),
        next_step=next_step,
        evidence_source=[
            "workspace_config/operator_program_registry.json",
            "workspace_config/operator_command_registry.json",
            "runtime/repo_control_center/one_screen_status.json",
            "runtime/repo_control_center/repo_control_status.json",
            "runtime/operator_command_layer/command_surface_status.json",
        ],
        mode_payload=mode_payload,
        rollback_result=rollback_result,
    )

    persist_execution(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["execution_result"]["verdict"] == "SUCCESS" else 1


def classify_mode(args: argparse.Namespace) -> int:
    _, program_index, class_to_programs = load_registry()
    request_text = (args.request or "").strip() or args.program_id.strip() or args.program_class.strip() or "safe status validation report"
    policy, route_basis = route_program(
        request_text,
        program_index,
        class_to_programs,
        program_id_override=args.program_id,
        class_override=args.program_class,
    )
    payload = {
        "request_text": request_text,
        "program_class": policy.program_class,
        "program_id": policy.program_id,
        "route_basis": route_basis,
        "resolved_goal": policy.resolved_goal,
        "wave": policy.wave,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def status_mode() -> int:
    if not STATUS_PATH.exists():
        print(
            json.dumps(
                {
                    "schema_version": STATUS_SCHEMA_VERSION,
                    "generated_at": utc_now(),
                    "status": "NO_RUNS_YET",
                    "next_step": "Run operator_program_surface.py execute --request 'safe status validation report'",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1
    print(json.dumps(load_json(STATUS_PATH), ensure_ascii=False, indent=2))
    return 0


def registry_mode() -> int:
    registry_payload, _, class_to_programs = load_registry()
    snapshot = registry_snapshot(registry_payload, class_to_programs)
    write_json(RUNTIME_DIR / "operator_program_registry_snapshot.json", snapshot)
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    return 0


def consistency_mode(args: argparse.Namespace) -> int:
    _, program_index, class_to_programs = load_registry()
    golden_path = Path(args.golden_pack)
    if not golden_path.is_absolute():
        golden_path = (REPO_ROOT / golden_path).resolve()
    if not golden_path.exists():
        raise RuntimeError(f"golden pack not found: {golden_path}")
    result = run_golden_consistency(program_index, class_to_programs, golden_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["consistency_verdict"] == "PASS" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Operator Task/Program Layer (policy-bound, checkpointed execution).")
    sub = parser.add_subparsers(dest="mode", required=True)

    execute = sub.add_parser("execute", help="Execute one operator program with authority/policy/precondition checks.")
    execute.add_argument("--request", default="")
    execute.add_argument("--command-id", default="")
    execute.add_argument("--program-id", default="")
    execute.add_argument("--program-class", default="")
    execute.add_argument("--allow-mutation", action="store_true")
    execute.add_argument("--confirm-mutation", action="store_true")
    execute.add_argument("--resume-from-step", type=int, default=1)
    execute.add_argument("--attempt-rollback", action="store_true")
    execute.add_argument("--task-id", default="")
    execute.add_argument("--node-id", default="")
    execute.add_argument("--project-slug", default="")
    execute.add_argument("--system-slug", default="")
    execute.add_argument("--policy-topic", default="")
    execute.add_argument("--output-dir", default="")
    execute.add_argument("--request-file", default="")
    execute.add_argument("--route", action="store_true")
    execute.add_argument("--changed-file", action="append", default=[])
    execute.add_argument("--check", action="append", default=[])
    execute.add_argument("--risk", action="append", default=[])
    execute.add_argument("--blocker", action="append", default=[])
    execute.add_argument("--attachment", action="append", default=[])

    classify = sub.add_parser("classify", help="Classify operator program request without execution.")
    classify.add_argument("--request", default="")
    classify.add_argument("--program-id", default="")
    classify.add_argument("--program-class", default="")

    sub.add_parser("status", help="Print latest program surface status.")
    sub.add_parser("registry", help="Print program registry snapshot.")

    consistency = sub.add_parser("consistency-check", help="Replay golden program pack and validate routing consistency.")
    consistency.add_argument("--golden-pack", default="docs/review_artifacts/OPERATOR_PROGRAM_GOLDEN_PACK.json")

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
