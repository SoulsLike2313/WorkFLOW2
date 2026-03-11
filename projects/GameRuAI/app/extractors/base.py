from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from app.core.models import ExtractionRecord
from app.normalizers.line_classifier import classify_context
from app.normalizers.placeholder_guard import extract_placeholders
from app.normalizers.tag_guard import extract_tags
from app.normalizers.text_cleaner import clean_text


class BaseExtractor(ABC):
    extensions: set[str] = set()

    def supports(self, path: Path) -> bool:
        return path.suffix.lower().lstrip(".") in self.extensions

    @abstractmethod
    def extract(self, path: Path, *, project_id: int, rel_path: str) -> list[ExtractionRecord]:
        raise NotImplementedError

    def make_record(
        self,
        *,
        project_id: int,
        line_id: str,
        rel_path: str,
        text: str,
        speaker_id: str | None = None,
        tags: list[str] | None = None,
        voice_link: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExtractionRecord:
        tags = tags or []
        cleaned = clean_text(text)
        return ExtractionRecord(
            project_id=project_id,
            line_id=line_id,
            file_path=rel_path,
            source_text=cleaned,
            speaker_id=speaker_id,
            context_type=classify_context(rel_path, tags),
            tags=tags + extract_tags(cleaned),
            placeholders=extract_placeholders(cleaned),
            voice_link=voice_link,
            metadata=metadata or {},
        )
