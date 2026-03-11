from __future__ import annotations

import re
from dataclasses import asdict

from app.storage.repositories import RepositoryHub

from .models import GlossaryTerm


class GlossaryService:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def add_term(self, project_id: int, term: GlossaryTerm) -> None:
        self.repo.upsert_glossary_term(
            project_id=project_id,
            source_term=term.source_term,
            target_term=term.target_term,
            source_lang=term.source_lang,
            case_sensitive=term.case_sensitive,
            priority=term.priority,
        )
        self.repo.add_adaptation_event(
            project_id,
            event_type="glossary_added",
            event_scope="glossary",
            event_ref=term.source_term,
            details=asdict(term),
        )

    def list_terms(self, project_id: int) -> list[dict]:
        return self.repo.list_glossary_terms(project_id)

    def apply(self, project_id: int, source_lang: str, text: str) -> tuple[str, list[dict]]:
        terms = [
            t
            for t in self.repo.list_glossary_terms(project_id)
            if t["source_lang"] in {source_lang, "any"}
        ]
        transformed = text
        hits: list[dict] = []
        for term in terms:
            source = term["source_term"]
            target = term["target_term"]
            case_sensitive = bool(term["case_sensitive"])
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(re.escape(source), flags)
            if pattern.search(transformed):
                transformed = pattern.sub(target, transformed)
                hits.append({"source": source, "target": target, "priority": term["priority"]})
        return transformed, hits
