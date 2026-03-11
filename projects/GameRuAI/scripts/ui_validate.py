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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_run_dir(stdout_text: str) -> Path | None:
    for line in stdout_text.splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists() and path.is_dir():
            return path.resolve()
    return None


def _run_command(command: list[str], cwd: Path) -> tuple[int, str, str]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    return completed.returncode, completed.stdout, completed.stderr


def _render_md(summary: dict[str, Any]) -> str:
    lines = [
        "# UI Validation Summary",
        "",
        f"- Run ID: `{summary.get('run_id')}`",
        f"- Started: `{summary.get('started_at')}`",
        f"- Finished: `{summary.get('finished_at')}`",
        f"- Duration: `{summary.get('duration_seconds')}s`",
        f"- Overall status: `{summary.get('overall_status')}`",
        f"- Manual acceptance recommended: `{summary.get('manual_acceptance_recommended')}`",
        "",
        "## Sub-runs",
        "",
    ]

    doctor = summary.get("ui_doctor", {})
    snapshot = summary.get("ui_snapshot_runner", {})
    lines.append(f"- ui_doctor: run=`{doctor.get('run_id', '-')}` status=`{doctor.get('status', '-')}`")
    lines.append(f"- ui_snapshot_runner: run=`{snapshot.get('run_id', '-')}` status=`{snapshot.get('status', '-')}`")

    lines.extend(["", "## Screen Audit", ""])
    screen_audit = summary.get("screen_audit", {})
    if not screen_audit:
        lines.append("- no screen-level diagnostics")
    else:
        for tab_name, counts in sorted(screen_audit.items()):
            lines.append(
                f"- {tab_name}: critical={counts.get('critical', 0)}, major={counts.get('major', 0)}, minor={counts.get('minor', 0)}"
            )

    lines.extend(["", "## Artifacts", ""])
    for key, value in (summary.get("artifacts", {}) or {}).items():
        lines.append(f"- {key}: `{value}`")

    warnings = summary.get("warnings", [])
    lines.extend(["", "## Warnings", ""])
    if warnings:
        for item in warnings:
            lines.append(f"- {item}")
    else:
        lines.append("- none")

    failures = summary.get("failures", [])
    lines.extend(["", "## Failures", ""])
    if failures:
        for item in failures:
            lines.append(f"- {item}")
    else:
        lines.append("- none")

    return "\n".join(lines).strip() + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run full GameRuAI UI validation pipeline (doctor + snapshots).")
    parser.add_argument("--scales", default="1.0,1.25,1.5", help="Comma-separated UI scales.")
    parser.add_argument("--sizes", default="1600x960,1366x768,1280x800", help="Comma-separated window sizes.")
    parser.add_argument("--project-name", default="GameRuAI UI-QA Project", help="Project name used in demo bootstrap.")
    parser.add_argument("--skip-snapshots", action="store_true", help="Skip ui_snapshot_runner step.")
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
        "--project-name",
        args.project_name,
    ]
    executed_commands.append(doctor_cmd)
    doctor_code, doctor_out, doctor_err = _run_command(doctor_cmd, PROJECT_ROOT)

    doctor_run_dir = _extract_run_dir(doctor_out)
    doctor_summary: dict[str, Any] = {}
    doctor_manifest: dict[str, Any] = {"screenshots": []}
    doctor_summary_path: Path | None = None
    doctor_manifest_path: Path | None = None

    if doctor_code not in {0, 2}:
        failures.append(f"ui_doctor exited with code {doctor_code}")
    if doctor_err.strip():
        warnings.append(f"ui_doctor stderr: {doctor_err.strip()}")
    if doctor_run_dir is None:
        failures.append("ui_doctor run directory was not detected from stdout.")
    else:
        doctor_summary_path = doctor_run_dir / "ui_doctor_summary.json"
        if not doctor_summary_path.exists():
            doctor_summary_path = doctor_run_dir / "ui_validation_summary.json"
        doctor_manifest_path = doctor_run_dir / "ui_screenshots_manifest.json"
        if doctor_summary_path.exists():
            doctor_summary = _read_json(doctor_summary_path)
        else:
            failures.append("ui_doctor summary json is missing.")
        if doctor_manifest_path.exists():
            doctor_manifest = _read_json(doctor_manifest_path)
        else:
            warnings.append("ui_doctor screenshot manifest is missing.")

    snapshot_summary: dict[str, Any] = {}
    snapshot_manifest: dict[str, Any] = {"screenshots": []}
    snapshot_run_dir: Path | None = None
    snapshot_summary_path: Path | None = None
    snapshot_manifest_path: Path | None = None

    if not args.skip_snapshots:
        snapshot_cmd = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "ui_snapshot_runner.py"),
            "--scales",
            args.scales,
            "--sizes",
            args.sizes,
            "--project-name",
            args.project_name,
        ]
        executed_commands.append(snapshot_cmd)
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
            if snapshot_summary_path.exists():
                snapshot_summary = _read_json(snapshot_summary_path)
            else:
                failures.append("ui_snapshot_runner summary json is missing.")
            if snapshot_manifest_path.exists():
                snapshot_manifest = _read_json(snapshot_manifest_path)
            else:
                warnings.append("ui_snapshot_runner screenshot manifest is missing.")

    doctor_status = str(doctor_summary.get("overall_status", "FAIL"))
    snapshot_status = str(snapshot_summary.get("status", "PASS")) if snapshot_summary else "SKIPPED"

    if failures or doctor_status == "FAIL" or snapshot_status == "FAIL":
        overall_status = "FAIL"
    elif doctor_status == "PASS_WITH_WARNINGS" or snapshot_status == "PASS_WITH_WARNINGS" or warnings:
        overall_status = "PASS_WITH_WARNINGS"
    else:
        overall_status = "PASS"

    combined_screenshots: list[dict[str, Any]] = []
    for source_name, manifest in (("ui_doctor", doctor_manifest), ("ui_snapshot_runner", snapshot_manifest)):
        for shot in manifest.get("screenshots", []):
            if not isinstance(shot, dict):
                continue
            item = dict(shot)
            item["source"] = source_name
            combined_screenshots.append(item)

    screenshot_manifest = {
        "run_id": validate_run_id,
        "generated_at": _now_iso(),
        "doctor_run_id": doctor_summary.get("run_id"),
        "snapshot_run_id": snapshot_summary.get("run_id"),
        "screenshots": combined_screenshots,
    }

    finished_at = _now_iso()
    duration_seconds = round(time.time() - validate_started, 2)
    screen_audit = doctor_summary.get("tab_issue_counts", {}) if isinstance(doctor_summary, dict) else {}

    summary = {
        "run_id": validate_run_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration_seconds,
        "overall_status": overall_status,
        "manual_acceptance_recommended": overall_status != "FAIL",
        "project_root": str(PROJECT_ROOT),
        "executed_commands": executed_commands,
        "ui_doctor": {
            "run_id": doctor_summary.get("run_id"),
            "status": doctor_status,
            "run_path": str(doctor_run_dir) if doctor_run_dir else "",
        },
        "ui_snapshot_runner": {
            "run_id": snapshot_summary.get("run_id"),
            "status": snapshot_status,
            "run_path": str(snapshot_run_dir) if snapshot_run_dir else "",
            "skipped": bool(args.skip_snapshots),
        },
        "warnings": warnings,
        "failures": failures,
        "screen_audit": screen_audit,
        "artifacts": {
            "root_summary_json": str((PROJECT_ROOT / "ui_validation_summary.json").resolve()),
            "root_summary_md": str((PROJECT_ROOT / "ui_validation_summary.md").resolve()),
            "root_screenshots_manifest": str((PROJECT_ROOT / "ui_screenshots_manifest.json").resolve()),
            "validate_run_dir": str(validate_run_dir.resolve()),
            "latest_run_txt": str((VALIDATION_ROOT / "latest_run.txt").resolve()),
            "doctor_summary_json": str(doctor_summary_path.resolve()) if doctor_summary_path else "",
            "doctor_manifest_json": str(doctor_manifest_path.resolve()) if doctor_manifest_path else "",
            "snapshot_summary_json": str(snapshot_summary_path.resolve()) if snapshot_summary_path else "",
            "snapshot_manifest_json": str(snapshot_manifest_path.resolve()) if snapshot_manifest_path else "",
        },
    }

    run_summary_json = validate_run_dir / "ui_validation_summary.json"
    run_summary_md = validate_run_dir / "ui_validation_summary.md"
    run_manifest_json = validate_run_dir / "ui_screenshots_manifest.json"

    run_summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    run_summary_md.write_text(_render_md(summary), encoding="utf-8")
    run_manifest_json.write_text(json.dumps(screenshot_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    shutil.copyfile(run_summary_json, PROJECT_ROOT / "ui_validation_summary.json")
    shutil.copyfile(run_summary_md, PROJECT_ROOT / "ui_validation_summary.md")
    shutil.copyfile(run_manifest_json, PROJECT_ROOT / "ui_screenshots_manifest.json")

    (VALIDATION_ROOT / "latest_run.txt").write_text(str(validate_run_dir.resolve()) + "\n", encoding="utf-8")
    (VALIDATION_ROOT / "latest_run.json").write_text(
        json.dumps(
            {
                "run_id": validate_run_id,
                "status": overall_status,
                "path": str(validate_run_dir.resolve()),
                "timestamp": finished_at,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(str(validate_run_dir.resolve()))
    print(f"UI validate status: {overall_status}")
    return 0 if overall_status != "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
