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
SEVERITY_RANK = {"none": 0, "minor": 1, "major": 2, "critical": 3}


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


def _render_md(summary: dict[str, Any]) -> str:
    lines = [
        "# UI Validation Summary",
        "",
        f"- Run ID: `{summary.get('run_id')}`",
        f"- Started at: `{summary.get('started_at')}`",
        f"- Finished at: `{summary.get('finished_at')}`",
        f"- Duration: `{summary.get('duration_seconds')}s`",
        f"- Overall status: `{summary.get('overall_status')}`",
        f"- Manual acceptance recommended: `{summary.get('manual_acceptance_recommended')}`",
        f"- Manual testing allowed: `{summary.get('manual_testing_allowed')}`",
        "",
        "## Sub-runs",
        "",
    ]

    doctor = summary.get("ui_doctor", {})
    snapshot = summary.get("ui_snapshot_runner", {})
    lines.extend(
        [
            f"- ui_doctor run: `{doctor.get('run_id', '-')}` (`{doctor.get('status', '-')}`)",
            f"- ui_snapshot_runner run: `{snapshot.get('run_id', '-')}` (`{snapshot.get('status', '-')}`)",
            "",
            "## Screen Audit",
            "",
        ]
    )
    screen_audit = summary.get("screen_audit", {})
    if not screen_audit:
        lines.append("- no screen-level audit data")
    else:
        for page, details in screen_audit.items():
            lines.append(
                f"- {page}: critical={details.get('critical', 0)}, "
                f"major={details.get('major', 0)}, minor={details.get('minor', 0)}"
            )

    lines.extend(["", "## Artifacts", ""])
    artifacts = summary.get("artifacts", {})
    for key, value in artifacts.items():
        lines.append(f"- {key}: `{value}`")

    warnings = summary.get("warnings", [])
    if warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.extend(["", "## Warnings", "", "- none"])

    failures = summary.get("failures", [])
    if failures:
        lines.extend(["", "## Failures", ""])
        for failure in failures:
            lines.append(f"- {failure}")
    else:
        lines.extend(["", "## Failures", "", "- none"])
    return "\n".join(lines).strip() + "\n"


def _build_screen_audit(doctor_summary: dict[str, Any]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for issue in _safe_list(doctor_summary.get("issues")):
        if not isinstance(issue, dict):
            continue
        page = str(issue.get("page", "unknown"))
        severity = str(issue.get("severity", "minor")).lower()
        if severity not in {"critical", "major", "minor"}:
            severity = "minor"
        if page not in result:
            result[page] = {"critical": 0, "major": 0, "minor": 0}
        result[page][severity] += 1
    return result


def _build_issue_index(doctor_summary: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, str]]:
    issue_index: dict[tuple[str, str, str], dict[str, str]] = {}
    for idx, issue in enumerate(_safe_list(doctor_summary.get("issues"))):
        if not isinstance(issue, dict):
            continue
        page = str(issue.get("page", "unknown"))
        size = str(issue.get("screen_size", "unknown"))
        scale = str(issue.get("scale", "1.0"))
        severity = str(issue.get("severity", "minor")).lower()
        category = str(issue.get("category", "unspecified"))
        description = str(issue.get("description", ""))
        key = (page, size, scale)
        issue_ref = f"doctor:{category}:{idx + 1}"
        current = issue_index.get(key)
        candidate_rank = SEVERITY_RANK.get(severity, 1)
        current_rank = (
            SEVERITY_RANK.get(str(current.get("severity_reference", "none")).lower(), 0)
            if current
            else 0
        )
        if current is None or candidate_rank >= current_rank:
            issue_index[key] = {
                "severity_reference": severity,
                "issue_reference": issue_ref,
                "notes": description[:220] if description else "",
            }
    return issue_index


def _render_visual_review_md(summary: dict[str, Any]) -> str:
    lines = [
        "# UI Visual Review",
        "",
        f"- Validate run: `{summary.get('run_id')}`",
        f"- Overall status: `{summary.get('overall_status')}`",
        f"- Doctor run: `{summary.get('ui_doctor', {}).get('run_id', '-')}`",
        f"- Snapshot run: `{summary.get('ui_snapshot_runner', {}).get('run_id', '-')}`",
        "",
        "## Automated Signals",
        "",
    ]
    screen_audit = summary.get("screen_audit", {})
    if not screen_audit:
        lines.append("- No per-screen issues were emitted by ui_doctor.")
    else:
        for page, details in screen_audit.items():
            lines.append(
                f"- {page}: critical={details.get('critical', 0)}, "
                f"major={details.get('major', 0)}, minor={details.get('minor', 0)}"
            )

    lines.extend(
        [
            "",
            "## Manual Visual Focus",
            "",
            "- Dashboard: читаемость блока состояния ядра и next-actions.",
            "- Sessions: геометрия session frame и статусных зон на 125%/150%.",
            "- Analytics/AI Studio: плотность длинных текстовых блоков и иерархия CTA.",
            "- Context panel: отсутствие сжатия и потерянных action-блоков при resize.",
            "",
            "## Recommendation",
            "",
        ]
    )
    status = str(summary.get("overall_status", "FAIL"))
    if status == "FAIL":
        lines.append("- Автоматический гейт не пройден: ручной acceptance запрещён.")
    elif status == "PASS_WITH_WARNINGS":
        lines.append("- Гейт с предупреждениями: ручной acceptance заблокирован до выхода на PASS.")
    else:
        lines.append("- Гейт пройден. Выполните финальный ручной visual acceptance перед freeze.")
    return "\n".join(lines).strip() + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ui_doctor + ui_snapshot_runner and build consolidated artifacts.")
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
    executed_commands.append(
        [
            "python",
            "scripts/ui_doctor.py",
            "--scales",
            args.scales,
            "--sizes",
            args.sizes,
            "--api-base-url",
            args.api_base_url,
        ]
    )
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
        doctor_summary_path = doctor_run_dir / "ui_validation_summary.json"
        doctor_manifest_path = doctor_run_dir / "ui_screenshots_manifest.json"
        if doctor_summary_path.exists():
            doctor_summary = _read_json(doctor_summary_path)
        else:
            failures.append("ui_doctor summary json is missing.")
        if doctor_manifest_path.exists():
            doctor_manifest = _read_json(doctor_manifest_path)
        else:
            warnings.append("ui_doctor screenshots manifest is missing.")

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
            "--api-base-url",
            args.api_base_url,
        ]
        executed_commands.append(
            [
                "python",
                "scripts/ui_snapshot_runner.py",
                "--scales",
                args.scales,
                "--sizes",
                args.sizes,
                "--api-base-url",
                args.api_base_url,
            ]
        )
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
                warnings.append("ui_snapshot_runner screenshots manifest is missing.")

    doctor_status = str(doctor_summary.get("overall_status", "FAIL"))
    snapshot_status = str(snapshot_summary.get("status", "PASS")) if snapshot_summary else "PASS"

    if failures or doctor_status == "FAIL" or snapshot_status == "FAIL":
        overall_status = "FAIL"
    elif doctor_status == "PASS_WITH_WARNINGS" or snapshot_status == "PASS_WITH_WARNINGS":
        overall_status = "PASS_WITH_WARNINGS"
    else:
        overall_status = "PASS"

    issue_index = _build_issue_index(doctor_summary)
    combined_screenshots: list[dict[str, Any]] = []
    for source_name, manifest in (("ui_doctor", doctor_manifest), ("ui_snapshot_runner", snapshot_manifest)):
        for shot in _safe_list(manifest.get("screenshots")):
            if not isinstance(shot, dict):
                continue
            entry = dict(shot)
            page = str(entry.get("screen_name") or entry.get("page") or "unknown")
            size = str(entry.get("size", "unknown"))
            scale = str(entry.get("scale", "1.0"))
            state_name = str(entry.get("state_name") or f"loaded/{size}/scale_{scale}")
            screenshot_path = str(entry.get("screenshot_path") or entry.get("path") or "").replace("\\", "/")
            if screenshot_path.startswith("./"):
                screenshot_path = screenshot_path[2:]
            timestamp = str(entry.get("timestamp") or entry.get("captured_at") or _now_iso())

            tags = entry.get("tags")
            if not isinstance(tags, list):
                tags = [f"screen:{page}", f"size:{size}", f"scale:{scale}"]
            if source_name not in tags:
                tags.append(source_name)

            linkage = issue_index.get(
                (page, size, scale),
                {"severity_reference": "none", "issue_reference": None, "notes": ""},
            )

            entry.update(
                {
                    "source": source_name,
                    "screen_name": page,
                    "state_name": state_name,
                    "screenshot_path": screenshot_path,
                    "path": screenshot_path,
                    "timestamp": timestamp,
                    "captured_at": timestamp,
                    "notes": entry.get("notes") or linkage.get("notes", ""),
                    "tags": tags,
                    "severity_reference": entry.get("severity_reference") or linkage.get("severity_reference"),
                    "issue_reference": entry.get("issue_reference") or linkage.get("issue_reference"),
                }
            )
            combined_screenshots.append(entry)

    screenshot_manifest = {
        "run_id": validate_run_id,
        "generated_at": _now_iso(),
        "doctor_run_id": doctor_summary.get("run_id"),
        "snapshot_run_id": snapshot_summary.get("run_id"),
        "review_scope": "ui_validation",
        "screenshots": combined_screenshots,
    }
    screen_audit = _build_screen_audit(doctor_summary)

    finished_at = _now_iso()
    duration = round(time.time() - validate_started, 2)
    summary = {
        "run_id": validate_run_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration,
        "overall_status": overall_status,
        "manual_acceptance_recommended": overall_status == "PASS",
        "manual_testing_allowed": overall_status == "PASS",
        "project_root": ".",
        "executed_commands": executed_commands,
        "ui_doctor": {
            "run_id": doctor_summary.get("run_id"),
            "status": doctor_status,
            "run_path": _repo_relative(doctor_run_dir) if doctor_run_dir else "",
        },
        "ui_snapshot_runner": {
            "run_id": snapshot_summary.get("run_id"),
            "status": snapshot_status if snapshot_summary else "SKIPPED",
            "run_path": _repo_relative(snapshot_run_dir) if snapshot_run_dir else "",
            "skipped": bool(args.skip_snapshots),
        },
        "warnings": warnings,
        "failures": failures,
        "screen_audit": screen_audit,
        "artifacts": {
            "root_summary_json": _repo_relative(PROJECT_ROOT / "ui_validation_summary.json"),
            "root_summary_md": _repo_relative(PROJECT_ROOT / "ui_validation_summary.md"),
            "root_screenshots_manifest": _repo_relative(PROJECT_ROOT / "ui_screenshots_manifest.json"),
            "validate_run_dir": _repo_relative(validate_run_dir),
            "latest_run_txt": _repo_relative(VALIDATION_ROOT / "latest_run.txt"),
            "validate_visual_review_md": _repo_relative(validate_run_dir / "ui_visual_review.md"),
            "doctor_summary_json": _repo_relative(doctor_summary_path) if doctor_summary_path else "",
            "doctor_manifest_json": _repo_relative(doctor_manifest_path) if doctor_manifest_path else "",
            "snapshot_summary_json": _repo_relative(snapshot_summary_path) if snapshot_summary_path else "",
            "snapshot_manifest_json": _repo_relative(snapshot_manifest_path) if snapshot_manifest_path else "",
        },
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

    (VALIDATION_ROOT / "latest_run.txt").write_text(_repo_relative(validate_run_dir) + "\n", encoding="utf-8")
    (VALIDATION_ROOT / "latest_run.json").write_text(
        json.dumps(
            {
                "run_id": validate_run_id,
                "status": overall_status,
                "path": _repo_relative(validate_run_dir),
                "timestamp": finished_at,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(_repo_relative(validate_run_dir))
    print(f"UI validate status: {overall_status}")
    return 0 if overall_status != "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
