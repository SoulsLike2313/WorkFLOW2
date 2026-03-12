from __future__ import annotations

from app.knowledge.source_registry import SourceRegistry


class LocaleRulesSource:
    def __init__(self, registry: SourceRegistry):
        self.registry = registry

    def mark_active(self, project_id: int, *, version: str, locale: str = "ru-RU") -> None:
        self.registry.upsert_source(
            project_id=project_id,
            source_key=f"locale_rules:{locale}",
            source_type="locale_rules",
            version=version,
            status="active",
            metadata={"locale": locale},
        )

