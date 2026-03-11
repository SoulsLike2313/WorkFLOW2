from __future__ import annotations

from app.normalizers.placeholder_guard import placeholders_preserved
from app.normalizers.tag_guard import tags_preserved


def score_translation(
    source: str,
    translated: str,
    *,
    glossary_hits: int,
    tm_hits: int,
    uncertainty: float,
) -> float:
    if not translated.strip():
        return 0.0

    ratio = min(len(translated), len(source) + 20) / max(1, len(source))
    base = 0.55 + min(0.25, ratio * 0.2)

    if placeholders_preserved(source, translated):
        base += 0.08
    else:
        base -= 0.2

    if tags_preserved(source, translated):
        base += 0.05
    else:
        base -= 0.1

    base += min(0.06, glossary_hits * 0.02)
    base += min(0.1, tm_hits * 0.05)
    base -= min(0.25, uncertainty * 0.4)
    return round(max(0.0, min(base, 0.99)), 4)
