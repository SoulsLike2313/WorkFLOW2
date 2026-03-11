from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class VoiceSynthesizer(ABC):
    @abstractmethod
    def synthesize(
        self,
        text: str,
        *,
        speaker_profile: dict[str, Any],
        output_path: Path,
        source_duration_ms: int = 1500,
        style_override: str | None = None,
        emotion: str | None = None,
        duration_plan: dict[str, Any] | None = None,
        synthesis_mode: str = "mock_demo_tts_stub",
    ) -> dict[str, Any]:
        raise NotImplementedError
