from __future__ import annotations

import math
import sys
import wave
from array import array
from pathlib import Path


class TtsStubGenerator:
    def synthesize_wav(self, output_path: Path, *, duration_ms: int, frequency: int, volume: float = 0.25) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sample_rate = 22050
        total_samples = int(sample_rate * (duration_ms / 1000.0))
        amplitude = int(32767 * max(0.05, min(volume, 0.95)))
        angular_step = (2 * math.pi * frequency) / sample_rate

        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            samples = array(
                "h",
                (
                    int(amplitude * math.sin(angular_step * idx))
                    for idx in range(total_samples)
                ),
            )
            if sys.byteorder != "little":
                samples.byteswap()
            wav_file.writeframes(samples.tobytes())
