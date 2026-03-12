from __future__ import annotations

from app.audio.analysis_service import AudioAnalysisService
from app.audio.waveform_summary import summarize_waveform


def test_waveform_summary_on_demo_audio(services) -> None:
    wav_path = sorted((services.config.paths.fixtures_root / "audio").glob("voice_*.wav"))[0]
    summary = summarize_waveform(wav_path)
    assert summary["status"] in {"ok", "metadata_only"}
    assert summary["duration_ms"] >= 0


def test_audio_analysis_service_returns_segments(services) -> None:
    wav_path = sorted((services.config.paths.fixtures_root / "audio").glob("voice_*.wav"))[1]
    report = AudioAnalysisService().analyze(wav_path, line_id="l1", transcript_text="hello world")
    assert "summary" in report
    assert "segments" in report
    assert "transcript_links" in report
