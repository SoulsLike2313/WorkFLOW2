from __future__ import annotations

from typing import Any

from app.storage.repositories import RepositoryHub


class SourceRegistry:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def upsert_source(
        self,
        *,
        project_id: int,
        source_key: str,
        source_type: str,
        version: str,
        status: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.repo.upsert_knowledge_source(
            project_id=project_id,
            source_key=source_key,
            source_type=source_type,
            version=version,
            status=status,
            metadata=metadata or {},
        )

    def list_sources(self, project_id: int, limit: int = 300) -> list[dict[str, Any]]:
        return self.repo.list_knowledge_sources(project_id, limit=limit)

