from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SubtitleAlignmentResult:
    line_id: str
    has_audio_link: bool
    alignment_confidence: float
    note: str


class SubtitleAlignmentService:
    def align(self, *, line_id: str, voice_link: str | None, content_type: str) -> SubtitleAlignmentResult:
        has_audio = bool((voice_link or "").strip())
        if content_type in {"dialogue", "radio", "combat"} and has_audio:
            return SubtitleAlignmentResult(line_id=line_id, has_audio_link=True, alignment_confidence=0.86, note="line has voice link")
        if content_type in {"ui", "tutorial", "system"}:
            return SubtitleAlignmentResult(line_id=line_id, has_audio_link=has_audio, alignment_confidence=0.55, note="likely text-only context")
        return SubtitleAlignmentResult(line_id=line_id, has_audio_link=has_audio, alignment_confidence=0.4, note="weak subtitle/audio relation")

