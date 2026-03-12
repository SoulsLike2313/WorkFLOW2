from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.assets.asset_types import ARCHIVE_EXTENSIONS


@dataclass(slots=True)
class ContainerHeuristicResult:
    suspected_container: bool
    confidence: float
    reason: str
    signals: list[str]


def evaluate_container(path: Path, *, media_type: str, size_bytes: int) -> ContainerHeuristicResult:
    ext = path.suffix.lower().lstrip(".")
    signals: list[str] = []
    score = 0.0

    if ext in ARCHIVE_EXTENSIONS:
        score += 0.6
        signals.append(f"archive_ext:{ext}")
    name_low = path.name.lower()
    if any(token in name_low for token in ("pack", "bundle", "archive", "assets")):
        score += 0.2
        signals.append("archive_like_name")
    if media_type in {"binary", "container"} and size_bytes > 2 * 1024 * 1024:
        score += 0.2
        signals.append("large_binary_payload")

    confidence = round(min(1.0, score), 3)
    suspected = confidence >= 0.45
    reason = ", ".join(signals) if signals else "no container/archive signals"
    return ContainerHeuristicResult(
        suspected_container=suspected,
        confidence=confidence,
        reason=reason,
        signals=signals,
    )

