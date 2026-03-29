from __future__ import annotations

import json
from pathlib import Path

from app.prompt_lineage import build_prompt_lineage_snapshot


def test_prompt_lineage_snapshot_tracks_brief_only_boundary(tmp_path: Path):
    manifest = {
        "schema_version": "2.1.0",
        "name": "TikTok Agent Platform",
        "slug": "tiktok_agent_platform",
        "notes": ["Lineage check note."],
    }
    (tmp_path / "PROJECT_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "PROMPT_FOR_CODEX.txt").write_text("system prompt baseline text", encoding="utf-8")

    snapshot = build_prompt_lineage_snapshot(project_root=tmp_path)
    assert snapshot["active_prompt_state"] == "PROMPT_LINEAGE_TRACKED_BRIEF_ONLY"
    assert snapshot["trusted_boundary"] == "PARTIAL_TEXT_ONLY"
    assert snapshot["text_boundary"]["full_prompt_text_exposed"] is False
    assert snapshot["lineage"]["project_slug"] == "tiktok_agent_platform"
    assert snapshot["source_brief"]["prompt_excerpt"].startswith("system prompt baseline")


def test_prompt_lineage_snapshot_reports_missing_text_boundary(tmp_path: Path):
    snapshot = build_prompt_lineage_snapshot(project_root=tmp_path)
    assert snapshot["active_prompt_state"] == "PROMPT_LINEAGE_INCOMPLETE"
    assert snapshot["trusted_boundary"] == "MISSING_TEXT_BOUNDARY"
    assert "PROMPT_FOR_CODEX.txt" in snapshot["integrity"]["missing_fields"]
