from __future__ import annotations

from pathlib import Path
from typing import Any

from app.storage.repositories import RepositoryHub


class VoiceLinker:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def analyze_links(
        self,
        project_id: int,
        *,
        game_root: Path | None = None,
        scene_index: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        entries = self.repo.list_entries(project_id, limit=10000)
        scene_index = scene_index or {}
        analyzed: list[dict[str, Any]] = []
        for item in entries:
            voice_link = str(item.get("voice_link") or "").strip()
            speaker_id = str(item.get("speaker_id") or "unknown")
            line_id = str(item.get("line_id") or "")
            scene_id = scene_index.get(line_id, "")
            reason_tokens: list[str] = []

            confidence = 0.0
            if voice_link:
                confidence += 0.45
                reason_tokens.append("voice_link present")
            if speaker_id and speaker_id != "unknown":
                confidence += 0.2
                reason_tokens.append("speaker id")
            if scene_id:
                confidence += 0.15
                reason_tokens.append("scene mapping")
            if str(item.get("context_type") or ""):
                confidence += 0.05
                reason_tokens.append("context metadata")

            link_valid = bool(voice_link)
            if voice_link and game_root:
                source_path = game_root / voice_link
                if source_path.exists() and source_path.is_file():
                    confidence += 0.15
                    reason_tokens.append("source file exists")
                else:
                    link_valid = False
                    confidence -= 0.25
                    reason_tokens.append("broken source link")

            analyzed.append(
                {
                    **item,
                    "scene_id": scene_id,
                    "link_valid": link_valid,
                    "link_reason": ", ".join(reason_tokens) if reason_tokens else "no link data",
                    "link_confidence": round(max(0.01, min(0.99, confidence)), 3),
                    "linking_strategy": "speaker_id+metadata+scene",
                }
            )
        return analyzed

    def get_voiced_entries(
        self,
        project_id: int,
        *,
        game_root: Path | None = None,
        scene_index: dict[str, str] | None = None,
        include_invalid: bool = False,
    ) -> list[dict[str, Any]]:
        analyzed = self.analyze_links(project_id, game_root=game_root, scene_index=scene_index)
        out = [item for item in analyzed if item.get("voice_link")]
        if not include_invalid:
            out = [item for item in out if item.get("link_valid", True)]
        return out
