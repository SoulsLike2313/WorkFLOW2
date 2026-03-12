from __future__ import annotations


def infer_emotion_hint(text: str) -> dict:
    raw = text or ""
    low = raw.lower()
    score = {
        "anger": 0.0,
        "fear": 0.0,
        "joy": 0.0,
        "neutral": 0.4,
    }
    if "!" in raw:
        score["anger"] += 0.25
        score["joy"] += 0.1
    if "?" in raw:
        score["fear"] += 0.15
    if any(token in low for token in ("danger", "alert", "warning", "tehlike", "danger")):
        score["fear"] += 0.35
    if any(token in low for token in ("hello", "bonjour", "hola", "ciao", "merhaba")):
        score["joy"] += 0.35
    dominant = max(score, key=score.get)
    confidence = round(min(0.99, score[dominant]), 3)
    return {
        "dominant_emotion": dominant,
        "confidence": confidence,
        "prosody_hint": "faster" if dominant in {"anger", "fear"} else "balanced",
    }

