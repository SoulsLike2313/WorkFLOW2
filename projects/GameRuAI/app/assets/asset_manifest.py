from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class AssetManifestEntry:
    file_path: str
    media_type: str
    content_role: str
    extension: str
    size_bytes: int
    relevance_score: float
    suspected_container: bool
    metadata: dict[str, Any] = field(default_factory=dict)


def build_asset_manifest(entries: list[AssetManifestEntry], *, root: Path) -> dict[str, Any]:
    by_media = Counter(item.media_type for item in entries)
    by_ext = Counter(item.extension for item in entries)
    by_role = Counter(item.content_role for item in entries)

    groups: dict[str, int] = defaultdict(int)
    for item in entries:
        head = item.file_path.split("/", 1)[0] if "/" in item.file_path else "root"
        groups[head] += 1

    return {
        "root": str(root),
        "assets_total": len(entries),
        "by_media_type": dict(sorted(by_media.items())),
        "by_extension": dict(sorted(by_ext.items())),
        "by_content_role": dict(sorted(by_role.items())),
        "by_group": dict(sorted(groups.items())),
        "assets": [
            {
                "file_path": item.file_path,
                "media_type": item.media_type,
                "content_role": item.content_role,
                "extension": item.extension,
                "size_bytes": item.size_bytes,
                "relevance_score": item.relevance_score,
                "suspected_container": item.suspected_container,
                "metadata": item.metadata,
            }
            for item in entries
        ],
    }

