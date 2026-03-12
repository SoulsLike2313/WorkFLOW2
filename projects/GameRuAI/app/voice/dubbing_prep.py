from __future__ import annotations

from app.sync.duration_alignment import build_duration_alignment
from app.voice.prosody_hints import build_prosody_hints


def build_dubbing_prep(
    *,
    source_duration_ms: int,
    translated_text: str,
    emotion: str,
    style: str,
    speech_rate: float,
) -> dict:
    word_count = len((translated_text or "").split())
    estimated_target = int(max(250, (word_count / max(0.4, speech_rate)) * 340))
    alignment = build_duration_alignment(source_duration_ms=source_duration_ms, target_duration_ms=estimated_target)
    prosody = build_prosody_hints(text=translated_text, emotion=emotion, style=style)
    return {
        "estimated_target_duration_ms": estimated_target,
        "alignment": alignment,
        "prosody_hints": prosody,
        "prep_status": "ready" if translated_text.strip() else "missing_translation",
    }

