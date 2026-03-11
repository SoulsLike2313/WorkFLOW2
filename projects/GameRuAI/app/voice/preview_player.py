from __future__ import annotations

from pathlib import Path
from typing import Any


class VoicePreviewPlayer:
    """Path resolver for preview UI (no real playback engine in MVP)."""

    def resolve_audio_path(self, candidate: str | None, *, game_root: Path, repo_root: Path) -> dict[str, Any]:
        raw = str(candidate or "").strip()
        if not raw:
            return {"status": "missing", "path": "", "exists": False, "playable": False}

        candidate_path = Path(raw)
        options: list[Path] = []
        if candidate_path.is_absolute():
            options.append(candidate_path)
        else:
            options.extend([game_root / candidate_path, repo_root / candidate_path])

        for path in options:
            if path.exists() and path.is_file():
                ext = path.suffix.lower().lstrip(".")
                return {
                    "status": "ready",
                    "path": str(path),
                    "exists": True,
                    "playable": ext in {"wav", "ogg", "mp3"},
                    "extension": ext,
                }
        return {"status": "not_found", "path": str(options[0]) if options else raw, "exists": False, "playable": False}

    def preview_payload(
        self,
        *,
        source_voice_path: str,
        generated_voice_path: str,
        game_root: Path,
        repo_root: Path,
    ) -> dict[str, Any]:
        source = self.resolve_audio_path(source_voice_path, game_root=game_root, repo_root=repo_root)
        generated = self.resolve_audio_path(generated_voice_path, game_root=game_root, repo_root=repo_root)
        return {"source": source, "generated": generated}

