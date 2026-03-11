from __future__ import annotations

from pathlib import Path
from typing import Any

from app.assets.archive_report import inspect_archive_suspicion
from app.assets.audio_preview import build_audio_preview
from app.assets.preview_models import ArchiveReportRecord, AssetIndexRecord, AssetPreviewRecord
from app.assets.texture_preview import build_texture_preview
from app.assets.type_classifier import (
    classify_asset_type,
    preview_status_for_asset,
    preview_type_for_asset,
    relevance_score,
)
from app.storage.repositories import RepositoryHub


class AssetExplorerService:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def index_project_assets(
        self,
        *,
        project_id: int,
        game_root: Path,
        changed_paths: list[str] | None = None,
    ) -> dict[str, Any]:
        scanned = self.repo.list_scanned_files(project_id)
        if changed_paths is not None:
            changed = set(changed_paths)
            scanned = [row for row in scanned if str(row["file_path"]) in changed]
        else:
            self.repo.clear_asset_research(project_id)

        indexed = 0
        preview_ready = 0
        metadata_only = 0
        suspected = 0

        for row in scanned:
            rel_path = str(row["file_path"])
            abs_path = game_root / rel_path
            file_type = str(row.get("file_type") or "other")
            file_ext = str(row.get("file_ext") or "").lower().lstrip(".")
            size_bytes = int(row.get("size_bytes") or 0)

            asset_type = classify_asset_type(abs_path, file_type, file_ext)
            flagged, confidence, reason, archive_meta = inspect_archive_suspicion(abs_path, asset_type, size_bytes)
            preview_type = preview_type_for_asset(asset_type, file_ext)
            preview_status = preview_status_for_asset(asset_type, file_ext)

            metadata: dict[str, Any] = {
                "file_type": file_type,
                "file_ext": file_ext or "unknown",
                "size_bytes": size_bytes,
                "sha1": row.get("sha1", ""),
                "manifest_group": row.get("manifest_group", "root"),
                "absolute_path": str(abs_path),
            }
            preview_metadata: dict[str, Any] = {}

            if asset_type == "texture":
                preview_type, preview_status, preview_metadata = build_texture_preview(abs_path)
            elif asset_type == "audio":
                preview_type, preview_status, preview_metadata = build_audio_preview(abs_path)
            else:
                preview_metadata = {"absolute_path": str(abs_path), "size_bytes": size_bytes}

            if preview_status == "ready":
                preview_ready += 1
            else:
                metadata_only += 1
            if flagged:
                suspected += 1

            score = relevance_score(abs_path, asset_type, size_bytes, flagged)
            metadata.update(preview_metadata)

            self.repo.upsert_asset_index(
                AssetIndexRecord(
                    project_id=project_id,
                    file_path=rel_path,
                    asset_type=asset_type,
                    preview_type=preview_type,
                    preview_status=preview_status,
                    metadata=metadata,
                    suspected_container=flagged,
                    relevance_score=score,
                )
            )
            self.repo.upsert_asset_preview(
                AssetPreviewRecord(
                    project_id=project_id,
                    file_path=rel_path,
                    preview_type=preview_type,
                    preview_status=preview_status,
                    preview_path=(str(abs_path) if preview_status == "ready" else None),
                    metadata=preview_metadata,
                )
            )
            self.repo.upsert_archive_report(
                ArchiveReportRecord(
                    project_id=project_id,
                    file_path=rel_path,
                    suspected_container=flagged,
                    confidence=confidence,
                    reason=reason,
                    metadata=archive_meta,
                )
            )
            indexed += 1

        return {
            "indexed_files": indexed,
            "preview_ready": preview_ready,
            "metadata_only": metadata_only,
            "suspected_containers": suspected,
        }

    def list_index(self, project_id: int, *, limit: int = 5000) -> list[dict[str, Any]]:
        return self.repo.list_asset_index(project_id, limit=limit)

    def list_archive_reports(self, project_id: int, *, suspected_only: bool = False, limit: int = 1000) -> list[dict[str, Any]]:
        return self.repo.list_archive_reports(project_id, suspected_only=suspected_only, limit=limit)

    def get_resource_details(self, project_id: int, file_path: str) -> dict[str, Any]:
        asset = self.repo.get_asset_index(project_id, file_path) or {}
        preview = self.repo.get_asset_preview(project_id, file_path) or {}
        archive = self.repo.get_archive_report(project_id, file_path) or {}
        return {"asset": asset, "preview": preview, "archive": archive}

    def build_tree(self, project_id: int) -> dict[str, Any]:
        tree: dict[str, Any] = {}
        for row in self.repo.list_asset_index(project_id, limit=20000):
            parts = str(row["file_path"]).split("/")
            cursor = tree
            for part in parts:
                cursor = cursor.setdefault(part, {})
        return tree

