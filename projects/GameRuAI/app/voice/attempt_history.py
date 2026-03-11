from __future__ import annotations

from typing import Any

from app.storage.repositories import RepositoryHub


class VoiceAttemptHistoryService:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def record(
        self,
        *,
        project_id: int,
        entry_id: int | None,
        speaker_id: str,
        source_file: str,
        source_duration_ms: int,
        generated_file: str,
        synthesis_mode: str,
        alignment_ratio: float,
        quality_score: float,
        confidence_score: float,
        metadata: dict[str, Any],
    ) -> None:
        self.repo.add_voice_attempt_history(
            project_id=project_id,
            entry_id=entry_id,
            speaker_id=speaker_id,
            source_file=source_file,
            source_duration_ms=source_duration_ms,
            generated_file=generated_file,
            synthesis_mode=synthesis_mode,
            alignment_ratio=alignment_ratio,
            quality_score=quality_score,
            confidence_score=confidence_score,
            metadata_json=metadata,
        )

    def list_recent(self, project_id: int, *, speaker_id: str | None = None, limit: int = 300) -> list[dict[str, Any]]:
        return self.repo.list_voice_attempt_history(project_id=project_id, speaker_id=speaker_id, limit=limit)

