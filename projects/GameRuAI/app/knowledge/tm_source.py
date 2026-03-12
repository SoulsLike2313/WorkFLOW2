from __future__ import annotations

from app.knowledge.source_registry import SourceRegistry


class TmSource:
    def __init__(self, registry: SourceRegistry):
        self.registry = registry

    def mark_active(self, project_id: int, *, version: str, entries_count: int) -> None:
        self.registry.upsert_source(
            project_id=project_id,
            source_key="translation_memory",
            source_type="tm",
            version=version,
            status="active",
            metadata={"entries_count": entries_count},
        )

