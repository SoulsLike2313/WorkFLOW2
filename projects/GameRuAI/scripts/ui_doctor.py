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

from scripts.ui_qa_product import apply_scenario_state, expected_screen_names, scenario_catalog

REQUIRED_CTA_BY_SCREEN: dict[str, list[str]] = {
    "Project": ["Create/Select Project", "Run Full Demo Pipeline"],
    "Scan": ["Run Scan", "Extract Strings"],
    "Asset Explorer": ["Refresh Asset Index"],
    "Entries": ["Detect Language", "Refresh"],
    "Language Hub": ["Refresh Language Blocks"],
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

CATEGORY_META: dict[str, tuple[str, str]] = {
    "navigation_missing_screen": ("navigation", "Restore missing tab in MainWindow and keep tab order stable."),
    "missing_critical_cta": ("cta", "Expose critical CTA in viewport; avoid hidden or collapsed actions."),
    "hover_only_critical_cta": ("cta", "Make critical CTA persistent without hover dependency."),
    "floating_critical_cta": ("layout", "Attach CTA to layout container; avoid absolute geometry drift."),
    "missing_root_layout": ("layout", "Ensure each screen has a root layout."),
    "empty_or_broken_zone": ("visibility", "Show meaningful content area, not empty placeholders."),
    "text_clipping": ("typography", "Enable wrapping/eliding or increase width for text labels."),
    "button_clipping": ("typography", "Increase button min width or shorten label."),
    "overflow_out_of_bounds": ("overflow", "Constrain child widgets to screen bounds and splitter limits."),
    "sibling_overlap": ("layout", "Adjust spacing/size policies to remove overlaps."),
    "splitter_collapse": ("layout", "Set minimum splitter sizes for critical panes."),
    "tight_spacing": ("spacing", "Increase spacing/margins in dense control rows."),
    "font_or_localization_glyph_issue": ("localization", "Use glyph-complete font and UTF-8 safe strings."),
    "localization_missing_ru_content": ("localization", "Ensure RU text renders in translation-heavy states."),
    "state_expected_loaded": ("state_handling", "Populate loaded state and refresh dependent widgets."),
    "state_expected_empty": ("state_handling", "Keep clear empty-state guidance before project loading."),
    "state_incorrect_filter": ("state_handling", "Apply filters consistently and refresh data."),
    "state_summary_missing": ("state_handling", "Fill summary/info zones for current state."),
    "state_selection_missing": ("state_handling", "Update details area when selection changes."),
}

SEVERITY_WEIGHT = {"critical": 0, "major": 1, "minor": 2}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in value.lower()).strip("_") or "item"


def _parse_sizes(raw: str) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for token in raw.split(","):
        token = token.strip().lower()
        if not token:
            continue
        if "x" not in token:
            raise ValueError(f"Invalid size token: {token}")
        w_raw, h_raw = token.split("x", 1)
        result.append((int(w_raw), int(h_raw)))
    if not result:
        raise ValueError("No sizes provided")
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


def _contains_cyrillic(text: str) -> bool:
    return any("\u0400" <= ch <= "\u04FF" for ch in text)


@dataclass
class Issue:
    severity: str
    category: str
    issue_type: str
    recommendation: str
    screen_name: str
    state_name: str
    description: str
    widget: str = ""
    screen_size: str = ""
    scale: str = ""
    screenshot_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "category": self.category,
            "issue_type": self.issue_type,
            "recommendation": self.recommendation,
            "screen_name": self.screen_name,
            "state_name": self.state_name,
            "description": self.description,
            "widget": self.widget,
            "screen_size": self.screen_size,
            "scale": self.scale,
            "screenshot_path": self.screenshot_path,
        }


def _issue_meta(category: str) -> tuple[str, str]:
    return CATEGORY_META.get(category, ("layout", "Review layout constraints and rerun UI doctor."))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GameRuAI UI doctor (product-specific)")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--scale", default="1.0")
    parser.add_argument("--scales", default="1.0,1.25,1.5")
    parser.add_argument("--sizes", default="1600x960,1366x768,1280x800")
    parser.add_argument("--output-dir", default="runtime/ui_validation")
    parser.add_argument("--run-dir", default="")
    parser.add_argument("--worker-output", default="")
    parser.add_argument("--wait-ms", type=int, default=250)
    parser.add_argument("--project-name", default="GameRuAI UI-QA Project")
    return parser


def _render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# UI Doctor Summary",
        "",
        f"- Run ID: `{summary.get('run_id')}`",
        f"- Status: `{summary.get('overall_status')}`",
        f"- Duration: `{summary.get('duration_seconds')}s`",
        "",
        "## Severity",
        f"- critical: {summary.get('severity_counts', {}).get('critical', 0)}",
        f"- major: {summary.get('severity_counts', {}).get('major', 0)}",
        f"- minor: {summary.get('severity_counts', {}).get('minor', 0)}",
        "",
        "## Issues By Screen",
    ]
    for screen, counts in sorted((summary.get("issues_by_screen") or {}).items()):
        lines.append(f"- {screen}: critical={counts.get('critical', 0)}, major={counts.get('major', 0)}, minor={counts.get('minor', 0)}")
    lines.extend(["", "## Issues By Type"])
    for issue_type, count in sorted((summary.get("issues_by_type") or {}).items()):
        lines.append(f"- {issue_type}: {count}")
    lines.extend(["", "## Top Recommendations"])
    recs = summary.get("fix_recommendations", [])
    if recs:
        for rec in recs:
            lines.append(f"- [{rec.get('issue_type')}] {rec.get('count')}x: {rec.get('recommendation')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Top Issues"])
    for issue in (summary.get("top_issues") or [])[:25]:
        lines.append(f"- [{issue.get('severity')}] {issue.get('screen_name')}::{issue.get('state_name')} / {issue.get('category')}: {issue.get('description')}")
    lines.extend(["", "## Artifacts"])
    for key, value in (summary.get("artifacts") or {}).items():
        lines.append(f"- {key}: `{value}`")
    return "\n".join(lines).strip() + "\n"

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
    scenarios = scenario_catalog()

    config = AppConfig.load()
    ensure_demo_assets(config)
    services = AppServices(config)
    app = QApplication([])
    window = MainWindow(services)

    issues: list[Issue] = []
    captures: list[dict[str, Any]] = []

    def _wait() -> None:
        QTest.qWait(args.wait_ms)
        app.processEvents()

    def _widget_id(widget: QWidget | None) -> str:
        return "" if widget is None else f"{widget.__class__.__name__}::{widget.objectName() or 'anon'}"

    def _add_issue(severity: str, category: str, scenario_key: str, screen_name: str, state_name: str, description: str, size_label: str, shot_path: str, widget: QWidget | None = None) -> None:
        issue_type, recommendation = _issue_meta(category)
        issues.append(
            Issue(
                severity=severity,
                category=category,
                issue_type=issue_type,
                recommendation=recommendation,
                screen_name=screen_name,
                state_name=state_name,
                description=f"{description} [scenario={scenario_key}]",
                widget=_widget_id(widget),
                screen_size=size_label,
                scale=args.scale,
                screenshot_path=shot_path,
            )
        )

    def _find_button(screen_widget: QWidget, text_fragment: str) -> QPushButton | None:
        needle = text_fragment.lower().strip()
        for button in screen_widget.findChildren(QPushButton):
            if not button.isVisible() or button.width() <= 0:
                continue
            if needle in (button.text() or "").lower():
                return button
        return None

    def _check_generic(screen_widget: QWidget, scenario: Any, size_label: str, shot_path: str) -> None:
        screen_name = scenario.screen_name
        state_name = scenario.state_name
        if screen_widget.layout() is None:
            _add_issue("major", "missing_root_layout", scenario.key, screen_name, state_name, "Screen root layout is missing.", size_label, shot_path, screen_widget)
        else:
            spacing = screen_widget.layout().spacing()
            if spacing >= 0 and spacing < 2:
                _add_issue("minor", "tight_spacing", scenario.key, screen_name, state_name, f"Layout spacing is very tight ({spacing}).", size_label, shot_path, screen_widget)

        for cta in REQUIRED_CTA_BY_SCREEN.get(screen_name, []):
            button = _find_button(screen_widget, cta)
            if button is None:
                _add_issue("critical", "missing_critical_cta", scenario.key, screen_name, state_name, f"Missing critical CTA: {cta}", size_label, shot_path)
                continue
            parent_layout = button.parentWidget().layout() if button.parentWidget() else None
            if parent_layout is None or parent_layout.indexOf(button) < 0:
                _add_issue("major", "floating_critical_cta", scenario.key, screen_name, state_name, f"CTA not anchored to layout: {button.text()}", size_label, shot_path, button)
            before = button.isVisible() and button.width() > 0 and button.height() > 0
            QTest.mouseMove(button, button.rect().center())
            _wait()
            QTest.mouseMove(screen_widget, QPoint(3, 3))
            _wait()
            after = button.isVisible() and button.width() > 0 and button.height() > 0
            if before and not after:
                _add_issue("critical", "hover_only_critical_cta", scenario.key, screen_name, state_name, f"CTA disappears outside hover: {button.text()}", size_label, shot_path, button)

        structural = [w for w in screen_widget.findChildren(QWidget) if w.isVisible() and isinstance(w, (QPushButton, QLineEdit, QTextEdit, QPlainTextEdit, QTableWidget, QTreeWidget, QComboBox))]
        if not structural:
            _add_issue("critical", "empty_or_broken_zone", scenario.key, screen_name, state_name, "No visible interactive/content widgets.", size_label, shot_path, screen_widget)

        for label in screen_widget.findChildren(QLabel):
            if not label.isVisible():
                continue
            text = (label.text() or "").strip()
            if not text:
                continue
            if "\ufffd" in text:
                _add_issue("major", "font_or_localization_glyph_issue", scenario.key, screen_name, state_name, "Replacement glyph detected in label.", size_label, shot_path, label)
            if not label.wordWrap() and label.width() + 2 < label.sizeHint().width():
                _add_issue("major", "text_clipping", scenario.key, screen_name, state_name, f"Label clipping: {text[:80]}", size_label, shot_path, label)

        for button in screen_widget.findChildren(QAbstractButton):
            if not button.isVisible():
                continue
            text = (button.text() or "").replace("&", "").strip()
            if text and button.width() + 2 < button.sizeHint().width():
                _add_issue("major", "button_clipping", scenario.key, screen_name, state_name, f"Button clipping: {text[:80]}", size_label, shot_path, button)

        rect_parent = screen_widget.rect()
        probe: list[QWidget] = []
        for widget_type in (QPushButton, QLineEdit, QTextEdit, QPlainTextEdit, QTableWidget, QTreeWidget, QComboBox):
            probe.extend([w for w in screen_widget.findChildren(widget_type) if w.isVisible()])
        for widget in probe:
            top_left = widget.mapTo(screen_widget, QPoint(0, 0))
            rect = QRect(top_left, widget.size())
            if rect.right() > rect_parent.right() + 2 or rect.bottom() > rect_parent.bottom() + 2:
                _add_issue("major", "overflow_out_of_bounds", scenario.key, screen_name, state_name, "Widget extends beyond screen bounds.", size_label, shot_path, widget)

        controls: list[QWidget] = []
        for widget_type in (QPushButton, QComboBox, QLineEdit):
            controls.extend([w for w in screen_widget.findChildren(widget_type) if w.isVisible()])
        for idx, first in enumerate(controls):
            for second in controls[idx + 1:]:
                if first.parentWidget() is None or first.parentWidget() is not second.parentWidget():
                    continue
                r1 = QRect(first.mapTo(screen_widget, QPoint(0, 0)), first.size())
                r2 = QRect(second.mapTo(screen_widget, QPoint(0, 0)), second.size())
                overlap = r1.intersected(r2)
                if overlap.isValid() and overlap.width() * overlap.height() > 36:
                    _add_issue("major", "sibling_overlap", scenario.key, screen_name, state_name, "Sibling controls overlap.", size_label, shot_path, first)

        for splitter in screen_widget.findChildren(QSplitter):
            sizes_local = splitter.sizes()
            if sizes_local and min(sizes_local) < 110:
                _add_issue("major", "splitter_collapse", scenario.key, screen_name, state_name, f"Splitter collapse: {sizes_local}", size_label, shot_path, splitter)

    def _check_state(scenario: Any, size_label: str, shot_path: str) -> None:
        k = scenario.key
        s = scenario.screen_name
        st = scenario.state_name
        if k == "project_initial_empty":
            if window.current_project_id is not None:
                _add_issue("major", "state_expected_empty", k, s, st, "Startup should be empty but project is already active.", size_label, shot_path)
        elif k == "project_loaded_pipeline":
            if window.current_project_id is None:
                _add_issue("critical", "state_expected_loaded", k, s, st, "Loaded project state missing current_project_id.", size_label, shot_path)
            if "n/a" in window.hud_panel.project_label.text().lower() or "n/a" in window.hud_panel.language_map_label.text().lower():
                _add_issue("major", "state_summary_missing", k, s, st, "HUD project/language summary is not populated.", size_label, shot_path, window.hud_panel)
        elif k == "scan_manifest_loaded":
            if not window.scan_panel.manifest_view.toPlainText().strip() or window.scan_panel.table.rowCount() <= 0:
                _add_issue("major", "state_expected_loaded", k, s, st, "Scan loaded state is empty.", size_label, shot_path, window.scan_panel.table)
        elif k == "asset_tree_loaded":
            if window.asset_panel.resource_tree.topLevelItemCount() <= 0:
                _add_issue("critical", "state_expected_loaded", k, s, st, "Asset tree has no items.", size_label, shot_path, window.asset_panel.resource_tree)
        elif k == "asset_active_selection":
            if not window.asset_panel.selected_file_path() or len(window.asset_panel.metadata_view.toPlainText().strip()) < 30:
                _add_issue("major", "state_selection_missing", k, s, st, "Asset active selection details not ready.", size_label, shot_path, window.asset_panel.metadata_view)
        elif k == "entries_many_items":
            if window.entries_panel.table.rowCount() < 120:
                _add_issue("major", "state_expected_loaded", k, s, st, "Entries table expected many rows.", size_label, shot_path, window.entries_panel.table)
        elif k == "entries_filtered_fr":
            if window.entries_panel.table.rowCount() <= 0:
                _add_issue("major", "state_expected_loaded", k, s, st, "French filter returned empty set.", size_label, shot_path, window.entries_panel.table)
        elif k == "entries_long_search":
            if len(window.entries_panel.search_edit.text()) < 25:
                _add_issue("minor", "state_summary_missing", k, s, st, "Long search text not applied.", size_label, shot_path, window.entries_panel.search_edit)
        elif k == "language_hub_overview":
            if window.language_hub_panel.overview_table.rowCount() <= 0:
                _add_issue("major", "state_expected_loaded", k, s, st, "Language overview table is empty.", size_label, shot_path, window.language_hub_panel.overview_table)
            if window.language_hub_panel.queue_table.rowCount() <= 0:
                _add_issue("major", "state_expected_loaded", k, s, st, "Language queue table is empty.", size_label, shot_path, window.language_hub_panel.queue_table)
            backend_text = " ".join(label.text().lower() for label in window.language_hub_panel.backend_labels)
            if "n/a" in backend_text:
                _add_issue("major", "state_summary_missing", k, s, st, "Language backend status block has unresolved n/a values.", size_label, shot_path, window.language_hub_panel)
        elif k == "language_hub_review_focus":
            if window.language_hub_panel.review_table.rowCount() <= 0:
                _add_issue("major", "state_expected_loaded", k, s, st, "Language review block has no rows.", size_label, shot_path, window.language_hub_panel.review_table)
            if window.language_hub_panel.stress_table.rowCount() <= 0:
                _add_issue("major", "state_expected_loaded", k, s, st, "Localization stress block has no rows.", size_label, shot_path, window.language_hub_panel.stress_table)
            if window.language_hub_panel.flow_table.rowCount() < 5:
                _add_issue("major", "state_summary_missing", k, s, st, "Language flow summary does not expose all pipeline stages.", size_label, shot_path, window.language_hub_panel.flow_table)
        elif k == "translation_loaded":
            if window.translation_panel.table.rowCount() <= 0:
                _add_issue("major", "state_expected_loaded", k, s, st, "Translation table is empty.", size_label, shot_path, window.translation_panel.table)
            has_ru = False
            for row_index in range(min(20, window.translation_panel.table.rowCount())):
                cell = window.translation_panel.table.item(row_index, 4)
                if cell and _contains_cyrillic(cell.text()):
                    has_ru = True
                    break
            if not has_ru:
                _add_issue("major", "localization_missing_ru_content", k, s, st, "No visible Cyrillic translations in top rows.", size_label, shot_path, window.translation_panel.table)
        elif k == "translation_correction_prefilled":
            if len(window.translation_panel.correction_text.toPlainText().strip()) < 40:
                _add_issue("major", "state_expected_loaded", k, s, st, "Correction long-content state missing.", size_label, shot_path, window.translation_panel.correction_text)
        elif k == "voice_no_selection":
            if window.voice_panel.attempts_table.rowCount() <= 0:
                _add_issue("major", "state_expected_loaded", k, s, st, "Voice attempts table is empty.", size_label, shot_path, window.voice_panel.attempts_table)
        elif k == "voice_active_selection":
            if len(window.voice_panel.preview_panel.toPlainText().strip()) < 20 or len(window.voice_panel.duration_plan_panel.toPlainText().strip()) < 20:
                _add_issue("major", "state_summary_missing", k, s, st, "Voice details state missing preview/plan data.", size_label, shot_path, window.voice_panel.preview_panel)
        elif k == "learning_loaded":
            if len(window.learning_panel.summary.toPlainText().strip()) < 20:
                _add_issue("major", "state_summary_missing", k, s, st, "Learning summary is too short/empty.", size_label, shot_path, window.learning_panel.summary)
        elif k == "qa_loaded":
            if not window.qa_panel.info_label.text().startswith("QA findings:"):
                _add_issue("major", "state_summary_missing", k, s, st, "QA summary label missing.", size_label, shot_path, window.qa_panel.info_label)
        elif k == "reports_loaded":
            if window.reports_panel.translation_table.rowCount() <= 0 or "n/a" in window.reports_panel.coverage_label.text().lower():
                _add_issue("major", "state_expected_loaded", k, s, st, "Reports loaded state is incomplete.", size_label, shot_path, window.reports_panel.translation_table)
        elif k == "diagnostics_loaded":
            if window.diagnostics_panel.backend_table.rowCount() <= 0:
                _add_issue("major", "state_expected_loaded", k, s, st, "Diagnostics backend table is empty.", size_label, shot_path, window.diagnostics_panel.backend_table)
        elif k == "export_log_loaded":
            txt = window.export_panel.info.toPlainText()
            if "Export directory:" not in txt or "Manifest:" not in txt:
                _add_issue("major", "state_summary_missing", k, s, st, "Export log not populated.", size_label, shot_path, window.export_panel.info)
        elif k == "jobs_loaded":
            if len(window.jobs_panel.log_view.toPlainText().strip()) < 20:
                _add_issue("major", "state_summary_missing", k, s, st, "Jobs payload looks empty.", size_label, shot_path, window.jobs_panel.log_view)
        elif k == "live_scene_selected":
            if window.live_panel.scene_combo.count() <= 0 or window.live_panel.scene_combo.currentData() is None:
                _add_issue("major", "state_selection_missing", k, s, st, "Live demo scene selection not ready.", size_label, shot_path, window.live_panel.scene_combo)
        elif k == "companion_invalid_exec":
            if not window.companion_panel.executable_edit.text().strip().endswith("missing_game.exe"):
                _add_issue("major", "state_incorrect_filter", k, s, st, "Companion invalid executable state not configured.", size_label, shot_path, window.companion_panel.executable_edit)

    actual_screens = [window.tabs.tabText(i) for i in range(window.tabs.count())]
    for expected in expected_screen_names():
        if expected not in actual_screens:
            _add_issue("critical", "navigation_missing_screen", "bootstrap", "Navigation", "tab_registry", f"Missing screen tab: {expected}", "n/a", "")

    for size_index, (width, height) in enumerate(sizes):
        window.resize(width, height)
        window.show()
        _wait()
        size_label = f"{width}x{height}"
        for scenario in scenarios:
            if not scenario.requires_loaded and size_index > 0:
                continue
            if not apply_scenario_state(window, scenario, project_name=args.project_name, wait_fn=_wait):
                _add_issue("critical", "navigation_missing_screen", scenario.key, scenario.screen_name, scenario.state_name, "Scenario screen missing in tab navigation.", size_label, "")
                continue
            _wait()
            file_name = f"doctor__{_slug(scenario.screen_name)}__{_slug(scenario.state_name)}__{size_label}__scale_{args.scale.replace('.', '_')}.png"
            out_path = screenshots_dir / file_name
            window.grab().save(str(out_path))
            shot_path = str(out_path.resolve())
            captures.append({
                "run_id": args.run_id,
                "screen_name": scenario.screen_name,
                "state_name": scenario.state_name,
                "screenshot_path": shot_path,
                "timestamp": _now_iso(),
                "notes": scenario.notes,
                "size": size_label,
                "scale": args.scale,
                "sha256": _hash_file(out_path),
            })
            screen_widget = window.tabs.currentWidget()
            if isinstance(screen_widget, QWidget):
                _check_generic(screen_widget, scenario, size_label, shot_path)
                _check_state(scenario, size_label, shot_path)

    window.close()
    services.close()
    app.quit()
    payload = {"run_id": args.run_id, "scale": args.scale, "sizes": args.sizes, "issues": [i.as_dict() for i in issues], "captures": captures}
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
    all_captures: list[dict[str, Any]] = []
    failed_workers: list[str] = []
    commands: list[list[str]] = []

    scales = [token.strip() for token in args.scales.split(",") if token.strip()]
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
        all_issues.extend(payload.get("issues", []))
        all_captures.extend(payload.get("captures", []))

    severity_counts = {"critical": 0, "major": 0, "minor": 0}
    issues_by_screen: dict[str, dict[str, int]] = {}
    issues_by_type: dict[str, int] = {}
    issues_by_category: dict[str, int] = {}

    for issue in all_issues:
        severity = str(issue.get("severity", "minor")).lower()
        if severity not in severity_counts:
            severity = "minor"
        screen_name = str(issue.get("screen_name", "unknown"))
        issue_type = str(issue.get("issue_type", "layout"))
        category = str(issue.get("category", "unknown"))

        severity_counts[severity] += 1
        issues_by_screen.setdefault(screen_name, {"critical": 0, "major": 0, "minor": 0})
        issues_by_screen[screen_name][severity] += 1
        issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
        issues_by_category[category] = issues_by_category.get(category, 0) + 1

    captures_by_screen: dict[str, int] = {}
    captures_by_state: dict[str, int] = {}
    for capture in all_captures:
        screen_name = str(capture.get("screen_name", "unknown"))
        state_key = f"{capture.get('screen_name', 'unknown')}|{capture.get('state_name', 'unknown')}"
        captures_by_screen[screen_name] = captures_by_screen.get(screen_name, 0) + 1
        captures_by_state[state_key] = captures_by_state.get(state_key, 0) + 1

    sorted_issues = sorted(
        all_issues,
        key=lambda item: (
            SEVERITY_WEIGHT.get(str(item.get("severity", "minor")).lower(), 3),
            str(item.get("screen_name", "")),
            str(item.get("state_name", "")),
            str(item.get("category", "")),
        ),
    )

    recommendation_count: dict[tuple[str, str], int] = {}
    for issue in all_issues:
        issue_type = str(issue.get("issue_type", "layout"))
        recommendation = str(issue.get("recommendation", "Review layout constraints and rerun UI doctor."))
        key = (issue_type, recommendation)
        recommendation_count[key] = recommendation_count.get(key, 0) + 1

    fix_recommendations = [
        {"issue_type": key[0], "recommendation": key[1], "count": count}
        for key, count in sorted(recommendation_count.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))[:12]
    ]

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
        "captures": all_captures,
        "screenshots": all_captures,
        "captures_by_screen": dict(sorted(captures_by_screen.items())),
        "captures_by_state": dict(sorted(captures_by_state.items())),
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
        "issues_by_screen": dict(sorted(issues_by_screen.items())),
        "issues_by_type": dict(sorted(issues_by_type.items())),
        "issues_by_category": dict(sorted(issues_by_category.items())),
        "fix_recommendations": fix_recommendations,
        "captures_by_screen": dict(sorted(captures_by_screen.items())),
        "captures_by_state": dict(sorted(captures_by_state.items())),
        "issues": all_issues,
        "top_issues": sorted_issues[:60],
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
        if not args.run_id or not args.run_dir or not args.worker_output:
            parser.error("--run-id, --run-dir and --worker-output are required in worker mode.")
        return _run_worker(args)
    return _run_master(args)


if __name__ == "__main__":
    raise SystemExit(main())
