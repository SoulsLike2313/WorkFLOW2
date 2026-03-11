from __future__ import annotations

import json
from pathlib import Path

from app.storage.repositories import RepositoryHub


class SpeakerProfileService:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def load_from_metadata(self, project_id: int, metadata_file: Path) -> dict[str, dict]:
        payload = json.loads(metadata_file.read_text(encoding="utf-8-sig"))
        profiles: dict[str, dict] = {}
        for item in payload:
            speaker_id = item.get("speaker_id")
            if not speaker_id:
                continue
            self.repo.upsert_voice_profile(project_id, speaker_id, item)
            profiles[speaker_id] = item
        return profiles

    def get_profiles(self, project_id: int) -> dict[str, dict]:
        return self.repo.list_voice_profiles(project_id)

    def update_profile(self, project_id: int, speaker_id: str, patch: dict) -> dict:
        profiles = self.repo.list_voice_profiles(project_id)
        current = profiles.get(speaker_id, {"speaker_id": speaker_id})
        current.update(patch)
        self.repo.upsert_voice_profile(project_id, speaker_id, current)
        self.repo.add_adaptation_event(
            project_id,
            event_type="voice_profile_updated",
            event_scope="voice",
            event_ref=speaker_id,
            details={"patch": patch, "result_profile": current},
        )
        return current
