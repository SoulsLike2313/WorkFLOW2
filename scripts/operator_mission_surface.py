
#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
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

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ROOT = r"E:\CVVCODEX"
REGISTRY_PATH = ROOT / "workspace_config" / "operator_mission_registry.json"
TASK_REGISTRY_PATH = ROOT / "workspace_config" / "operator_task_program_registry.json"
TASK_SCRIPT = ROOT / "scripts" / "operator_task_program_surface.py"
ONE_SCREEN_PATH = ROOT / "runtime" / "repo_control_center" / "one_screen_status.json"
GOLDEN_3C = ROOT / "docs" / "review_artifacts" / "OPERATOR_MISSION_GOLDEN_PACK_WAVE_3C.json"

RUNTIME_DIR = ROOT / "runtime" / "repo_control_center"
OUTPUTS_DIR = RUNTIME_DIR / "operator_mission_outputs"
STATUS_PATH = RUNTIME_DIR / "operator_mission_status.json"
REPORT_PATH = RUNTIME_DIR / "operator_mission_report.md"
CHECKPOINT_PATH = RUNTIME_DIR / "operator_mission_checkpoint.json"
HISTORY_PATH = RUNTIME_DIR / "operator_mission_history.json"
AUDIT_TRAIL_PATH = RUNTIME_DIR / "operator_mission_audit_trail.json"
CONSISTENCY_PATH = RUNTIME_DIR / "operator_mission_consistency.json"
LOG_PATH = RUNTIME_DIR / "operator_mission_log.jsonl"

EXEC_SCHEMA = "operator_mission_contract.wave3c.v1.0.0"
CONSISTENCY_SCHEMA = "operator_mission_consistency.wave3c.v1.0.0"
MUTABILITY_LEVELS = {
    "READ_ONLY",
    "REFRESH_ONLY",
    "PACKAGE_ONLY",
    "REVIEW_DELIVERY",
    "GUARDED_STATE_CHANGE",
    "CREATOR_ONLY_TRANSITION",
}
DEFAULT_CLASS_ORDER = (
    "guarded_baseline_transition_mission",
    "creator_only_certification_mission",
    "controlled_upgrade_mission",
    "blocked_mutation_mission",
    "external_review_mission",
    "readiness_transition_mission",
    "handoff_delivery_mission",
    "evidence_consolidation_mission",
    "certification_mission",
    "readiness_mission",
    "review_prep_mission",
    "status_consolidation_mission",
)
FAILURE_POLICIES = {"stop_on_failure", "stop_on_blocked", "continue_on_failure"}


def now_utc() -> str:
    return common_utc_now_iso()


def normalize_rel(path: str) -> str:
    return common_normalize_rel(path)


def rel(path: Path) -> str:
    return normalize_rel(str(path.relative_to(ROOT)))


def read_json(path: Path) -> dict[str, Any]:
    return common_read_json(path)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    common_write_json(path, payload)


def write_md(path: Path, text: str) -> None:
    common_write_markdown(path, text)


def run(cmd: list[str], allow_fail: bool = False) -> subprocess.CompletedProcess[str]:
    return common_run_command(cmd, cwd=ROOT, allow_fail=allow_fail, error_prefix="failed")


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
    }

def load_registry() -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, list[str]], tuple[str, ...]]:
    payload = read_json(REGISTRY_PATH)
    task_registry = read_json(TASK_REGISTRY_PATH)
    known_programs = {
        p.get("program_id", "")
        for c in task_registry.get("program_classes", [])
        for p in c.get("programs", [])
        if p.get("program_id", "")
    }

    index: dict[str, dict[str, Any]] = {}
    class_map: dict[str, list[str]] = {}

    for cls in payload.get("mission_classes", []):
        mission_class = str(cls.get("mission_class", "")).strip()
        if not mission_class:
            continue
        class_map.setdefault(mission_class, [])

        defaults = {
            "wave": cls.get("wave", "unknown"),
            "mission_class": mission_class,
            "description": cls.get("description", ""),
            "allowed_modes": cls.get("allowed_modes", []),
            "authority_requirement": cls.get("authority_requirement", "none"),
            "creator_authority_required": bool(
                cls.get("creator_authority_required", False)
                or str(cls.get("authority_requirement", "none")) == "creator_required"
            ),
            "requires_in_sync": bool(cls.get("requires_in_sync", False)),
            "requires_clean_worktree": bool(cls.get("requires_clean_worktree", False)),
            "policy_basis": cls.get("policy_basis", []),
            "non_goals": cls.get("non_goals", []),
            "acceptance_criteria": cls.get("acceptance_criteria", []),
            "acceptance_gates": cls.get("acceptance_gates", []),
            "mutability_level": str(cls.get("mutability_level", "READ_ONLY")).upper(),
            "resume_supported": bool(cls.get("resume_supported", True)),
            "rollback_supported": bool(cls.get("rollback_supported", False)),
            "mission_priority": cls.get("mission_priority", "normal"),
            "evidence_outputs": cls.get("evidence_outputs", []),
            "audit_outputs": cls.get("audit_outputs", []),
            "program_dependencies": cls.get("program_dependencies", []),
            "program_sequences": cls.get("program_sequences", []),
            "dependency_set": cls.get("dependency_set", []),
            "review_dependencies": cls.get("review_dependencies", []),
            "delivery_artifacts": cls.get("delivery_artifacts", []),
            "failure_policy": str(cls.get("failure_policy_default", "stop_on_failure")),
            "stop_conditions": cls.get("stop_conditions", []),
            "delivery_target": cls.get("delivery_target", "none"),
            "review_requirement": cls.get("review_requirement", "none"),
            "escalation_requirement": bool(cls.get("escalation_requirement", False)),
            "escalation_path": cls.get("escalation_path", "mission_escalation"),
            "required_context": cls.get("required_context", []),
            "default_context": cls.get("default_context", {}),
            "blocking_conditions": cls.get("blocking_conditions", []),
            "approval_basis": cls.get("approval_basis", []),
            "audit_trail_reference": cls.get("audit_trail_reference", "runtime/repo_control_center/operator_mission_audit_trail.json"),
            "acceptance_transition_semantics": cls.get("acceptance_transition_semantics", "no_acceptance_transition"),
            "policy_supported": bool(cls.get("policy_supported", True)),
        }

        if defaults["mutability_level"] not in MUTABILITY_LEVELS:
            raise RuntimeError(f"unsupported mutability level at class {mission_class}: {defaults['mutability_level']}")
        if defaults["failure_policy"] not in FAILURE_POLICIES:
            raise RuntimeError(f"unsupported failure_policy at class {mission_class}: {defaults['failure_policy']}")

        for mission in cls.get("missions", []):
            mission_id = str(mission.get("mission_id", "")).strip()
            if not mission_id:
                continue
            merged = {k: mission.get(k, v) for k, v in defaults.items()}
            merged.update(
                {
                    "mission_id": mission_id,
                    "resolved_goal": mission.get("resolved_goal", f"Execute {mission_id}"),
                    "mission_scope": mission.get("mission_scope", mission_class),
                    "route_tokens": [str(x).lower().strip() for x in mission.get("route_tokens", []) if str(x).strip()],
                    "program_plan": mission.get("program_plan", []),
                    "completion_rule": mission.get("completion_rule", "certify_on_success"),
                }
            )
            merged["creator_authority_required"] = bool(
                merged.get("creator_authority_required", False)
                or str(merged.get("authority_requirement", "none")) == "creator_required"
            )

            for step in merged.get("program_plan", []):
                pid = str(step.get("program_id", "")).strip()
                if pid and pid not in known_programs:
                    raise RuntimeError(f"unknown program_id in mission {mission_id}: {pid}")

            index[mission_id] = merged
            class_map[mission_class].append(mission_id)

    for key in class_map:
        class_map[key] = sorted(class_map[key])
    if not index:
        raise RuntimeError("empty operator_mission_registry")

    class_order = tuple(
        str(x).strip() for x in payload.get("routing_precedence", {}).get("class_order", []) if str(x).strip()
    ) or DEFAULT_CLASS_ORDER
    return payload, index, class_map, class_order


def route(
    request: str,
    index: dict[str, dict[str, Any]],
    class_map: dict[str, list[str]],
    class_order: tuple[str, ...],
    mission_id: str,
    mission_class: str,
) -> tuple[str, dict[str, Any], str]:
    if mission_id.strip():
        key = mission_id.strip()
        if key not in index:
            raise RuntimeError(f"unknown mission-id: {key}")
        return key, index[key], "explicit_mission_id_override"
    if mission_class.strip():
        cls = mission_class.strip()
        if cls not in class_map or not class_map[cls]:
            raise RuntimeError(f"unknown mission-class: {cls}")
        key = class_map[cls][0]
        return key, index[key], "explicit_mission_class_override"
    if request.strip() in index:
        key = request.strip()
        return key, index[key], "direct_mission_id_match"

    normalized = f" {' '.join(request.lower().split())} "
    for cls in class_order:
        for key in class_map.get(cls, []):
            for token in index[key].get("route_tokens", []):
                if token and token in normalized:
                    return key, index[key], "token_match"

    fallback = "mission.wave3a.status_consolidation.complete.v1"
    key = fallback if fallback in index else sorted(index.keys())[0]
    return key, index[key], "fallback_status_consolidation"


def merged_context(policy: dict[str, Any], args: argparse.Namespace) -> dict[str, str]:
    context = {str(k): str(v) for k, v in dict(policy.get("default_context", {})).items() if str(v).strip()}
    cli_values = {
        "task_id": args.task_id or "",
        "node_id": args.node_id or "",
        "inbox_mode": args.inbox_mode or "",
        "package_path": args.package_path or "",
        "delivery_target": args.delivery_target or "",
        "policy_topic": args.policy_topic or "",
    }
    for key, value in cli_values.items():
        if str(value).strip():
            context[key] = str(value).strip()
    return context

def gate(
    policy: dict[str, Any],
    context: dict[str, str],
    mode_payload: dict[str, Any],
    one_screen: dict[str, Any],
    git_before: dict[str, Any],
    resume_from_program: int,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[str]]:
    machine_mode = str(mode_payload.get("machine_mode", "unknown"))
    authority_present = bool(mode_payload.get("authority", {}).get("authority_present", False))
    mutability_level = str(policy.get("mutability_level", "READ_ONLY")).upper()

    blockers: list[str] = []
    allowed_modes = list(policy.get("allowed_modes") or [])
    creator_alias_allowed = machine_mode == "emperor" and ("creator" in allowed_modes)
    if allowed_modes and machine_mode not in allowed_modes and not creator_alias_allowed:
        blockers.append(f"machine_mode '{machine_mode}' not allowed")
    if bool(policy.get("creator_authority_required", False)) and not authority_present:
        blockers.append("creator authority required but not present")
    if mutability_level in {"GUARDED_STATE_CHANGE", "CREATOR_ONLY_TRANSITION"} and not authority_present:
        blockers.append(f"guarded mission mutability '{mutability_level}' requires creator authority")
    if not bool(policy.get("policy_supported", True)):
        blockers.append("policy support explicitly disabled for this mission")

    missing_policy = [p for p in policy.get("policy_basis", []) if not (ROOT / str(p)).exists()]

    pre_failed: list[str] = []
    if str(ROOT).lower() != CANONICAL_ROOT.lower():
        pre_failed.append("repo_root_is_canonical")
    if bool(policy.get("requires_in_sync", False)) and str(one_screen.get("sync_verdict", "UNKNOWN")) != "IN_SYNC":
        pre_failed.append("sync_in_sync")
    if bool(policy.get("requires_clean_worktree", False)) and not git_before.get("worktree_clean", False):
        pre_failed.append("worktree_clean")
    total = max(len(policy.get("program_plan", [])), 1)
    if resume_from_program < 1 or resume_from_program > total:
        pre_failed.append("resume_program_in_range")
    if resume_from_program > 1 and not bool(policy.get("resume_supported", True)):
        pre_failed.append("resume_supported")
    for key in policy.get("required_context", []) or []:
        if not str(context.get(str(key), "")).strip():
            pre_failed.append(f"context_{key}_required")

    authority = {
        "verdict": "PASS" if not blockers else "BLOCKED",
        "machine_mode": machine_mode,
        "authority_present": authority_present,
        "details": blockers or ["authority contract satisfied"],
    }
    policy_check = {
        "verdict": "PASS" if not missing_policy else "BLOCKED",
        "missing_policy_files": missing_policy,
        "policy_basis": policy.get("policy_basis", []),
    }
    preconditions = {"verdict": "PASS" if not pre_failed else "BLOCKED", "failed": pre_failed}

    all_blockers = blockers + [f"missing policy file: {x}" for x in missing_policy] + [f"failed precondition: {x}" for x in pre_failed]
    return authority, policy_check, preconditions, all_blockers


def execute_program_step(run_id: str, mission_id: str, step: dict[str, Any], intent: str, context: dict[str, str]) -> tuple[dict[str, Any], list[str], list[str]]:
    program_id = str(step.get("program_id", "")).strip()
    expected = [str(x).upper().strip() for x in step.get("expected_verdicts", ["SUCCESS"]) if str(x).strip()] or ["SUCCESS"]
    cmd = [
        "python",
        str(TASK_SCRIPT.relative_to(ROOT)),
        "execute",
        "--program-id",
        program_id,
        "--intent",
        intent,
        "--dry-run",
    ]
    flag_map = {
        "task_id": "--task-id",
        "node_id": "--node-id",
        "inbox_mode": "--inbox-mode",
        "package_path": "--package-path",
        "delivery_target": "--delivery-target",
        "policy_topic": "--policy-topic",
    }
    for key, flag in flag_map.items():
        value = str(context.get(key, "")).strip()
        if value:
            cmd.extend([flag, value])

    cp = run(cmd, allow_fail=True)
    parsed = parse_json(cp.stdout) or parse_json(cp.stderr) or {}
    verdict = str(parsed.get("execution_result", {}).get("verdict", "FAILED")).upper()
    ok = verdict in expected

    output_path = OUTPUTS_DIR / run_id / f"{normalize_rel(program_id).replace('/', '__')}.json"
    write_json(
        output_path,
        {
            "run_id": run_id,
            "mission_id": mission_id,
            "program_id": program_id,
            "command": cmd,
            "expected_verdicts": expected,
            "actual_verdict": verdict,
            "payload": parsed,
        },
    )
    artifacts = [rel(output_path)] + [str(x) for x in parsed.get("artifacts_produced", []) if str(x).strip()]
    blockers = [] if ok else [f"program {program_id}: expected {expected}, got {verdict}"]
    result = {
        "program_id": program_id,
        "actual_verdict": verdict,
        "expected_verdicts": expected,
        "success": ok,
        "summary": parsed.get("execution_result", {}).get("summary", ""),
        "output_artifact": rel(output_path),
        "artifacts_produced": sorted(set(artifacts)),
        "blocking_factors": blockers + [str(x) for x in parsed.get("blocking_factors", []) if str(x).strip()],
    }
    return result, result["artifacts_produced"], result["blocking_factors"]


def should_stop(verdict: str, failure_policy: str, stop_conditions: list[str], step_success: bool) -> tuple[bool, str]:
    if step_success:
        return False, ""
    v = verdict.upper()
    cond = {str(x).strip() for x in stop_conditions}
    if v == "BLOCKED" and "any_program_blocked" in cond:
        return True, "any_program_blocked"
    if v == "FAILED" and "any_program_failed" in cond:
        return True, "any_program_failed"
    if failure_policy == "stop_on_failure" and v in {"FAILED", "BLOCKED"}:
        return True, "failure_policy_stop_on_failure"
    if failure_policy == "stop_on_blocked" and v == "BLOCKED":
        return True, "failure_policy_stop_on_blocked"
    return False, ""

def execute_mode(args: argparse.Namespace) -> int:
    run_id = f"mission-wave3c-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    payload_registry, index, class_map, class_order = load_registry()
    mission_id, policy, route_basis = route(args.request or "", index, class_map, class_order, args.mission_id or "", args.mission_class or "")

    mode_payload = build_mode_payload(intent=args.intent)
    one_screen = read_json(ONE_SCREEN_PATH) if ONE_SCREEN_PATH.exists() else {}
    git_before = git_state()
    context = merged_context(policy, args)
    authority, policy_check, preconditions, gate_blockers = gate(policy, context, mode_payload, one_screen, git_before, args.resume_from_program)

    failure_policy = str(policy.get("failure_policy", "stop_on_failure"))
    stop_conditions = list(policy.get("stop_conditions", []))

    program_results: list[dict[str, Any]] = []
    program_artifacts: list[str] = []
    program_blockers: list[str] = []
    completed: list[str] = []
    current_program = ""
    failed_program = ""
    failed_idx = 0
    stop_triggered = False
    stop_reason = ""

    if not gate_blockers:
        for idx in range(args.resume_from_program - 1, len(policy.get("program_plan", []))):
            step = policy["program_plan"][idx]
            current_program = str(step.get("program_id", "")).strip()
            result, artifacts, blockers = execute_program_step(run_id, mission_id, step, args.intent, context)
            program_results.append(result)
            program_artifacts.extend(artifacts)
            if result["success"]:
                completed.append(current_program)
            else:
                program_blockers.extend(blockers)
                failed_program = current_program
                failed_idx = idx + 1
            stop_now, reason = should_stop(
                result["actual_verdict"],
                failure_policy,
                stop_conditions,
                result["success"],
            )
            if stop_now:
                stop_triggered = True
                stop_reason = reason
                break

    unexpected_blocked = len(
        [x for x in program_results if not bool(x.get("success", False)) and x.get("actual_verdict", "").upper() == "BLOCKED"]
    )
    unexpected_failed = len(
        [x for x in program_results if not bool(x.get("success", False)) and x.get("actual_verdict", "").upper() == "FAILED"]
    )

    if gate_blockers:
        verdict, summary, exit_code = "BLOCKED", "blocked by authority/policy/preconditions", 2
    elif unexpected_blocked > 0:
        if failure_policy == "continue_on_failure" and not stop_triggered:
            verdict, summary, exit_code = "PARTIAL", "mission completed with blocked programs under continue_on_failure", 1
        else:
            verdict, summary, exit_code = "BLOCKED", f"blocked at program {failed_program or current_program}", 2
    elif unexpected_failed > 0:
        if failure_policy == "continue_on_failure" and not stop_triggered:
            verdict, summary, exit_code = "PARTIAL", "mission completed with failed programs under continue_on_failure", 1
        else:
            verdict, summary, exit_code = "FAILED", f"failed at program {failed_program or current_program}", 1
    else:
        verdict, summary, exit_code = "SUCCESS", "mission completed successfully", 0

    total = len(policy.get("program_plan", []))
    pending = [
        str(x.get("program_id", "")).strip()
        for x in policy.get("program_plan", [])[len(completed):]
        if str(x.get("program_id", "")).strip()
    ]
    checkpoint = {
        "total_programs": total,
        "start_program": args.resume_from_program,
        "completed_programs": completed,
        "pending_programs": pending,
        "current_program": current_program,
        "failed_program": failed_program,
        "resume_pointer": (failed_idx + 1 if failed_program else total + 1),
        "resume_supported": bool(policy.get("resume_supported", True)),
        "can_resume": bool((failed_program or unexpected_blocked > 0 or unexpected_failed > 0) and len(pending) > 0 and policy.get("resume_supported", True)),
        "stop_condition_triggered": stop_triggered,
        "stop_condition_reason": stop_reason,
    }

    completion_rule = str(policy.get("completion_rule", "certify_on_success"))
    if gate_blockers and completion_rule != "certify_on_expected_block":
        completion_verdict = "BLOCKED"
    elif verdict == "SUCCESS" and completion_rule.startswith("certify_on_"):
        completion_verdict = "CERTIFIED"
    elif verdict == "BLOCKED" and completion_rule == "certify_on_expected_block":
        completion_verdict = "CERTIFIED"
    elif verdict == "SUCCESS":
        completion_verdict = "SUCCESS"
    elif verdict == "PARTIAL":
        completion_verdict = "PARTIAL"
    else:
        completion_verdict = verdict

    blockers = sorted(set(gate_blockers + program_blockers))
    rollback_supported = bool(policy.get("rollback_supported", False))
    rollback_required = bool(
        rollback_supported
        and str(policy.get("mutability_level", "READ_ONLY")).upper() in {"GUARDED_STATE_CHANGE", "CREATOR_ONLY_TRANSITION"}
        and (verdict in {"FAILED", "BLOCKED"} or bool(gate_blockers))
    )
    next_step = "Mission certified. Use mission runtime artifacts as evidence."
    if verdict != "SUCCESS":
        if any("creator authority required" in x.lower() for x in blockers):
            next_step = "Enable creator authority and rerun creator-bound mission."
        elif completion_rule == "certify_on_expected_block" and verdict == "BLOCKED":
            next_step = "Expected blocked path certified. Review mission audit trail."
        elif rollback_required:
            next_step = "Rollback required before retrying guarded transition mission."
        elif checkpoint["can_resume"]:
            next_step = f"Resume mission with --mission-id {mission_id} --resume-from-program {checkpoint['resume_pointer']}."
        else:
            next_step = "Inspect blockers and rerun mission."

    artifacts = sorted(
        set(
            program_artifacts
            + list(policy.get("evidence_outputs", []))
            + [rel(STATUS_PATH), rel(REPORT_PATH), rel(CHECKPOINT_PATH), rel(HISTORY_PATH), rel(AUDIT_TRAIL_PATH)]
        )
    )

    payload = {
        "schema_version": EXEC_SCHEMA,
        "run_id": run_id,
        "generated_at": now_utc(),
        "registry_schema_version": payload_registry.get("schema_version", "unknown"),
        "mission_class": policy.get("mission_class", ""),
        "mission_id": mission_id,
        "request_text": args.request or mission_id,
        "resolved_goal": policy.get("resolved_goal", ""),
        "mission_scope": policy.get("mission_scope", ""),
        "non_goals": policy.get("non_goals", []),
        "authority_check": authority,
        "policy_check": policy_check,
        "preconditions": preconditions,
        "program_plan": policy.get("program_plan", []),
        "program_sequences": policy.get("program_sequences", []),
        "current_program": current_program,
        "mission_checkpoint_state": checkpoint,
        "execution_result": {"verdict": verdict, "summary": summary, "exit_code": exit_code},
        "artifacts_produced": artifacts,
        "state_change": {
            "mutability_level": str(policy.get("mutability_level", "READ_ONLY")).upper(),
            "execution_mode": "safe_program_execution",
            "state_change_detected": False,
            "rollback_supported": rollback_supported,
            "rollback_required": rollback_required,
        },
        "blocking_factors": blockers,
        "acceptance_criteria": policy.get("acceptance_criteria", []),
        "acceptance_gates": policy.get("acceptance_gates", []),
        "completion_verdict": completion_verdict,
        "next_step": next_step,
        "evidence_source": sorted(
            set(
                [
                    "workspace_config/operator_mission_registry.json",
                    "workspace_config/operator_task_program_registry.json",
                    "docs/governance/OPERATOR_MISSION_CONTRACT.md",
                ]
                + [str(x) for x in policy.get("policy_basis", [])]
                + [
                    str(x.get("output_artifact", "")).strip()
                    for x in program_results
                    if str(x.get("output_artifact", "")).strip()
                ]
            )
        ),
        "dependency_set": policy.get("dependency_set", []),
        "failure_policy": failure_policy,
        "resume_supported": bool(policy.get("resume_supported", True)),
        "rollback_supported": rollback_supported,
        "creator_authority_required": bool(policy.get("creator_authority_required", False)),
        "approval_basis": policy.get("approval_basis", []),
        "audit_trail_reference": policy.get("audit_trail_reference", rel(AUDIT_TRAIL_PATH)),
        "stop_conditions": stop_conditions,
        "delivery_target": policy.get("delivery_target", "none"),
        "review_requirement": policy.get("review_requirement", "none"),
        "escalation_requirement": bool(policy.get("escalation_requirement", False)),
        "escalation_path": policy.get("escalation_path", "mission_escalation"),
        "acceptance_transition_semantics": policy.get("acceptance_transition_semantics", "no_acceptance_transition"),
        "review_dependencies": policy.get("review_dependencies", []),
        "delivery_artifacts": policy.get("delivery_artifacts", []),
        "context": context,
        "mission_priority": policy.get("mission_priority", "normal"),
        "program_results": program_results,
        "route_basis": route_basis,
        "notes": [f"class_order={','.join(class_order)}", f"wave={policy.get('wave', 'unknown')}"] ,
    }

    write_json(
        STATUS_PATH,
        {
            "schema_version": "operator_mission_status.wave3c.v1.0.0",
            "generated_at": payload["generated_at"],
            "active_or_last_mission": mission_id,
            "mission_class": payload["mission_class"],
            "run_id": run_id,
            "mutability_level": payload["state_change"]["mutability_level"],
            "creator_authority_required": payload["creator_authority_required"],
            "rollback_supported": rollback_supported,
            "rollback_required": rollback_required,
            "execution_result": payload["execution_result"],
            "completion_verdict": completion_verdict,
            "current_program": current_program,
            "completed_mission_checkpoints": completed,
            "blocking_factors": blockers,
            "artifacts_produced": artifacts,
            "next_step": next_step,
        },
    )
    write_json(CHECKPOINT_PATH, checkpoint)

    history = {"schema_version": "operator_mission_history.wave3c.v1.0.0", "items": []}
    if HISTORY_PATH.exists():
        try:
            old = read_json(HISTORY_PATH)
            if isinstance(old.get("items"), list):
                history["items"] = old["items"]
        except Exception:
            history = {"schema_version": "operator_mission_history.wave3c.v1.0.0", "items": []}
    history["items"].append(
        {
            "run_id": run_id,
            "generated_at": payload["generated_at"],
            "mission_id": mission_id,
            "mission_class": payload["mission_class"],
            "mutability_level": payload["state_change"]["mutability_level"],
            "creator_authority_required": payload["creator_authority_required"],
            "execution_verdict": verdict,
            "completion_verdict": completion_verdict,
            "failure_policy": failure_policy,
            "rollback_supported": rollback_supported,
            "rollback_required": rollback_required,
            "delivery_target": policy.get("delivery_target", "none"),
            "review_requirement": policy.get("review_requirement", "none"),
            "blocking_factors": blockers,
        }
    )
    history["items"] = history["items"][-200:]
    write_json(HISTORY_PATH, history)

    audit = {"schema_version": "operator_mission_audit_trail.wave3c.v1.0.0", "entries": []}
    if AUDIT_TRAIL_PATH.exists():
        try:
            old_audit = read_json(AUDIT_TRAIL_PATH)
            if isinstance(old_audit.get("entries"), list):
                audit["entries"] = old_audit["entries"]
        except Exception:
            audit = {"schema_version": "operator_mission_audit_trail.wave3c.v1.0.0", "entries": []}
    audit["entries"].append(
        {
            "run_id": run_id,
            "generated_at": payload["generated_at"],
            "mission_id": mission_id,
            "mission_class": payload["mission_class"],
            "mutability_level": payload["state_change"]["mutability_level"],
            "creator_authority_required": payload["creator_authority_required"],
            "authority_context": {
                "machine_mode": authority.get("machine_mode", "unknown"),
                "authority_present": authority.get("authority_present", False),
            },
            "policy_check_verdict": policy_check.get("verdict", "UNKNOWN"),
            "preconditions_verdict": preconditions.get("verdict", "UNKNOWN"),
            "execution_verdict": verdict,
            "completion_verdict": completion_verdict,
            "stop_condition_triggered": stop_triggered,
            "stop_condition_reason": stop_reason,
            "rollback_supported": rollback_supported,
            "rollback_required": rollback_required,
            "escalation_requirement": bool(policy.get("escalation_requirement", False)),
            "escalation_path": policy.get("escalation_path", "mission_escalation"),
            "blocking_factors": blockers,
            "audit_outputs": policy.get("audit_outputs", []),
        }
    )
    audit["entries"] = audit["entries"][-300:]
    write_json(AUDIT_TRAIL_PATH, audit)

    report_lines = [
        "# Operator Mission Report (Wave 3C)",
        "",
        "## Runtime Identity",
        f"- run_id: `{run_id}`",
        f"- mission_class: `{payload['mission_class']}`",
        f"- mission_id: `{mission_id}`",
        f"- route_basis: `{route_basis}`",
        "",
        "## Mission Chain",
        f"- execution_verdict: `{verdict}`",
        f"- completion_verdict: `{completion_verdict}`",
        f"- mutability_level: `{payload['state_change']['mutability_level']}`",
        f"- creator_authority_required: `{payload['creator_authority_required']}`",
        f"- failure_policy: `{failure_policy}`",
        f"- stop_conditions: `{', '.join(stop_conditions) if stop_conditions else 'none'}`",
        f"- resume_supported: `{payload['resume_supported']}`",
        f"- rollback_supported: `{rollback_supported}`",
        f"- rollback_required: `{rollback_required}`",
        f"- delivery_target: `{policy.get('delivery_target', 'none')}`",
        f"- review_requirement: `{policy.get('review_requirement', 'none')}`",
        f"- escalation_requirement: `{bool(policy.get('escalation_requirement', False))}`",
        f"- escalation_path: `{policy.get('escalation_path', 'mission_escalation')}`",
        f"- acceptance_transition_semantics: `{policy.get('acceptance_transition_semantics', 'no_acceptance_transition')}`",
        "",
        "## Program Results",
    ]
    report_lines.extend([f"- `{x['program_id']}` => `{x['actual_verdict']}` ({'PASS' if x['success'] else 'FAIL'})" for x in program_results] or ["- none"])
    report_lines.extend(["", "## Blocking Factors"])
    report_lines.extend([f"- {x}" for x in blockers] or ["- none"])
    report_lines.extend(["", "## Next Step", f"- {next_step}"])
    write_md(REPORT_PATH, "\n".join(report_lines))

    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {
                    "run_id": run_id,
                    "generated_at": payload["generated_at"],
                    "mission_id": mission_id,
                    "mission_class": payload["mission_class"],
                    "execution_verdict": verdict,
                    "completion_verdict": completion_verdict,
                    "failure_policy": failure_policy,
                    "blocking_factors": blockers,
                },
                ensure_ascii=False,
            )
            + "\n"
        )

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


def classify_mode(args: argparse.Namespace) -> int:
    _, index, class_map, class_order = load_registry()
    mission_id, policy, route_basis = route(args.request, index, class_map, class_order, args.mission_id or "", args.mission_class or "")
    out = {
        "schema_version": EXEC_SCHEMA,
        "generated_at": now_utc(),
        "request_text": args.request,
        "route_basis": route_basis,
        "mission_class": policy.get("mission_class", ""),
        "mission_id": mission_id,
        "resolved_goal": policy.get("resolved_goal", ""),
        "mission_scope": policy.get("mission_scope", ""),
        "non_goals": policy.get("non_goals", []),
        "mutability_level": policy.get("mutability_level", "READ_ONLY"),
        "creator_authority_required": bool(policy.get("creator_authority_required", False)),
        "rollback_supported": bool(policy.get("rollback_supported", False)),
        "approval_basis": policy.get("approval_basis", []),
        "audit_trail_reference": policy.get("audit_trail_reference", rel(AUDIT_TRAIL_PATH)),
        "acceptance_transition_semantics": policy.get("acceptance_transition_semantics", "no_acceptance_transition"),
        "allowed_modes": policy.get("allowed_modes", []),
        "program_plan": [str(x.get("program_id", "")).strip() for x in policy.get("program_plan", [])],
        "program_sequences": policy.get("program_sequences", []),
        "dependency_set": policy.get("dependency_set", []),
        "failure_policy": policy.get("failure_policy", "stop_on_failure"),
        "stop_conditions": policy.get("stop_conditions", []),
        "resume_supported": bool(policy.get("resume_supported", True)),
        "delivery_target": policy.get("delivery_target", "none"),
        "review_requirement": policy.get("review_requirement", "none"),
        "escalation_requirement": bool(policy.get("escalation_requirement", False)),
        "review_dependencies": policy.get("review_dependencies", []),
        "delivery_artifacts": policy.get("delivery_artifacts", []),
        "required_context": policy.get("required_context", []),
        "default_context": policy.get("default_context", {}),
        "acceptance_criteria": policy.get("acceptance_criteria", []),
        "acceptance_gates": policy.get("acceptance_gates", []),
        "completion_rule": policy.get("completion_rule", "certify_on_success"),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def registry_mode() -> int:
    payload, index, class_map, class_order = load_registry()
    out = {
        "schema_version": payload.get("schema_version", "unknown"),
        "wave": payload.get("wave", "unknown"),
        "mission_count": len(index),
        "class_order": list(class_order),
        "mission_classes": [{"mission_class": k, "mission_ids": class_map[k]} for k in sorted(class_map.keys())],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0

def status_mode() -> int:
    if STATUS_PATH.exists():
        print(json.dumps(read_json(STATUS_PATH), ensure_ascii=False, indent=2))
    else:
        print(
            json.dumps(
                {
                    "schema_version": "operator_mission_status.wave3c.v1.0.0",
                    "generated_at": now_utc(),
                    "status": "NO_MISSION_RUN",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
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
        expected_class = str(item.get("mission_class", "")).strip()
        expected_id = str(item.get("expected_mission_id", "")).strip()
        expected_plan = [str(x).strip() for x in item.get("expected_program_plan", []) if str(x).strip()]
        expected_mutability = str(item.get("mutability_level", "")).strip().upper()
        expected_failure_policy = str(item.get("expected_failure_policy", "")).strip()
        expected_review = str(item.get("expected_review_requirement", "")).strip()
        expected_delivery = str(item.get("expected_delivery_target", "")).strip()
        expected_creator_required = item.get("expected_creator_authority_required", None)
        expected_rollback_supported = item.get("expected_rollback_supported", None)
        authority_expectation = str(item.get("authority_expectation", "")).strip().lower()
        item_id = str(item.get("id", "")).strip() or f"item-{idx}"

        actual_id, policy, route_basis = route(raw_request, index, class_map, class_order, "", "")
        actual_plan = [str(x.get("program_id", "")).strip() for x in policy.get("program_plan", []) if str(x.get("program_id", "")).strip()]

        reasons: list[str] = []
        if policy.get("mission_class") != expected_class:
            reasons.append("mission_class_mismatch")
        if expected_id and actual_id != expected_id:
            reasons.append("mission_id_mismatch")
        if expected_plan and actual_plan != expected_plan:
            reasons.append("program_plan_mismatch")
        if expected_mutability and str(policy.get("mutability_level", "")).upper() != expected_mutability:
            reasons.append("mutability_level_mismatch")
        if expected_failure_policy and str(policy.get("failure_policy", "")).strip() != expected_failure_policy:
            reasons.append("failure_policy_mismatch")
        if expected_review and str(policy.get("review_requirement", "")).strip() != expected_review:
            reasons.append("review_requirement_mismatch")
        if expected_delivery and str(policy.get("delivery_target", "")).strip() != expected_delivery:
            reasons.append("delivery_target_mismatch")
        if expected_creator_required is not None and bool(policy.get("creator_authority_required", False)) != bool(expected_creator_required):
            reasons.append("creator_authority_required_mismatch")
        if expected_rollback_supported is not None and bool(policy.get("rollback_supported", False)) != bool(expected_rollback_supported):
            reasons.append("rollback_supported_mismatch")
        if authority_expectation:
            actual_creator_required = bool(policy.get("creator_authority_required", False))
            if authority_expectation == "creator_required" and not actual_creator_required:
                reasons.append("authority_expectation_mismatch")
            if authority_expectation in {"none", "not_required"} and actual_creator_required:
                reasons.append("authority_expectation_mismatch")

        if reasons:
            failures.append(
                {
                    "id": item_id,
                    "raw_request": raw_request,
                    "route_basis": route_basis,
                    "expected_mission_class": expected_class,
                    "actual_mission_class": policy.get("mission_class", ""),
                    "expected_mission_id": expected_id,
                    "actual_mission_id": actual_id,
                    "expected_program_plan": expected_plan,
                    "actual_program_plan": actual_plan,
                    "reasons": reasons,
                }
            )
        else:
            passed += 1

    result = {
        "schema_version": CONSISTENCY_SCHEMA,
        "generated_at": now_utc(),
        "golden_pack_path": rel(golden_path),
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "verdict": "PASS" if total == passed else "FAIL",
        "failures": failures,
    }
    write_json(CONSISTENCY_PATH, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Operator mission execution surface (Wave 3A + Wave 3B + Wave 3C).")
    sub = p.add_subparsers(dest="mode", required=True)

    ex = sub.add_parser("execute")
    ex.add_argument("--request", default="")
    ex.add_argument("--mission-id", default="")
    ex.add_argument("--mission-class", default="")
    ex.add_argument("--task-id", default="")
    ex.add_argument("--node-id", default="")
    ex.add_argument("--inbox-mode", default="")
    ex.add_argument("--package-path", default="")
    ex.add_argument("--delivery-target", default="")
    ex.add_argument("--policy-topic", default="")
    ex.add_argument("--resume-from-program", type=int, default=1)
    ex.add_argument("--intent", choices=["auto", "creator", "helper", "integration"], default="auto")

    cl = sub.add_parser("classify")
    cl.add_argument("--request", required=True)
    cl.add_argument("--mission-id", default="")
    cl.add_argument("--mission-class", default="")

    sub.add_parser("registry")
    sub.add_parser("status")

    cc = sub.add_parser("consistency-check")
    cc.add_argument("--golden-file", default=str(GOLDEN_3C.relative_to(ROOT)))
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
