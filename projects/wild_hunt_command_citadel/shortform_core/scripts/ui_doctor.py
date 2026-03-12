from __future__ import annotations

import argparse
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

REQUIRED_BUTTONS_BY_PAGE: dict[str, list[str]] = {
    "dashboard": ["Добавить профиль", "Открыть сессию", "Собрать контент-план", "Открыть AI-студию"],
    "profiles": ["Создать профиль", "Подключить профиль", "Открыть сессию"],
    "sessions": ["Открыть сессию", "Закрыть сессию"],
    "content": ["Добавить демо-контент", "Проверить выбранное", "Поставить в очередь"],
    "ai_studio": ["Сгенерировать рекомендации", "Собрать пакет генерации"],
    "audit": ["Обновить таймлайн"],
    "updates": ["Проверить апдейты", "Запустить пост-проверку"],
    "settings": ["Открыть диагностику", "Обновить настройки"],
}

REQUIRED_LABELS_BY_PAGE: dict[str, list[str]] = {
    "analytics": ["Топ-контент", "Слабые сигналы", "Рекомендации"],
}


@dataclass
class Issue:
    severity: str
    category: str
    page: str
    description: str
    widget: str = ""
    screen_size: str = ""
    scale: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "category": self.category,
            "page": self.page,
            "description": self.description,
            "widget": self.widget,
            "screen_size": self.screen_size,
            "scale": self.scale,
        }


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


def _find_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run_master(args: argparse.Namespace) -> int:
    project_root = _find_project_root()
    output_root = (project_root / args.output_dir).resolve()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    started_at = _now_iso()
    commands: list[list[str]] = []
    worker_summaries: list[dict[str, Any]] = []
    all_issues: list[dict[str, Any]] = []
    all_shots: list[dict[str, Any]] = []
    failed_workers: list[str] = []

    scales = [token.strip() for token in args.scales.split(",") if token.strip()]
    for scale in scales:
        worker_json = run_dir / f"worker_{scale.replace('.', '_')}.json"
        cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--worker",
            "--scale",
            scale,
            "--sizes",
            args.sizes,
            "--api-base-url",
            args.api_base_url,
            "--worker-output",
            str(worker_json),
            "--run-dir",
            str(run_dir),
        ]
        commands.append(
            [
                "python",
                "scripts/ui_doctor.py",
                "--worker",
                "--scale",
                scale,
                "--sizes",
                args.sizes,
                "--api-base-url",
                args.api_base_url,
                "--worker-output",
                _repo_relative(worker_json),
                "--run-dir",
                _repo_relative(run_dir),
            ]
        )
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        env["QT_SCALE_FACTOR"] = scale
        completed = subprocess.run(
            cmd,
            cwd=project_root,
            env=env,
            text=True,
            capture_output=True,
        )
        if completed.returncode != 0:
            failed_workers.append(scale)
            all_issues.append(
                Issue(
                    severity="critical",
                    category="worker_failure",
                    page="all",
                    description=f"UI worker failed for scale={scale}: {completed.stderr.strip() or completed.stdout.strip()}",
                    scale=scale,
                ).as_dict()
            )
            continue
        if not worker_json.exists():
            failed_workers.append(scale)
            all_issues.append(
                Issue(
                    severity="critical",
                    category="worker_output_missing",
                    page="all",
                    description=f"UI worker finished but output was not found for scale={scale}",
                    scale=scale,
                ).as_dict()
            )
            continue
        payload = json.loads(worker_json.read_text(encoding="utf-8"))
        worker_summaries.append(payload)
        all_issues.extend(payload.get("issues", []))
        all_shots.extend(payload.get("screenshots", []))

    severity_counts = {"critical": 0, "major": 0, "minor": 0}
    issue_categories: dict[str, int] = {}
    for issue in all_issues:
        sev = str(issue.get("severity", "minor")).lower()
        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            severity_counts["minor"] += 1
        category = str(issue.get("category", "unknown"))
        issue_categories[category] = issue_categories.get(category, 0) + 1

    shots_by_page: dict[str, int] = {}
    for shot in all_shots:
        page = str(shot.get("page", "unknown"))
        shots_by_page[page] = shots_by_page.get(page, 0) + 1

    if severity_counts["critical"] > 0 or failed_workers:
        overall_status = "FAIL"
    elif severity_counts["major"] > 0:
        overall_status = "PASS_WITH_WARNINGS"
    else:
        overall_status = "PASS"

    finished = time.time()
    finished_at = _now_iso()
    duration_seconds = round(finished - started, 2)
    summary = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration_seconds,
        "overall_status": overall_status,
        "manual_acceptance_recommended": overall_status != "FAIL",
        "project_root": ".",
        "scales": scales,
        "sizes": args.sizes,
        "commands": commands,
        "failed_workers": failed_workers,
        "severity_counts": severity_counts,
        "issue_categories": issue_categories,
        "screenshots_by_page": shots_by_page,
        "issues": all_issues,
        "artifacts": {
            "screenshots_manifest": _repo_relative(run_dir / "ui_screenshots_manifest.json"),
            "summary_json": _repo_relative(run_dir / "ui_validation_summary.json"),
            "summary_md": _repo_relative(run_dir / "ui_validation_summary.md"),
        },
    }

    manifest = {
        "run_id": run_id,
        "screenshots": all_shots,
        "screenshots_by_page": shots_by_page,
    }
    (run_dir / "ui_screenshots_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (run_dir / "ui_validation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (run_dir / "ui_validation_summary.md").write_text(
        _render_summary_md(summary),
        encoding="utf-8",
    )
    print(_repo_relative(run_dir))
    print(f"UI validation status: {overall_status}")
    return 0 if overall_status != "FAIL" else 2


def _render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# UI Validation Summary",
        "",
        f"- Run ID: `{summary.get('run_id')}`",
        f"- Status: `{summary.get('overall_status')}`",
        f"- Duration: `{summary.get('duration_seconds')}s`",
        f"- Scales: `{', '.join(summary.get('scales', []))}`",
        f"- Sizes: `{summary.get('sizes')}`",
        "",
        "## Severity Counts",
        "",
    ]
    counts = summary.get("severity_counts", {})
    lines.append(f"- critical: {counts.get('critical', 0)}")
    lines.append(f"- major: {counts.get('major', 0)}")
    lines.append(f"- minor: {counts.get('minor', 0)}")
    screen_counts = summary.get("screenshots_by_page", {})
    if isinstance(screen_counts, dict) and screen_counts:
        lines.append("")
        lines.append("## Screenshots By Page")
        lines.append("")
        for page, amount in screen_counts.items():
            lines.append(f"- {page}: {amount}")
    category_counts = summary.get("issue_categories", {})
    if isinstance(category_counts, dict) and category_counts:
        lines.append("")
        lines.append("## Issue Categories")
        lines.append("")
        for category, amount in category_counts.items():
            lines.append(f"- {category}: {amount}")
    lines.append("")
    lines.append("## Issues")
    lines.append("")
    issues = summary.get("issues", [])
    if not issues:
        lines.append("- No issues found.")
    else:
        for issue in issues[:120]:
            lines.append(
                f"- [{issue.get('severity')}] `{issue.get('page')}` / `{issue.get('category')}`: "
                f"{issue.get('description')}"
            )
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    artifacts = summary.get("artifacts", {})
    for key, path in artifacts.items():
        lines.append(f"- {key}: `{path}`")
    return "\n".join(lines).strip() + "\n"


def _run_worker(args: argparse.Namespace) -> int:
    # Local imports in worker mode to keep master mode lightweight.
    from PySide6.QtCore import QPoint, QRect, Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import (
        QAbstractButton,
        QApplication,
        QComboBox,
        QGraphicsOpacityEffect,
        QLabel,
        QLineEdit,
        QListWidget,
        QPushButton,
        QTableWidget,
        QTextEdit,
        QWidget,
    )
    from app.desktop.user_window import UserWorkspaceWindow

    run_dir = Path(args.run_dir).resolve()
    screenshots_dir = run_dir / "screenshots" / f"scale_{args.scale.replace('.', '_')}"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    sizes = _parse_sizes(args.sizes)
    app = QApplication([])
    window = UserWorkspaceWindow(api_base_url=args.api_base_url)
    if hasattr(window, "_auto_refresh"):
        window._auto_refresh.stop()

    issues: list[Issue] = []
    screenshots: list[dict[str, Any]] = []

    def wait_ms(ms: int) -> None:
        QTest.qWait(ms)
        app.processEvents()

    def widget_label(widget: QWidget) -> str:
        name = widget.objectName() or widget.__class__.__name__
        return f"{widget.__class__.__name__}::{name}"

    def add_issue(
        severity: str,
        category: str,
        page: str,
        description: str,
        widget: QWidget | None,
        size_label: str,
    ) -> None:
        issues.append(
            Issue(
                severity=severity,
                category=category,
                page=page,
                description=description,
                widget=widget_label(widget) if widget is not None else "",
                screen_size=size_label,
                scale=args.scale,
            )
        )

    def find_button(page_widget: QWidget, text_fragment: str) -> QPushButton | None:
        for button in page_widget.findChildren(QPushButton):
            text = (button.text() or "").strip()
            if text_fragment in text and button.isVisible():
                return button
        return None

    for width, height in sizes:
        size_label = f"{width}x{height}"
        window.resize(width, height)
        window.show()
        wait_ms(260)

        splitter = getattr(window, "main_splitter", None)
        if splitter is None:
            add_issue(
                "critical",
                "missing_main_splitter",
                "all",
                "Main splitter is missing from workspace window.",
                None,
                size_label,
            )
        else:
            split_sizes = splitter.sizes()
            if len(split_sizes) == 2:
                left_size, right_size = split_sizes
                total = max(1, left_size + right_size)
                right_ratio = right_size / total
                if left_size < 620:
                    add_issue(
                        "major",
                        "splitter_left_too_small",
                        "all",
                        f"Main workspace column is too narrow ({left_size}px).",
                        splitter,
                        size_label,
                    )
                if right_size < 280:
                    add_issue(
                        "major",
                        "splitter_right_too_small",
                        "all",
                        f"Context panel is too narrow ({right_size}px).",
                        splitter,
                        size_label,
                    )
                if right_ratio < 0.18 or right_ratio > 0.42:
                    add_issue(
                        "major",
                        "splitter_ratio_unstable",
                        "all",
                        f"Context panel ratio is outside expected range ({right_ratio:.2f}).",
                        splitter,
                        size_label,
                    )

        top_status = getattr(window, "top_status", None)
        if top_status is None or not top_status.isVisible():
            add_issue(
                "critical",
                "missing_top_status_bar",
                "all",
                "Top status bar is not visible.",
                top_status if isinstance(top_status, QWidget) else None,
                size_label,
            )
        else:
            pills = getattr(top_status, "pills", {})
            if not isinstance(pills, dict) or len(pills) < 5:
                add_issue(
                    "major",
                    "insufficient_status_pills",
                    "all",
                    "Top status bar does not expose required status pills.",
                    top_status,
                    size_label,
                )
            else:
                for key, pill in pills.items():
                    if not pill.isVisible():
                        add_issue(
                            "major",
                            "status_pill_hidden",
                            "all",
                            f"Status pill '{key}' is hidden.",
                            pill,
                            size_label,
                        )
                        continue
                    text = (pill.text() or "").strip()
                    if not text:
                        add_issue(
                            "major",
                            "status_pill_empty",
                            "all",
                            f"Status pill '{key}' has empty text.",
                            pill,
                            size_label,
                        )

        context_panel = getattr(window, "context_panel", None)
        if context_panel is None or not context_panel.isVisible():
            add_issue(
                "critical",
                "missing_context_panel",
                "all",
                "Context panel is not visible.",
                context_panel if isinstance(context_panel, QWidget) else None,
                size_label,
            )
        else:
            context_actions = [btn for btn in context_panel.findChildren(QPushButton) if btn.isVisible()]
            if len(context_actions) < 2:
                add_issue(
                    "major",
                    "context_actions_missing",
                    "all",
                    "Context panel has fewer than 2 visible actions.",
                    context_panel,
                    size_label,
                )
            context_labels = [lbl for lbl in context_panel.findChildren(QLabel) if lbl.isVisible()]
            meaningful_labels = [lbl for lbl in context_labels if len((lbl.text() or "").strip()) >= 8]
            if len(meaningful_labels) < 3:
                add_issue(
                    "major",
                    "context_information_thin",
                    "all",
                    "Context panel does not provide enough readable context lines.",
                    context_panel,
                    size_label,
                )

        for page_key in PAGE_KEYS:
            window._switch_page(page_key)
            wait_ms(320)

            screenshot_path = screenshots_dir / f"{page_key}_{size_label}.png"
            window.grab().save(str(screenshot_path))
            captured_at = _now_iso()
            screenshots.append(
                {
                    "screen_name": page_key,
                    "state_name": f"layout_check/{size_label}/scale_{args.scale}",
                    "scale": args.scale,
                    "page": page_key,
                    "size": size_label,
                    "path": _repo_relative(screenshot_path),
                    "screenshot_path": _repo_relative(screenshot_path),
                    "timestamp": captured_at,
                    "captured_at": captured_at,
                    "notes": "auto-captured during ui_doctor layout checks",
                    "tags": [
                        "ui_doctor",
                        f"screen:{page_key}",
                        f"size:{size_label}",
                        f"scale:{args.scale}",
                    ],
                    "severity_reference": None,
                    "issue_reference": None,
                }
            )

            page_widget = window._pages.get(page_key)
            if page_widget is None:
                add_issue(
                    "critical",
                    "missing_page",
                    page_key,
                    "Page widget is not registered in workspace.",
                    None,
                    size_label,
                )
                continue

            if page_key == "dashboard":
                core_state_label = getattr(page_widget, "core_state_summary", None)
                next_actions_label = getattr(page_widget, "next_action_summary", None)
                if core_state_label is None or not isinstance(core_state_label, QLabel):
                    add_issue(
                        "major",
                        "dashboard_core_state_missing",
                        page_key,
                        "Dashboard does not expose a core system state summary block.",
                        page_widget,
                        size_label,
                    )
                elif not (core_state_label.text() or "").strip():
                    add_issue(
                        "major",
                        "dashboard_core_state_empty",
                        page_key,
                        "Core system state summary is empty.",
                        core_state_label,
                        size_label,
                    )

                if next_actions_label is None or not isinstance(next_actions_label, QLabel):
                    add_issue(
                        "major",
                        "dashboard_next_actions_missing",
                        page_key,
                        "Dashboard does not expose next recommended actions.",
                        page_widget,
                        size_label,
                    )
                elif not (next_actions_label.text() or "").strip():
                    add_issue(
                        "major",
                        "dashboard_next_actions_empty",
                        page_key,
                        "Next actions summary is empty.",
                        next_actions_label,
                        size_label,
                    )

            effect = page_widget.graphicsEffect()
            if isinstance(effect, QGraphicsOpacityEffect) and effect.opacity() < 0.95:
                add_issue(
                    "critical",
                    "stuck_opacity",
                    page_key,
                    f"Page opacity is {effect.opacity():.2f}, expected >= 0.95",
                    page_widget,
                    size_label,
                )

            for cta_label in REQUIRED_BUTTONS_BY_PAGE.get(page_key, []):
                button = find_button(page_widget, cta_label)
                if button is None:
                    add_issue(
                        "critical",
                        "missing_critical_cta",
                        page_key,
                        f"Critical CTA '{cta_label}' is not visible.",
                        None,
                        size_label,
                    )
                    continue

                before = button.isVisible() and button.width() > 0 and button.height() > 0
                QTest.mouseMove(button, button.rect().center())
                wait_ms(40)
                QTest.mouseMove(page_widget, QPoint(5, 5))
                wait_ms(40)
                after = button.isVisible() and button.width() > 0 and button.height() > 0
                if before and not after:
                    add_issue(
                        "critical",
                        "hover_only_cta",
                        page_key,
                        f"CTA '{button.text()}' disappears outside hover state.",
                        button,
                        size_label,
                    )

            for label_fragment in REQUIRED_LABELS_BY_PAGE.get(page_key, []):
                found = False
                for label in page_widget.findChildren(QLabel):
                    if not label.isVisible():
                        continue
                    text = (label.text() or "").strip()
                    if label_fragment in text:
                        found = True
                        break
                if not found:
                    add_issue(
                        "critical",
                        "missing_required_label",
                        page_key,
                        f"Required label '{label_fragment}' is not visible.",
                        None,
                        size_label,
                    )

            # Clipping checks for labels/buttons.
            for label in page_widget.findChildren(QLabel):
                if not label.isVisible():
                    continue
                text = (label.text() or "").strip()
                if not text:
                    continue
                if label.wordWrap():
                    continue
                if label.width() + 1 < label.sizeHint().width():
                    add_issue(
                        "major",
                        "text_clipping",
                        page_key,
                        f"Label text likely clipped: '{text[:80]}'",
                        label,
                        size_label,
                    )
            for button in page_widget.findChildren(QAbstractButton):
                if not button.isVisible():
                    continue
                text = (button.text() or "").replace("&", "").strip()
                if not text:
                    continue
                if button.width() + 1 < button.sizeHint().width():
                    add_issue(
                        "major",
                        "button_clipping",
                        page_key,
                        f"Button text likely clipped: '{text[:80]}'",
                        button,
                        size_label,
                    )

            # Out-of-bounds checks within page rect.
            page_rect = page_widget.rect()
            check_types = [QPushButton, QComboBox, QLineEdit, QTextEdit, QTableWidget, QListWidget]
            check_widgets: list[QWidget] = []
            for widget_type in check_types:
                check_widgets.extend(page_widget.findChildren(widget_type))
            for widget in check_widgets:
                if not widget.isVisible():
                    continue
                top_left = widget.mapTo(page_widget, QPoint(0, 0))
                rect = QRect(top_left, widget.size())
                if rect.right() > page_rect.right() + 2 or rect.bottom() > page_rect.bottom() + 2:
                    add_issue(
                        "major",
                        "out_of_bounds",
                        page_key,
                        "Interactive widget extends beyond page bounds.",
                        widget,
                        size_label,
                    )
                if rect.left() < -2 or rect.top() < -2:
                    add_issue(
                        "major",
                        "negative_position",
                        page_key,
                        "Interactive widget has negative position relative to page.",
                        widget,
                        size_label,
                    )

            # Sibling overlap checks for interactive controls.
            interactive: list[QWidget] = []
            for widget_type in (QPushButton, QComboBox, QLineEdit):
                interactive.extend([widget for widget in page_widget.findChildren(widget_type) if widget.isVisible()])
            for i in range(len(interactive)):
                a = interactive[i]
                for j in range(i + 1, len(interactive)):
                    b = interactive[j]
                    if a.parentWidget() is None or b.parentWidget() is None:
                        continue
                    if a.parentWidget() is not b.parentWidget():
                        continue
                    a_pos = a.mapTo(page_widget, QPoint(0, 0))
                    b_pos = b.mapTo(page_widget, QPoint(0, 0))
                    rect_a = QRect(a_pos, a.size())
                    rect_b = QRect(b_pos, b.size())
                    overlap = rect_a.intersected(rect_b)
                    if overlap.isValid() and overlap.width() * overlap.height() > 24:
                        add_issue(
                            "major",
                            "sibling_overlap",
                            page_key,
                            "Sibling controls overlap in the same parent container.",
                            a,
                            size_label,
                        )

    window.close()
    app.quit()

    payload = {
        "scale": args.scale,
        "sizes": args.sizes,
        "issues": [issue.as_dict() for issue in issues],
        "screenshots": screenshots,
    }
    worker_output = Path(args.worker_output).resolve()
    worker_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="UI Doctor: validate desktop UI layouts and CTA visibility.")
    parser.add_argument("--worker", action="store_true", help="Run in worker mode (internal).")
    parser.add_argument("--scale", default="1.0", help="Single UI scale for worker mode.")
    parser.add_argument("--scales", default="1.0,1.25,1.5", help="Comma-separated UI scales for master mode.")
    parser.add_argument("--sizes", default="1540x920,1366x768,1280x800", help="Comma-separated window sizes.")
    parser.add_argument("--api-base-url", default="http://127.0.0.1:9", help="API base URL for UI bootstrapping.")
    parser.add_argument("--output-dir", default="runtime/ui_validation", help="Output directory for UI validation runs.")
    parser.add_argument("--run-dir", default="", help="Run directory for worker mode.")
    parser.add_argument("--worker-output", default="", help="Worker JSON output path.")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    if args.worker:
        if not args.worker_output or not args.run_dir:
            parser.error("--worker-output and --run-dir are required in worker mode.")
        return _run_worker(args)
    return _run_master(args)


if __name__ == "__main__":
    raise SystemExit(main())
