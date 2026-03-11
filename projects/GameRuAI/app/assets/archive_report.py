from __future__ import annotations

from pathlib import Path
from typing import Any

from .type_classifier import ARCHIVE_EXTENSIONS


def inspect_archive_suspicion(path: Path, asset_type: str, size_bytes: int) -> tuple[bool, float, str, dict[str, Any]]:
    ext = path.suffix.lower().lstrip(".")
    reasons: list[str] = []
    confidence = 0.0

    if ext in ARCHIVE_EXTENSIONS:
        reasons.append(f"archive extension: .{ext}")
        confidence += 0.65
    if "pack" in path.name.lower() or "archive" in path.name.lower():
        reasons.append("archive-like filename")
        confidence += 0.2
    if asset_type in {"binary", "binary_unknown"} and size_bytes > 2 * 1024 * 1024:
        reasons.append("large opaque binary")
        confidence += 0.25

    suspected = confidence >= 0.45
    reason = ", ".join(reasons) if reasons else "no archive/container signals"
    metadata: dict[str, Any] = {
        "extension": ext or "unknown",
        "size_bytes": size_bytes,
        "reason_tokens": reasons,
    }
    return suspected, round(min(1.0, confidence), 3), reason, metadata

