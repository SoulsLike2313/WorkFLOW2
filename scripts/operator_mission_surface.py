
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
GOLDEN_3A = ROOT / "docs" / "review_artifacts" / "OPERATOR_MISSION_GOLDEN_PACK_WAVE_3A.json"

RUNTIME_DIR = ROOT / "runtime" / "repo_control_center"
OUTPUTS_DIR = RUNTIME_DIR / "operator_mission_outputs"
STATUS_PATH = RUNTIME_DIR / "operator_mission_status.json"
REPORT_PATH = RUNTIME_DIR / "operator_mission_report.md"
CHECKPOINT_PATH = RUNTIME_DIR / "operator_mission_checkpoint.json"
LOG_PATH = RUNTIME_DIR / "operator_mission_log.jsonl"
CONSISTENCY_PATH = RUNTIME_DIR / "operator_mission_consistency.json"

EXEC_SCHEMA = "operator_mission_contract.wave3a.v1.0.0"
CONSISTENCY_SCHEMA = "operator_mission_consistency.wave3a.v1.0.0"
MUTABILITY_LEVELS = {"READ_ONLY", "REFRESH_ONLY", "PACKAGE_ONLY", "CERTIFICATION_ONLY"}
DEFAULT_CLASS_ORDER = (
    "certification_mission",
    "readiness_mission",
    "review_prep_mission",
    "status_consolidation_mission",
)


def now_utc() -> str:
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
            "mission_class": mission_class,
            "allowed_modes": cls.get("allowed_modes", []),
            "authority_requirement": cls.get("authority_requirement", "none"),
            "requires_in_sync": bool(cls.get("requires_in_sync", False)),
            "requires_clean_worktree": bool(cls.get("requires_clean_worktree", False)),
            "policy_basis": cls.get("policy_basis", []),
            "non_goals": cls.get("non_goals", []),
            "acceptance_criteria": cls.get("acceptance_criteria", []),
            "mutability_level": str(cls.get("mutability_level", "READ_ONLY")).upper(),
            "resume_supported": bool(cls.get("resume_supported", True)),
            "mission_priority": cls.get("mission_priority", "normal"),
            "evidence_outputs": cls.get("evidence_outputs", []),
        }
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
            merged["creator_authority_required"] = str(merged.get("authority_requirement", "none")) == "creator_required"
            if merged["mutability_level"] not in MUTABILITY_LEVELS:
                raise RuntimeError(f"unsupported mutability for {mission_id}: {merged['mutability_level']}")
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


def gate(
    policy: dict[str, Any],
    mode_payload: dict[str, Any],
    one_screen: dict[str, Any],
    git_before: dict[str, Any],
    resume_from_program: int,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[str]]:
    machine_mode = str(mode_payload.get("machine_mode", "unknown"))
    authority_present = bool(mode_payload.get("authority", {}).get("authority_present", False))
    blockers: list[str] = []
    if policy.get("allowed_modes") and machine_mode not in policy["allowed_modes"]:
        blockers.append(f"machine_mode '{machine_mode}' not allowed")
    if bool(policy.get("creator_authority_required", False)) and not authority_present:
        blockers.append("creator authority required but not present")

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


def execute_program_step(run_id: str, mission_id: str, step: dict[str, Any], intent: str) -> tuple[dict[str, Any], list[str], list[str]]:
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

def execute_mode(args: argparse.Namespace) -> int:
    run_id = f"mission-wave3a-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    payload_registry, index, class_map, class_order = load_registry()
    mission_id, policy, route_basis = route(args.request or "", index, class_map, class_order, args.mission_id or "", args.mission_class or "")

    mode_payload = build_mode_payload(intent=args.intent)
    one_screen = read_json(ONE_SCREEN_PATH) if ONE_SCREEN_PATH.exists() else {}
    git_before = git_state()
    authority, policy_check, preconditions, gate_blockers = gate(policy, mode_payload, one_screen, git_before, args.resume_from_program)

    program_results: list[dict[str, Any]] = []
    program_artifacts: list[str] = []
    program_blockers: list[str] = []
    completed: list[str] = []
    current_program = ""
    failed_program = ""
    failed_idx = 0

    if not gate_blockers:
        for idx in range(args.resume_from_program - 1, len(policy.get("program_plan", []))):
            step = policy["program_plan"][idx]
            current_program = str(step.get("program_id", "")).strip()
            result, artifacts, blockers = execute_program_step(run_id, mission_id, step, args.intent)
            program_results.append(result)
            program_artifacts.extend(artifacts)
            if result["success"]:
                completed.append(current_program)
                continue
            program_blockers.extend(blockers)
            failed_program = current_program
            failed_idx = idx + 1
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
        "can_resume": bool(failed_program and failed_idx < total and policy.get("resume_supported", True)),
    }

    completion_verdict = "BLOCKED" if gate_blockers else (
        "CERTIFIED"
        if verdict == "SUCCESS" and str(policy.get("completion_rule", "certify_on_success")).startswith("certify_on_")
        else ("SUCCESS" if verdict == "SUCCESS" else ("BLOCKED" if verdict == "BLOCKED" else "PARTIAL"))
    )

    blockers = sorted(set(gate_blockers + program_blockers))
    next_step = "Mission certified. Use mission runtime artifacts as evidence."
    if verdict != "SUCCESS":
        if any("creator authority required" in x.lower() for x in blockers):
            next_step = "Enable creator authority and rerun creator-bound mission."
        elif checkpoint["can_resume"]:
            next_step = f"Resume mission with --mission-id {mission_id} --resume-from-program {checkpoint['resume_pointer']}."
        else:
            next_step = "Inspect blockers and rerun mission."

    git_after = git_state()
    state_changed = git_before["head"] != git_after["head"] or git_before["worktree_clean"] != git_after["worktree_clean"]
    artifacts = sorted(
        set(
            program_artifacts
            + list(policy.get("evidence_outputs", []))
            + [rel(STATUS_PATH), rel(REPORT_PATH), rel(CHECKPOINT_PATH)]
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
        "current_program": current_program,
        "mission_checkpoint_state": checkpoint,
        "execution_result": {"verdict": verdict, "summary": summary, "exit_code": exit_code},
        "artifacts_produced": artifacts,
        "state_change": {
            "mutability_level": str(policy.get("mutability_level", "READ_ONLY")).upper(),
            "execution_mode": "safe_program_execution",
            "state_change_detected": state_changed,
        },
        "blocking_factors": blockers,
        "acceptance_criteria": policy.get("acceptance_criteria", []),
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
        "resume_supported": bool(policy.get("resume_supported", True)),
        "mission_priority": policy.get("mission_priority", "normal"),
        "program_results": program_results,
        "route_basis": route_basis,
        "notes": [f"class_order={','.join(class_order)}", "wave=3A_safe_only"],
    }

    write_json(
        STATUS_PATH,
        {
            "schema_version": "operator_mission_status.wave3a.v1.0.0",
            "generated_at": payload["generated_at"],
            "run_id": run_id,
            "mission_class": payload["mission_class"],
            "mission_id": mission_id,
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

    report_lines = [
        "# Operator Mission Report (Wave 3A)",
        "",
        f"- run_id: `{run_id}`",
        f"- mission_class: `{payload['mission_class']}`",
        f"- mission_id: `{mission_id}`",
        f"- execution_verdict: `{verdict}`",
        f"- completion_verdict: `{completion_verdict}`",
        f"- current_program: `{current_program}`",
        "",
        "## Completed Mission Checkpoints",
    ]
    report_lines.extend([f"- `{x}`" for x in completed] or ["- none"])
    report_lines.extend(["", "## Blocking Factors"])
    report_lines.extend([f"- {x}" for x in blockers] or ["- none"])
    report_lines.extend(["", "## Artifacts Produced"])
    report_lines.extend([f"- `{x}`" for x in artifacts] or ["- none"])
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
        "allowed_modes": policy.get("allowed_modes", []),
        "program_plan": [str(x.get("program_id", "")).strip() for x in policy.get("program_plan", [])],
        "acceptance_criteria": policy.get("acceptance_criteria", []),
        "completion_rule": policy.get("completion_rule", "certify_on_success"),
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
            {"mission_class": k, "mission_ids": class_map[k]} for k in sorted(class_map.keys())
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
                    "schema_version": "operator_mission_status.wave3a.v1.0.0",
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
        expected_plan = [
            str(x).strip() for x in item.get("expected_program_plan", []) if str(x).strip()
        ]
        expected_mutability = str(item.get("mutability_level", "")).strip().upper()
        authority_expectation = str(item.get("authority_expectation", "")).strip().lower()
        item_id = str(item.get("id", "")).strip() or f"item-{idx}"

        actual_id, policy, route_basis = route(raw_request, index, class_map, class_order, "", "")
        actual_plan = [
            str(x.get("program_id", "")).strip()
            for x in policy.get("program_plan", [])
            if str(x.get("program_id", "")).strip()
        ]

        reasons: list[str] = []
        if policy.get("mission_class") != expected_class:
            reasons.append("mission_class_mismatch")
        if expected_id and actual_id != expected_id:
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
    p = argparse.ArgumentParser(
        description="Operator mission execution surface (Wave 3A safe mission foundation)."
    )
    sub = p.add_subparsers(dest="mode", required=True)

    ex = sub.add_parser("execute")
    ex.add_argument("--request", default="")
    ex.add_argument("--mission-id", default="")
    ex.add_argument("--mission-class", default="")
    ex.add_argument("--resume-from-program", type=int, default=1)
    ex.add_argument("--intent", choices=["auto", "creator", "helper", "integration"], default="auto")

    cl = sub.add_parser("classify")
    cl.add_argument("--request", required=True)
    cl.add_argument("--mission-id", default="")
    cl.add_argument("--mission-class", default="")

    sub.add_parser("registry")
    sub.add_parser("status")

    cc = sub.add_parser("consistency-check")
    cc.add_argument("--golden-file", default=str(GOLDEN_3A.relative_to(ROOT)))
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
