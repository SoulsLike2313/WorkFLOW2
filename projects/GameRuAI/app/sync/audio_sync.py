from __future__ import annotations

from app.sync.duration_alignment import build_duration_alignment


def plan_audio_sync(*, source_duration_ms: int, generated_duration_ms: int) -> dict:
    alignment = build_duration_alignment(
        source_duration_ms=source_duration_ms,
        target_duration_ms=generated_duration_ms,
    )
    risk = "low"
    if abs(int(alignment["delta_ms"])) > 450:
        risk = "high"
    elif abs(int(alignment["delta_ms"])) > 220:
        risk = "medium"
    return {
        **alignment,
        "sync_risk": risk,
        "status": "ok" if risk == "low" else "needs_review",
    }

