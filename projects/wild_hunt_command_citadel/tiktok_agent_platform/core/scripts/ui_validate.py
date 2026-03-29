from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_ROOT = PROJECT_ROOT / "runtime" / "ui_validation"
SNAPSHOT_ROOT = PROJECT_ROOT / "runtime" / "ui_snapshots"

REQUIRED_SCREENS = [
    "dashboard",
    "profiles",
    "sessions",
    "content",
    "analytics",
    "ai_studio",
    "audit",
    "updates",
    "settings",
]
REQUIRED_LOADED_STATES = {screen: "loaded_state" for screen in REQUIRED_SCREENS}
REQUIRED_STATES_BY_SCREEN: dict[str, list[str]] = {
    "dashboard": ["initial_state", "loaded_state"],
    "profiles": ["loaded_state", "no_selection_state"],
    "sessions": ["loaded_state", "no_selection_state"],
    "content": ["loaded_state", "no_selection_state"],
    "analytics": ["loaded_state"],
    "ai_studio": ["loaded_state"],
    "audit": ["loaded_state"],
    "updates": ["loaded_state"],
    "settings": ["loaded_state"],
}
CRITICAL_WALKTHROUGH_ACTIONS = [
    "boot_window",
    "switch_page",
    "capture_loaded_state",
    "verify_no_selection_state",
    "capture_empty_state",
    "capture_dense_state",
    "capture_anomaly_state",
]

RELEASE_SHAPE_REQUIRED_STATES = {
    "dashboard:initial_state",
    "dashboard:loaded_state",
    "profiles:no_selection_state",
    "sessions:no_selection_state",
    "content:no_selection_state",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_run_dir(stdout_text: str) -> Path | None:
    for line in stdout_text.splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        path = Path(candidate)
        if not path.is_absolute():
            path = (PROJECT_ROOT / path).resolve()
        if path.exists() and path.is_dir():
            return path
    return None


def _run_command(command: list[str], cwd: Path) -> tuple[int, str, str]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    return completed.returncode, completed.stdout, completed.stderr


def _build_screen_state_index(screenshots: list[dict[str, Any]]) -> dict[str, set[str]]:
    state_index: dict[str, set[str]] = {}
    for shot in screenshots:
        if not isinstance(shot, dict):
            continue
        screen = _safe_str(shot.get("screen_name") or shot.get("page") or "unknown")
        state = _safe_str(shot.get("state_name"))
        if not screen or not state:
            continue
        state_index.setdefault(screen, set()).add(state)
    return state_index


def _build_issue_index(doctor_summary: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, str | None]]:
    index: dict[tuple[str, str, str], dict[str, str | None]] = {}
    for idx, issue in enumerate(_safe_list(doctor_summary.get("issues")), start=1):
        if not isinstance(issue, dict):
            continue
        page = _safe_str(issue.get("page") or "unknown")
        size = _safe_str(issue.get("screen_size") or "unknown")
        scale = _safe_str(issue.get("scale") or "1.0")
        severity = _safe_str(issue.get("severity") or "minor").lower()
        issue_type = _safe_str(issue.get("issue_type") or "unknown_issue")
        issue_ref = f"doctor:{issue_type}:{idx}"
        key = (page, size, scale)
        prev = index.get(key)
        rank_map = {"none": 0, "minor": 1, "major": 2, "critical": 3}
        prev_rank = rank_map.get(_safe_str(prev.get("severity_reference")).lower(), 0) if prev else 0
        new_rank = rank_map.get(severity, 1)
        if prev is None or new_rank >= prev_rank:
            index[key] = {
                "severity_reference": severity,
                "issue_reference": issue_ref,
                "notes": _safe_str(issue.get("description"))[:220],
            }
    return index


def _render_md(summary: dict[str, Any]) -> str:
    lines = [
        "# UI Validation Summary",
        "",
        f"- Run ID: `{summary.get('run_id')}`",
        f"- Started at: `{summary.get('started_at')}`",
        f"- Finished at: `{summary.get('finished_at')}`",
        f"- Duration: `{summary.get('duration_seconds')}s`",
        f"- Overall status: `{summary.get('overall_status')}`",
        f"- Manual testing allowed: `{summary.get('manual_testing_allowed')}`",
        "",
        "## Sub-runs",
        "",
        f"- ui_doctor: `{_safe_dict(summary.get('ui_doctor')).get('run_id', '-')}` (`{_safe_dict(summary.get('ui_doctor')).get('status', '-')}`)",
        f"- ui_snapshot_runner: `{_safe_dict(summary.get('ui_snapshot_runner')).get('run_id', '-')}` (`{_safe_dict(summary.get('ui_snapshot_runner')).get('status', '-')}`)",
        "",
        "## Checks",
        "",
    ]
    for item in _safe_list(summary.get("passed_checks")):
        lines.append(f"- PASS: {item}")
    for item in _safe_list(summary.get("warned_checks")):
        lines.append(f"- WARN: {item}")
    for item in _safe_list(summary.get("failed_checks")):
        lines.append(f"- FAIL: {item}")
    lines.extend(["", "## Artifacts", ""])
    for key, value in _safe_dict(summary.get("artifacts")).items():
        lines.append(f"- {key}: `{value}`")
    return "\n".join(lines).strip() + "\n"


def _render_visual_review_md(summary: dict[str, Any]) -> str:
    lines = [
        "# UI Visual Review Summary",
        "",
        f"- Validate run: `{summary.get('run_id')}`",
        f"- Overall status: `{summary.get('overall_status')}`",
        f"- Manual testing allowed: `{summary.get('manual_testing_allowed')}`",
        "",
        "## Findings Snapshot",
        "",
    ]
    for check in _safe_list(summary.get("failed_checks")):
        lines.append(f"- blocker: {check}")
    for check in _safe_list(summary.get("warned_checks")):
        lines.append(f"- warning: {check}")
    if not _safe_list(summary.get("failed_checks")) and not _safe_list(summary.get("warned_checks")):
        lines.append("- no warnings or failures")
    lines.extend(["", "## Known Blind Spots", ""])
    for item in _safe_list(summary.get("known_blind_spots")):
        lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ui_doctor + ui_snapshot_runner and build consolidated UI validation.")
    parser.add_argument("--scales", default="1.0,1.25,1.5", help="Comma-separated UI scale factors.")
    parser.add_argument("--sizes", default="1540x920,1366x768,1280x800", help="Comma-separated window sizes.")
    parser.add_argument("--api-base-url", default="http://127.0.0.1:9", help="API URL used by UI in validation mode.")
    parser.add_argument("--skip-snapshots", action="store_true", help="Skip ui_snapshot_runner.")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    validate_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    validate_started = time.time()
    started_at = _now_iso()

    VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    validate_run_dir = VALIDATION_ROOT / f"validate_{validate_run_id}"
    validate_run_dir.mkdir(parents=True, exist_ok=True)

    passed_checks: list[str] = []
    warned_checks: list[str] = []
    failed_checks: list[str] = []
    warnings: list[str] = []
    failures: list[str] = []
    executed_commands: list[list[str]] = []

    doctor_cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "ui_doctor.py"),
        "--scales",
        args.scales,
        "--sizes",
        args.sizes,
        "--api-base-url",
        args.api_base_url,
    ]
    executed_commands.append(["python", "scripts/ui_doctor.py", "--scales", args.scales, "--sizes", args.sizes, "--api-base-url", args.api_base_url])
    doctor_code, doctor_out, doctor_err = _run_command(doctor_cmd, PROJECT_ROOT)
    doctor_run_dir = _extract_run_dir(doctor_out)
    doctor_summary: dict[str, Any] = {}
    doctor_manifest: dict[str, Any] = {"screenshots": []}
    doctor_trace: dict[str, Any] = {"steps": []}
    doctor_summary_path: Path | None = None
    doctor_manifest_path: Path | None = None
    doctor_trace_path: Path | None = None
    if doctor_code not in {0, 2}:
        failures.append(f"ui_doctor exited with code {doctor_code}")
    if doctor_err.strip():
        warnings.append(f"ui_doctor stderr: {doctor_err.strip()}")
    if doctor_run_dir is None:
        failures.append("ui_doctor run directory was not detected from stdout.")
    else:
        doctor_summary_path = doctor_run_dir / "ui_validation_summary.json"
        doctor_manifest_path = doctor_run_dir / "ui_screenshots_manifest.json"
        doctor_trace_path = doctor_run_dir / "ui_walkthrough_trace.json"
        if doctor_summary_path.exists():
            doctor_summary = _read_json(doctor_summary_path)
        else:
            failures.append("ui_doctor summary json is missing.")
        if doctor_manifest_path.exists():
            doctor_manifest = _read_json(doctor_manifest_path)
        else:
            warnings.append("ui_doctor screenshots manifest is missing.")
        if doctor_trace_path.exists():
            doctor_trace = _read_json(doctor_trace_path)
        else:
            warnings.append("ui_doctor walkthrough trace is missing.")

    snapshot_summary: dict[str, Any] = {}
    snapshot_manifest: dict[str, Any] = {"screenshots": []}
    snapshot_trace: dict[str, Any] = {"steps": []}
    snapshot_run_dir: Path | None = None
    snapshot_summary_path: Path | None = None
    snapshot_manifest_path: Path | None = None
    snapshot_trace_path: Path | None = None

    if not args.skip_snapshots:
        snapshot_cmd = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "ui_snapshot_runner.py"),
            "--scales",
            args.scales,
            "--sizes",
            args.sizes,
            "--api-base-url",
            args.api_base_url,
        ]
        executed_commands.append(["python", "scripts/ui_snapshot_runner.py", "--scales", args.scales, "--sizes", args.sizes, "--api-base-url", args.api_base_url])
        snap_code, snap_out, snap_err = _run_command(snapshot_cmd, PROJECT_ROOT)
        snapshot_run_dir = _extract_run_dir(snap_out)
        if snap_code not in {0, 2}:
            failures.append(f"ui_snapshot_runner exited with code {snap_code}")
        if snap_err.strip():
            warnings.append(f"ui_snapshot_runner stderr: {snap_err.strip()}")
        if snapshot_run_dir is None:
            failures.append("ui_snapshot_runner run directory was not detected from stdout.")
        else:
            snapshot_summary_path = snapshot_run_dir / "ui_snapshot_summary.json"
            snapshot_manifest_path = snapshot_run_dir / "ui_screenshots_manifest.json"
            snapshot_trace_path = snapshot_run_dir / "ui_walkthrough_trace.json"
            if snapshot_summary_path.exists():
                snapshot_summary = _read_json(snapshot_summary_path)
            else:
                failures.append("ui_snapshot_runner summary json is missing.")
            if snapshot_manifest_path.exists():
                snapshot_manifest = _read_json(snapshot_manifest_path)
            else:
                warnings.append("ui_snapshot_runner screenshots manifest is missing.")
            if snapshot_trace_path.exists():
                snapshot_trace = _read_json(snapshot_trace_path)
            else:
                warnings.append("ui_snapshot_runner walkthrough trace is missing.")

    doctor_status = _safe_str(doctor_summary.get("overall_status") or "FAIL")
    snapshot_status = _safe_str(snapshot_summary.get("status") or ("SKIPPED" if args.skip_snapshots else "FAIL"))
    if doctor_status == "PASS":
        passed_checks.append("ui_doctor_status")
    elif doctor_status == "PASS_WITH_WARNINGS":
        warned_checks.append("ui_doctor_status=PASS_WITH_WARNINGS")
    else:
        failed_checks.append(f"ui_doctor_status={doctor_status or 'FAIL'}")

    if snapshot_status == "PASS":
        passed_checks.append("ui_snapshot_status")
    elif snapshot_status == "PASS_WITH_WARNINGS":
        warned_checks.append("ui_snapshot_status=PASS_WITH_WARNINGS")
    elif snapshot_status == "SKIPPED":
        warned_checks.append("ui_snapshot_status=SKIPPED")
    else:
        failed_checks.append(f"ui_snapshot_status={snapshot_status or 'FAIL'}")

    doctor_issues = _safe_list(doctor_summary.get("issues"))
    blockers = _safe_list(doctor_summary.get("acceptance_blockers"))
    if blockers:
        failed_checks.append(f"doctor_acceptance_blockers={len(blockers)}")
    else:
        passed_checks.append("doctor_acceptance_blockers=0")

    severity_counts = _safe_dict(doctor_summary.get("severity_counts"))
    critical_count = int(severity_counts.get("critical", 0))
    major_count = int(severity_counts.get("major", 0))
    minor_count = int(severity_counts.get("minor", 0))
    if critical_count > 0:
        failed_checks.append(f"doctor_critical_issues={critical_count}")
    else:
        passed_checks.append("doctor_critical_issues=0")
    if major_count > 0:
        warned_checks.append(f"doctor_major_issues={major_count}")
    if minor_count > 0:
        warned_checks.append(f"doctor_minor_issues={minor_count}")

    snapshot_shots = _safe_list(snapshot_manifest.get("screenshots"))
    state_index = _build_screen_state_index(snapshot_shots)
    for screen_name, state_name in REQUIRED_LOADED_STATES.items():
        if state_name in state_index.get(screen_name, set()):
            continue
        failed_checks.append(f"missing_loaded_state:{screen_name}")
    for screen_name, required_states in REQUIRED_STATES_BY_SCREEN.items():
        for state_name in required_states:
            if state_name in state_index.get(screen_name, set()):
                continue
            warned_checks.append(f"state_not_observed:{screen_name}:{state_name}")

    observed_state_pairs = {
        f"{screen_name}:{state_name}"
        for screen_name, states in state_index.items()
        for state_name in states
    }
    missing_release_shape_states = sorted(RELEASE_SHAPE_REQUIRED_STATES - observed_state_pairs)
    if missing_release_shape_states:
        warned_checks.append(f"release_shape_state_gaps={len(missing_release_shape_states)}")
    else:
        passed_checks.append("release_shape_state_observations_complete")

    walkthrough_steps = _safe_list(snapshot_trace.get("steps")) if snapshot_trace else []
    if not walkthrough_steps:
        walkthrough_steps = _safe_list(doctor_trace.get("steps"))
    if walkthrough_steps:
        passed_checks.append("walkthrough_trace_present")
    else:
        failed_checks.append("walkthrough_trace_missing")

    action_hits: dict[str, int] = {}
    screen_hits: dict[str, int] = {}
    for step in walkthrough_steps:
        if not isinstance(step, dict):
            continue
        action = _safe_str(step.get("action"))
        screen = _safe_str(step.get("screen"))
        result = _safe_str(step.get("result")).lower()
        if action:
            action_hits[action] = action_hits.get(action, 0) + 1
        if screen and result in {"pass", "warning", "not_available", "not_applicable"}:
            screen_hits[screen] = screen_hits.get(screen, 0) + 1
    for action in CRITICAL_WALKTHROUGH_ACTIONS:
        if action_hits.get(action, 0) == 0:
            failed_checks.append(f"walkthrough_action_missing:{action}")
    for screen in REQUIRED_SCREENS:
        if screen_hits.get(screen, 0) == 0:
            failed_checks.append(f"walkthrough_screen_missing:{screen}")

    issue_index = _build_issue_index(doctor_summary)
    combined_screenshots: list[dict[str, Any]] = []
    for source_name, manifest in (("ui_doctor", doctor_manifest), ("ui_snapshot_runner", snapshot_manifest)):
        for shot in _safe_list(manifest.get("screenshots")):
            if not isinstance(shot, dict):
                continue
            entry = dict(shot)
            page = _safe_str(entry.get("screen_name") or entry.get("page") or "unknown")
            size = _safe_str(entry.get("size") or "unknown")
            scale = _safe_str(entry.get("scale") or "1.0")
            screenshot_path = _safe_str(entry.get("screenshot_path") or entry.get("path")).replace("\\", "/")
            if screenshot_path.startswith("./"):
                screenshot_path = screenshot_path[2:]
            linkage = issue_index.get((page, size, scale), {"severity_reference": "none", "issue_reference": None, "notes": ""})
            entry.update(
                {
                    "source": source_name,
                    "screen_name": page,
                    "screenshot_path": screenshot_path,
                    "path": screenshot_path,
                    "severity_reference": entry.get("severity_reference") or linkage.get("severity_reference"),
                    "issue_reference": entry.get("issue_reference") or linkage.get("issue_reference"),
                    "notes": entry.get("notes") or linkage.get("notes", ""),
                }
            )
            combined_screenshots.append(entry)

    walkthrough_payload = {
        "run_id": validate_run_id,
        "doctor_run_id": _safe_str(doctor_summary.get("run_id")),
        "snapshot_run_id": _safe_str(snapshot_summary.get("run_id")),
        "steps": walkthrough_steps,
    }
    run_walkthrough_path = validate_run_dir / "ui_walkthrough_trace.json"
    run_walkthrough_path.write_text(json.dumps(walkthrough_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    known_blind_spots = [
        "semantic visual quality (style/taste) still requires human review",
        "color contrast perception across physical monitors is not machine-validated",
        "animation smoothness and perceived latency still require manual UX pass",
    ]
    if failures:
        failed_checks.extend(failures)
    if warnings:
        warned_checks.extend(warnings)

    if failed_checks:
        overall_status = "FAIL"
    elif warned_checks:
        overall_status = "PASS_WITH_WARNINGS"
    else:
        overall_status = "PASS"

    summary = {
        "run_id": validate_run_id,
        "started_at": started_at,
        "finished_at": _now_iso(),
        "duration_seconds": round(time.time() - validate_started, 2),
        "overall_status": overall_status,
        "manual_acceptance_recommended": overall_status == "PASS",
        "manual_testing_allowed": overall_status == "PASS",
        "project_root": ".",
        "executed_commands": executed_commands,
        "passed_checks": sorted(set(passed_checks)),
        "warned_checks": sorted(set(warned_checks)),
        "failed_checks": sorted(set(failed_checks)),
        "warnings": warnings,
        "failures": failures,
        "known_blind_spots": known_blind_spots,
        "ui_doctor": {
            "run_id": _safe_str(doctor_summary.get("run_id")),
            "status": doctor_status,
            "run_path": _repo_relative(doctor_run_dir) if doctor_run_dir else "",
        },
        "ui_snapshot_runner": {
            "run_id": _safe_str(snapshot_summary.get("run_id")),
            "status": snapshot_status,
            "run_path": _repo_relative(snapshot_run_dir) if snapshot_run_dir else "",
            "skipped": bool(args.skip_snapshots),
        },
        "screen_audit": _safe_dict(doctor_summary.get("issues_by_page")),
        "behavior_depth_profile": {
            "required_screens": REQUIRED_SCREENS,
            "observed_screens": sorted(state_index.keys()),
            "required_loaded_states": REQUIRED_LOADED_STATES,
            "critical_walkthrough_actions": CRITICAL_WALKTHROUGH_ACTIONS,
        },
        "release_shape_truth": {
            "required_states": sorted(RELEASE_SHAPE_REQUIRED_STATES),
            "observed_states": sorted(observed_state_pairs),
            "missing_required_states": missing_release_shape_states,
            "ready": not missing_release_shape_states,
            "claim_boundary": "release-grade-claim-forbidden-until-wave-1-and-gate-d",
        },
        "artifacts": {
            "root_summary_json": _repo_relative(PROJECT_ROOT / "ui_validation_summary.json"),
            "root_summary_md": _repo_relative(PROJECT_ROOT / "ui_validation_summary.md"),
            "root_screenshots_manifest": _repo_relative(PROJECT_ROOT / "ui_screenshots_manifest.json"),
            "root_walkthrough_trace": _repo_relative(PROJECT_ROOT / "ui_walkthrough_trace.json"),
            "validate_run_dir": _repo_relative(validate_run_dir),
            "latest_run_txt": _repo_relative(VALIDATION_ROOT / "latest_run.txt"),
            "latest_run_json": _repo_relative(VALIDATION_ROOT / "latest_run.json"),
            "validate_visual_review_md": _repo_relative(validate_run_dir / "ui_visual_review.md"),
            "validate_walkthrough_trace_json": _repo_relative(run_walkthrough_path),
            "doctor_summary_json": _repo_relative(doctor_summary_path) if doctor_summary_path else "",
            "doctor_manifest_json": _repo_relative(doctor_manifest_path) if doctor_manifest_path else "",
            "doctor_walkthrough_trace_json": _repo_relative(doctor_trace_path) if doctor_trace_path else "",
            "snapshot_summary_json": _repo_relative(snapshot_summary_path) if snapshot_summary_path else "",
            "snapshot_manifest_json": _repo_relative(snapshot_manifest_path) if snapshot_manifest_path else "",
            "snapshot_walkthrough_trace_json": _repo_relative(snapshot_trace_path) if snapshot_trace_path else "",
        },
    }

    screenshot_manifest = {
        "run_id": validate_run_id,
        "generated_at": _now_iso(),
        "doctor_run_id": _safe_str(doctor_summary.get("run_id")),
        "snapshot_run_id": _safe_str(snapshot_summary.get("run_id")),
        "review_scope": "ui_validation",
        "screenshots": combined_screenshots,
    }

    run_summary_json = validate_run_dir / "ui_validation_summary.json"
    run_summary_md = validate_run_dir / "ui_validation_summary.md"
    run_manifest_json = validate_run_dir / "ui_screenshots_manifest.json"
    run_visual_review_md = validate_run_dir / "ui_visual_review.md"
    run_summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    run_summary_md.write_text(_render_md(summary), encoding="utf-8")
    run_manifest_json.write_text(json.dumps(screenshot_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    run_visual_review_md.write_text(_render_visual_review_md(summary), encoding="utf-8")

    shutil.copyfile(run_summary_json, PROJECT_ROOT / "ui_validation_summary.json")
    shutil.copyfile(run_summary_md, PROJECT_ROOT / "ui_validation_summary.md")
    shutil.copyfile(run_manifest_json, PROJECT_ROOT / "ui_screenshots_manifest.json")
    shutil.copyfile(run_walkthrough_path, PROJECT_ROOT / "ui_walkthrough_trace.json")

    (VALIDATION_ROOT / "latest_run.txt").write_text(_repo_relative(validate_run_dir) + "\n", encoding="utf-8")
    (VALIDATION_ROOT / "latest_run.json").write_text(
        json.dumps(
            {
                "run_id": validate_run_id,
                "status": overall_status,
                "path": _repo_relative(validate_run_dir),
                "summary_path": _repo_relative(run_summary_json),
                "manifest_path": _repo_relative(run_manifest_json),
                "walkthrough_trace_path": _repo_relative(run_walkthrough_path),
                "timestamp": _now_iso(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(_repo_relative(validate_run_dir))
    print(f"UI validate status: {overall_status}")
    return 0 if overall_status == "PASS" else (2 if overall_status == "FAIL" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
