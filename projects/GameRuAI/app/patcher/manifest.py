from __future__ import annotations

from datetime import datetime, timezone


def build_export_manifest(*, project_id: int, translated_entries: int, voiced_entries: int, output_dir: str) -> dict:
    return {
        "project_id": project_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "output_dir": output_dir,
        "translated_entries": translated_entries,
        "voice_attempts": voiced_entries,
        "version": "0.1.0-demo",
    }
