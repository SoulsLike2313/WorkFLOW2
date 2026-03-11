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
        style_override: str | None = None,
        emotion: str | None = None,
        duration_plan: dict[str, Any] | None = None,
        synthesis_mode: str = "mock_demo_tts_stub",
    ) -> dict[str, Any]:
        speaker_id = str(speaker_profile.get("speaker_id", "unknown"))
        speech_rate = float(speaker_profile.get("speech_rate", 1.0))
        base_frequency = int(speaker_profile.get("base_frequency", 220))
        style_preset = str(style_override or speaker_profile.get("style_preset", "neutral"))
        emotion_bias = str(emotion or speaker_profile.get("emotion_bias", "neutral"))

        # Stable per-speaker offset to make voice attempts reproducible.
        speaker_variation = (sum(ord(ch) for ch in speaker_id) % 21) - 10
        style_shift = {"neutral": 0, "dramatic": 12, "calm": -8, "radio": 5}.get(style_preset, 0)
        emotion_shift = {
            "neutral": 0,
            "focused": -2,
            "energetic": 6,
            "urgent": 8,
            "gentle": -4,
            "assertive": 3,
            "relaxed": -3,
        }.get(emotion_bias, 0)
        frequency = max(120, base_frequency + speaker_variation + style_shift + emotion_shift)

        if duration_plan and duration_plan.get("target_output_ms"):
            target_duration = int(duration_plan["target_output_ms"])
        else:
            target_duration = int(max(600, min(7000, (len(text) * 44) / max(0.5, speech_rate))))
        self.tts_stub.synthesize_wav(output_path, duration_ms=target_duration, frequency=frequency)

        return {
            "duration_ms": target_duration,
            "frequency": frequency,
            "speaker_variation": speaker_variation,
            "style_preset": style_preset,
            "emotion": emotion_bias,
            "speech_rate": speech_rate,
            "source_duration_ms": source_duration_ms,
            "synthesis_mode": synthesis_mode,
            "engine": "tts_stub",
            "duration_plan": duration_plan or {},
        }
