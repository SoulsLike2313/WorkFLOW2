from __future__ import annotations


def plan_subtitle_sync(*, source_duration_ms: int, translated_text: str) -> dict:
    char_count = len(translated_text or "")
    cps = round(char_count / max(0.5, source_duration_ms / 1000), 3) if source_duration_ms else 0.0
    issue = "ok"
    if cps > 20:
        issue = "too_fast_for_reading"
    elif cps > 16:
        issue = "borderline"
    return {
        "source_duration_ms": int(source_duration_ms),
        "chars": char_count,
        "chars_per_second": cps,
        "status": issue,
        "confidence": 0.75 if issue == "ok" else 0.52,
    }

