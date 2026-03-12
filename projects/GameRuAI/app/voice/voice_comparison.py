from __future__ import annotations

from app.audio.source_audio_compare import compare_audio_metadata


def compare_source_and_generated(source_summary: dict, generated_summary: dict) -> dict:
    cmp_result = compare_audio_metadata(source_summary, generated_summary)
    return {
        **cmp_result,
        "recommendation": "keep" if cmp_result.get("quality", 0) >= 0.65 else "retune_profile_or_style",
    }

