from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DurationPlan:
    source_duration_ms: int
    target_output_ms: int
    alignment_ratio: float
    recommended_action: str
    confidence: float
    notes: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_duration_ms": self.source_duration_ms,
            "target_output_ms": self.target_output_ms,
            "alignment_ratio": self.alignment_ratio,
            "recommended_action": self.recommended_action,
            "confidence": self.confidence,
            "notes": list(self.notes),
        }


def plan_duration(
    text: str,
    *,
    source_duration_ms: int,
    speech_rate: float = 1.0,
    style_preset: str = "neutral",
    emotion: str = "neutral",
) -> DurationPlan:
    notes: list[str] = []
    src_ms = max(1, int(source_duration_ms or 1))
    effective_rate = max(0.55, min(float(speech_rate or 1.0), 2.2))
    char_based_ms = int(max(450, min(8000, (len(text) * 40) / effective_rate)))

    style_mul = {
        "neutral": 1.0,
        "dramatic": 1.08,
        "calm": 1.05,
        "radio": 0.94,
    }.get(style_preset, 1.0)
    emotion_mul = {
        "neutral": 1.0,
        "focused": 0.98,
        "composed": 1.02,
        "energetic": 0.94,
        "urgent": 0.92,
        "gentle": 1.06,
        "assertive": 0.97,
        "relaxed": 1.04,
    }.get(emotion, 1.0)
    adjusted = int(char_based_ms * style_mul * emotion_mul)

    if source_duration_ms > 0:
        target_ms = int((src_ms * 0.65) + (adjusted * 0.35))
        notes.append("blended source duration with text-length estimate")
    else:
        target_ms = adjusted
        notes.append("source duration missing, text-length estimate only")

    target_ms = max(380, min(9000, target_ms))
    ratio = round(target_ms / src_ms, 3)

    if ratio > 1.2:
        action = "time_compress"
    elif ratio < 0.8:
        action = "time_stretch"
    else:
        action = "aligned"

    confidence = max(0.2, 1.0 - min(0.7, abs(1.0 - ratio)))
    if source_duration_ms <= 0:
        confidence = max(0.2, confidence - 0.2)
    confidence = round(confidence, 3)

    notes.append(f"style={style_preset} emotion={emotion} speech_rate={effective_rate}")
    return DurationPlan(
        source_duration_ms=src_ms,
        target_output_ms=target_ms,
        alignment_ratio=ratio,
        recommended_action=action,
        confidence=confidence,
        notes=notes,
    )

