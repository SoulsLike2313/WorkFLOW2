from __future__ import annotations

from typing import Any

from app.storage.repositories import RepositoryHub


class SpeakerProfileBank:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def list_profiles(self, project_id: int) -> dict[str, dict[str, Any]]:
        return self.repo.list_voice_profiles(project_id)

    def update_profile(self, project_id: int, speaker_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        profile = self.repo.list_voice_profiles(project_id).get(speaker_id, {})
        merged = {**profile, **patch}
        self.repo.upsert_voice_profile(project_id, speaker_id, merged)
        return merged

