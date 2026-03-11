from __future__ import annotations

from app.storage.repositories import RepositoryHub


class CorrectionTracker:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def list_recent(self, project_id: int, limit: int = 100) -> list[dict]:
        return self.repo.list_corrections(project_id, limit=limit)
