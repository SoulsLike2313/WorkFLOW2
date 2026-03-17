#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from detect_machine_mode import build_mode_payload

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ROOT = r"E:\CVVCODEX"
REGISTRY_PATH = ROOT / "workspace_config" / "operator_task_program_registry.json"
GOLDEN_2B = ROOT / "docs" / "review_artifacts" / "OPERATOR_TASK_PROGRAM_GOLDEN_PACK_WAVE_2B.json"
RUNTIME_DIR = ROOT / "runtime" / "repo_control_center"
OUTPUTS_DIR = RUNTIME_DIR / "operator_program_outputs"
STATUS_PATH = RUNTIME_DIR / "operator_program_status.json"
REPORT_PATH = RUNTIME_DIR / "operator_program_report.md"
CHECKPOINT_PATH = RUNTIME_DIR / "operator_program_checkpoint.json"
HISTORY_PATH = RUNTIME_DIR / "operator_program_history.json"
CONSISTENCY_PATH = RUNTIME_DIR / "operator_task_program_consistency.json"
LOG_PATH = RUNTIME_DIR / "operator_program_log.jsonl"
ONE_SCREEN_PATH = RUNTIME_DIR / "one_screen_status.json"
COMMAND_SCRIPT = ROOT / "scripts" / "operator_command_surface.py"

EXEC_SCHEMA = "operator_task_program_contract.wave2b.v1.0.0"
STATUS_SCHEMA = "operator_task_program_status.wave2b.v1.0.0"
HISTORY_SCHEMA = "operator_task_program_history.wave2b.v1.0.0"
CONSISTENCY_SCHEMA = "operator_task_program_consistency.wave2b.v1.0.0"
DEFAULT_ORDER = (
    "certification_program",
    "evidence_delivery_program",
    "inbox_review_program",
    "handoff_preparation_program",
    "validation_program",
    "evidence_pack_program",
    "report_program",
    "status_refresh_program",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_rel(path: str) -> str:
    value = path.replace("\\", "/").strip()
    while value.startswith("./"):
        value = value[2:]
    return value.strip("/")


def rel(path: Path) -> str:
    return normalize_rel(str(path.relative_to(ROOT)))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def run(cmd: list[str], allow_fail: bool = False) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    if cp.returncode != 0 and not allow_fail:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip() or f"failed: {' '.join(cmd)}")
    return cp


def parse_json(raw: str) -> dict[str, Any] | None:
    text = raw.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except Exception:
        return None
    return parsed if isinstance(parsed, dict) else {"value": parsed}


def git_state() -> dict[str, Any]:
    out = run(["git", "status", "--porcelain"], allow_fail=True).stdout
    files = sorted({normalize_rel(line[3:].strip()) for line in out.splitlines() if len(line) >= 4})
    return {
        "head": run(["git", "rev-parse", "HEAD"], allow_fail=True).stdout.strip(),
        "worktree_clean": len(files) == 0,
        "status_files": files,
    }


def load_registry() -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, list[str]], tuple[str, ...]]:
    payload = read_json(REGISTRY_PATH)
    index: dict[str, dict[str, Any]] = {}
    class_map: dict[str, list[str]] = {}

    for cls in payload.get("program_classes", []):
        program_class = str(cls.get("program_class", "")).strip()
        if not program_class:
            continue
        class_map.setdefault(program_class, [])

        defaults = {
            "allowed_modes": cls.get("allowed_modes", []),
            "authority_requirement": cls.get("authority_requirement", "none"),
            "policy_basis": cls.get("policy_basis", []),
            "mutability_level": cls.get("mutability_level", "READ_ONLY"),
            "resume_supported": bool(cls.get("resume_supported", True)),
            "failure_policy": cls.get("failure_policy_default", "stop_on_failure"),
            "requires_in_sync": bool(cls.get("requires_in_sync", False)),
            "requires_clean_worktree": bool(cls.get("requires_clean_worktree", False)),
            "blocking_conditions": cls.get("blocking_conditions", []),
            "command_dependencies": cls.get("command_dependencies", []),
            "review_dependencies": cls.get("review_dependencies", []),
            "delivery_artifacts": cls.get("delivery_artifacts", []),
            "evidence_outputs": cls.get("evidence_outputs", []),
            "review_requirement": cls.get("review_requirement", "none"),
            "escalation_requirement": bool(cls.get("escalation_requirement", False)),
            "stop_conditions": cls.get("stop_conditions", []),
            "delivery_target": cls.get("delivery_target", "none"),
            "required_inputs": cls.get("required_inputs", []),
            "step_sequences": cls.get("step_sequences", []),
        }

        for program in cls.get("programs", []):
            program_id = str(program.get("program_id", "")).strip()
            if not program_id:
                continue
            merged = {
                "program_id": program_id,
                "program_class": program_class,
                "resolved_goal": program.get("resolved_goal", f"Execute {program_id}"),
                "execution_scope": program.get("execution_scope", program_class),
                "route_tokens": [str(x).lower().strip() for x in program.get("route_tokens", []) if str(x).strip()],
                "step_plan": program.get("step_plan", []),
                "step_sequences": program.get("step_sequences", defaults["step_sequences"]),
            }
            for key, value in defaults.items():
                merged[key] = program.get(key, value)

            index[program_id] = merged
            class_map[program_class].append(program_id)

    for program_class in class_map:
        class_map[program_class] = sorted(class_map[program_class])
    if not index:
        raise RuntimeError("empty operator_task_program_registry")

    configured_order = tuple(
        str(x).strip() for x in payload.get("routing_precedence", {}).get("class_order", []) if str(x).strip()
    )
    order = configured_order or DEFAULT_ORDER
    return payload, index, class_map, order


def route(
    request: str,
    index: dict[str, dict[str, Any]],
    class_map: dict[str, list[str]],
    class_order: tuple[str, ...],
    program_id_override: str,
    program_class_override: str,
) -> tuple[str, dict[str, Any], str]:
    if program_id_override.strip():
        key = program_id_override.strip()
        if key not in index:
            raise RuntimeError(f"unknown program-id: {key}")
        return key, index[key], "explicit_program_id_override"
    if program_class_override.strip():
        program_class = program_class_override.strip()
        if program_class not in class_map or not class_map[program_class]:
            raise RuntimeError(f"unknown program-class: {program_class}")
        key = class_map[program_class][0]
        return key, index[key], "explicit_program_class_override"
    if request.strip() in index:
        key = request.strip()
        return key, index[key], "direct_program_id_match"

    normalized_request = f" {' '.join(request.lower().split())} "
    for program_class in class_order:
        for program_id in class_map.get(program_class, []):
            for token in index[program_id].get("route_tokens", []):
                if token and token in normalized_request:
                    return program_id, index[program_id], "token_match"

    fallback = "program.wave2a.status_refresh_surface.v1"
    key = fallback if fallback in index else sorted(index.keys())[0]
    return key, index[key], "fallback_status_refresh"

def add_arg(cmd: list[str], key: str, value: Any) -> None:
    if value is None:
        return
    flag = "--" + str(key).replace("_", "-")
    if isinstance(value, bool):
        if value:
            cmd.append(flag)
        return
    if isinstance(value, list):
        for item in value:
            text = str(item).strip()
            if text:
                cmd.extend([flag, text])
        return
    text = str(value).strip()
    if text:
        cmd.extend([flag, text])


def merge_step_args(step: dict[str, Any], context: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    merged = {str(key): value for key, value in (step.get("static_args", {}) or {}).items()}
    missing: list[str] = []
    for arg_name in step.get("pass_args", []) or []:
        key = str(arg_name).strip()
        if not key:
            continue
        value = context.get(key)
        if (value is None or (isinstance(value, str) and not value.strip())) and key not in merged:
            missing.append(key)
        elif value is not None and not (isinstance(value, str) and not value.strip()):
            merged[key] = value
    return merged, missing


def execute_step(
    run_id: str,
    program_id: str,
    step: dict[str, Any],
    context: dict[str, Any],
    allow_mutation: bool,
) -> tuple[dict[str, Any], list[str], list[str]]:
    step_id = str(step.get("step_id", "STEP")).strip()
    merged_args, missing_args = merge_step_args(step, context)

    if missing_args:
        blockers = [f"missing_step_input={x}" for x in missing_args]
        return {
            "step_id": step_id,
            "step_type": "command_execute",
            "execution_result": "BLOCKED",
            "summary": f"missing step inputs: {', '.join(missing_args)}",
            "exit_code": 2,
            "blocking_factors": blockers,
            "command": [],
            "resolved_action": str(step.get("action", "")),
            "output_artifact": "",
            "artifacts_produced": [],
        }, [], [f"step {step_id}: {x}" for x in blockers]

    action = str(step.get("action", "")).strip()
    if not action:
        return {
            "step_id": step_id,
            "step_type": "command_execute",
            "execution_result": "FAILED",
            "summary": "missing step action",
            "exit_code": 1,
            "blocking_factors": ["missing_step_action"],
            "command": [],
            "resolved_action": "unknown",
            "output_artifact": "",
            "artifacts_produced": [],
        }, [], [f"step {step_id}: missing_step_action"]

    command = [
        sys.executable,
        str(COMMAND_SCRIPT),
        "execute",
        "--command",
        str(step.get("command", action)),
        "--action",
        action,
        "--command-id",
        f"{program_id}:{step_id}:{run_id}",
    ]
    command.append("--allow-mutation" if allow_mutation else "--dry-run")
    for key, value in merged_args.items():
        add_arg(command, key, value)

    completed = run(command, allow_fail=True)
    parsed_stdout = parse_json(completed.stdout)
    output_path = OUTPUTS_DIR / run_id / f"{step_id}_output.json"
    write_json(
        output_path,
        {
            "run_id": run_id,
            "step_id": step_id,
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "stdout_json": parsed_stdout,
            "generated_at": utc_now(),
        },
    )

    artifacts = [rel(output_path)]
    blockers: list[str] = []
    verdict = "SUCCESS"
    summary = f"command step return code {completed.returncode}"
    exit_code = completed.returncode

    if parsed_stdout:
        result_payload = parsed_stdout.get("execution_result", {})
        candidate_verdict = str(result_payload.get("verdict", "")).upper()
        if candidate_verdict in {"SUCCESS", "FAILED", "BLOCKED"}:
            verdict = candidate_verdict
        if str(result_payload.get("summary", "")).strip():
            summary = str(result_payload.get("summary", "")).strip()
        if isinstance(result_payload.get("exit_code"), int):
            exit_code = int(result_payload["exit_code"])
        artifacts.extend([str(x).strip() for x in parsed_stdout.get("artifacts_produced", []) or [] if str(x).strip()])
        blockers.extend([str(x).strip() for x in parsed_stdout.get("blocking_factors", []) or [] if str(x).strip()])

    if completed.returncode != 0 and verdict == "SUCCESS":
        verdict = "FAILED"
    if completed.returncode != 0 and not blockers:
        blockers.append(f"command_return_code={completed.returncode}")

    result = {
        "step_id": step_id,
        "step_type": "command_execute",
        "execution_result": verdict,
        "summary": summary,
        "exit_code": exit_code,
        "command": command,
        "resolved_action": action,
        "output_artifact": rel(output_path),
        "artifacts_produced": sorted(set(artifacts)),
        "blocking_factors": blockers,
    }
    return result, sorted(set(artifacts)), [f"step {step_id}: {x}" for x in blockers]


def should_stop(verdict: str, stop_conditions: list[str], failure_policy: str) -> tuple[bool, str]:
    verdict_upper = verdict.upper()
    conditions = {str(x).strip() for x in stop_conditions if str(x).strip()}
    if verdict_upper == "BLOCKED" and "any_step_blocked" in conditions:
        return True, "any_step_blocked"
    if verdict_upper == "FAILED" and "any_step_failed" in conditions:
        return True, "any_step_failed"
    if failure_policy == "stop_on_failure" and verdict_upper in {"FAILED", "BLOCKED"}:
        return True, "failure_policy_stop_on_failure"
    if failure_policy == "stop_on_blocked" and verdict_upper == "BLOCKED":
        return True, "failure_policy_stop_on_blocked"
    return False, ""


def gate(
    policy: dict[str, Any],
    mode_payload: dict[str, Any],
    one_screen: dict[str, Any],
    git_before: dict[str, Any],
    context: dict[str, Any],
    resume_from_step: int,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[str]]:
    machine_mode = str(mode_payload.get("machine_mode", "unknown"))
    authority = mode_payload.get("authority", {})
    authority_present = bool(authority.get("authority_present", False))

    authority_blockers: list[str] = []
    if policy.get("allowed_modes") and machine_mode not in policy["allowed_modes"]:
        authority_blockers.append(f"machine_mode '{machine_mode}' not allowed for '{policy['program_id']}'")
    if str(policy.get("authority_requirement", "none")) == "creator_required" and not authority_present:
        authority_blockers.append("creator authority required but not present")

    missing_policy_files = [p for p in policy.get("policy_basis", []) if not (ROOT / str(p)).exists()]

    precondition_failures: list[str] = []
    if str(ROOT).lower() != CANONICAL_ROOT.lower():
        precondition_failures.append("repo_root_is_canonical")
    if bool(policy.get("requires_in_sync", False)) and str(one_screen.get("sync_verdict", "UNKNOWN")) != "IN_SYNC":
        precondition_failures.append("sync_in_sync")
    if bool(policy.get("requires_clean_worktree", False)) and not git_before.get("worktree_clean", False):
        precondition_failures.append("worktree_clean")

    total_steps = max(len(policy.get("step_plan", [])), 1)
    if resume_from_step < 1 or resume_from_step > total_steps:
        precondition_failures.append("resume_step_in_range")
    if resume_from_step > 1 and not bool(policy.get("resume_supported", True)):
        precondition_failures.append("resume_supported")

    for required in policy.get("required_inputs", []) or []:
        key = str(required).strip()
        value = context.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            precondition_failures.append(f"{key}_provided")

    authority_check = {
        "required_modes": policy.get("allowed_modes", []),
        "authority_requirement": policy.get("authority_requirement", "none"),
        "machine_mode": machine_mode,
        "authority_present": authority_present,
        "detection_state": authority.get("detection_state", "unknown"),
        "verdict": "PASS" if not authority_blockers else "BLOCKED",
        "details": authority_blockers or ["authority contract satisfied"],
    }
    policy_check = {
        "policy_basis": policy.get("policy_basis", []),
        "missing_policy_files": missing_policy_files,
        "verdict": "PASS" if not missing_policy_files else "BLOCKED",
    }
    preconditions = {
        "failed": precondition_failures,
        "verdict": "PASS" if not precondition_failures else "BLOCKED",
    }
    blockers = authority_blockers + [f"missing policy file: {x}" for x in missing_policy_files] + [f"failed precondition: {x}" for x in precondition_failures]
    return authority_check, policy_check, preconditions, blockers

def write_runtime(payload: dict[str, Any]) -> None:
    status_payload = {
        "schema_version": STATUS_SCHEMA,
        "generated_at": payload.get("generated_at", utc_now()),
        "active_or_last_program": payload.get("task_id_or_program_id", ""),
        "program_class": payload.get("program_class", ""),
        "execution_result": payload.get("execution_result", {}),
        "current_step": payload.get("current_step", ""),
        "checkpoint_state": payload.get("checkpoint_state", {}),
        "completed_steps": payload.get("checkpoint_state", {}).get("completed_steps", []),
        "pending_steps": payload.get("checkpoint_state", {}).get("pending_steps", []),
        "review_requirement": payload.get("review_requirement", "none"),
        "delivery_target": payload.get("delivery_target", "none"),
        "artifacts_produced": payload.get("artifacts_produced", []),
        "blocking_factors": payload.get("blocking_factors", []),
        "next_step": payload.get("next_step", ""),
    }
    write_json(STATUS_PATH, status_payload)
    write_json(CHECKPOINT_PATH, payload.get("checkpoint_state", {}))

    history_payload: dict[str, Any]
    if HISTORY_PATH.exists():
        try:
            history_payload = read_json(HISTORY_PATH)
        except Exception:
            history_payload = {"schema_version": HISTORY_SCHEMA, "entries": []}
    else:
        history_payload = {"schema_version": HISTORY_SCHEMA, "entries": []}
    entries = history_payload.get("entries", [])
    if not isinstance(entries, list):
        entries = []
    entries.append(
        {
            "run_id": payload.get("run_id", ""),
            "generated_at": payload.get("generated_at", utc_now()),
            "program_id": payload.get("task_id_or_program_id", ""),
            "program_class": payload.get("program_class", ""),
            "execution_result": payload.get("execution_result", {}).get("verdict", ""),
            "current_step": payload.get("current_step", ""),
            "resume_pointer": payload.get("checkpoint_state", {}).get("resume_pointer", 1),
            "can_resume": payload.get("checkpoint_state", {}).get("can_resume", False),
            "stop_condition_triggered": payload.get("checkpoint_state", {}).get("stop_condition_triggered", False),
            "stop_condition_reason": payload.get("checkpoint_state", {}).get("stop_condition_reason", ""),
            "blocking_factors": payload.get("blocking_factors", []),
        }
    )
    write_json(HISTORY_PATH, {"schema_version": HISTORY_SCHEMA, "generated_at": payload.get("generated_at", utc_now()), "entries": entries[-200:]})

    lines = [
        "# OPERATOR PROGRAM REPORT",
        "",
        "## Runtime Identity",
        f"- run_id: `{payload.get('run_id', '')}`",
        f"- program: `{payload.get('task_id_or_program_id', '')}`",
        f"- class: `{payload.get('program_class', '')}`",
        f"- route_basis: `{payload.get('route_basis', '')}`",
        "",
        "## Program Contract",
        f"- failure_policy: `{payload.get('failure_policy', '')}`",
        f"- resume_supported: `{payload.get('resume_supported', False)}`",
        f"- stop_conditions: `{', '.join(payload.get('stop_conditions', [])) or 'none'}`",
        f"- delivery_target: `{payload.get('delivery_target', 'none')}`",
        f"- review_requirement: `{payload.get('review_requirement', 'none')}`",
        f"- escalation_requirement: `{payload.get('escalation_requirement', False)}`",
        "",
        "## Result",
        f"- verdict: `{payload.get('execution_result', {}).get('verdict', '')}`",
        f"- summary: `{payload.get('execution_result', {}).get('summary', '')}`",
        "",
        "## Checkpoint",
        f"- current_step: `{payload.get('current_step', '')}`",
        f"- completed_steps: `{len(payload.get('checkpoint_state', {}).get('completed_steps', []))}`",
        f"- pending_steps: `{len(payload.get('checkpoint_state', {}).get('pending_steps', []))}`",
        f"- failed_step: `{payload.get('checkpoint_state', {}).get('failed_step', '')}`",
        f"- resume_pointer: `{payload.get('checkpoint_state', {}).get('resume_pointer', 1)}`",
        f"- can_resume: `{payload.get('checkpoint_state', {}).get('can_resume', False)}`",
        f"- stop_condition_triggered: `{payload.get('checkpoint_state', {}).get('stop_condition_triggered', False)}`",
        f"- stop_condition_reason: `{payload.get('checkpoint_state', {}).get('stop_condition_reason', '')}`",
        "",
        "## Blocking Factors",
    ]
    lines.extend([f"- `{x}`" for x in payload.get("blocking_factors", [])] or ["- none"])
    lines.extend(["", "## Artifacts Produced"])
    lines.extend([f"- `{x}`" for x in payload.get("artifacts_produced", [])] or ["- none"])
    lines.extend(["", "## Next Step", f"- {payload.get('next_step', '')}"])
    write_md(REPORT_PATH, "\n".join(lines))
    append_jsonl(LOG_PATH, payload)


def execute_mode(args: argparse.Namespace) -> int:
    registry_payload, index, class_map, class_order = load_registry()
    run_id = f"program-wave2b-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    mode_payload = build_mode_payload(intent=args.intent)
    one_screen = read_json(ONE_SCREEN_PATH) if ONE_SCREEN_PATH.exists() else {}
    git_before = git_state()

    context = {
        "request_text": args.request or "",
        "task_id": args.task_id or "",
        "node_id": args.node_id or "",
        "policy_topic": args.policy_topic or "",
        "output_dir": args.output_dir or "",
        "inbox_mode": args.inbox_mode or "",
        "package_path": args.package_path or "",
        "delivery_target": args.delivery_target or "",
    }
    program_id, policy, route_basis = route(
        context["request_text"], index, class_map, class_order, args.program_id or "", args.program_class or ""
    )
    context["program_id"] = program_id

    authority_check, policy_check, preconditions, gate_blockers = gate(
        policy, mode_payload, one_screen, git_before, context, args.resume_from_step
    )

    step_results: list[dict[str, Any]] = []
    step_artifacts: list[str] = []
    step_blockers: list[str] = []
    completed_steps: list[str] = []
    current_step = ""
    failed_step = ""
    failed_index = 0
    stop_triggered = False
    stop_reason = ""

    if not gate_blockers:
        allow_mutation = bool(args.allow_mutation and not args.dry_run and policy.get("mutability_level") != "READ_ONLY")
        for idx in range(args.resume_from_step - 1, len(policy.get("step_plan", []))):
            step = policy["step_plan"][idx]
            current_step = str(step.get("step_id", f"S{idx + 1}")).strip()
            if str(step.get("step_type", "command_execute")) != "command_execute":
                result = {
                    "step_id": current_step,
                    "step_type": str(step.get("step_type", "")),
                    "execution_result": "FAILED",
                    "summary": "unsupported step_type",
                    "exit_code": 1,
                    "command": [],
                    "resolved_action": "unsupported",
                    "output_artifact": "",
                    "artifacts_produced": [],
                    "blocking_factors": ["unsupported_step_type"],
                }
                artifacts: list[str] = []
                blockers = [f"step {current_step}: unsupported_step_type"]
            else:
                result, artifacts, blockers = execute_step(run_id, program_id, step, context, allow_mutation)

            step_results.append(result)
            step_artifacts.extend([x for x in artifacts if str(x).strip()])
            verdict = str(result.get("execution_result", "")).upper()
            if verdict == "SUCCESS":
                completed_steps.append(current_step)
                continue

            step_blockers.extend(blockers)
            failed_step = current_step
            failed_index = idx + 1
            stop_now, reason = should_stop(verdict, policy.get("stop_conditions", []), str(policy.get("failure_policy", "stop_on_failure")))
            if stop_now:
                stop_triggered = True
                stop_reason = reason
                break

    total_steps = len(policy.get("step_plan", []))
    all_step_ids = [str(x.get("step_id", f"S{i + 1}")).strip() for i, x in enumerate(policy.get("step_plan", []))]
    pending_steps = [step_id for step_id in all_step_ids if step_id not in completed_steps]
    resume_pointer = (failed_index + 1) if failed_step else (total_steps + 1)
    checkpoint = {
        "total_steps": total_steps,
        "start_step": args.resume_from_step,
        "completed_steps": completed_steps,
        "pending_steps": pending_steps,
        "current_step": current_step,
        "failed_step": failed_step,
        "resume_pointer": resume_pointer,
        "resume_supported": bool(policy.get("resume_supported", True)),
        "can_resume": bool(failed_step and policy.get("resume_supported", True) and resume_pointer <= total_steps),
        "failure_policy": policy.get("failure_policy", "stop_on_failure"),
        "stop_condition_triggered": stop_triggered,
        "stop_condition_reason": stop_reason,
    }

    if gate_blockers:
        verdict, summary, exit_code = "BLOCKED", "blocked by authority/policy/preconditions", 2
    elif failed_step:
        blocked_seen = any(str(x.get("execution_result", "")).upper() == "BLOCKED" for x in step_results)
        verdict = "BLOCKED" if blocked_seen else "FAILED"
        summary = f"{verdict.lower()} at step {failed_step}"
        exit_code = 2 if verdict == "BLOCKED" else 1
    else:
        verdict, summary, exit_code = "SUCCESS", "program completed successfully", 0

    if verdict == "SUCCESS":
        if str(policy.get("review_requirement", "none")) != "none":
            next_step = (
                f"Run review requirement '{policy.get('review_requirement', 'none')}' for delivery target "
                f"'{context.get('delivery_target') or policy.get('delivery_target', 'none')}'."
            )
        else:
            next_step = "Run python scripts/repo_control_center.py full-check."
    else:
        all_blockers = gate_blockers + step_blockers
        if any("creator authority required" in x.lower() for x in all_blockers):
            next_step = "Enable creator authority and rerun creator-bound program."
        elif checkpoint["can_resume"]:
            next_step = f"Resume with --program-id {program_id} --resume-from-step {resume_pointer}."
        else:
            next_step = "Inspect step outputs and clear blockers before rerun."

    git_after = git_state()
    changed_files = sorted(set(git_before["status_files"]).symmetric_difference(set(git_after["status_files"])))
    artifacts = sorted(set(step_artifacts + list(policy.get("evidence_outputs", [])) + [rel(STATUS_PATH), rel(REPORT_PATH), rel(CHECKPOINT_PATH), rel(HISTORY_PATH)]))

    payload = {
        "schema_version": EXEC_SCHEMA,
        "run_id": run_id,
        "generated_at": utc_now(),
        "registry_schema_version": registry_payload.get("schema_version", "unknown"),
        "program_class": policy.get("program_class", ""),
        "task_id_or_program_id": program_id,
        "request_text": context.get("request_text") or program_id,
        "resolved_goal": policy.get("resolved_goal", ""),
        "execution_scope": policy.get("execution_scope", ""),
        "authority_check": authority_check,
        "policy_check": policy_check,
        "preconditions": preconditions,
        "step_plan": policy.get("step_plan", []),
        "current_step": current_step,
        "checkpoint_state": checkpoint,
        "execution_result": {"verdict": verdict, "summary": summary, "exit_code": exit_code},
        "artifacts_produced": artifacts,
        "state_change": {
            "mutability_level": policy.get("mutability_level", "READ_ONLY"),
            "execution_mode": (
                "live_mutation"
                if (args.allow_mutation and not args.dry_run and policy.get("mutability_level", "READ_ONLY") != "READ_ONLY")
                else ("read_only" if policy.get("mutability_level", "READ_ONLY") == "READ_ONLY" else "dry_run")
            ),
            "state_change_detected": bool(changed_files),
            "changed_files": changed_files,
        },
        "blocking_factors": sorted(set(gate_blockers + step_blockers)),
        "next_step": next_step,
        "evidence_source": sorted(
            set(
                ["workspace_config/operator_task_program_registry.json", "docs/governance/OPERATOR_TASK_PROGRAM_CONTRACT.md"]
                + [str(x) for x in policy.get("policy_basis", [])]
                + [str(x.get("output_artifact", "")).strip() for x in step_results if str(x.get("output_artifact", "")).strip()]
            )
        ),
        "command_dependencies": policy.get("command_dependencies", []),
        "review_dependencies": policy.get("review_dependencies", []),
        "delivery_artifacts": policy.get("delivery_artifacts", []),
        "failure_policy": policy.get("failure_policy", "stop_on_failure"),
        "resume_supported": bool(policy.get("resume_supported", True)),
        "stop_conditions": policy.get("stop_conditions", []),
        "delivery_target": context.get("delivery_target") or policy.get("delivery_target", "none"),
        "review_requirement": policy.get("review_requirement", "none"),
        "escalation_requirement": bool(policy.get("escalation_requirement", False)),
        "step_results": step_results,
        "route_basis": route_basis,
        "notes": [f"mutability_level={policy.get('mutability_level', 'READ_ONLY')}", f"class_order={','.join(class_order)}"],
    }

    write_runtime(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


def classify_mode(args: argparse.Namespace) -> int:
    _, index, class_map, class_order = load_registry()
    program_id, policy, route_basis = route(args.request, index, class_map, class_order, args.program_id or "", args.program_class or "")
    print(
        json.dumps(
            {
                "schema_version": EXEC_SCHEMA,
                "generated_at": utc_now(),
                "request_text": args.request,
                "route_basis": route_basis,
                "program_class": policy.get("program_class", ""),
                "task_id_or_program_id": program_id,
                "resolved_goal": policy.get("resolved_goal", ""),
                "execution_scope": policy.get("execution_scope", ""),
                "command_dependencies": policy.get("command_dependencies", []),
                "review_dependencies": policy.get("review_dependencies", []),
                "mutability_level": policy.get("mutability_level", "READ_ONLY"),
                "failure_policy": policy.get("failure_policy", "stop_on_failure"),
                "resume_supported": bool(policy.get("resume_supported", True)),
                "stop_conditions": policy.get("stop_conditions", []),
                "delivery_target": policy.get("delivery_target", "none"),
                "review_requirement": policy.get("review_requirement", "none"),
                "escalation_requirement": bool(policy.get("escalation_requirement", False)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def registry_mode() -> int:
    payload, index, class_map, class_order = load_registry()
    out = {
        "schema_version": payload.get("schema_version", "unknown"),
        "wave": payload.get("wave", "unknown"),
        "program_count": len(index),
        "class_order": list(class_order),
        "program_classes": [{"program_class": program_class, "program_ids": class_map[program_class]} for program_class in sorted(class_map.keys())],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def status_mode() -> int:
    if STATUS_PATH.exists():
        print(json.dumps(read_json(STATUS_PATH), ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"schema_version": STATUS_SCHEMA, "generated_at": utc_now(), "status": "NO_PROGRAM_RUN"}, ensure_ascii=False, indent=2))
    return 0

def consistency_mode(args: argparse.Namespace) -> int:
    _, index, class_map, class_order = load_registry()
    golden_path = Path(args.golden_file).expanduser()
    if not golden_path.is_absolute():
        golden_path = (ROOT / golden_path).resolve()
    payload = read_json(golden_path)
    items = payload.get("items", [])

    total, passed = len(items), 0
    failures: list[dict[str, Any]] = []
    for idx, item in enumerate(items, start=1):
        raw_request = str(item.get("raw_request", "")).strip()
        expected_class = str(item.get("program_class", "")).strip()
        expected_program_id = str(item.get("expected_program_id", "")).strip()
        expected_actions = [str(x).strip() for x in item.get("expected_step_plan", []) if str(x).strip()]
        item_id = str(item.get("id", "")).strip() or f"item-{idx}"

        actual_program_id, policy, route_basis = route(raw_request, index, class_map, class_order, "", "")
        actual_actions = [str(step.get("action", "")).strip() for step in policy.get("step_plan", [])]

        reasons: list[str] = []
        if policy.get("program_class") != expected_class:
            reasons.append("program_class_mismatch")
        if actual_program_id != expected_program_id:
            reasons.append("program_id_mismatch")
        if expected_actions and actual_actions != expected_actions:
            reasons.append("step_plan_mismatch")

        if reasons:
            failures.append(
                {
                    "id": item_id,
                    "raw_request": raw_request,
                    "route_basis": route_basis,
                    "expected_program_class": expected_class,
                    "actual_program_class": policy.get("program_class", ""),
                    "expected_program_id": expected_program_id,
                    "actual_program_id": actual_program_id,
                    "expected_step_plan": expected_actions,
                    "actual_step_plan": actual_actions,
                    "reasons": reasons,
                }
            )
            continue
        passed += 1

    result = {
        "schema_version": CONSISTENCY_SCHEMA,
        "generated_at": utc_now(),
        "golden_pack_path": rel(golden_path),
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "verdict": "PASS" if passed == total else "FAIL",
        "failures": failures,
    }
    write_json(CONSISTENCY_PATH, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Wave 2B controlled operator task/program surface.")
    sub = p.add_subparsers(dest="mode", required=True)

    ex = sub.add_parser("execute")
    ex.add_argument("--request", default="")
    ex.add_argument("--program-id", default="")
    ex.add_argument("--program-class", default="")
    ex.add_argument("--task-id", default="")
    ex.add_argument("--node-id", default="")
    ex.add_argument("--policy-topic", default="")
    ex.add_argument("--output-dir", default="")
    ex.add_argument("--inbox-mode", default="")
    ex.add_argument("--package-path", default="")
    ex.add_argument("--delivery-target", default="")
    ex.add_argument("--resume-from-step", type=int, default=1)
    ex.add_argument("--intent", choices=["auto", "creator", "helper", "integration"], default="auto")
    ex.add_argument("--allow-mutation", action="store_true")
    ex.add_argument("--dry-run", action="store_true")

    cl = sub.add_parser("classify")
    cl.add_argument("--request", required=True)
    cl.add_argument("--program-id", default="")
    cl.add_argument("--program-class", default="")

    sub.add_parser("registry")
    sub.add_parser("status")
    cc = sub.add_parser("consistency-check")
    cc.add_argument("--golden-file", default=str(GOLDEN_2B.relative_to(ROOT)))
    return p


def main() -> int:
    args = parser().parse_args()
    if args.mode == "execute":
        return execute_mode(args)
    if args.mode == "classify":
        return classify_mode(args)
    if args.mode == "registry":
        return registry_mode()
    if args.mode == "status":
        return status_mode()
    if args.mode == "consistency-check":
        return consistency_mode(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
