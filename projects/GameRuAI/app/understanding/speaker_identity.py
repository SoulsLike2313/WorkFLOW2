from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SpeakerIdentity:
    speaker_id: str
    confidence: float
    reason: str


class SpeakerIdentityService:
    def infer(self, *, entry_speaker_id: str | None, metadata_speaker: str | None, scene_hint: str | None) -> SpeakerIdentity:
        if entry_speaker_id:
            return SpeakerIdentity(entry_speaker_id, 0.92, "entry speaker_id")
        if metadata_speaker:
            return SpeakerIdentity(metadata_speaker, 0.75, "metadata speaker")
        if scene_hint:
            return SpeakerIdentity("scene_unknown", 0.35, "scene fallback")
        return SpeakerIdentity("unknown", 0.2, "no speaker evidence")

