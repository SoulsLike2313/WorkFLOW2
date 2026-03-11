from __future__ import annotations

from pathlib import Path


TEXT_EXTENSIONS = {".txt", ".json", ".xml", ".csv", ".ini", ".yaml", ".yml"}
AUDIO_EXTENSIONS = {".wav", ".ogg", ".mp3"}


def classify_file(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower()
    normalized_ext = ext.lstrip(".")
    parts = {part.lower() for part in path.parts}

    if ext in TEXT_EXTENSIONS:
        if "texts" in parts:
            return "text", normalized_ext
        if "metadata" in parts:
            return "metadata", normalized_ext
        if "config" in parts:
            return "config", normalized_ext
        return "text", normalized_ext

    if ext in AUDIO_EXTENSIONS:
        return "audio", normalized_ext

    if "metadata" in parts:
        return "metadata", normalized_ext or "unknown"
    if "config" in parts:
        return "config", normalized_ext or "unknown"
    return "other", normalized_ext or "unknown"
