from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


REQUIRED_CTA_BY_TAB: dict[str, list[str]] = {
    "Project": ["Create/Select Project", "Run Full Demo Pipeline"],
    "Scan": ["Run Scan", "Extract Strings"],
    "Asset Explorer": ["Refresh Asset Index"],
    "Entries": ["Detect Language", "Refresh"],
    "Translation": ["Translate to Russian", "Apply Correction"],
    "Voice": ["Generate Demo Voice Attempts", "Update Speaker Profile"],
    "Learning": ["Refresh Learning Snapshot"],
    "Glossary": ["Add Term"],
    "QA": ["Run QA Checks"],
    "Reports": ["Generate Reports", "Refresh Reports"],
    "Diagnostics": ["Refresh Diagnostics"],
    "Export": ["Export Patch Output"],
    "Jobs / Logs": ["Refresh Job States"],
    "Live Demo": ["Start Live Demo"],
    "Companion": ["Launch Companion Session", "Poll Status / Watch", "Stop Session"],
}

PRIMARY_ACTION_HINTS = [
    "Run",
    "Generate",
    "Translate",
    "Export",
    "Launch",
    "Start",
    "Create",
    "Detect",
    "Refresh",
]


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


@dataclass
class Issue:
    severity: str
    category: str
    tab: str
    description: str
    widget: str = ""
    screen_size: str = ""
    scale: str = ""
    screenshot_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "category": self.category,
            "tab": self.tab,
            "description": self.description,
            "widget": self.widget,
            "screen_size": self.screen_size,
            "scale": self.scale,
            "screenshot_path": self.screenshot_path,
        }


def _render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# UI Doctor Summary",
        "",
        f"- Run ID: `{summary.get('run_id')}`",
        f"- Status: `{summary.get('overall_status')}`",
        f"- Duration: `{summary.get('duration_seconds')}s`",
        f"- Scales: `{', '.join(summary.get('scales', []))}`",
        f"- Sizes: `{summary.get('sizes')}`",
        "",
        "## Severity",
        "",
    ]
    counts = summary.get("severity_counts", {})
    lines.append(f"- critical: {counts.get('critical', 0)}")
    lines.append(f"- major: {counts.get('major', 0)}")
    lines.append(f"- minor: {counts.get('minor', 0)}")

    category_counts = summary.get("issue_categories", {})
    lines.extend(["", "## Categories", ""])
    if category_counts:
        for category, count in sorted(category_counts.items()):
            lines.append(f"- {category}: {count}")
    else:
        lines.append("- none")

    lines.extend(["", "## Top Issues", ""])
    issues = summary.get("issues", [])
    if not issues:
        lines.append("- no issues detected")
    else:
        for issue in issues[:120]:
            lines.append(
                f"- [{issue.get('severity')}] {issue.get('tab')} / {issue.get('category')}: {issue.get('description')}"
            )

    lines.extend(["", "## Artifacts", ""])
    for key, value in (summary.get("artifacts", {}) or {}).items():
        lines.append(f"- {key}: `{value}`")

    return "\n".join(lines).strip() + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GameRuAI UI doctor: detect layout and usability regressions.")
    parser.add_argument("--worker", action="store_true", help="Internal worker mode.")
    parser.add_argument("--scale", default="1.0", help="Scale for worker mode.")
    parser.add_argument("--scales", default="1.0,1.25,1.5", help="Scales for master mode.")
    parser.add_argument("--sizes", default="1600x960,1366x768,1280x800", help="Window sizes (comma-separated).")
    parser.add_argument("--output-dir", default="runtime/ui_validation", help="Output root for doctor runs.")
    parser.add_argument("--run-dir", default="", help="Run directory for worker mode.")
    parser.add_argument("--worker-output", default="", help="Worker JSON output path.")
    parser.add_argument("--wait-ms", type=int, default=250, help="Wait between checks.")
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
            tree.setCurrentItem(tree.topLevelItem(0))
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
    from PySide6.QtCore import QPoint, QRect
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import (
        QApplication,
        QAbstractButton,
        QComboBox,
        QLabel,
        QLineEdit,
        QPlainTextEdit,
        QPushButton,
        QSplitter,
        QTableWidget,
        QTextEdit,
        QTreeWidget,
        QWidget,
    )

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

    issues: list[Issue] = []
    screenshots: list[dict[str, Any]] = []
    cta_presence_by_tab: dict[str, list[int]] = {}

    def _wait() -> None:
        QTest.qWait(args.wait_ms)
        app.processEvents()

    def _widget_id(widget: QWidget | None) -> str:
        if widget is None:
            return ""
        return f"{widget.__class__.__name__}::{widget.objectName() or 'anon'}"

    def _add_issue(
        *,
        severity: str,
        category: str,
        tab_name: str,
        description: str,
        size_label: str,
        shot_path: str,
        widget: QWidget | None = None,
    ) -> None:
        issues.append(
            Issue(
                severity=severity,
                category=category,
                tab=tab_name,
                description=description,
                widget=_widget_id(widget),
                screen_size=size_label,
                scale=args.scale,
                screenshot_path=shot_path,
            )
        )

    def _visible_buttons(tab_widget: QWidget) -> list[QPushButton]:
        return [button for button in tab_widget.findChildren(QPushButton) if button.isVisible() and button.width() > 0]

    def _find_button(tab_widget: QWidget, text_fragment: str) -> QPushButton | None:
        needle = text_fragment.strip().lower()
        for button in _visible_buttons(tab_widget):
            text = (button.text() or "").strip().lower()
            if needle in text:
                return button
        return None

    def _is_layout_anchored(button: QPushButton) -> bool:
        parent = button.parentWidget()
        if parent is None:
            return False
        layout = parent.layout()
        if layout is None:
            return False
        return layout.indexOf(button) >= 0

    for width, height in sizes:
        window.resize(width, height)
        window.show()
        _wait()

        size_label = f"{width}x{height}"
        tab_count = window.tabs.count()

        for tab_index in range(tab_count):
            window.tabs.setCurrentIndex(tab_index)
            tab_name = window.tabs.tabText(tab_index)
            tab_widget = window.tabs.currentWidget()
            if not isinstance(tab_widget, QWidget):
                continue

            _prime_tab_state(window, tab_name)
            _wait()

            file_name = f"doctor_tab_{tab_index:02d}_{_slug(tab_name)}__{size_label}__scale_{args.scale.replace('.', '_')}.png"
            out_path = screenshots_dir / file_name
            window.grab().save(str(out_path))
            shot_path = str(out_path.resolve())

            screenshots.append(
                {
                    "tab_index": tab_index,
                    "tab_name": tab_name,
                    "size": size_label,
                    "scale": args.scale,
                    "path": shot_path,
                    "sha256": _hash_file(out_path),
                    "captured_at": _now_iso(),
                }
            )

            required_cta = REQUIRED_CTA_BY_TAB.get(tab_name, [])
            found_count = 0
            for cta in required_cta:
                button = _find_button(tab_widget, cta)
                if button is None:
                    _add_issue(
                        severity="critical",
                        category="missing_critical_cta",
                        tab_name=tab_name,
                        description=f"Critical CTA '{cta}' is not visible.",
                        size_label=size_label,
                        shot_path=shot_path,
                    )
                    continue

                found_count += 1
                if not _is_layout_anchored(button):
                    _add_issue(
                        severity="major",
                        category="floating_critical_cta",
                        tab_name=tab_name,
                        description=f"CTA '{button.text()}' is not layout-anchored to its parent.",
                        size_label=size_label,
                        shot_path=shot_path,
                        widget=button,
                    )

                before_visible = button.isVisible() and button.width() > 0 and button.height() > 0
                QTest.mouseMove(button, button.rect().center())
                _wait()
                QTest.mouseMove(tab_widget, QPoint(3, 3))
                _wait()
                after_visible = button.isVisible() and button.width() > 0 and button.height() > 0
                if before_visible and not after_visible:
                    _add_issue(
                        severity="critical",
                        category="hover_only_critical_cta",
                        tab_name=tab_name,
                        description=f"CTA '{button.text()}' disappears when hover is lost.",
                        size_label=size_label,
                        shot_path=shot_path,
                        widget=button,
                    )

            cta_presence_by_tab.setdefault(tab_name, []).append(found_count)

            if tab_widget.layout() is None:
                _add_issue(
                    severity="major",
                    category="missing_root_layout",
                    tab_name=tab_name,
                    description="Tab root layout is missing.",
                    size_label=size_label,
                    shot_path=shot_path,
                    widget=tab_widget,
                )

            visible_buttons = _visible_buttons(tab_widget)
            visible_structural_widgets = [
                widget
                for widget in tab_widget.findChildren(QWidget)
                if widget.isVisible()
                and isinstance(
                    widget,
                    (QPushButton, QLineEdit, QTextEdit, QPlainTextEdit, QTableWidget, QTreeWidget, QComboBox),
                )
            ]
            if not visible_structural_widgets:
                _add_issue(
                    severity="critical",
                    category="empty_or_broken_zone",
                    tab_name=tab_name,
                    description="No visible interactive/content widgets detected in tab.",
                    size_label=size_label,
                    shot_path=shot_path,
                    widget=tab_widget,
                )

            if len(visible_buttons) >= 3:
                if not any(any(hint.lower() in (button.text() or "").lower() for hint in PRIMARY_ACTION_HINTS) for button in visible_buttons):
                    _add_issue(
                        severity="minor",
                        category="weak_action_hierarchy",
                        tab_name=tab_name,
                        description="Tab has many controls but no clear primary action label.",
                        size_label=size_label,
                        shot_path=shot_path,
                        widget=tab_widget,
                    )

            for label in tab_widget.findChildren(QLabel):
                if not label.isVisible():
                    continue
                text = (label.text() or "").strip()
                if not text:
                    continue
                if "\ufffd" in text:
                    _add_issue(
                        severity="major",
                        category="font_or_localization_glyph_issue",
                        tab_name=tab_name,
                        description=f"Label contains replacement glyphs: '{text[:60]}'.",
                        size_label=size_label,
                        shot_path=shot_path,
                        widget=label,
                    )
                if not label.wordWrap() and label.width() + 2 < label.sizeHint().width():
                    _add_issue(
                        severity="major",
                        category="text_clipping",
                        tab_name=tab_name,
                        description=f"Label text appears clipped: '{text[:80]}'.",
                        size_label=size_label,
                        shot_path=shot_path,
                        widget=label,
                    )

            for button in tab_widget.findChildren(QAbstractButton):
                if not button.isVisible():
                    continue
                text = (button.text() or "").replace("&", "").strip()
                if text and button.width() + 2 < button.sizeHint().width():
                    _add_issue(
                        severity="major",
                        category="button_clipping",
                        tab_name=tab_name,
                        description=f"Button text appears clipped: '{text[:80]}'.",
                        size_label=size_label,
                        shot_path=shot_path,
                        widget=button,
                    )

            tab_rect = tab_widget.rect()
            check_widgets: list[QWidget] = []
            for widget_type in (QPushButton, QLineEdit, QTextEdit, QPlainTextEdit, QTableWidget, QTreeWidget, QComboBox):
                check_widgets.extend([widget for widget in tab_widget.findChildren(widget_type) if widget.isVisible()])

            for widget in check_widgets:
                top_left = widget.mapTo(tab_widget, QPoint(0, 0))
                widget_rect = QRect(top_left, widget.size())
                if widget_rect.right() > tab_rect.right() + 2 or widget_rect.bottom() > tab_rect.bottom() + 2:
                    _add_issue(
                        severity="major",
                        category="overflow_out_of_bounds",
                        tab_name=tab_name,
                        description="Interactive widget extends beyond tab bounds.",
                        size_label=size_label,
                        shot_path=shot_path,
                        widget=widget,
                    )
                if widget_rect.left() < -2 or widget_rect.top() < -2:
                    _add_issue(
                        severity="major",
                        category="negative_widget_position",
                        tab_name=tab_name,
                        description="Interactive widget has a negative position in tab coordinates.",
                        size_label=size_label,
                        shot_path=shot_path,
                        widget=widget,
                    )

            interactive: list[QWidget] = []
            for widget_type in (QPushButton, QComboBox, QLineEdit):
                interactive.extend([widget for widget in tab_widget.findChildren(widget_type) if widget.isVisible()])

            for idx, first in enumerate(interactive):
                for second in interactive[idx + 1 :]:
                    if first.parentWidget() is None or second.parentWidget() is None:
                        continue
                    if first.parentWidget() is not second.parentWidget():
                        continue
                    first_rect = QRect(first.mapTo(tab_widget, QPoint(0, 0)), first.size())
                    second_rect = QRect(second.mapTo(tab_widget, QPoint(0, 0)), second.size())
                    overlap = first_rect.intersected(second_rect)
                    if overlap.isValid() and overlap.width() * overlap.height() > 36:
                        _add_issue(
                            severity="major",
                            category="sibling_overlap",
                            tab_name=tab_name,
                            description="Sibling interactive widgets overlap each other.",
                            size_label=size_label,
                            shot_path=shot_path,
                            widget=first,
                        )

            for splitter in tab_widget.findChildren(QSplitter):
                split_sizes = splitter.sizes()
                if split_sizes and min(split_sizes) < 110:
                    _add_issue(
                        severity="major",
                        category="splitter_collapse",
                        tab_name=tab_name,
                        description=f"Splitter section collapsed below 110px ({split_sizes}).",
                        size_label=size_label,
                        shot_path=shot_path,
                        widget=splitter,
                    )

    # Cross-size stability checks for required CTA visibility.
    for tab_name, counts in cta_presence_by_tab.items():
        if len(counts) <= 1:
            continue
        if min(counts) != max(counts):
            issues.append(
                Issue(
                    severity="major",
                    category="resize_instability",
                    tab=tab_name,
                    description=f"Required CTA count changed across sizes: {counts}.",
                    screen_size="multi",
                    scale=args.scale,
                    screenshot_path="",
                )
            )

    window.close()
    services.close()
    app.quit()

    payload = {
        "scale": args.scale,
        "sizes": args.sizes,
        "issues": [issue.as_dict() for issue in issues],
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

    all_issues: list[dict[str, Any]] = []
    all_screenshots: list[dict[str, Any]] = []
    failed_workers: list[str] = []
    commands: list[list[str]] = []

    scales = [token.strip() for token in args.scales.split(",") if token.strip()]
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
            all_issues.append(
                Issue(
                    severity="critical",
                    category="worker_failure",
                    tab="all",
                    description=f"Worker failed at scale={scale}.",
                    scale=scale,
                ).as_dict()
            )
            continue
        if not worker_output.exists():
            failed_workers.append(f"scale={scale} (missing worker output)")
            all_issues.append(
                Issue(
                    severity="critical",
                    category="worker_output_missing",
                    tab="all",
                    description=f"Worker output is missing at scale={scale}.",
                    scale=scale,
                ).as_dict()
            )
            continue

        payload = json.loads(worker_output.read_text(encoding="utf-8"))
        all_issues.extend(payload.get("issues", []))
        all_screenshots.extend(payload.get("screenshots", []))

    severity_counts = {"critical": 0, "major": 0, "minor": 0}
    issue_categories: dict[str, int] = {}
    tab_issue_counts: dict[str, dict[str, int]] = {}

    for issue in all_issues:
        severity = str(issue.get("severity", "minor")).lower()
        category = str(issue.get("category", "unknown"))
        tab_name = str(issue.get("tab", "unknown"))

        if severity not in severity_counts:
            severity = "minor"
        severity_counts[severity] += 1
        issue_categories[category] = issue_categories.get(category, 0) + 1

        tab_issue_counts.setdefault(tab_name, {"critical": 0, "major": 0, "minor": 0})
        tab_issue_counts[tab_name][severity] += 1

    shots_by_tab: dict[str, int] = {}
    for shot in all_screenshots:
        tab_name = str(shot.get("tab_name", "unknown"))
        shots_by_tab[tab_name] = shots_by_tab.get(tab_name, 0) + 1

    if severity_counts["critical"] > 0 or failed_workers:
        overall_status = "FAIL"
    elif severity_counts["major"] > 0:
        overall_status = "PASS_WITH_WARNINGS"
    else:
        overall_status = "PASS"

    finished_at = _now_iso()
    duration_seconds = round(time.time() - started, 2)

    manifest = {
        "run_id": run_id,
        "generated_at": finished_at,
        "sizes": args.sizes,
        "scales": scales,
        "screenshots": all_screenshots,
        "screenshots_by_tab": dict(sorted(shots_by_tab.items())),
    }
    manifest_path = run_dir / "ui_screenshots_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration_seconds,
        "overall_status": overall_status,
        "manual_acceptance_recommended": overall_status != "FAIL",
        "project_root": str(PROJECT_ROOT),
        "scales": scales,
        "sizes": args.sizes,
        "commands": commands,
        "failed_workers": failed_workers,
        "severity_counts": severity_counts,
        "issue_categories": dict(sorted(issue_categories.items())),
        "tab_issue_counts": tab_issue_counts,
        "screenshots_by_tab": dict(sorted(shots_by_tab.items())),
        "issues": all_issues,
        "artifacts": {
            "ui_doctor_summary": str((run_dir / "ui_doctor_summary.json").resolve()),
            "ui_validation_summary": str((run_dir / "ui_validation_summary.json").resolve()),
            "ui_validation_summary_md": str((run_dir / "ui_validation_summary.md").resolve()),
            "ui_screenshots_manifest": str(manifest_path.resolve()),
            "run_dir": str(run_dir.resolve()),
        },
    }

    doctor_summary_path = run_dir / "ui_doctor_summary.json"
    validation_summary_path = run_dir / "ui_validation_summary.json"
    validation_summary_md_path = run_dir / "ui_validation_summary.md"
    doctor_summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    validation_summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    validation_summary_md_path.write_text(_render_summary_md(summary), encoding="utf-8")

    latest = {
        "run_id": run_id,
        "status": overall_status,
        "path": str(run_dir.resolve()),
        "summary_path": str(doctor_summary_path.resolve()),
        "timestamp": finished_at,
    }
    (output_root / "latest_run.json").write_text(json.dumps(latest, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_root / "latest_run.txt").write_text(str(run_dir.resolve()) + "\n", encoding="utf-8")

    print(str(run_dir.resolve()))
    print(f"UI doctor status: {overall_status}")
    return 0 if overall_status != "FAIL" else 2


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
