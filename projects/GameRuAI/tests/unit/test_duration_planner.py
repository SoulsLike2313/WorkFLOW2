from __future__ import annotations

from app.voice.duration_planner import plan_duration


def test_duration_planner_returns_alignment_plan() -> None:
    plan = plan_duration(
        "This is a fairly long line for duration planning.",
        source_duration_ms=1500,
        speech_rate=1.0,
        style_preset="dramatic",
        emotion="energetic",
    )
    assert plan.target_output_ms > 0
    assert 0.0 < plan.alignment_ratio
    assert plan.recommended_action in {"aligned", "time_stretch", "time_compress"}
    assert 0.0 < plan.confidence <= 1.0

