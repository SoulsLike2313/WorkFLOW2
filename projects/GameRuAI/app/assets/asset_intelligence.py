from __future__ import annotations

from pathlib import Path
from typing import Any

from app.assets.asset_manifest import AssetManifestEntry, build_asset_manifest
from app.assets.asset_types import classify_asset
from app.assets.container_heuristics import evaluate_container
from app.assets.relevance_scoring import score_relevance
from app.storage.repositories import RepositoryHub


class AssetIntelligenceCore:
    """Builds a multimodal-ready asset manifest from scanned files."""

    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def build_and_store_manifest(self, *, project_id: int, game_root: Path) -> dict[str, Any]:
        scanned = self.repo.list_scanned_files(project_id)
        entries: list[AssetManifestEntry] = []

        for row in scanned:
            rel_path = str(row.get("file_path") or "")
            abs_path = game_root / rel_path
            descriptor = classify_asset(abs_path, scanned_file_type=str(row.get("file_type") or "other"))
            size_bytes = int(row.get("size_bytes") or 0)
            container = evaluate_container(abs_path, media_type=descriptor.media_type, size_bytes=size_bytes)
            relevance = score_relevance(
                abs_path,
                media_type=descriptor.media_type,
                has_voice_link=False,
                suspected_container=container.suspected_container,
            )
            entries.append(
                AssetManifestEntry(
                    file_path=rel_path,
                    media_type=descriptor.media_type,
                    content_role=descriptor.content_role,
                    extension=descriptor.extension,
                    size_bytes=size_bytes,
                    relevance_score=relevance,
                    suspected_container=container.suspected_container,
                    metadata={
                        "scanner_file_type": row.get("file_type"),
                        "manifest_group": row.get("manifest_group"),
                        "container_confidence": container.confidence,
                        "container_reason": container.reason,
                    },
                )
            )

        manifest = build_asset_manifest(entries, root=game_root)
        self.repo.replace_asset_manifest(project_id, manifest.get("assets", []))
        return manifest

