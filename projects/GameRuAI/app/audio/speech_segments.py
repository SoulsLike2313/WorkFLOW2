from __future__ import annotations

from typing import Any


def build_speech_segments(duration_ms: int, *, chunk_ms: int = 1200) -> list[dict[str, Any]]:
    if duration_ms <= 0:
        return []
    out: list[dict[str, Any]] = []
    start = 0
    idx = 1
    while start < duration_ms:
        end = min(duration_ms, start + chunk_ms)
        out.append(
            {
                "segment_id": idx,
                "start_ms": start,
                "end_ms": end,
                "duration_ms": end - start,
                "speech_probability": 0.6,
            }
        )
        start = end
        idx += 1
    return out

