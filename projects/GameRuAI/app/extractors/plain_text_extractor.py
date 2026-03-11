from __future__ import annotations

from pathlib import Path

from .base import BaseExtractor


class PlainTextExtractor(BaseExtractor):
    extensions = {"txt"}

    def extract(self, path: Path, *, project_id: int, rel_path: str):
        records = []
        for idx, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [chunk.strip() for chunk in line.split("|")]
            if len(parts) >= 6:
                line_id, speaker, context, voice_link, tags_raw = parts[:5]
                text = "|".join(parts[5:]).strip()
                tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]
                record = self.make_record(
                    project_id=project_id,
                    line_id=line_id or f"{path.stem}_{idx}",
                    rel_path=rel_path,
                    text=text,
                    speaker_id=speaker or None,
                    tags=tags + ([context] if context else []),
                    voice_link=voice_link or None,
                    metadata={"source_format": "txt"},
                )
                records.append(record)
                continue
            records.append(
                self.make_record(
                    project_id=project_id,
                    line_id=f"{path.stem}_{idx}",
                    rel_path=rel_path,
                    text=line,
                    metadata={"source_format": "txt_fallback"},
                )
            )
        return records
