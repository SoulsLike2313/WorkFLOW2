from __future__ import annotations

from app.sync.export_targets import default_export_targets


def build_rebuild_plan(*, audio_sync: dict, subtitle_sync: dict) -> dict:
    high_risk = audio_sync.get("sync_risk") == "high" or subtitle_sync.get("status") == "too_fast_for_reading"
    return {
        "audio_sync": audio_sync,
        "subtitle_sync": subtitle_sync,
        "export_targets": default_export_targets(),
        "overall_risk": "high" if high_risk else "normal",
        "recommendation": "manual_review_before_export" if high_risk else "safe_to_export_demo_patch",
    }

