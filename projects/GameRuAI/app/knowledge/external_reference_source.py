from __future__ import annotations

from app.knowledge.source_registry import SourceRegistry


class ExternalReferenceSource:
    def __init__(self, registry: SourceRegistry):
        self.registry = registry

    def mark_state(self, project_id: int, *, version: str, status: str, provider: str) -> None:
        self.registry.upsert_source(
            project_id=project_id,
            source_key=f"external_reference:{provider}",
            source_type="external_reference",
            version=version,
            status=status,
            metadata={"provider": provider},
        )

