from __future__ import annotations


def build_prosody_hints(*, text: str, emotion: str, style: str) -> dict:
    words = len((text or "").split())
    pace = "normal"
    if emotion in {"anger", "fear"} or style in {"dramatic", "radio"}:
        pace = "faster"
    elif emotion == "neutral" and style == "calm":
        pace = "slower"
    energy = "medium"
    if "!" in (text or ""):
        energy = "high"
    if style == "calm":
        energy = "low"
    return {
        "pace": pace,
        "energy": energy,
        "pause_hint_ms": 120 if words > 15 else 70,
    }

