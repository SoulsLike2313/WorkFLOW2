from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import VoiceSynthesizer
from .tts_stub import TtsStubGenerator


class MockVoiceSynthesizer(VoiceSynthesizer):
    def __init__(self):
        self.tts_stub = TtsStubGenerator()

    def synthesize(
        self,
        text: str,
        *,
        speaker_profile: dict[str, Any],
        output_path: Path,
        source_duration_ms: int = 1500,
    ) -> dict[str, Any]:
        speech_rate = float(speaker_profile.get("speech_rate", 1.0))
        base_frequency = int(speaker_profile.get("base_frequency", 220))
        style_preset = str(speaker_profile.get("style_preset", "neutral"))

        # Duration roughly follows text length and speaker speed.
        target_duration = int(max(600, min(6000, (len(text) * 45) / max(0.5, speech_rate))))
        frequency = base_frequency + (10 if style_preset == "dramatic" else 0)
        self.tts_stub.synthesize_wav(output_path, duration_ms=target_duration, frequency=frequency)

        return {
            "duration_ms": target_duration,
            "frequency": frequency,
            "style_preset": style_preset,
            "source_duration_ms": source_duration_ms,
        }
