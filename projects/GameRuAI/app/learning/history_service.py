from __future__ import annotations

from app.storage.repositories import RepositoryHub


class HistoryService:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def translation_history(self, project_id: int, limit: int = 500) -> list[dict]:
        return self.repo.list_translations(project_id)[:limit]

    def adaptation_history(self, project_id: int, limit: int = 200) -> list[dict]:
        return self.repo.list_adaptation_events(project_id, limit=limit)
