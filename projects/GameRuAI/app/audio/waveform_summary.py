from __future__ import annotations

import audioop
import wave
from pathlib import Path
from typing import Any


def summarize_waveform(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {
            "path": str(path),
            "status": "missing",
            "duration_ms": 0,
            "sample_rate": 0,
            "channels": 0,
            "rms": 0,
        }

    if path.suffix.lower() != ".wav":
        return {
            "path": str(path),
            "status": "metadata_only",
            "duration_ms": 0,
            "sample_rate": 0,
            "channels": 0,
            "rms": 0,
        }

    try:
        with wave.open(str(path), "rb") as wf:
            frames = wf.getnframes()
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            raw = wf.readframes(min(frames, sample_rate * 2))
            rms = int(audioop.rms(raw, sample_width)) if raw else 0
            duration_ms = int((frames / max(1, sample_rate)) * 1000)
        return {
            "path": str(path),
            "status": "ok",
            "duration_ms": duration_ms,
            "sample_rate": sample_rate,
            "channels": channels,
            "rms": rms,
        }
    except Exception:
        return {
            "path": str(path),
            "status": "read_error",
            "duration_ms": 0,
            "sample_rate": 0,
            "channels": 0,
            "rms": 0,
        }

