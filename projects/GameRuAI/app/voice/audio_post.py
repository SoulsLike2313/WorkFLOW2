from __future__ import annotations


def alignment_plan(source_duration_ms: int, output_duration_ms: int) -> dict[str, float | str]:
    if source_duration_ms <= 0:
        source_duration_ms = 1
    ratio = output_duration_ms / source_duration_ms
    if ratio > 1.2:
        action = "time_compress"
    elif ratio < 0.8:
        action = "time_stretch"
    else:
        action = "aligned"
    return {
        "ratio": round(ratio, 3),
        "recommended_action": action,
    }
