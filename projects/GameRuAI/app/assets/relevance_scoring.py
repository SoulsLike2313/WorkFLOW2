from __future__ import annotations

from pathlib import Path


def score_relevance(path: Path, *, media_type: str, has_voice_link: bool, suspected_container: bool) -> float:
    parts = {part.lower() for part in path.parts}
    score = 0.15

    if media_type in {"text", "subtitle"}:
        score += 0.45
    elif media_type == "audio":
        score += 0.3
    elif media_type == "image":
        score += 0.2
    elif media_type == "video":
        score += 0.15
    elif media_type == "container":
        score += 0.18

    if "texts" in parts:
        score += 0.22
    if "metadata" in parts:
        score += 0.16
    if "audio" in parts and has_voice_link:
        score += 0.15
    if suspected_container:
        score += 0.08

    return round(min(1.0, score), 3)

