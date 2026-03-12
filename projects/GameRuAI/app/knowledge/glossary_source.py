from __future__ import annotations

from app.knowledge.source_registry import SourceRegistry


class GlossarySource:
    def __init__(self, registry: SourceRegistry):
        self.registry = registry

    def mark_active(self, project_id: int, *, version: str, term_count: int) -> None:
        self.registry.upsert_source(
            project_id=project_id,
            source_key="glossary",
            source_type="glossary",
            version=version,
            status="active",
            metadata={"term_count": term_count},
        )

