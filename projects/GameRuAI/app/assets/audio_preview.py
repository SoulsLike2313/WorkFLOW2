from __future__ import annotations

import wave
from pathlib import Path
from typing import Any

from .type_classifier import AUDIO_EXTENSIONS


def can_preview_audio(path: Path) -> bool:
    return path.suffix.lower().lstrip(".") in AUDIO_EXTENSIONS and path.exists() and path.is_file()


def audio_metadata(path: Path) -> dict[str, Any]:
    ext = path.suffix.lower().lstrip(".")
    metadata: dict[str, Any] = {
        "extension": ext,
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }
    if ext == "wav":
        metadata.update(_wav_metadata(path))
    return metadata


def build_audio_preview(path: Path) -> tuple[str, str, dict[str, Any]]:
    if not can_preview_audio(path):
        return "audio", "metadata_only", audio_metadata(path)
    metadata = audio_metadata(path)
    if path.suffix.lower() == ".wav":
        metadata["preview_source"] = str(path)
        metadata["preview_note"] = "wav metadata preview"
        return "audio", "ready", metadata
    return "audio", "metadata_only", metadata


def _wav_metadata(path: Path) -> dict[str, Any]:
    try:
        with wave.open(str(path), "rb") as wav:
            frames = wav.getnframes()
            framerate = wav.getframerate()
            duration = (frames / framerate) if framerate else 0.0
            return {
                "channels": wav.getnchannels(),
                "sample_rate": framerate,
                "sample_width": wav.getsampwidth(),
                "duration_ms": int(duration * 1000),
                "frames": frames,
            }
    except Exception as exc:
        return {"audio_error": str(exc)}

