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


def _repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


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


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _sanitize_token(value: str) -> str:
    sanitized = []
    for char in value.lower():
        if char.isalnum() or char in {"_", "-", "."}:
            sanitized.append(char)
        else:
            sanitized.append("_")
    while "__" in "".join(sanitized):
        sanitized = list("".join(sanitized).replace("__", "_"))
    return "".join(sanitized).strip("_") or "state"


def _extract_run_dir(stdout_text: str) -> Path | None:
    for line in stdout_text.splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        maybe_path = Path(candidate)
        if not maybe_path.is_absolute():
            maybe_path = (PROJECT_ROOT / maybe_path).resolve()
        if maybe_path.exists() and maybe_path.is_dir():
            return maybe_path
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
        f"- Total screenshots: `{summary.get('screenshot_count', 0)}`",
        f"- Walkthrough steps: `{summary.get('walkthrough_step_count', 0)}`",
        "",
        "## Coverage by Screen",
        "",
    ]
    coverage = summary.get("state_coverage", {})
    if not isinstance(coverage, dict) or not coverage:
        lines.append("- no coverage entries")
    else:
        for screen_name, states in coverage.items():
            state_line = ", ".join(_safe_list(states)) if _safe_list(states) else "-"
            lines.append(f"- {screen_name}: `{state_line}`")

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Manifest: `{summary.get('manifest_path')}`",
            f"- Walkthrough trace: `{summary.get('walkthrough_trace_path')}`",
            f"- Screenshots dir: `{summary.get('screenshots_dir')}`",
        ]
    )

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
    all_trace: list[dict[str, Any]] = []
    coverage_map: dict[str, set[str]] = {}

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
        commands.append(
            [
                "python",
                "scripts/ui_snapshot_runner.py",
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
                _repo_relative(run_dir),
                "--worker-output",
                _repo_relative(worker_output),
            ]
        )

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
        worker_shots = _safe_list(payload.get("screenshots"))
        worker_trace = _safe_list(payload.get("walkthrough_trace"))
        all_screenshots.extend(worker_shots)
        all_trace.extend(worker_trace)
        worker_coverage = payload.get("state_coverage", {})
        if isinstance(worker_coverage, dict):
            for screen_name, states in worker_coverage.items():
                screen = _safe_str(screen_name) or "unknown"
                coverage_map.setdefault(screen, set())
                for state_name in _safe_list(states):
                    state = _safe_str(state_name)
                    if state:
                        coverage_map[screen].add(state)

    finished = time.time()
    finished_at = _now_iso()
    duration_seconds = round(finished - started, 2)
    status = "PASS" if not failed_workers else "FAIL"

    sorted_trace: list[dict[str, Any]] = []
    for idx, step in enumerate(all_trace, start=1):
        if not isinstance(step, dict):
            continue
        entry = dict(step)
        entry["step_index"] = idx
        sorted_trace.append(entry)
    trace_path = run_dir / "ui_walkthrough_trace.json"
    trace_payload = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "steps": sorted_trace,
    }
    trace_path.write_text(json.dumps(trace_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    coverage_sorted = {
        screen: sorted(list(states))
        for screen, states in sorted(coverage_map.items(), key=lambda pair: pair[0])
    }
    screens_by_page: dict[str, int] = {}
    for shot in all_screenshots:
        page = _safe_str(shot.get("screen_name") or shot.get("page") or "unknown")
        screens_by_page[page] = screens_by_page.get(page, 0) + 1

    manifest = {
        "run_id": run_id,
        "label": args.label,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration_seconds,
        "scales": scales,
        "sizes": args.sizes,
        "review_scope": "ui_snapshots",
        "screenshots": all_screenshots,
        "screens_by_page": screens_by_page,
        "state_coverage": coverage_sorted,
        "walkthrough_trace_path": _repo_relative(trace_path),
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
        "walkthrough_step_count": len(sorted_trace),
        "failed_workers": failed_workers,
        "state_coverage": coverage_sorted,
        "manifest_path": _repo_relative(manifest_path),
        "walkthrough_trace_path": _repo_relative(trace_path),
        "screenshots_dir": _repo_relative(run_dir / "screenshots"),
        "commands": commands,
    }
    summary_json = run_dir / "ui_snapshot_summary.json"
    summary_md = run_dir / "ui_snapshot_summary.md"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_md.write_text(_render_summary_md(summary), encoding="utf-8")

    latest = {
        "run_id": run_id,
        "status": status,
        "path": _repo_relative(run_dir),
        "manifest_path": _repo_relative(manifest_path),
        "summary_path": _repo_relative(summary_json),
        "walkthrough_trace_path": _repo_relative(trace_path),
        "timestamp": finished_at,
    }
    (output_root / "latest_run.json").write_text(json.dumps(latest, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_root / "latest_run.txt").write_text(_repo_relative(run_dir) + "\n", encoding="utf-8")

    print(_repo_relative(run_dir))
    print(f"UI snapshot status: {status}")
    return 0 if status == "PASS" else 2


def _run_worker(args: argparse.Namespace) -> int:
    from PySide6.QtCore import QPoint
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QAbstractItemView, QApplication, QLabel, QListWidget, QPushButton, QTableWidget

    from app.desktop.user_window import UserWorkspaceWindow

    run_dir = Path(args.run_dir).resolve()
    screenshots_dir = run_dir / "screenshots" / f"scale_{args.scale.replace('.', '_')}"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    app = QApplication([])
    window = UserWorkspaceWindow(api_base_url=args.api_base_url)
    if hasattr(window, "_auto_refresh"):
        window._auto_refresh.stop()

    screenshots: list[dict[str, Any]] = []
    walkthrough: list[dict[str, Any]] = []
    state_coverage: dict[str, set[str]] = {}
    sizes = _parse_sizes(args.sizes)
    worker_step = 0

    def wait_ui(ms: int) -> None:
        QTest.qWait(ms)
        app.processEvents()

    def add_trace(
        *,
        screen: str,
        action: str,
        result: str,
        notes: str,
        screenshot_ref: str | None = None,
    ) -> None:
        nonlocal worker_step
        worker_step += 1
        walkthrough.append(
            {
                "run_id": "",
                "worker_scale": args.scale,
                "step_index": worker_step,
                "screen": screen,
                "action": action,
                "result": result,
                "screenshot_ref": screenshot_ref,
                "timestamp": _now_iso(),
                "notes": notes,
            }
        )

    def capture(
        *,
        screen_name: str,
        state_name: str,
        size_label: str,
        notes: str,
        tags: list[str],
        importance: str,
        scenario_reference: str,
        issue_reference: str | None = None,
    ) -> dict[str, Any]:
        state_token = _sanitize_token(state_name)
        file_name = f"{screen_name}_{state_token}_{size_label}_scale_{args.scale.replace('.', '_')}.png"
        out_path = screenshots_dir / file_name
        image = window.grab()
        image.save(str(out_path))
        captured_at = _now_iso()
        record = {
            "screen_name": screen_name,
            "state_name": state_name,
            "page": screen_name,
            "size": size_label,
            "scale": args.scale,
            "path": _repo_relative(out_path),
            "screenshot_path": _repo_relative(out_path),
            "sha256": _hash_file(out_path),
            "width": int(size_label.split("x")[0]),
            "height": int(size_label.split("x")[1]),
            "timestamp": captured_at,
            "captured_at": captured_at,
            "notes": notes,
            "tags": tags,
            "importance": importance,
            "scenario_reference": scenario_reference,
            "severity_reference": "none",
            "issue_reference": issue_reference,
        }
        screenshots.append(record)
        state_coverage.setdefault(screen_name, set()).add(state_name)
        return record

    def visible_item_views(page_widget: Any) -> list[QAbstractItemView]:
        views = []
        for view in page_widget.findChildren(QAbstractItemView):
            if view.isVisible():
                views.append(view)
        return views

    def view_item_count(view: QAbstractItemView) -> int:
        if hasattr(view, "count"):
            try:
                return int(getattr(view, "count")())
            except Exception:
                return 0
        if hasattr(view, "rowCount"):
            try:
                return int(getattr(view, "rowCount")())
            except Exception:
                return 0
        model = view.model()
        if model is None:
            return 0
        try:
            return int(model.rowCount())
        except Exception:
            return 0

    for width, height in sizes:
        size_label = f"{width}x{height}"
        window.resize(width, height)
        window.show()
        wait_ui(args.wait_ms)
        add_trace(
            screen="dashboard",
            action="boot_window",
            result="pass",
            notes=f"window shown at {size_label} scale={args.scale}",
        )

        window._switch_page("dashboard")
        wait_ui(args.wait_ms)
        initial = capture(
            screen_name="dashboard",
            state_name="initial_state",
            size_label=size_label,
            notes="initial workspace state after boot",
            tags=["ui_snapshot", "state:initial", "screen:dashboard"],
            importance="high",
            scenario_reference="boot_initial_state",
        )
        add_trace(
            screen="dashboard",
            action="capture_initial_state",
            result="pass",
            screenshot_ref=initial["screenshot_path"],
            notes="initial dashboard state captured",
        )

        for page_key in PAGE_KEYS:
            window._switch_page(page_key)
            wait_ui(args.wait_ms)
            add_trace(
                screen=page_key,
                action="switch_page",
                result="pass",
                notes=f"page switched for {size_label}",
            )

            loaded = capture(
                screen_name=page_key,
                state_name="loaded_state",
                size_label=size_label,
                notes="loaded page state after navigation",
                tags=["ui_snapshot", "state:loaded", f"screen:{page_key}", f"size:{size_label}", f"scale:{args.scale}"],
                importance="high",
                scenario_reference="core_navigation",
            )
            add_trace(
                screen=page_key,
                action="capture_loaded_state",
                result="pass",
                screenshot_ref=loaded["screenshot_path"],
                notes="loaded state captured",
            )

            page_widget = window._pages.get(page_key) if hasattr(window, "_pages") else None
            if page_widget is None:
                add_trace(
                    screen=page_key,
                    action="resolve_page_widget",
                    result="fail",
                    notes="page widget missing in registry",
                )
                continue

            item_views = visible_item_views(page_widget)
            if item_views:
                for view in item_views:
                    view.clearSelection()
                wait_ui(90)
                selected_count = sum(len(view.selectedIndexes()) for view in item_views)
                no_selection = capture(
                    screen_name=page_key,
                    state_name="no_selection_state",
                    size_label=size_label,
                    notes="selection cleared across visible item views",
                    tags=["ui_snapshot", "state:no_selection", f"screen:{page_key}"],
                    importance="medium",
                    scenario_reference="selection_reset",
                )
                add_trace(
                    screen=page_key,
                    action="verify_no_selection_state",
                    result="pass" if selected_count == 0 else "warning",
                    screenshot_ref=no_selection["screenshot_path"],
                    notes=f"selected indexes after clearSelection={selected_count}",
                )
            else:
                add_trace(
                    screen=page_key,
                    action="verify_no_selection_state",
                    result="not_applicable",
                    notes="page has no visible item views",
                )

            dense_available = False
            if item_views:
                for view in item_views:
                    total_items = view_item_count(view)
                    if total_items <= 1:
                        continue
                    if isinstance(view, QListWidget):
                        view.setCurrentRow(total_items - 1)
                        if view.item(total_items - 1) is not None:
                            view.scrollToItem(view.item(total_items - 1))
                        dense_available = True
                    elif isinstance(view, QTableWidget):
                        view.selectRow(total_items - 1)
                        cell = view.item(total_items - 1, 0)
                        if cell is not None:
                            view.scrollToItem(cell)
                        dense_available = True
                if dense_available:
                    wait_ui(90)
                    dense = capture(
                        screen_name=page_key,
                        state_name="dense_state",
                        size_label=size_label,
                        notes="dense state captured after selecting/scanning bottom items",
                        tags=["ui_snapshot", "state:dense", f"screen:{page_key}"],
                        importance="medium",
                        scenario_reference="dense_content_probe",
                    )
                    add_trace(
                        screen=page_key,
                        action="capture_dense_state",
                        result="pass",
                        screenshot_ref=dense["screenshot_path"],
                        notes="dense list/table state captured",
                    )
                else:
                    add_trace(
                        screen=page_key,
                        action="capture_dense_state",
                        result="not_available",
                        notes="visible item views exist but not enough rows/items for dense probe",
                    )
            else:
                add_trace(
                    screen=page_key,
                    action="capture_dense_state",
                    result="not_applicable",
                    notes="page has no list/table widgets",
                )

            if item_views:
                all_empty = all(view_item_count(view) == 0 for view in item_views)
                if all_empty:
                    empty_shot = capture(
                        screen_name=page_key,
                        state_name="empty_state",
                        size_label=size_label,
                        notes="all visible item views are empty",
                        tags=["ui_snapshot", "state:empty", f"screen:{page_key}"],
                        importance="medium",
                        scenario_reference="empty_state_probe",
                    )
                    add_trace(
                        screen=page_key,
                        action="capture_empty_state",
                        result="pass",
                        screenshot_ref=empty_shot["screenshot_path"],
                        notes="empty state detected and captured",
                    )
                else:
                    add_trace(
                        screen=page_key,
                        action="capture_empty_state",
                        result="not_available",
                        notes="page contains loaded rows/items; empty state not available",
                    )
            else:
                add_trace(
                    screen=page_key,
                    action="capture_empty_state",
                    result="not_applicable",
                    notes="page has no item views for empty-state detection",
                )

            clipping_hits: list[str] = []
            for label in page_widget.findChildren(QLabel):
                if not label.isVisible() or label.wordWrap():
                    continue
                text = _safe_str(label.text())
                if not text:
                    continue
                if label.width() + 1 < label.sizeHint().width():
                    clipping_hits.append(f"label:{text[:60]}")
                    if len(clipping_hits) >= 4:
                        break
            if len(clipping_hits) < 4:
                for button in page_widget.findChildren(QPushButton):
                    if not button.isVisible():
                        continue
                    text = _safe_str(button.text()).replace("&", "")
                    if not text:
                        continue
                    if button.width() + 1 < button.sizeHint().width():
                        clipping_hits.append(f"button:{text[:60]}")
                        if len(clipping_hits) >= 4:
                            break
            if clipping_hits:
                anomaly = capture(
                    screen_name=page_key,
                    state_name="anomaly_state",
                    size_label=size_label,
                    notes="possible clipping detected: " + "; ".join(clipping_hits),
                    tags=["ui_snapshot", "state:anomaly", f"screen:{page_key}"],
                    importance="high",
                    scenario_reference="anomaly_capture",
                    issue_reference=f"snapshot:clipping:{page_key}:{size_label}:scale_{args.scale}",
                )
                add_trace(
                    screen=page_key,
                    action="capture_anomaly_state",
                    result="warning",
                    screenshot_ref=anomaly["screenshot_path"],
                    notes="anomaly screenshot captured for clipping review",
                )
            else:
                add_trace(
                    screen=page_key,
                    action="capture_anomaly_state",
                    result="pass",
                    notes="no clipping anomalies detected by snapshot probe",
                )

    window.close()
    app.quit()

    output = {
        "scale": args.scale,
        "sizes": args.sizes,
        "screenshots": screenshots,
        "walkthrough_trace": walkthrough,
        "state_coverage": {screen: sorted(list(states)) for screen, states in state_coverage.items()},
    }
    Path(args.worker_output).resolve().write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture UI snapshots across screens, states, sizes and scales.")
    parser.add_argument("--worker", action="store_true", help="Internal worker mode.")
    parser.add_argument("--scale", default="1.0", help="Single scale for worker mode.")
    parser.add_argument("--scales", default="1.0,1.25,1.5", help="Comma-separated scales for master mode.")
    parser.add_argument("--sizes", default="1540x920,1366x768,1280x800", help="Comma-separated window sizes.")
    parser.add_argument("--api-base-url", default="http://127.0.0.1:9", help="API base URL.")
    parser.add_argument("--output-dir", default="runtime/ui_snapshots", help="Output directory for snapshot runs.")
    parser.add_argument("--run-dir", default="", help="Run directory for worker mode.")
    parser.add_argument("--worker-output", default="", help="Worker JSON output path.")
    parser.add_argument("--wait-ms", type=int, default=320, help="Wait between transitions.")
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
