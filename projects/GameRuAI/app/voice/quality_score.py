from __future__ import annotations


def score_voice_attempt(*, has_translation: bool, alignment_ratio: float, style_match: bool) -> float:
    if not has_translation:
        return 0.0
    score = 0.55
    score += max(0.0, 0.25 - abs(1.0 - alignment_ratio))
    if style_match:
        score += 0.1
    return round(max(0.0, min(score, 0.99)), 4)
