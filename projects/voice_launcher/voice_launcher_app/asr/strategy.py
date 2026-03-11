from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List


@dataclass
class AsrStrategyResult:
    candidates: List[str]
    engine_used: str
    note: str = ""


def recognize_with_fallback(
    *,
    prefer_engine: str,
    whisper_ready: bool,
    whisper_loading: bool,
    whisper_func: Callable[[], List[str]],
    google_func: Callable[[], List[str]],
) -> AsrStrategyResult:
    prefer_engine = (prefer_engine or "whisper").strip().lower()
    if prefer_engine == "whisper":
        if whisper_ready:
            try:
                return AsrStrategyResult(whisper_func(), "whisper")
            except Exception:
                pass
        if whisper_loading:
            return AsrStrategyResult(google_func(), "google", "cold-start fallback")
        try:
            return AsrStrategyResult(whisper_func(), "whisper")
        except Exception:
            return AsrStrategyResult(google_func(), "google", "whisper-error fallback")
    return AsrStrategyResult(google_func(), "google")

