from __future__ import annotations

from app.glossary.service import GlossaryService


class GlossaryInjector:
    def __init__(self, glossary_service: GlossaryService):
        self.glossary_service = glossary_service

    def inject(self, project_id: int, source_lang: str, text: str) -> tuple[str, list[dict]]:
        return self.glossary_service.apply(project_id, source_lang, text)
