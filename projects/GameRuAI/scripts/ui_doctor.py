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
