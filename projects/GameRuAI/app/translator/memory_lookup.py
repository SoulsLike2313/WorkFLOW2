from __future__ import annotations

from app.memory.service import TranslationMemoryService


class MemoryLookup:
    def __init__(self, memory_service: TranslationMemoryService):
        self.memory_service = memory_service

    def find(self, project_id: int, source_lang: str, source_text: str) -> list[dict]:
        return self.memory_service.lookup(project_id, source_lang, source_text)
