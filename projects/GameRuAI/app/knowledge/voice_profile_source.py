from __future__ import annotations

from app.knowledge.source_registry import SourceRegistry


class VoiceProfileSource:
    def __init__(self, registry: SourceRegistry):
        self.registry = registry

    def mark_active(self, project_id: int, *, version: str, profile_count: int) -> None:
        self.registry.upsert_source(
            project_id=project_id,
            source_key="voice_profiles",
            source_type="voice_profiles",
            version=version,
            status="active",
            metadata={"profile_count": profile_count},
        )

