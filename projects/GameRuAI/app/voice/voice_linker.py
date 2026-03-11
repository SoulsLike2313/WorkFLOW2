from __future__ import annotations

from app.storage.repositories import RepositoryHub


class VoiceLinker:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def get_voiced_entries(self, project_id: int) -> list[dict]:
        entries = self.repo.list_entries(project_id, limit=10000)
        return [item for item in entries if item.get("voice_link")]
