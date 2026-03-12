from __future__ import annotations

from app.storage.repositories import RepositoryHub


class RegressionMemory:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def remember_snapshot(self, *, project_id: int, snapshot_type: str, payload: dict) -> None:
        self.repo.add_quality_snapshot(project_id=project_id, snapshot_type=snapshot_type, payload=payload)

    def latest(self, project_id: int, snapshot_type: str, limit: int = 30) -> list[dict]:
        return self.repo.list_quality_snapshots(project_id, snapshot_type=snapshot_type, limit=limit)

