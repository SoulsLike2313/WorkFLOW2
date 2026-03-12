from __future__ import annotations

from app.storage.repositories import RepositoryHub


class CorrectionMemory:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def recent_corrections(self, project_id: int, limit: int = 200) -> list[dict]:
        return self.repo.list_corrections(project_id, limit=limit)

    def remembered_pairs(self, project_id: int, limit: int = 200) -> list[dict]:
        return self.repo.list_translation_memory(project_id)[:limit]

