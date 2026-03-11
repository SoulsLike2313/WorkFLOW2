from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TranslationContext:
    speaker_id: str | None = None
    scene_id: str | None = None
    neighboring_lines: list[str] = field(default_factory=list)
    line_type: str = "unknown"
    file_group: str = "unknown"
    style_preset: str = "neutral"

    def used(self) -> bool:
        return bool(
            self.speaker_id
            or self.scene_id
            or self.neighboring_lines
            or self.line_type != "unknown"
            or self.file_group != "unknown"
            or self.style_preset != "neutral"
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "speaker_id": self.speaker_id,
            "scene_id": self.scene_id,
            "neighboring_lines": list(self.neighboring_lines),
            "line_type": self.line_type,
            "file_group": self.file_group,
            "style_preset": self.style_preset,
            "context_used": self.used(),
        }
