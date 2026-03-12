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

SEVERITY_RANK = {"critical": 3, "major": 2, "minor": 1}
BLOCKER_TYPES = {
    "missing_main_splitter",
    "missing_top_status_bar",
    "missing_context_panel",
    "missing_page",
    "missing_critical_cta",
    "hover_only_critical_control",
    "sibling_overlap",
    "out_of_bounds",
    "critical_button_clipping",
    "critical_text_clipping",
    "layout_break",
    "context_panel_conflict",
    "severe_resize_instability",
    "session_placeholder_broken",
}


@dataclass
class Issue:
    severity: str
    category: str
    issue_type: str
    page: str
    description: str
    acceptance_blocker: bool
    likely_user_visible: bool
    likely_false_positive: bool
    widget: str = ""
    screen_size: str = ""
    scale: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "category": self.category,
            "issue_type": self.issue_type,
            "page": self.page,
            "description": self.description,
            "acceptance_blocker": self.acceptance_blocker,
            "likely_user_visible": self.likely_user_visible,
            "likely_false_positive": self.likely_false_positive,
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


def _render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        "# UI Doctor Summary",
        "",
        f"- Run ID: `{summary.get('run_id')}`",
        f"- Status: `{summary.get('overall_status')}`",
        f"- Duration: `{summary.get('duration_seconds')}s`",
        f"- Scales: `{', '.join(summary.get('scales', []))}`",
        f"- Sizes: `{summary.get('sizes')}`",
        f"- Manual testing allowed: `{summary.get('manual_testing_allowed')}`",
        "",
        "## Severity Counts",
        "",
    ]
    counts = summary.get("severity_counts", {})
    lines.append(f"- critical: {counts.get('critical', 0)}")
    lines.append(f"- major: {counts.get('major', 0)}")
    lines.append(f"- minor: {counts.get('minor', 0)}")

    lines.extend(["", "## Acceptance Blockers", ""])
    blockers = _safe_list(summary.get("acceptance_blockers"))
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")

    lines.extend(["", "## Issues by Page", ""])
    by_page = summary.get("issues_by_page", {})
    if isinstance(by_page, dict) and by_page:
        for page, data in by_page.items():
            lines.append(
                f"- {page}: critical={data.get('critical', 0)}, "
                f"major={data.get('major', 0)}, minor={data.get('minor', 0)}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Issues by Category", ""])
    by_category = summary.get("issues_by_category", {})
    if isinstance(by_category, dict) and by_category:
        for category, amount in by_category.items():
            lines.append(f"- {category}: {amount}")
    else:
        lines.append("- none")

    lines.extend(["", "## Artifacts", ""])
    artifacts = summary.get("artifacts", {})
    for key, path in artifacts.items():
        lines.append(f"- {key}: `{path}`")
    return "\n".join(lines).strip() + "\n"

def _run_master(args: argparse.Namespace) -> int:
    output_root = (PROJECT_ROOT / args.output_dir).resolve()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    started_at = _now_iso()
    commands: list[list[str]] = []
    all_issues: list[dict[str, Any]] = []
    all_shots: list[dict[str, Any]] = []
    all_trace: list[dict[str, Any]] = []
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
            cwd=PROJECT_ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
        if completed.returncode != 0:
            failed_workers.append(scale)
            all_issues.append(
                Issue(
                    severity="critical",
                    category="product_clarity",
                    issue_type="worker_failure",
                    page="all",
                    description=f"UI worker failed for scale={scale}: {completed.stderr.strip() or completed.stdout.strip()}",
                    acceptance_blocker=True,
                    likely_user_visible=True,
                    likely_false_positive=False,
                    scale=scale,
                ).as_dict()
            )
            continue
        if not worker_json.exists():
            failed_workers.append(scale)
            all_issues.append(
                Issue(
                    severity="critical",
                    category="product_clarity",
                    issue_type="worker_output_missing",
                    page="all",
                    description=f"UI worker finished but output is missing for scale={scale}",
                    acceptance_blocker=True,
                    likely_user_visible=True,
                    likely_false_positive=False,
                    scale=scale,
                ).as_dict()
            )
            continue
        payload = json.loads(worker_json.read_text(encoding="utf-8"))
        all_issues.extend(_safe_list(payload.get("issues")))
        all_shots.extend(_safe_list(payload.get("screenshots")))
        all_trace.extend(_safe_list(payload.get("walkthrough_trace")))

    severity_counts = {"critical": 0, "major": 0, "minor": 0}
    issue_categories: dict[str, int] = {}
    issues_by_page: dict[str, dict[str, int]] = {}
    acceptance_blockers: list[str] = []
    likely_user_visible = 0
    likely_false_positive = 0

    for idx, issue in enumerate(all_issues, start=1):
        if not isinstance(issue, dict):
            continue
        sev = _safe_str(issue.get("severity")).lower() or "minor"
        category = _safe_str(issue.get("category")) or "unknown"
        page = _safe_str(issue.get("page")) or "unknown"
        issue_type = _safe_str(issue.get("issue_type")) or "unknown_issue"
        if sev not in severity_counts:
            sev = "minor"
        severity_counts[sev] += 1
        issue_categories[category] = issue_categories.get(category, 0) + 1
        if page not in issues_by_page:
            issues_by_page[page] = {"critical": 0, "major": 0, "minor": 0}
        issues_by_page[page][sev] += 1
        if bool(issue.get("acceptance_blocker", False)):
            acceptance_blockers.append(f"{page}:{issue_type}:{idx}")
        if bool(issue.get("likely_user_visible", False)):
            likely_user_visible += 1
        if bool(issue.get("likely_false_positive", False)):
            likely_false_positive += 1

    shots_by_page: dict[str, int] = {}
    for shot in all_shots:
        if not isinstance(shot, dict):
            continue
        page = _safe_str(shot.get("screen_name") or shot.get("page") or "unknown")
        shots_by_page[page] = shots_by_page.get(page, 0) + 1

    trace_sorted: list[dict[str, Any]] = []
    for idx, step in enumerate(all_trace, start=1):
        if not isinstance(step, dict):
            continue
        entry = dict(step)
        entry["step_index"] = idx
        trace_sorted.append(entry)

    has_blocker = len(acceptance_blockers) > 0
    if severity_counts["critical"] > 0 or failed_workers or has_blocker:
        overall_status = "FAIL"
    elif severity_counts["major"] > 0 or severity_counts["minor"] > 0:
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
        "manual_acceptance_recommended": overall_status == "PASS",
        "manual_testing_allowed": overall_status == "PASS",
        "project_root": ".",
        "scales": scales,
        "sizes": args.sizes,
        "commands": commands,
        "failed_workers": failed_workers,
        "severity_counts": severity_counts,
        "issues_by_category": dict(sorted(issue_categories.items(), key=lambda pair: pair[0])),
        "issues_by_page": dict(sorted(issues_by_page.items(), key=lambda pair: pair[0])),
        "acceptance_blockers": acceptance_blockers,
        "likely_user_visible_count": likely_user_visible,
        "likely_false_positive_count": likely_false_positive,
        "screenshots_by_page": dict(sorted(shots_by_page.items(), key=lambda pair: pair[0])),
        "walkthrough_step_count": len(trace_sorted),
        "issues": all_issues,
        "artifacts": {
            "screenshots_manifest": _repo_relative(run_dir / "ui_screenshots_manifest.json"),
            "summary_json": _repo_relative(run_dir / "ui_validation_summary.json"),
            "summary_md": _repo_relative(run_dir / "ui_validation_summary.md"),
            "walkthrough_trace_json": _repo_relative(run_dir / "ui_walkthrough_trace.json"),
        },
    }

    manifest = {
        "run_id": run_id,
        "generated_at": finished_at,
        "review_scope": "ui_doctor",
        "screenshots": all_shots,
        "screenshots_by_page": dict(sorted(shots_by_page.items(), key=lambda pair: pair[0])),
    }
    walkthrough_payload = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "steps": trace_sorted,
    }
    (run_dir / "ui_screenshots_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (run_dir / "ui_walkthrough_trace.json").write_text(
        json.dumps(walkthrough_payload, ensure_ascii=False, indent=2),
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

    latest_payload = {
        "run_id": run_id,
        "status": overall_status,
        "path": _repo_relative(run_dir),
        "summary_path": _repo_relative(run_dir / "ui_validation_summary.json"),
        "manifest_path": _repo_relative(run_dir / "ui_screenshots_manifest.json"),
        "walkthrough_trace_path": _repo_relative(run_dir / "ui_walkthrough_trace.json"),
        "timestamp": finished_at,
    }
    (output_root / "latest_run.json").write_text(
        json.dumps(latest_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_root / "latest_run.txt").write_text(_repo_relative(run_dir) + "\n", encoding="utf-8")
    print(_repo_relative(run_dir))
    print(f"UI validation status: {overall_status}")
    return 0 if overall_status != "FAIL" else 2


def _run_worker(args: argparse.Namespace) -> int:
    from PySide6.QtCore import QPoint, QRect
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import (
        QAbstractItemView,
        QApplication,
        QComboBox,
        QGraphicsOpacityEffect,
        QLabel,
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
    walkthrough: list[dict[str, Any]] = []
    step_index = 0
    splitter_ratios: list[tuple[str, float]] = []

    def wait_ms(ms: int) -> None:
        QTest.qWait(ms)
        app.processEvents()

    def widget_label(widget: QWidget | None) -> str:
        if widget is None:
            return ""
        name = widget.objectName() or widget.__class__.__name__
        return f"{widget.__class__.__name__}::{name}"

    def record_step(
        *,
        screen: str,
        action: str,
        result: str,
        notes: str,
        screenshot_ref: str | None = None,
    ) -> None:
        nonlocal step_index
        step_index += 1
        walkthrough.append(
            {
                "run_id": "",
                "worker_scale": args.scale,
                "step_index": step_index,
                "screen": screen,
                "action": action,
                "result": result,
                "screenshot_ref": screenshot_ref,
                "timestamp": _now_iso(),
                "notes": notes,
            }
        )

    def add_issue(
        *,
        severity: str,
        category: str,
        issue_type: str,
        page: str,
        description: str,
        size_label: str,
        widget: QWidget | None = None,
        acceptance_blocker: bool | None = None,
        likely_user_visible: bool = True,
        likely_false_positive: bool = False,
    ) -> None:
        if acceptance_blocker is None:
            acceptance_blocker = severity == "critical" or issue_type in BLOCKER_TYPES
        issues.append(
            Issue(
                severity=severity,
                category=category,
                issue_type=issue_type,
                page=page,
                description=description,
                acceptance_blocker=acceptance_blocker,
                likely_user_visible=likely_user_visible,
                likely_false_positive=likely_false_positive,
                widget=widget_label(widget),
                screen_size=size_label,
                scale=args.scale,
            )
        )

    def capture_page(page_key: str, size_label: str, *, state_name: str = "layout_check") -> str:
        token = _sanitize_token(state_name)
        screenshot_path = screenshots_dir / f"{page_key}_{token}_{size_label}.png"
        window.grab().save(str(screenshot_path))
        captured_at = _now_iso()
        screenshots.append(
            {
                "screen_name": page_key,
                "state_name": state_name,
                "scale": args.scale,
                "page": page_key,
                "size": size_label,
                "path": _repo_relative(screenshot_path),
                "screenshot_path": _repo_relative(screenshot_path),
                "timestamp": captured_at,
                "captured_at": captured_at,
                "notes": "auto-captured during ui_doctor validation checks",
                "tags": ["ui_doctor", f"screen:{page_key}", f"size:{size_label}", f"scale:{args.scale}"],
                "importance": "high",
                "scenario_reference": "doctor_layout_validation",
                "severity_reference": None,
                "issue_reference": None,
            }
        )
        return _repo_relative(screenshot_path)

    def find_required_controls(page_key: str, page_widget: QWidget) -> list[QPushButton]:
        visible_buttons = [button for button in page_widget.findChildren(QPushButton) if button.isVisible()]
        if page_key == "dashboard":
            return [button for button in visible_buttons if str(button.property("dashboardQuickButton")) == "true"]
        if page_key == "profiles":
            return [button for button in visible_buttons if str(button.property("profilesQuickAction")) == "true"]
        if page_key == "sessions":
            return [button for button in visible_buttons if str(button.property("sessionsAction")) == "true"]
        if page_key == "ai_studio":
            return [button for button in visible_buttons if str(button.property("aiAction")) == "true"]
        if page_key == "content":
            return [button for button in visible_buttons if button.objectName() in {"PrimaryCTA", "SecondaryCTA", "OutlineCTA"}]
        if page_key == "updates":
            return [button for button in visible_buttons if button.objectName() in {"PrimaryCTA", "SecondaryCTA"}]
        if page_key == "settings":
            return [button for button in visible_buttons if button.objectName() in {"PrimaryCTA", "OutlineCTA"}]
        return [button for button in visible_buttons if button.objectName() in {"PrimaryCTA", "SecondaryCTA", "OutlineCTA", "DangerCTA"}]
