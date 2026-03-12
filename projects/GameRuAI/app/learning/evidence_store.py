from __future__ import annotations

from typing import Any

from app.storage.repositories import RepositoryHub


class EvidenceStore:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def record(
        self,
        *,
        project_id: int,
        evidence_type: str,
        entity_ref: str,
        confidence: float,
        status: str,
        payload: dict[str, Any],
    ) -> None:
        self.repo.add_evidence_record(
            project_id=project_id,
            evidence_type=evidence_type,
            entity_ref=entity_ref,
            confidence=confidence,
            status=status,
            payload=payload,
        )

    def list_recent(self, project_id: int, limit: int = 200) -> list[dict[str, Any]]:
        return self.repo.list_evidence_records(project_id, limit=limit)

