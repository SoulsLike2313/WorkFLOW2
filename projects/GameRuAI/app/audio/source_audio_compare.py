from __future__ import annotations

from typing import Any


def compare_audio_metadata(source: dict[str, Any], generated: dict[str, Any]) -> dict[str, Any]:
    source_duration = int(source.get("duration_ms") or 0)
    generated_duration = int(generated.get("duration_ms") or 0)
    delta = generated_duration - source_duration
    ratio = round((generated_duration / max(1, source_duration)), 4) if source_duration else 0.0
    quality = 1.0 - min(1.0, abs(delta) / max(250, source_duration))
    return {
        "source_duration_ms": source_duration,
        "generated_duration_ms": generated_duration,
        "delta_ms": delta,
        "ratio": ratio,
        "quality": round(max(0.0, quality), 4),
        "status": "aligned" if abs(delta) <= 250 else "mismatch",
    }

