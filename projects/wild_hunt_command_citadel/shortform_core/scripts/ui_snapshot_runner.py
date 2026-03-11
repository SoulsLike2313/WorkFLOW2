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


PAGE_KEYS = [
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_sizes(raw: str) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for token in raw.split(","):
        token = token.strip().lower()
        if not token:
            continue
        if "x" not in token:
            raise ValueError(f"Invalid size token: {token}")
        w_s, h_s = token.split("x", 1)
        result.append((int(w_s), int(h_s)))
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
        f"- Total screenshots: `{summary.get('screenshot_count', 0)}`",
        "",
        "## Artifacts",
        "",
        f"- Manifest: `{summary.get('manifest_path')}`",
        f"- Screenshots dir: `{summary.get('screenshots_dir')}`",
    ]
    failures = summary.get("failed_workers", [])
    if failures:
        lines.extend(["", "## Failed Workers", ""])
        for item in failures:
            lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def _run_master(args: argparse.Namespace) -> int:
    output_root = (PROJECT_ROOT / args.output_dir).resolve()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    started_at = _now_iso()
    scales = [item.strip() for item in args.scales.split(",") if item.strip()]
    commands: list[list[str]] = []
    failed_workers: list[str] = []
    all_screenshots: list[dict[str, Any]] = []

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
            "--api-base-url",
            args.api_base_url,
            "--wait-ms",
            str(args.wait_ms),
            "--run-dir",
            str(run_dir),
            "--worker-output",
            str(worker_output),
        ]
        commands.append(command)

        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        env["QT_SCALE_FACTOR"] = scale
        proc = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            failed_workers.append(f"scale={scale}")
            continue
        if not worker_output.exists():
            failed_workers.append(f"scale={scale} (missing worker output)")
            continue
        payload = json.loads(worker_output.read_text(encoding="utf-8"))
        all_screenshots.extend(payload.get("screenshots", []))

    finished = time.time()
    finished_at = _now_iso()
    duration_seconds = round(finished - started, 2)
    status = "PASS" if not failed_workers else "FAIL"

    manifest = {
        "run_id": run_id,
        "label": args.label,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration_seconds,
        "scales": scales,
        "sizes": args.sizes,
        "screenshots": all_screenshots,
    }
    screens_by_page: dict[str, int] = {}
    for shot in all_screenshots:
        page = str(shot.get("page", "unknown"))
        screens_by_page[page] = screens_by_page.get(page, 0) + 1
    manifest["screens_by_page"] = screens_by_page
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
        "failed_workers": failed_workers,
        "manifest_path": str(manifest_path.resolve()),
        "screenshots_dir": str((run_dir / "screenshots").resolve()),
        "commands": commands,
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


def _run_worker(args: argparse.Namespace) -> int:
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    from app.desktop.user_window import UserWorkspaceWindow

    run_dir = Path(args.run_dir).resolve()
    screenshots_dir = run_dir / "screenshots" / f"scale_{args.scale.replace('.', '_')}"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    app = QApplication([])
    window = UserWorkspaceWindow(api_base_url=args.api_base_url)
    if hasattr(window, "_auto_refresh"):
        window._auto_refresh.stop()

    screenshots: list[dict[str, Any]] = []
    sizes = _parse_sizes(args.sizes)

    for width, height in sizes:
        size_label = f"{width}x{height}"
        window.resize(width, height)
        window.show()
        QTest.qWait(args.wait_ms)
        app.processEvents()
        for page_key in PAGE_KEYS:
            window._switch_page(page_key)
            QTest.qWait(args.wait_ms)
            app.processEvents()
            image = window.grab()
            file_name = f"{page_key}_{size_label}_scale_{args.scale.replace('.', '_')}.png"
            out_path = screenshots_dir / file_name
            image.save(str(out_path))
            screenshots.append(
                {
                    "page": page_key,
                    "size": size_label,
                    "scale": args.scale,
                    "path": str(out_path.resolve()),
                    "sha256": _hash_file(out_path),
                    "width": width,
                    "height": height,
                    "captured_at": _now_iso(),
                }
            )

    window.close()
    app.quit()

    output = {
        "scale": args.scale,
        "sizes": args.sizes,
        "screenshots": screenshots,
    }
    Path(args.worker_output).resolve().write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture UI snapshots across screens/sizes/scales.")
    parser.add_argument("--worker", action="store_true", help="Internal worker mode.")
    parser.add_argument("--scale", default="1.0", help="Single scale for worker mode.")
    parser.add_argument("--scales", default="1.0,1.25,1.5", help="Comma-separated scales for master mode.")
    parser.add_argument("--sizes", default="1540x920,1366x768,1280x800", help="Comma-separated window sizes.")
    parser.add_argument("--api-base-url", default="http://127.0.0.1:9", help="API base URL.")
    parser.add_argument("--output-dir", default="runtime/ui_snapshots", help="Output directory for snapshot runs.")
    parser.add_argument("--run-dir", default="", help="Run directory for worker mode.")
    parser.add_argument("--worker-output", default="", help="Worker JSON output path.")
    parser.add_argument("--wait-ms", type=int, default=320, help="Wait between screen transitions.")
    parser.add_argument("--label", default="snapshot", help="Optional label for iteration tracking.")
    return parser


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
