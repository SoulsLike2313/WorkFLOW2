from __future__ import annotations

import wave
from pathlib import Path
from typing import Any

from app.storage.repositories import RepositoryHub


class VoiceSampleBankService:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def rebuild(
        self,
        *,
        project_id: int,
        linked_entries: list[dict[str, Any]],
        game_root: Path,
    ) -> dict[str, Any]:
        samples: list[dict[str, Any]] = []
        for row in linked_entries:
            if not row.get("voice_link"):
                continue
            source_rel = str(row.get("voice_link"))
            source_path = game_root / source_rel
            duration_ms = self._wav_duration_ms(source_path)
            samples.append(
                {
                    "project_id": project_id,
                    "speaker_id": str(row.get("speaker_id") or "unknown"),
                    "line_id": str(row.get("line_id") or ""),
                    "scene_id": str(row.get("scene_id") or ""),
                    "source_file": source_rel,
                    "source_duration_ms": duration_ms,
                    "metadata_json": {
                        "source_exists": source_path.exists(),
                        "context_type": row.get("context_type", ""),
                        "link_valid": bool(row.get("link_valid", True)),
                        "link_confidence": float(row.get("link_confidence") or 0.0),
                    },
                }
            )

        self.repo.replace_voice_sample_bank(project_id, samples)
        return {"samples_total": len(samples)}

    @staticmethod
    def _wav_duration_ms(path: Path) -> int:
        if not path.exists():
            return 0
        try:
            with wave.open(str(path), "rb") as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                return int((frames / max(1, rate)) * 1000)
        except Exception:
            return 0

