from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AssetIndexRecord:
    project_id: int
    file_path: str
    asset_type: str
    preview_type: str
    preview_status: str
    metadata: dict[str, Any] = field(default_factory=dict)
    suspected_container: bool = False
    relevance_score: float = 0.0


@dataclass(slots=True)
class AssetPreviewRecord:
    project_id: int
    file_path: str
    preview_type: str
    preview_status: str
    preview_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ArchiveReportRecord:
    project_id: int
    file_path: str
    suspected_container: bool
    confidence: float
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)

