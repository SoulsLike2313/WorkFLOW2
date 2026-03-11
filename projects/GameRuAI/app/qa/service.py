from __future__ import annotations

from app.core.models import QaFinding
from app.storage.repositories import RepositoryHub

from . import (
    checks_language_detection,
    checks_missing,
    checks_placeholders,
    checks_tags,
    checks_translation_presence,
    checks_voice_links,
)


class QaService:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def run(self, project_id: int) -> list[QaFinding]:
        entries = self.repo.list_entries(project_id, limit=100000)
        findings: list[QaFinding] = []
        for checker in (
            checks_missing,
            checks_placeholders,
            checks_tags,
            checks_language_detection,
            checks_translation_presence,
            checks_voice_links,
        ):
            findings.extend(checker.run(entries, project_id))
        self.repo.replace_qa_findings(project_id, findings)
        return findings
