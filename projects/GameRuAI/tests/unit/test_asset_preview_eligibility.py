from __future__ import annotations

import wave
from pathlib import Path

from app.assets.audio_preview import build_audio_preview
from app.assets.texture_preview import build_texture_preview


def _write_minimal_png(path: Path) -> None:
    # PNG signature + IHDR with 1x1 dimensions.
    png = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\x0dIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
        b"\x90wS\xde"
    )
    path.write_bytes(png)


def _write_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 1600)


def test_texture_preview_for_supported_png(tmp_path: Path) -> None:
    png = tmp_path / "img.png"
    _write_minimal_png(png)

    preview_type, preview_status, metadata = build_texture_preview(png)
    assert preview_type == "texture"
    assert preview_status == "ready"
    assert metadata.get("width") == 1
    assert metadata.get("height") == 1


def test_audio_preview_for_supported_wav(tmp_path: Path) -> None:
    wav_path = tmp_path / "voice.wav"
    _write_wav(wav_path)
    preview_type, preview_status, metadata = build_audio_preview(wav_path)
    assert preview_type == "audio"
    assert preview_status == "ready"
    assert int(metadata.get("duration_ms", 0)) > 0


def test_metadata_fallback_for_unsupported_audio(tmp_path: Path) -> None:
    mp3 = tmp_path / "track.mp3"
    mp3.write_bytes(b"ID3-demo")
    preview_type, preview_status, metadata = build_audio_preview(mp3)
    assert preview_type == "audio"
    assert preview_status == "metadata_only"
    assert metadata.get("extension") == "mp3"
