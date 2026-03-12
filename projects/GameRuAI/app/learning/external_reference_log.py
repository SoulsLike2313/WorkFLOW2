from __future__ import annotations

from typing import Any

from app.storage.repositories import RepositoryHub


class ExternalReferenceLog:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def record(self, *, project_id: int, entry_id: int | None, provider: str, payload: dict[str, Any]) -> None:
        self.repo.add_external_reference_event(
            project_id=project_id,
            entry_id=entry_id,
            provider=provider,
            payload=payload,
        )

    def list_recent(self, project_id: int, limit: int = 300) -> list[dict[str, Any]]:
        return self.repo.list_external_reference_events(project_id, limit=limit)

