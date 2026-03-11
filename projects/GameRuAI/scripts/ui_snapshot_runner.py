from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from scripts.ui_qa_product import apply_scenario_state, scenario_catalog


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    out = []
    for char in value.lower():
        out.append(char if char.isalnum() else "_")
    return "".join(out).strip("_") or "item"


def _parse_sizes(raw: str) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for token in raw.split(","):
        token = token.strip().lower()
        if not token:
            continue
        if "x" not in token:
            raise ValueError(f"Invalid size token: {token}")
        width_raw, height_raw = token.split("x", 1)
        result.append((int(width_raw), int(height_raw)))
    if not result:
        raise ValueError("No sizes were provided.")
    return result


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# UI Snapshot Summary",
        "",
        f"- Run ID: `{summary.get('run_id')}`",
        f"- Label: `{summary.get('label')}`",
        f"- Status: `{summary.get('status')}`",
        f"- Duration: `{summary.get('duration_seconds')}s`",
        f"- Scales: `{', '.join(summary.get('scales', []))}`",
        f"- Sizes: `{summary.get('sizes')}`",
        f"- Captures: `{summary.get('capture_count', 0)}`",
        "",
        "## Coverage By Screen",
        "",
    ]

    coverage_by_screen = summary.get("coverage_by_screen", {})
    if coverage_by_screen:
        for screen_name, count in coverage_by_screen.items():
            lines.append(f"- {screen_name}: {count}")
    else:
        lines.append("- none")

    lines.extend(["", "## Coverage By State", ""])
    coverage_by_state = summary.get("coverage_by_state", {})
    if coverage_by_state:
        for state_name, count in coverage_by_state.items():
            lines.append(f"- {state_name}: {count}")
    else:
        lines.append("- none")

    lines.extend(["", "## Artifacts", ""])
    lines.append(f"- Manifest: `{summary.get('manifest_path', '')}`")
    lines.append(f"- Run dir: `{summary.get('run_dir', '')}`")

    failed_workers = summary.get("failed_workers", [])
    if failed_workers:
        lines.extend(["", "## Failed Workers", ""])
        for item in failed_workers:
            lines.append(f"- {item}")

    return "\n".join(lines).strip() + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture product-specific GameRuAI UI screenshots by screen/state.")
    parser.add_argument("--worker", action="store_true", help="Internal worker mode.")
    parser.add_argument("--run-id", default="", help="Master run ID for worker mode.")
    parser.add_argument("--scale", default="1.0", help="Scale for worker mode.")
    parser.add_argument("--scales", default="1.0,1.25,1.5", help="Scales for master mode.")
    parser.add_argument("--sizes", default="1600x960,1366x768,1280x800", help="Window sizes (comma-separated).")
    parser.add_argument("--output-dir", default="runtime/ui_snapshots", help="Output root for snapshot runs.")
    parser.add_argument("--run-dir", default="", help="Run directory for worker mode.")
    parser.add_argument("--worker-output", default="", help="Worker JSON output path.")
    parser.add_argument("--wait-ms", type=int, default=220, help="Wait between scenario transitions.")
    parser.add_argument("--label", default="ui_snapshot", help="Optional run label.")
    parser.add_argument("--project-name", default="GameRuAI UI-QA Project", help="Project name used in demo bootstrap.")
    return parser


def _run_worker(args: argparse.Namespace) -> int:
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from app.bootstrap import AppServices
    from app.config import AppConfig
    from app.main import ensure_demo_assets
    from app.ui.main_window import MainWindow

    run_dir = Path(args.run_dir).resolve()
    screenshots_dir = run_dir / "screenshots" / f"scale_{args.scale.replace('.', '_')}"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    sizes = _parse_sizes(args.sizes)
    scenarios = scenario_catalog()

    config = AppConfig.load()
    ensure_demo_assets(config)
    services = AppServices(config)

    app = QApplication([])
    window = MainWindow(services)

    captures: list[dict[str, Any]] = []
    errors: list[str] = []

    def _wait() -> None:
        QTest.qWait(args.wait_ms)
        app.processEvents()

    for size_index, (width, height) in enumerate(sizes):
        window.resize(width, height)
        window.show()
        _wait()

        size_label = f"{width}x{height}"
        for scenario in scenarios:
            if not scenario.requires_loaded and size_index > 0:
                continue

            ok = apply_scenario_state(window, scenario, project_name=args.project_name, wait_fn=_wait)
            if not ok:
                errors.append(f"screen_not_found::{scenario.screen_name}::{scenario.state_name}")
                continue

            _wait()
            file_name = (
                f"{_slug(scenario.screen_name)}__{_slug(scenario.state_name)}"
                f"__{size_label}__scale_{args.scale.replace('.', '_')}.png"
            )
            out_path = screenshots_dir / file_name
            image = window.grab()
            image.save(str(out_path))

            captures.append(
                {
                    "run_id": args.run_id,
                    "screen_name": scenario.screen_name,
                    "state_name": scenario.state_name,
                    "screenshot_path": str(out_path.resolve()),
                    "timestamp": _now_iso(),
                    "notes": scenario.notes,
                    "size": size_label,
                    "scale": args.scale,
                    "width": width,
                    "height": height,
                    "sha256": _hash_file(out_path),
                }
            )

    window.close()
    services.close()
    app.quit()

    payload = {
        "run_id": args.run_id,
        "scale": args.scale,
        "sizes": args.sizes,
        "captures": captures,
        "errors": errors,
    }
    Path(args.worker_output).resolve().write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


def _run_master(args: argparse.Namespace) -> int:
    output_root = (PROJECT_ROOT / args.output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    started_at = _now_iso()

    scales = [token.strip() for token in args.scales.split(",") if token.strip()]
    all_captures: list[dict[str, Any]] = []
    all_errors: list[str] = []
    failed_workers: list[str] = []
    commands: list[list[str]] = []

    for scale in scales:
        worker_output = run_dir / f"worker_{scale.replace('.', '_')}.json"
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--worker",
            "--run-id",
            run_id,
            "--scale",
            scale,
            "--sizes",
            args.sizes,
            "--wait-ms",
            str(args.wait_ms),
            "--project-name",
            args.project_name,
            "--run-dir",
            str(run_dir),
            "--worker-output",
            str(worker_output),
        ]
        commands.append(command)

        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        env["QT_SCALE_FACTOR"] = scale
        completed = subprocess.run(command, cwd=PROJECT_ROOT, env=env, text=True, capture_output=True)
        if completed.returncode != 0:
            failed_workers.append(f"scale={scale} code={completed.returncode}")
            continue
        if not worker_output.exists():
            failed_workers.append(f"scale={scale} (missing worker output)")
            continue

        payload = json.loads(worker_output.read_text(encoding="utf-8"))
        all_captures.extend(payload.get("captures", []))
        all_errors.extend(payload.get("errors", []))

    coverage_by_screen: dict[str, int] = {}
    coverage_by_state: dict[str, int] = {}
    for capture in all_captures:
        screen_name = str(capture.get("screen_name", "unknown"))
        state_key = f"{capture.get('screen_name', 'unknown')}|{capture.get('state_name', 'unknown')}"
        coverage_by_screen[screen_name] = coverage_by_screen.get(screen_name, 0) + 1
        coverage_by_state[state_key] = coverage_by_state.get(state_key, 0) + 1

    status = "PASS" if not failed_workers else "FAIL"
    if status == "PASS" and all_errors:
        status = "PASS_WITH_WARNINGS"

    finished_at = _now_iso()
    duration_seconds = round(time.time() - started, 2)

    manifest = {
        "run_id": run_id,
        "label": args.label,
        "generated_at": finished_at,
        "sizes": args.sizes,
        "scales": scales,
        "captures": all_captures,
        "screenshots": all_captures,
        "coverage_by_screen": dict(sorted(coverage_by_screen.items())),
        "coverage_by_state": dict(sorted(coverage_by_state.items())),
        "worker_errors": all_errors,
    }
    manifest_path = run_dir / "ui_screenshots_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "run_id": run_id,
        "label": args.label,
        "status": status,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration_seconds,
        "scales": scales,
        "sizes": args.sizes,
        "capture_count": len(all_captures),
        "coverage_by_screen": dict(sorted(coverage_by_screen.items())),
        "coverage_by_state": dict(sorted(coverage_by_state.items())),
        "worker_errors": all_errors,
        "failed_workers": failed_workers,
        "commands": commands,
        "manifest_path": str(manifest_path.resolve()),
        "run_dir": str(run_dir.resolve()),
    }
    summary_json = run_dir / "ui_snapshot_summary.json"
    summary_md = run_dir / "ui_snapshot_summary.md"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_md.write_text(_render_summary_md(summary), encoding="utf-8")

    latest = {
        "run_id": run_id,
        "status": status,
        "path": str(run_dir.resolve()),
        "manifest_path": str(manifest_path.resolve()),
        "summary_path": str(summary_json.resolve()),
        "timestamp": finished_at,
    }
    (output_root / "latest_run.json").write_text(json.dumps(latest, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_root / "latest_run.txt").write_text(str(run_dir.resolve()) + "\n", encoding="utf-8")

    print(str(run_dir.resolve()))
    print(f"UI snapshot status: {status}")
    return 0 if status != "FAIL" else 2


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    if args.worker:
        if not args.run_dir or not args.worker_output or not args.run_id:
            parser.error("--run-id, --run-dir and --worker-output are required in worker mode.")
        return _run_worker(args)
    return _run_master(args)


if __name__ == "__main__":
    raise SystemExit(main())
