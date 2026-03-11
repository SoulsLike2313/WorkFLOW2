from __future__ import annotations

import csv
from pathlib import Path

from .base import BaseExtractor


class CsvExtractor(BaseExtractor):
    extensions = {"csv"}

    def extract(self, path: Path, *, project_id: int, rel_path: str):
        records = []
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for idx, row in enumerate(reader, start=1):
                text = (
                    row.get("text")
                    or row.get("source_text")
                    or row.get("line_text")
                    or row.get("value")
                    or ""
                ).strip()
                if not text:
                    continue
                line_id = (row.get("line_id") or row.get("id") or f"{path.stem}_{idx}").strip()
                tags_raw = row.get("tags", "")
                tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]
                speaker = (row.get("speaker_id") or row.get("speaker") or "").strip() or None
                voice_link = (row.get("voice_link") or row.get("voice") or "").strip() or None
                metadata = {k: v for k, v in row.items() if k not in {"text", "source_text", "line_text", "value"}}
                records.append(
                    self.make_record(
                        project_id=project_id,
                        line_id=line_id,
                        rel_path=rel_path,
                        text=text,
                        speaker_id=speaker,
                        tags=tags,
                        voice_link=voice_link,
                        metadata=metadata,
                    )
                )
        return records
