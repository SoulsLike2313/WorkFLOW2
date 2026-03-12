from __future__ import annotations


def track_confidence(*, confidence: float, uncertainty: float) -> dict:
    level = "high"
    if uncertainty >= 0.28 or confidence < 0.6:
        level = "low"
    elif uncertainty >= 0.16 or confidence < 0.8:
        level = "medium"
    return {
        "confidence": round(float(confidence), 4),
        "uncertainty": round(float(uncertainty), 4),
        "level": level,
    }

