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
REGISTRY = ROOT / "workspace_config" / "operator_task_program_registry.json"
GOLDEN = ROOT / "docs" / "review_artifacts" / "OPERATOR_TASK_PROGRAM_GOLDEN_PACK_WAVE_2A.json"
RUNTIME = ROOT / "runtime" / "repo_control_center"
OUT_DIR = RUNTIME / "operator_program_outputs"
STATUS_PATH = RUNTIME / "operator_program_status.json"
REPORT_PATH = RUNTIME / "operator_program_report.md"
CHECKPOINT_PATH = RUNTIME / "operator_program_checkpoint.json"
CONSISTENCY_PATH = RUNTIME / "operator_task_program_consistency.json"
LOG_PATH = RUNTIME / "operator_program_log.jsonl"
ONE_SCREEN = RUNTIME / "one_screen_status.json"
CMD_SCRIPT = ROOT / "scripts" / "operator_command_surface.py"

EXEC_SCHEMA = "operator_task_program_contract.wave2a.v1.0.0"
STATUS_SCHEMA = "operator_task_program_status.wave2a.v1.0.0"
CONSISTENCY_SCHEMA = "operator_task_program_consistency.wave2a.v1.0.0"
CLASS_ORDER = ("validation_program", "evidence_pack_program", "report_program", "status_refresh_program")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run(cmd: list[str], allow_fail: bool = False) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
    if p.returncode != 0 and not allow_fail:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip() or f"failed: {' '.join(cmd)}")
    return p


def parse_json(raw: str) -> dict[str, Any] | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except Exception:
        return None
    return data if isinstance(data, dict) else {"value": data}


def git_state() -> dict[str, Any]:
    st = run(["git", "status", "--porcelain"], allow_fail=True).stdout
    files = []
    for line in st.splitlines():
        if len(line) >= 4:
            files.append(line[3:].strip().replace("\\", "/"))
    return {"head": run(["git", "rev-parse", "HEAD"], allow_fail=True).stdout.strip(), "worktree_clean": not files, "status_files": sorted(set(files))}


def load_registry() -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, list[str]]]:
    payload = read_json(REGISTRY)
    index: dict[str, dict[str, Any]] = {}
    class_map: dict[str, list[str]] = {}
    for cls in payload.get("program_classes", []):
        c = str(cls.get("program_class", "")).strip()
        if not c:
            continue
        class_map.setdefault(c, [])
        for p in cls.get("programs", []):
            pid = str(p.get("program_id", "")).strip()
            if not pid:
                continue
            merged = {
                "program_class": c,
                "description": str(cls.get("description", "")).strip(),
                "allowed_modes": p.get("allowed_modes", cls.get("allowed_modes", [])),
                "authority_requirement": p.get("authority_requirement", cls.get("authority_requirement", "none")),
                "policy_basis": p.get("policy_basis", cls.get("policy_basis", [])),
                "mutability_level": p.get("mutability_level", cls.get("mutability_level", "READ_ONLY")),
                "resume_supported": bool(p.get("resume_supported", cls.get("resume_supported", True))),
                "failure_policy": str(p.get("failure_policy", "stop_on_failure")),
                "requires_in_sync": bool(p.get("requires_in_sync", False)),
                "requires_clean_worktree": bool(p.get("requires_clean_worktree", False)),
                "blocking_conditions": p.get("blocking_conditions", cls.get("blocking_conditions", [])),
                "command_dependencies": p.get("command_dependencies", cls.get("command_dependencies", [])),
                "evidence_outputs": p.get("evidence_outputs", cls.get("evidence_outputs", [])),
                "resolved_goal": p.get("resolved_goal", f"Execute {pid}"),
                "execution_scope": p.get("execution_scope", c),
                "route_tokens": [str(x).lower().strip() for x in p.get("route_tokens", []) if str(x).strip()],
                "step_plan": p.get("step_plan", []),
            }
            index[pid] = merged
            class_map[c].append(pid)
    for c in class_map:
        class_map[c].sort()
    if not index:
        raise RuntimeError("empty operator_task_program_registry")
    return payload, index, class_map


def route(request: str, index: dict[str, dict[str, Any]], class_map: dict[str, list[str]], program_id: str, program_class: str) -> tuple[str, dict[str, Any], str]:
    if program_id.strip():
        key = program_id.strip()
        if key not in index:
            raise RuntimeError(f"unknown program-id: {key}")
        return key, index[key], "explicit_program_id_override"
    if program_class.strip():
        c = program_class.strip()
        if c not in class_map or not class_map[c]:
            raise RuntimeError(f"unknown program-class: {c}")
        key = class_map[c][0]
        return key, index[key], "explicit_program_class_override"
    if request.strip() in index:
        key = request.strip()
        return key, index[key], "direct_program_id_match"
    norm = f" {' '.join(request.lower().split())} "
    for c in CLASS_ORDER:
        for pid in class_map.get(c, []):
            for token in index[pid].get("route_tokens", []):
                if token and token in norm:
                    return pid, index[pid], "token_match"
    fallback = "program.wave2a.status_refresh_surface.v1"
    key = fallback if fallback in index else sorted(index.keys())[0]
    return key, index[key], "fallback_status_refresh"


def merge_step_args(step: dict[str, Any], ctx: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    merged: dict[str, Any] = {str(k): v for k, v in (step.get("static_args", {}) or {}).items()}
    missing: list[str] = []
    for name in step.get("pass_args", []) or []:
        k = str(name).strip()
        if not k:
            continue
        v = ctx.get(k)
        if (v is None or (isinstance(v, str) and not v.strip())) and k not in merged:
            missing.append(k)
        elif v is not None and not (isinstance(v, str) and not v.strip()):
            merged[k] = v
    return merged, missing


def execute_step(run_id: str, pid: str, step: dict[str, Any], ctx: dict[str, Any], allow_mutation: bool) -> tuple[dict[str, Any], list[str]]:
    sid = str(step.get("step_id", "STEP")).strip()
    merged, missing = merge_step_args(step, ctx)
    if missing:
        return {
            "step_id": sid, "step_type": "command_execute", "execution_result": "BLOCKED", "summary": f"missing step inputs: {', '.join(missing)}",
            "exit_code": 2, "blocking_factors": [f"missing_step_input={x}" for x in missing], "command": [], "resolved_action": str(step.get("action", "")),
            "output_artifact": "", "artifacts_produced": []
        }, [f"step {sid}: missing step inputs {', '.join(missing)}"]
    action = str(step.get("action", "")).strip()
    if not action:
        return {
            "step_id": sid, "step_type": "command_execute", "execution_result": "FAILED", "summary": "missing step action",
            "exit_code": 1, "blocking_factors": ["missing_step_action"], "command": [], "resolved_action": "unknown", "output_artifact": "", "artifacts_produced": []
        }, [f"step {sid}: missing step action"]
    cmd = [sys.executable, str(CMD_SCRIPT), "execute", "--command", str(step.get("command", action)), "--action", action, "--command-id", f"{pid}:{sid}:{run_id}"]
    cmd.append("--allow-mutation" if allow_mutation else "--dry-run")
    for k, v in merged.items():
        flag = "--" + str(k).replace("_", "-")
        if isinstance(v, bool):
            if v:
                cmd.append(flag)
        elif isinstance(v, list):
            for item in v:
                txt = str(item).strip()
                if txt:
                    cmd.extend([flag, txt])
        else:
            txt = str(v).strip()
            if txt:
                cmd.extend([flag, txt])
    cp = run(cmd, allow_fail=True)
    parsed = parse_json(cp.stdout)
    out = OUT_DIR / run_id / f"{sid}_output.json"
    write_json(out, {"run_id": run_id, "step_id": sid, "command": cmd, "returncode": cp.returncode, "stdout": cp.stdout, "stderr": cp.stderr, "stdout_json": parsed, "generated_at": utc_now()})
    artifacts = [rel(out)]
    blockers: list[str] = []
    verdict = "SUCCESS"
    summary = f"command step return code {cp.returncode}"
    exit_code = cp.returncode
    if parsed:
        res = parsed.get("execution_result", {})
        v = str(res.get("verdict", "")).upper()
        if v in {"SUCCESS", "FAILED", "BLOCKED"}:
            verdict = v
        if str(res.get("summary", "")).strip():
            summary = str(res.get("summary", "")).strip()
        if isinstance(res.get("exit_code"), int):
            exit_code = int(res["exit_code"])
        artifacts += [str(x).strip() for x in parsed.get("artifacts_produced", []) or [] if str(x).strip()]
        blockers += [str(x).strip() for x in parsed.get("blocking_factors", []) or [] if str(x).strip()]
    if cp.returncode != 0 and verdict == "SUCCESS":
        verdict = "FAILED"
    if cp.returncode != 0 and not blockers:
        blockers.append(f"command_return_code={cp.returncode}")
    return {
        "step_id": sid, "step_type": "command_execute", "execution_result": verdict, "summary": summary, "exit_code": exit_code,
        "command": cmd, "resolved_action": action, "output_artifact": rel(out), "artifacts_produced": sorted(set(artifacts)), "blocking_factors": blockers
    }, [f"step {sid}: {x}" for x in blockers]


def write_runtime(payload: dict[str, Any]) -> None:
    status = {
        "schema_version": STATUS_SCHEMA,
        "generated_at": payload.get("generated_at", utc_now()),
        "active_or_last_program": payload.get("task_id_or_program_id", ""),
        "program_class": payload.get("program_class", ""),
        "execution_result": payload.get("execution_result", {}),
        "current_step": payload.get("current_step", ""),
        "checkpoint_state": payload.get("checkpoint_state", {}),
        "completed_steps": payload.get("checkpoint_state", {}).get("completed_steps", []),
        "artifacts_produced": payload.get("artifacts_produced", []),
        "blocking_factors": payload.get("blocking_factors", []),
        "next_step": payload.get("next_step", ""),
    }
    write_json(STATUS_PATH, status)
    write_json(CHECKPOINT_PATH, payload.get("checkpoint_state", {}))
    lines = ["# OPERATOR PROGRAM REPORT", "", "## Runtime Identity", f"- run_id: `{payload.get('run_id', '')}`", f"- program: `{payload.get('task_id_or_program_id', '')}`", f"- class: `{payload.get('program_class', '')}`", "", "## Result", f"- verdict: `{payload.get('execution_result', {}).get('verdict', '')}`", f"- summary: `{payload.get('execution_result', {}).get('summary', '')}`", "", "## Checkpoint", f"- current_step: `{payload.get('current_step', '')}`", f"- completed_steps: `{len(payload.get('checkpoint_state', {}).get('completed_steps', []))}`", f"- failed_step: `{payload.get('checkpoint_state', {}).get('failed_step', '')}`", f"- can_resume: `{payload.get('checkpoint_state', {}).get('can_resume', False)}`", "", "## Blocking Factors"]
    lines += [f"- `{x}`" for x in payload.get("blocking_factors", [])] or ["- none"]
    lines += ["", "## Artifacts Produced"]
    lines += [f"- `{x}`" for x in payload.get("artifacts_produced", [])] or ["- none"]
    lines += ["", "## Next Step", f"- {payload.get('next_step', '')}"]
    write_md(REPORT_PATH, "\n".join(lines))
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def execute_mode(args: argparse.Namespace) -> int:
    registry, index, class_map = load_registry()
    run_id = f"program-wave2a-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    mode = build_mode_payload(intent=args.intent)
    one = read_json(ONE_SCREEN) if ONE_SCREEN.exists() else {}
    git_before = git_state()
    pid, policy, route_basis = route(args.request or "", index, class_map, args.program_id or "", args.program_class or "")
    authority = mode.get("authority", {})
    machine_mode = str(mode.get("machine_mode", "unknown"))
    authority_present = bool(authority.get("authority_present", False))
    authority_blockers = []
    if policy["allowed_modes"] and machine_mode not in policy["allowed_modes"]:
        authority_blockers.append(f"machine_mode '{machine_mode}' not allowed for '{pid}'")
    if policy["authority_requirement"] == "creator_required" and not authority_present:
        authority_blockers.append("creator authority required but not present")
    missing_policy = [p for p in policy["policy_basis"] if not (ROOT / p).exists()]
    pre_failed = []
    if str(ROOT).lower() != CANONICAL_ROOT.lower():
        pre_failed.append("repo_root_is_canonical")
    if policy["requires_in_sync"] and str(one.get("sync_verdict", "UNKNOWN")) != "IN_SYNC":
        pre_failed.append("sync_in_sync")
    if policy["requires_clean_worktree"] and not git_before["worktree_clean"]:
        pre_failed.append("worktree_clean")
    if args.resume_from_step < 1 or args.resume_from_step > max(len(policy["step_plan"]), 1):
        pre_failed.append("resume_step_in_range")
    if args.resume_from_step > 1 and not policy["resume_supported"]:
        pre_failed.append("resume_supported")
    gate_blockers = authority_blockers + [f"missing policy file: {x}" for x in missing_policy] + [f"failed precondition: {x}" for x in pre_failed]
    context = {"task_id": args.task_id or "", "policy_topic": args.policy_topic or "", "output_dir": args.output_dir or "", "request_text": args.request or "", "program_id": pid}
    step_results, step_blockers, step_artifacts, completed, current, failed, failed_idx = [], [], [], [], "", "", 0
    if not gate_blockers:
        allow_mut = bool(args.allow_mutation and not args.dry_run and policy["mutability_level"] != "READ_ONLY")
        for i in range(args.resume_from_step - 1, len(policy["step_plan"])):
            step = policy["step_plan"][i]
            current = str(step.get("step_id", f"S{i+1}")).strip()
            if str(step.get("step_type", "command_execute")) != "command_execute":
                res = {"step_id": current, "step_type": str(step.get("step_type", "")), "execution_result": "FAILED", "summary": "unsupported step_type in Wave 2A", "exit_code": 1, "command": [], "resolved_action": "unsupported", "output_artifact": "", "artifacts_produced": [], "blocking_factors": ["unsupported_step_type"]}
                blk = [f"step {current}: unsupported step_type"]
            else:
                res, blk = execute_step(run_id, pid, step, context, allow_mut)
            step_results.append(res)
            step_artifacts += [x for x in res.get("artifacts_produced", []) if str(x).strip()]
            if str(res.get("execution_result", "")).upper() == "SUCCESS":
                completed.append(current)
                continue
            step_blockers += blk
            failed = current
            failed_idx = i + 1
            if str(policy.get("failure_policy", "stop_on_failure")) == "stop_on_failure":
                break
    verdict = "BLOCKED" if gate_blockers else ("SUCCESS" if not failed else ("BLOCKED" if any(str(x.get("execution_result", "")).upper() == "BLOCKED" for x in step_results) else "FAILED"))
    summary = "blocked by authority/policy/preconditions" if gate_blockers else ("program completed successfully" if verdict == "SUCCESS" else f"{verdict.lower()} at step {failed}")
    exit_code = 2 if verdict == "BLOCKED" else (0 if verdict == "SUCCESS" else 1)
    total_steps = len(policy["step_plan"])
    resume_ptr = (failed_idx + 1) if failed else (total_steps + 1)
    checkpoint = {"total_steps": total_steps, "start_step": args.resume_from_step, "completed_steps": completed, "current_step": current, "failed_step": failed, "resume_pointer": resume_ptr, "resume_supported": policy["resume_supported"], "can_resume": bool(failed and policy["resume_supported"] and resume_ptr <= total_steps), "failure_policy": policy["failure_policy"]}
    next_step = "Run python scripts/repo_control_center.py full-check." if verdict == "SUCCESS" else ("Enable creator authority and rerun creator program." if any("creator authority required" in x.lower() for x in gate_blockers + step_blockers) else (f"Resume with --resume-from-step {resume_ptr}." if checkpoint["can_resume"] else "Inspect step outputs and clear blockers."))
    git_after = git_state()
    changed = sorted(set(git_before["status_files"]).symmetric_difference(set(git_after["status_files"])))
    payload = {
        "schema_version": EXEC_SCHEMA, "run_id": run_id, "generated_at": utc_now(), "registry_schema_version": registry.get("schema_version", "unknown"),
        "program_class": policy["program_class"], "task_id_or_program_id": pid, "request_text": context["request_text"] or pid,
        "resolved_goal": policy["resolved_goal"], "execution_scope": policy["execution_scope"],
        "authority_check": {"required_modes": policy["allowed_modes"], "authority_requirement": policy["authority_requirement"], "machine_mode": machine_mode, "authority_present": authority_present, "detection_state": authority.get("detection_state", "unknown"), "verdict": "PASS" if not authority_blockers else "BLOCKED", "details": authority_blockers or ["authority contract satisfied"]},
        "policy_check": {"policy_basis": policy["policy_basis"], "missing_policy_files": missing_policy, "verdict": "PASS" if not missing_policy else "BLOCKED"},
        "preconditions": {"failed": pre_failed, "verdict": "PASS" if not pre_failed else "BLOCKED"},
        "step_plan": policy["step_plan"], "current_step": current, "checkpoint_state": checkpoint, "execution_result": {"verdict": verdict, "summary": summary, "exit_code": exit_code},
        "artifacts_produced": sorted(set(step_artifacts + list(policy.get("evidence_outputs", [])))), "state_change": {"mutability_level": policy["mutability_level"], "execution_mode": ("live_mutation" if (args.allow_mutation and not args.dry_run and policy["mutability_level"] != "READ_ONLY") else ("read_only" if policy["mutability_level"] == "READ_ONLY" else "dry_run")), "state_change_detected": bool(changed), "changed_files": changed},
        "blocking_factors": sorted(set(gate_blockers + step_blockers)),
        "next_step": next_step,
        "evidence_source": sorted(set(["workspace_config/operator_task_program_registry.json", "docs/governance/OPERATOR_TASK_PROGRAM_CONTRACT.md"] + list(policy["policy_basis"]) + [x.get("output_artifact", "") for x in step_results if str(x.get("output_artifact", "")).strip()])),
        "step_results": step_results, "resume_supported": bool(policy["resume_supported"]), "failure_policy": policy["failure_policy"],
        "notes": [f"route_basis={route_basis}", f"mutability_level={policy['mutability_level']}"]
    }
    write_runtime(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


def classify_mode(args: argparse.Namespace) -> int:
    _, index, class_map = load_registry()
    pid, p, basis = route(args.request, index, class_map, args.program_id or "", args.program_class or "")
    print(json.dumps({"schema_version": EXEC_SCHEMA, "generated_at": utc_now(), "request_text": args.request, "route_basis": basis, "program_class": p["program_class"], "task_id_or_program_id": pid, "resolved_goal": p["resolved_goal"], "execution_scope": p["execution_scope"], "command_dependencies": p["command_dependencies"], "mutability_level": p["mutability_level"]}, ensure_ascii=False, indent=2))
    return 0


def registry_mode() -> int:
    payload, index, class_map = load_registry()
    out = {"schema_version": payload.get("schema_version", "unknown"), "wave": payload.get("wave", "unknown"), "program_count": len(index), "program_classes": [{"program_class": c, "program_ids": class_map[c]} for c in sorted(class_map.keys())]}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def status_mode() -> int:
    if STATUS_PATH.exists():
        print(json.dumps(read_json(STATUS_PATH), ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"schema_version": STATUS_SCHEMA, "generated_at": utc_now(), "status": "NO_PROGRAM_RUN"}, ensure_ascii=False, indent=2))
    return 0


def consistency_mode(args: argparse.Namespace) -> int:
    _, index, class_map = load_registry()
    golden_path = Path(args.golden_file).expanduser()
    if not golden_path.is_absolute():
        golden_path = (ROOT / golden_path).resolve()
    payload = read_json(golden_path)
    items = payload.get("items", [])
    total, passed = len(items), 0
    failures = []
    for item in items:
        raw = str(item.get("raw_request", "")).strip()
        exp_class = str(item.get("program_class", "")).strip()
        exp_pid = str(item.get("expected_program_id", "")).strip()
        item_id = str(item.get("id", "")).strip() or f"item-{len(failures)+1}"
        pid, p, basis = route(raw, index, class_map, "", "")
        if p["program_class"] == exp_class and pid == exp_pid:
            passed += 1
            continue
        failures.append({"id": item_id, "raw_request": raw, "expected_program_class": exp_class, "actual_program_class": p["program_class"], "expected_program_id": exp_pid, "actual_program_id": pid, "route_basis": basis})
    result = {"schema_version": CONSISTENCY_SCHEMA, "generated_at": utc_now(), "golden_pack_path": rel(golden_path), "total": total, "passed": passed, "failed": total - passed, "verdict": "PASS" if passed == total else "FAIL", "failures": failures}
    write_json(CONSISTENCY_PATH, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Wave 2A safe operator task/program surface.")
    sub = p.add_subparsers(dest="mode", required=True)
    ex = sub.add_parser("execute")
    ex.add_argument("--request", default="")
    ex.add_argument("--program-id", default="")
    ex.add_argument("--program-class", default="")
    ex.add_argument("--task-id", default="")
    ex.add_argument("--policy-topic", default="")
    ex.add_argument("--output-dir", default="")
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
    cc.add_argument("--golden-file", default=str(GOLDEN.relative_to(ROOT)))
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
