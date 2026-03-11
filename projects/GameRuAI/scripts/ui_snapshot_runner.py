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


def _extract_run_dir(stdout_text: str) -> Path | None:
    for line in stdout_text.splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists() and path.is_dir():
            return path.resolve()
    return None


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
        f"- Screenshots: `{summary.get('screenshot_count', 0)}`",
        "",
        "## Screenshots By Tab",
        "",
    ]
    shots_by_tab = summary.get("screenshots_by_tab", {})
    if shots_by_tab:
        for tab_name, count in shots_by_tab.items():
            lines.append(f"- {tab_name}: {count}")
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
    parser = argparse.ArgumentParser(description="Capture GameRuAI UI screenshots by tab and viewport.")
    parser.add_argument("--worker", action="store_true", help="Internal worker mode.")
    parser.add_argument("--scale", default="1.0", help="Scale for worker mode.")
    parser.add_argument("--scales", default="1.0,1.25,1.5", help="Scales for master mode.")
    parser.add_argument("--sizes", default="1600x960,1366x768,1280x800", help="Window sizes (comma-separated).")
    parser.add_argument("--output-dir", default="runtime/ui_snapshots", help="Output root for snapshot runs.")
    parser.add_argument("--run-dir", default="", help="Run directory for worker mode.")
    parser.add_argument("--worker-output", default="", help="Worker JSON output path.")
    parser.add_argument("--wait-ms", type=int, default=220, help="Wait between tab transitions.")
    parser.add_argument("--label", default="ui_snapshot", help="Optional run label.")
    parser.add_argument("--project-name", default="GameRuAI UI-QA Project", help="Project name used in demo bootstrap.")
    return parser


def _prepare_demo_state(window: Any, *, project_name: str) -> None:
    game_root = window.services.config.paths.fixtures_root
    summary = window.services.pipeline_end_to_end(project_name, game_root)

    window.current_project_id = int(summary["project"]["id"])
    window.current_game_root = game_root
    window.project_panel.project_name_edit.setText(project_name)
    window.project_panel.game_path_edit.setText(str(game_root))
    window.companion_panel.watched_path_edit.setText(str(game_root))
    window.live_panel.load_scenes(window.services.load_scenes(game_root))
    window.translation_panel.set_backend_status(summary.get("translate", {}))
    window.refresh_all_views()


def _prime_tab_state(window: Any, tab_name: str) -> None:
    if tab_name == "Asset Explorer":
        tree = window.asset_panel.resource_tree
        if tree.topLevelItemCount() > 0:
            first = tree.topLevelItem(0)
            tree.setCurrentItem(first)
    elif tab_name == "Entries":
        window.refresh_entries()
    elif tab_name == "Translation":
        window.refresh_translations()
    elif tab_name == "Voice":
        window.refresh_voice()
    elif tab_name == "Learning":
        window.refresh_learning()
    elif tab_name == "Glossary":
        window.refresh_glossary()
    elif tab_name == "QA":
        window.refresh_qa()
    elif tab_name == "Reports":
        window.refresh_reports()
    elif tab_name == "Diagnostics":
        window.refresh_diagnostics()
    elif tab_name == "Companion":
        window.refresh_companion()


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
    config = AppConfig.load()
    ensure_demo_assets(config)
    services = AppServices(config)

    app = QApplication([])
    window = MainWindow(services)
    _prepare_demo_state(window, project_name=args.project_name)

    screenshots: list[dict[str, Any]] = []
    for width, height in sizes:
        window.resize(width, height)
        window.show()
        QTest.qWait(args.wait_ms)
        app.processEvents()

        size_label = f"{width}x{height}"
        tab_count = window.tabs.count()
        for tab_index in range(tab_count):
            window.tabs.setCurrentIndex(tab_index)
            tab_name = window.tabs.tabText(tab_index)
            _prime_tab_state(window, tab_name)
            QTest.qWait(args.wait_ms)
            app.processEvents()

            file_name = f"tab_{tab_index:02d}_{_slug(tab_name)}__{size_label}__scale_{args.scale.replace('.', '_')}.png"
            out_path = screenshots_dir / file_name
            image = window.grab()
            image.save(str(out_path))

            screenshots.append(
                {
                    "tab_index": tab_index,
                    "tab_name": tab_name,
                    "size": size_label,
                    "scale": args.scale,
                    "width": width,
                    "height": height,
                    "path": str(out_path.resolve()),
                    "sha256": _hash_file(out_path),
                    "captured_at": _now_iso(),
                }
            )

    window.close()
    services.close()
    app.quit()

    payload = {
        "scale": args.scale,
        "sizes": args.sizes,
        "screenshots": screenshots,
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
    all_screenshots: list[dict[str, Any]] = []
    failed_workers: list[str] = []
    commands: list[list[str]] = []

    for scale in scales:
        worker_output = run_dir / f"worker_{scale.replace('.', '_')}.json"
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--worker",
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
        all_screenshots.extend(payload.get("screenshots", []))

    screenshots_by_tab: dict[str, int] = {}
    for shot in all_screenshots:
        tab_name = str(shot.get("tab_name", "unknown"))
        screenshots_by_tab[tab_name] = screenshots_by_tab.get(tab_name, 0) + 1

    status = "PASS" if not failed_workers else "FAIL"
    finished_at = _now_iso()
    duration_seconds = round(time.time() - started, 2)

    manifest = {
        "run_id": run_id,
        "label": args.label,
        "generated_at": finished_at,
        "sizes": args.sizes,
        "scales": scales,
        "screenshots": all_screenshots,
        "screenshots_by_tab": dict(sorted(screenshots_by_tab.items())),
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
        "screenshot_count": len(all_screenshots),
        "screenshots_by_tab": dict(sorted(screenshots_by_tab.items())),
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
    return 0 if status == "PASS" else 2


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    if args.worker:
        if not args.run_dir or not args.worker_output:
            parser.error("--run-dir and --worker-output are required in worker mode.")
        return _run_worker(args)
    return _run_master(args)


if __name__ == "__main__":
    raise SystemExit(main())
