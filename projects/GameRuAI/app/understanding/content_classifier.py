from __future__ import annotations

from dataclasses import dataclass

from app.normalizers.line_classifier import classify_context


@dataclass(slots=True)
class ContentUnit:
    entry_id: int
    line_id: str
    file_path: str
    content_type: str
    confidence: float
    speaker_id: str | None
    scene_id: str | None
    timing_hint_ms: int | None
    metadata: dict


class ContentClassifier:
    def classify(
        self,
        *,
        entry_id: int,
        line_id: str,
        file_path: str,
        source_text: str,
        speaker_id: str | None,
        tags: list[str],
        scene_id: str | None = None,
        timing_hint_ms: int | None = None,
    ) -> ContentUnit:
        line_type = classify_context(file_path, tags)
        confidence = 0.7 if line_type != "unknown" else 0.45
        if speaker_id:
            confidence += 0.1
        if source_text.strip().startswith("["):
            confidence += 0.05
        confidence = min(0.99, round(confidence, 3))
        return ContentUnit(
            entry_id=entry_id,
            line_id=line_id,
            file_path=file_path,
            content_type=line_type,
            confidence=confidence,
            speaker_id=speaker_id,
            scene_id=scene_id,
            timing_hint_ms=timing_hint_ms,
            metadata={"tags": tags, "length": len(source_text or "")},
        )

