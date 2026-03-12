from __future__ import annotations

from app.sync.audio_sync import plan_audio_sync
from app.sync.duration_alignment import build_duration_alignment
from app.sync.rebuild_plan import build_rebuild_plan
from app.sync.subtitle_sync import plan_subtitle_sync


def test_duration_alignment_structure() -> None:
    plan = build_duration_alignment(source_duration_ms=1200, target_duration_ms=1350)
    assert plan["source_duration_ms"] == 1200
    assert "recommended_adjustment" in plan


def test_sync_pipeline_outputs() -> None:
    audio = plan_audio_sync(source_duration_ms=1000, generated_duration_ms=1300)
    subtitle = plan_subtitle_sync(source_duration_ms=1000, translated_text="Это демонстрационная строка")
    rebuild = build_rebuild_plan(audio_sync=audio, subtitle_sync=subtitle)
    assert "overall_risk" in rebuild
    assert rebuild["export_targets"]

