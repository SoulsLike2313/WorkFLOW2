from __future__ import annotations


def build_duration_alignment(*, source_duration_ms: int, target_duration_ms: int) -> dict:
    delta = int(target_duration_ms) - int(source_duration_ms)
    ratio = round(int(target_duration_ms) / max(1, int(source_duration_ms)), 4) if source_duration_ms else 0.0
    if abs(delta) <= 180:
        adjustment = "none"
        confidence = 0.9
    elif abs(delta) <= 420:
        adjustment = "minor_time_stretch"
        confidence = 0.72
    else:
        adjustment = "rewrite_or_profile_tune"
        confidence = 0.45
    return {
        "source_duration_ms": int(source_duration_ms),
        "target_duration_ms": int(target_duration_ms),
        "delta_ms": delta,
        "alignment_ratio": ratio,
        "recommended_adjustment": adjustment,
        "confidence": round(confidence, 3),
    }

