from __future__ import annotations

from datetime import datetime, timezone

from app.knowledge.source_registry import SourceRegistry


class SourceRefreshService:
    def __init__(self, registry: SourceRegistry):
        self.registry = registry

    def refresh(self, *, project_id: int, source_key: str, source_type: str, version: str) -> None:
        self.registry.upsert_source(
            project_id=project_id,
            source_key=source_key,
            source_type=source_type,
            version=version,
            status="refreshed",
            metadata={"refreshed_at": datetime.now(timezone.utc).isoformat()},
        )

