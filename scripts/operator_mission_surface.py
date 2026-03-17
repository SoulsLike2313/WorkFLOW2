#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from detect_machine_mode import build_mode_payload

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ROOT = r"E:\CVVCODEX"
REGISTRY_PATH = ROOT / "workspace_config" / "operator_mission_registry.json"
TASK_REGISTRY_PATH = ROOT / "workspace_config" / "operator_task_program_registry.json"
TASK_SCRIPT = ROOT / "scripts" / "operator_task_program_surface.py"
ONE_SCREEN_PATH = ROOT / "runtime" / "repo_control_center" / "one_screen_status.json"

GOLDEN_FINAL = ROOT / "docs" / "review_artifacts" / "OPERATOR_MISSION_GOLDEN_PACK_FINAL.json"
RUNTIME_DIR = ROOT / "runtime" / "repo_control_center"
OUTPUTS_DIR = RUNTIME_DIR / "operator_mission_outputs"
STATUS_PATH = RUNTIME_DIR / "operator_mission_status.json"
REPORT_PATH = RUNTIME_DIR / "operator_mission_report.md"
CHECKPOINT_PATH = RUNTIME_DIR / "operator_mission_checkpoint.json"
HISTORY_PATH = RUNTIME_DIR / "operator_mission_history.json"
AUDIT_PATH = RUNTIME_DIR / "operator_mission_audit_trail.json"
CONSISTENCY_PATH = RUNTIME_DIR / "operator_mission_consistency.json"
LOG_PATH = RUNTIME_DIR / "operator_mission_log.jsonl"

EXEC_SCHEMA = "operator_mission_contract.wave3.v1.0.0"
CONSISTENCY_SCHEMA = "operator_mission_consistency.wave3.v1.0.0"

MUTABILITY_LEVELS = {
    "READ_ONLY",
    "PACKAGE_ONLY",
    "OPERATIONAL_ROUTING",
    "GUARDED_STATE_CHANGE",
    "CREATOR_ONLY_MUTATION",
}
RISKY_TOKENS = ("guarded", "creator only", "state change", "mutation", "lifecycle", "blocked mission")
DEFAULT_CLASS_ORDER = (
    "blocked_mission_test_mission",
    "creator_only_mission",
    "controlled_state_change_mission",
    "guarded_creator_mission",
    "readiness_transition_mission",
    "evidence_aggregation_mission",
    "packaging_review_transition_mission",
    "multi_program_operational_mission",
    "report_mission",
    "evidence_pack_mission",
    "validation_mission",
    "status_refresh_mission",
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


def load_one_screen() -> dict[str, Any]:
    if not ONE_SCREEN_PATH.exists():
        return {"sync_verdict": "UNKNOWN", "trust_verdict": "UNKNOWN", "governance_verdict": "UNKNOWN"}
    return read_json(ONE_SCREEN_PATH)


def load_registry() -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, list[str]], tuple[str, ...]]:
    payload = read_json(REGISTRY_PATH)
    task_registry = read_json(TASK_REGISTRY_PATH)
    task_program_ids = {
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
            "mutability_level": str(cls.get("mutability_level", "READ_ONLY")).upper(),
            "authority_requirement": cls.get("authority_requirement", "none"),
            "allowed_modes": cls.get("allowed_modes", []),
            "requires_in_sync": bool(cls.get("requires_in_sync", False)),
            "requires_clean_worktree": bool(cls.get("requires_clean_worktree", False)),
            "resume_supported": bool(cls.get("resume_supported", True)),
            "rollback_supported": bool(cls.get("rollback_supported", False)),
            "failure_policy": cls.get("failure_policy_default", "stop_on_failure"),
            "stop_conditions": cls.get("stop_conditions", []),
            "required_inputs": cls.get("required_inputs", []),
            "policy_basis": cls.get("policy_basis", []),
            "blocking_conditions": cls.get("blocking_conditions", []),
            "evidence_outputs": cls.get("evidence_outputs", []),
        }
        for mission in cls.get("missions", []):
            mission_id = str(mission.get("mission_id", "")).strip()
            if not mission_id:
                continue
            merged = {key: mission.get(key, val) for key, val in defaults.items()}
            merged.update(
                {
                    "mission_id": mission_id,
                    "resolved_goal": mission.get("resolved_goal", f"Execute {mission_id}"),
                    "mission_scope": mission.get("mission_scope", mission_class),
                    "non_goals": mission.get("non_goals", []),
                    "route_tokens": [str(x).lower().strip() for x in mission.get("route_tokens", []) if str(x).strip()],
                    "program_plan": mission.get("program_plan", []),
                    "acceptance_criteria": mission.get("acceptance_criteria", []),
                    "completion_rule": mission.get("completion_rule", "certify_on_success"),
                    "mission_priority": mission.get("mission_priority", "normal"),
                    "dependency_set": mission.get("dependency_set", []),
                }
            )
            merged["creator_authority_required"] = str(merged.get("authority_requirement", "none")) == "creator_required"
            if merged["mutability_level"] not in MUTABILITY_LEVELS:
                raise RuntimeError(f"unsupported mutability_level for {mission_id}: {merged['mutability_level']}")
            for step in merged["program_plan"]:
                pid = str(step.get("program_id", "")).strip()
                if pid and pid not in task_program_ids:
                    raise RuntimeError(f"mission {mission_id} references unknown task program: {pid}")
            index[mission_id] = merged
            class_map[mission_class].append(mission_id)
    for mission_class in class_map:
        class_map[mission_class] = sorted(class_map[mission_class])
    if not index:
        raise RuntimeError("empty operator_mission_registry")
    configured_order = tuple(
        str(x).strip() for x in payload.get("routing_precedence", {}).get("class_order", []) if str(x).strip()
    )
    class_order = configured_order or DEFAULT_CLASS_ORDER
    return payload, index, class_map, class_order

def route(request: str, index: dict[str, dict[str, Any]], class_map: dict[str, list[str]], class_order: tuple[str, ...], mission_id_override: str, mission_class_override: str) -> tuple[str, dict[str, Any], str]:
    if mission_id_override.strip():
        key = mission_id_override.strip()
        if key not in index:
            raise RuntimeError(f"unknown mission-id: {key}")
        return key, index[key], "explicit_mission_id_override"
    if mission_class_override.strip():
        cls = mission_class_override.strip()
        if cls not in class_map or not class_map[cls]:
            raise RuntimeError(f"unknown mission-class: {cls}")
        key = class_map[cls][0]
        return key, index[key], "explicit_mission_class_override"
    if request.strip() in index:
        key = request.strip()
        return key, index[key], "direct_mission_id_match"
    normalized = f" {' '.join(request.lower().split())} "
    for mission_class in class_order:
        for mission_id in class_map.get(mission_class, []):
            for token in index[mission_id].get("route_tokens", []):
                if token and token in normalized:
                    return mission_id, index[mission_id], "token_match"
    fallback = "mission.wave3a.status_refresh_certification.v1"
    key = fallback if fallback in index else sorted(index.keys())[0]
    return key, index[key], "fallback_status_refresh_mission"


def gate(policy: dict[str, Any], mode_payload: dict[str, Any], one_screen: dict[str, Any], git_before: dict[str, Any], context: dict[str, Any], resume_from_program: int) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[str]]:
    machine_mode = str(mode_payload.get("machine_mode", "unknown"))
    authority_present = bool(mode_payload.get("authority", {}).get("authority_present", False))
    authority_blockers: list[str] = []
    if policy.get("allowed_modes") and machine_mode not in policy["allowed_modes"]:
        authority_blockers.append(f"machine_mode '{machine_mode}' not allowed for '{policy['mission_id']}'")
    if policy.get("creator_authority_required") and not authority_present:
        authority_blockers.append("creator authority required but not present")
    missing_policy_files = [p for p in policy.get("policy_basis", []) if not (ROOT / str(p)).exists()]
    precondition_failures: list[str] = []
    if str(ROOT).lower() != CANONICAL_ROOT.lower():
        precondition_failures.append("repo_root_is_canonical")
    if bool(policy.get("requires_in_sync", False)) and str(one_screen.get("sync_verdict", "UNKNOWN")) != "IN_SYNC":
        precondition_failures.append("sync_in_sync")
    if bool(policy.get("requires_clean_worktree", False)) and not git_before.get("worktree_clean", False):
        precondition_failures.append("worktree_clean")
    total = max(len(policy.get("program_plan", [])), 1)
    if resume_from_program < 1 or resume_from_program > total:
        precondition_failures.append("resume_program_in_range")
    if resume_from_program > 1 and not bool(policy.get("resume_supported", True)):
        precondition_failures.append("resume_supported")
    for required in policy.get("required_inputs", []) or []:
        if not str(context.get(required, "")).strip():
            precondition_failures.append(f"{required}_provided")
    authority_check = {
        "required_modes": policy.get("allowed_modes", []),
        "authority_requirement": policy.get("authority_requirement", "none"),
        "creator_authority_required": bool(policy.get("creator_authority_required", False)),
        "machine_mode": machine_mode,
        "authority_present": authority_present,
        "detection_state": mode_payload.get("authority", {}).get("detection_state", "unknown"),
        "verdict": "PASS" if not authority_blockers else "BLOCKED",
        "details": authority_blockers or ["authority contract satisfied"],
    }
    policy_check = {
        "policy_basis": policy.get("policy_basis", []),
        "missing_policy_files": missing_policy_files,
        "verdict": "PASS" if not missing_policy_files else "BLOCKED",
    }
    preconditions = {"failed": sorted(precondition_failures), "verdict": "PASS" if not precondition_failures else "BLOCKED"}
    blockers = authority_blockers + [f"missing policy file: {x}" for x in missing_policy_files] + [f"failed precondition: {x}" for x in precondition_failures]
    return authority_check, policy_check, preconditions, blockers


def execute_program_step(run_id: str, mission_id: str, step: dict[str, Any], context: dict[str, Any], allow_mutation: bool) -> tuple[dict[str, Any], list[str], list[str]]:
    program_id = str(step.get("program_id", "")).strip()
    expected = [str(x).upper().strip() for x in step.get("expected_verdicts", ["SUCCESS"]) if str(x).strip()] or ["SUCCESS"]
    cmd = ["python", str(TASK_SCRIPT.relative_to(ROOT)), "execute", "--program-id", program_id, "--intent", context.get("intent", "auto")]
    if allow_mutation:
        cmd.append("--allow-mutation")
    else:
        cmd.append("--dry-run")
    arg_map = {
        "task_id": "--task-id",
        "node_id": "--node-id",
        "policy_topic": "--policy-topic",
        "delivery_target": "--delivery-target",
        "package_path": "--package-path",
        "inbox_mode": "--inbox-mode",
    }
    for key, flag in arg_map.items():
        val = str(context.get(key, "")).strip()
        if val:
            cmd.extend([flag, val])
    cp = run(cmd, allow_fail=True)
    payload = parse_json(cp.stdout) or parse_json(cp.stderr) or {}
    verdict = str(payload.get("execution_result", {}).get("verdict", "FAILED")).upper()
    ok = verdict in expected
    output_path = OUTPUTS_DIR / run_id / f"{normalize_rel(program_id).replace('/', '__')}.json"
    output_payload = {
        "schema_version": "operator_mission_program_step_output.v1.0.0",
        "run_id": run_id,
        "mission_id": mission_id,
        "program_id": program_id,
        "command": cmd,
        "command_rc": cp.returncode,
        "expected_verdicts": expected,
        "actual_verdict": verdict,
        "program_payload": payload,
    }
    write_json(output_path, output_payload)
    artifacts = [rel(output_path)] + [str(x) for x in payload.get("artifacts_produced", []) if str(x).strip()]
    blockers = [] if ok else [f"program {program_id}: expected {expected}, got {verdict}"]
    result = {
        "program_id": program_id,
        "expected_verdicts": expected,
        "actual_verdict": verdict,
        "success": ok,
        "summary": payload.get("execution_result", {}).get("summary", ""),
        "exit_code": payload.get("execution_result", {}).get("exit_code", cp.returncode),
        "output_artifact": rel(output_path),
        "artifacts_produced": artifacts,
        "blocking_factors": blockers + [str(x) for x in payload.get("blocking_factors", []) if str(x).strip()],
    }
    return result, artifacts, result["blocking_factors"]


def should_stop(verdict: str, stop_conditions: list[str], failure_policy: str) -> tuple[bool, str]:
    upper = verdict.upper()
    cond = {str(x).strip() for x in stop_conditions}
    if upper == "BLOCKED" and "any_program_blocked" in cond:
        return True, "any_program_blocked"
    if upper == "FAILED" and "any_program_failed" in cond:
        return True, "any_program_failed"
    if failure_policy == "stop_on_failure" and upper in {"FAILED", "BLOCKED"}:
        return True, "failure_policy_stop_on_failure"
    if failure_policy == "stop_on_blocked" and upper == "BLOCKED":
        return True, "failure_policy_stop_on_blocked"
    return False, ""

def write_runtime(payload: dict[str, Any]) -> None:
    status = {
        "schema_version": "operator_mission_status.wave3.v1.0.0",
        "generated_at": payload["generated_at"],
        "run_id": payload["run_id"],
        "mission_class": payload["mission_class"],
        "mission_id": payload["mission_id"],
        "execution_result": payload["execution_result"],
        "completion_verdict": payload["completion_verdict"],
        "current_program": payload["current_program"],
        "checkpoint_state": payload["mission_checkpoint_state"],
        "blocking_factors": payload["blocking_factors"],
        "next_step": payload["next_step"],
    }
    write_json(STATUS_PATH, status)
    write_json(CHECKPOINT_PATH, payload["mission_checkpoint_state"])

    history = read_json(HISTORY_PATH) if HISTORY_PATH.exists() else {"schema_version": "operator_mission_history.wave3.v1.0.0", "items": []}
    history.setdefault("items", []).append(
        {
            "run_id": payload["run_id"],
            "generated_at": payload["generated_at"],
            "mission_class": payload["mission_class"],
            "mission_id": payload["mission_id"],
            "execution_result": payload["execution_result"]["verdict"],
            "completion_verdict": payload["completion_verdict"],
            "blocking_factors": payload["blocking_factors"],
        }
    )
    history["items"] = history["items"][-200:]
    write_json(HISTORY_PATH, history)

    audit = read_json(AUDIT_PATH) if AUDIT_PATH.exists() else {"schema_version": "operator_mission_audit_trail.wave3.v1.0.0", "items": []}
    audit.setdefault("items", []).append(
        {
            "run_id": payload["run_id"],
            "generated_at": payload["generated_at"],
            "mission_class": payload["mission_class"],
            "mission_id": payload["mission_id"],
            "mutability_level": payload["mutability_level"],
            "authority_check": payload["authority_check"],
            "policy_check": payload["policy_check"],
            "execution_result": payload["execution_result"],
            "completion_verdict": payload["completion_verdict"],
            "blocking_factors": payload["blocking_factors"],
            "artifacts_produced": payload["artifacts_produced"],
        }
    )
    audit["items"] = audit["items"][-200:]
    write_json(AUDIT_PATH, audit)

    report_lines = [
        "# Operator Mission Report",
        "",
        f"- run_id: `{payload['run_id']}`",
        f"- mission_class: `{payload['mission_class']}`",
        f"- mission_id: `{payload['mission_id']}`",
        f"- execution_verdict: `{payload['execution_result']['verdict']}`",
        f"- completion_verdict: `{payload['completion_verdict']}`",
        f"- mutability_level: `{payload['mutability_level']}`",
        f"- authority_verdict: `{payload['authority_check']['verdict']}`",
        f"- policy_verdict: `{payload['policy_check']['verdict']}`",
        f"- preconditions_verdict: `{payload['preconditions']['verdict']}`",
        "",
        "## Program Results",
    ]
    report_lines.extend([f"- `{x['program_id']}` => `{x['actual_verdict']}` ({'PASS' if x['success'] else 'FAIL'})" for x in payload["program_results"]])
    report_lines.extend(["", "## Blocking Factors"])
    report_lines.extend([f"- {x}" for x in payload["blocking_factors"]] or ["- none"])
    report_lines.extend(["", f"- next_step: {payload['next_step']}"])
    write_md(REPORT_PATH, "\n".join(report_lines))

    append_jsonl(
        LOG_PATH,
        {
            "run_id": payload["run_id"],
            "generated_at": payload["generated_at"],
            "mission_id": payload["mission_id"],
            "execution_result": payload["execution_result"]["verdict"],
            "completion_verdict": payload["completion_verdict"],
            "blocking_factors": payload["blocking_factors"],
        },
    )


def execute_mode(args: argparse.Namespace) -> int:
    run_id = f"mission-wave3-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    registry_payload, index, class_map, class_order = load_registry()
    mission_id, policy, route_basis = route(args.request or "", index, class_map, class_order, args.mission_id or "", args.mission_class or "")

    mode_payload = build_mode_payload(intent=args.intent)
    one_screen = load_one_screen()
    git_before = git_state()
    context = {
        "request_text": args.request or mission_id,
        "intent": args.intent,
        "task_id": args.task_id or "",
        "node_id": args.node_id or "",
        "policy_topic": args.policy_topic or "",
        "delivery_target": args.delivery_target or "",
        "package_path": args.package_path or "",
        "inbox_mode": args.inbox_mode or "",
        "dry_run": bool(args.dry_run),
    }
    authority_check, policy_check, preconditions, gate_blockers = gate(policy, mode_payload, one_screen, git_before, context, args.resume_from_program)

    req_norm = " ".join((args.request or "").lower().split())
    if route_basis.startswith("fallback") and any(token in req_norm for token in RISKY_TOKENS):
        gate_blockers.append("risky_request_not_mapped_to_guarded_mission")

    mutability = str(policy.get("mutability_level", "READ_ONLY")).upper()
    allow_mutation = bool(args.allow_mutation and not args.dry_run and mutability in {"GUARDED_STATE_CHANGE", "CREATOR_ONLY_MUTATION", "OPERATIONAL_ROUTING"})

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
            result, artifacts, blockers = execute_program_step(run_id, mission_id, step, context, allow_mutation)
            program_results.append(result)
            program_artifacts.extend([x for x in artifacts if str(x).strip()])
            if result["success"]:
                completed.append(current_program)
                continue
            program_blockers.extend(blockers)
            failed_program = current_program
            failed_idx = idx + 1
            stop_now, reason = should_stop(result["actual_verdict"], policy.get("stop_conditions", []), str(policy.get("failure_policy", "stop_on_failure")))
            if stop_now:
                stop_triggered = True
                stop_reason = reason
                break

    if gate_blockers:
        verdict, summary, exit_code = "BLOCKED", "blocked by authority/policy/preconditions", 2
    elif failed_program:
        blocked_seen = any(x.get("actual_verdict", "").upper() == "BLOCKED" for x in program_results)
        verdict = "BLOCKED" if blocked_seen else "FAILED"
        summary = f"{verdict.lower()} at program {failed_program}"
        exit_code = 2 if verdict == "BLOCKED" else 1
    else:
        verdict, summary, exit_code = "SUCCESS", "mission completed successfully", 0

    total = len(policy.get("program_plan", []))
    pending = [str(x.get("program_id", "")).strip() for x in policy.get("program_plan", [])[len(completed):] if str(x.get("program_id", "")).strip()]
    checkpoint = {
        "total_programs": total,
        "start_program": args.resume_from_program,
        "completed_programs": completed,
        "pending_programs": pending,
        "current_program": current_program if failed_program else "",
        "failed_program": failed_program,
        "resume_pointer": (failed_idx + 1 if failed_program else total + 1),
        "resume_supported": bool(policy.get("resume_supported", True)),
        "can_resume": bool(failed_program and failed_idx < total and policy.get("resume_supported", True)),
        "stop_triggered": stop_triggered,
        "stop_reason": stop_reason,
    }
    completion_rule = str(policy.get("completion_rule", "certify_on_success"))
    if gate_blockers:
        completion_verdict = "BLOCKED"
    elif verdict == "SUCCESS" and completion_rule.startswith("certify_on_"):
        completion_verdict = "CERTIFIED"
    elif verdict == "SUCCESS":
        completion_verdict = "SUCCESS"
    elif completion_rule == "certify_on_expected_blocks" and program_results and all(x.get("success", False) for x in program_results):
        completion_verdict = "CERTIFIED"
    elif verdict == "BLOCKED":
        completion_verdict = "BLOCKED"
    else:
        completion_verdict = "PARTIAL"

    all_blockers = sorted(set(gate_blockers + program_blockers))
    next_step = "Mission certified. Use runtime mission artifacts as evidence."
    if verdict != "SUCCESS":
        if any("creator authority required" in x.lower() for x in all_blockers):
            next_step = "Enable creator authority and rerun creator-bound mission."
        elif checkpoint["can_resume"]:
            next_step = f"Resume mission with --mission-id {mission_id} --resume-from-program {checkpoint['resume_pointer']}."
        elif mutability in {"GUARDED_STATE_CHANGE", "CREATOR_ONLY_MUTATION"} and bool(policy.get("rollback_supported", False)):
            next_step = "Run rollback workflow per INCIDENT_AND_ROLLBACK_POLICY before rerun."
        else:
            next_step = "Inspect blockers and rerun mission."

    git_after = git_state()
    changed_files = sorted(set(git_before["status_files"]).symmetric_difference(set(git_after["status_files"])))
    rollback_required = bool(policy.get("rollback_supported", False) and verdict in {"FAILED", "BLOCKED"} and mutability in {"GUARDED_STATE_CHANGE", "CREATOR_ONLY_MUTATION"})
    artifacts = sorted(
        set(
            program_artifacts
            + list(policy.get("evidence_outputs", []))
            + [rel(STATUS_PATH), rel(REPORT_PATH), rel(CHECKPOINT_PATH), rel(HISTORY_PATH), rel(AUDIT_PATH)]
        )
    )

    payload = {
        "schema_version": EXEC_SCHEMA,
        "run_id": run_id,
        "generated_at": utc_now(),
        "registry_schema_version": registry_payload.get("schema_version", "unknown"),
        "mission_class": policy.get("mission_class", ""),
        "mission_id": mission_id,
        "task_id_or_program_id": mission_id,
        "request_text": context.get("request_text") or mission_id,
        "resolved_goal": policy.get("resolved_goal", ""),
        "mission_scope": policy.get("mission_scope", ""),
        "non_goals": policy.get("non_goals", []),
        "authority_check": authority_check,
        "policy_check": policy_check,
        "preconditions": preconditions,
        "program_plan": policy.get("program_plan", []),
        "current_program": current_program,
        "mission_checkpoint_state": checkpoint,
        "execution_result": {"verdict": verdict, "summary": summary, "exit_code": exit_code},
        "artifacts_produced": artifacts,
        "state_change": {
            "mutability_level": mutability,
            "execution_mode": (
                "live_mutation"
                if allow_mutation
                else ("read_only" if mutability == "READ_ONLY" else "dry_run")
            ),
            "state_change_detected": bool(changed_files),
            "changed_files": changed_files,
        },
        "blocking_factors": all_blockers,
        "acceptance_criteria": policy.get("acceptance_criteria", []),
        "completion_verdict": completion_verdict,
        "next_step": next_step,
        "evidence_source": sorted(
            set(
                [
                    "workspace_config/operator_mission_registry.json",
                    "docs/governance/OPERATOR_MISSION_CONTRACT.md",
                    "workspace_config/operator_task_program_registry.json",
                ]
                + [str(x) for x in policy.get("policy_basis", [])]
                + [
                    str(x.get("output_artifact", "")).strip()
                    for x in program_results
                    if str(x.get("output_artifact", "")).strip()
                ]
            )
        ),
        "mission_priority": policy.get("mission_priority", "normal"),
        "resume_supported": bool(policy.get("resume_supported", True)),
        "rollback_supported": bool(policy.get("rollback_supported", False)),
        "rollback_required": rollback_required,
        "escalation_requirement": bool(policy.get("escalation_requirement", False)),
        "mutability_level": mutability,
        "dependency_set": policy.get("dependency_set", []),
        "stop_conditions": policy.get("stop_conditions", []),
        "failure_policy": policy.get("failure_policy", "stop_on_failure"),
        "operator_confirmation_required": bool(policy.get("operator_confirmation_required", False)),
        "route_basis": route_basis,
        "program_results": program_results,
        "notes": [f"class_order={','.join(class_order)}"],
    }
    write_runtime(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


def classify_mode(args: argparse.Namespace) -> int:
    _, index, class_map, class_order = load_registry()
    mission_id, policy, route_basis = route(
        args.request,
        index,
        class_map,
        class_order,
        args.mission_id or "",
        args.mission_class or "",
    )
    out = {
        "schema_version": EXEC_SCHEMA,
        "generated_at": utc_now(),
        "request_text": args.request,
        "route_basis": route_basis,
        "mission_class": policy.get("mission_class", ""),
        "mission_id": mission_id,
        "resolved_goal": policy.get("resolved_goal", ""),
        "mission_scope": policy.get("mission_scope", ""),
        "non_goals": policy.get("non_goals", []),
        "mutability_level": policy.get("mutability_level", "READ_ONLY"),
        "creator_authority_required": bool(policy.get("creator_authority_required", False)),
        "allowed_modes": policy.get("allowed_modes", []),
        "program_plan": [str(x.get("program_id", "")).strip() for x in policy.get("program_plan", [])],
        "acceptance_criteria": policy.get("acceptance_criteria", []),
        "completion_rule": policy.get("completion_rule", "certify_on_success"),
        "failure_policy": policy.get("failure_policy", "stop_on_failure"),
        "resume_supported": bool(policy.get("resume_supported", True)),
        "rollback_supported": bool(policy.get("rollback_supported", False)),
        "policy_basis": policy.get("policy_basis", []),
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
        "mission_classes": [
            {"mission_class": mission_class, "mission_ids": class_map[mission_class]}
            for mission_class in sorted(class_map.keys())
        ],
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
                    "schema_version": "operator_mission_status.wave3.v1.0.0",
                    "generated_at": utc_now(),
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

    total = len(items)
    passed = 0
    failures: list[dict[str, Any]] = []
    for idx, item in enumerate(items, start=1):
        raw_request = str(item.get("raw_request", "")).strip()
        expected_class = str(item.get("mission_class", "")).strip()
        expected_id = str(item.get("expected_mission_id", "")).strip()
        expected_plan = [str(x).strip() for x in item.get("expected_program_plan", []) if str(x).strip()]
        expected_mutability = str(item.get("mutability_level", "")).strip().upper()
        authority_expectation = str(item.get("authority_expectation", "")).strip().lower()
        item_id = str(item.get("id", "")).strip() or f"item-{idx}"

        actual_id, policy, route_basis = route(raw_request, index, class_map, class_order, "", "")
        actual_plan = [str(x.get("program_id", "")).strip() for x in policy.get("program_plan", []) if str(x.get("program_id", "")).strip()]
        actual_class = str(policy.get("mission_class", "")).strip()

        reasons: list[str] = []
        if actual_class != expected_class:
            reasons.append("mission_class_mismatch")
        if actual_id != expected_id:
            reasons.append("mission_id_mismatch")
        if expected_plan and actual_plan != expected_plan:
            reasons.append("program_plan_mismatch")
        if expected_mutability and str(policy.get("mutability_level", "")).upper() != expected_mutability:
            reasons.append("mutability_level_mismatch")
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
                    "actual_mission_class": actual_class,
                    "expected_mission_id": expected_id,
                    "actual_mission_id": actual_id,
                    "expected_program_plan": expected_plan,
                    "actual_program_plan": actual_plan,
                    "expected_mutability_level": expected_mutability,
                    "actual_mutability_level": str(policy.get("mutability_level", "")),
                    "expected_authority_expectation": authority_expectation,
                    "actual_creator_authority_required": bool(policy.get("creator_authority_required", False)),
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
        "verdict": "PASS" if total == passed else "FAIL",
        "failures": failures,
    }
    write_json(CONSISTENCY_PATH, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Operator mission execution surface (Wave 3A/3B/3C + final baseline).")
    sub = p.add_subparsers(dest="mode", required=True)

    ex = sub.add_parser("execute")
    ex.add_argument("--request", default="")
    ex.add_argument("--mission-id", default="")
    ex.add_argument("--mission-class", default="")
    ex.add_argument("--task-id", default="")
    ex.add_argument("--node-id", default="")
    ex.add_argument("--policy-topic", default="")
    ex.add_argument("--delivery-target", default="")
    ex.add_argument("--package-path", default="")
    ex.add_argument("--inbox-mode", default="")
    ex.add_argument("--resume-from-program", type=int, default=1)
    ex.add_argument("--intent", choices=["auto", "creator", "helper", "integration"], default="auto")
    ex.add_argument("--allow-mutation", action="store_true")
    ex.add_argument("--dry-run", action="store_true")

    cl = sub.add_parser("classify")
    cl.add_argument("--request", required=True)
    cl.add_argument("--mission-id", default="")
    cl.add_argument("--mission-class", default="")

    sub.add_parser("registry")
    sub.add_parser("status")

    cc = sub.add_parser("consistency-check")
    cc.add_argument("--golden-file", default=str(GOLDEN_FINAL.relative_to(ROOT)))
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
