from __future__ import annotations


def test_attempt_history_persistence(services, demo_project) -> None:
    pid = int(demo_project["id"])
    services.voice_attempt_history.record(
        project_id=pid,
        entry_id=None,
        speaker_id="CHR_TEST",
        source_file="audio/source.wav",
        source_duration_ms=1200,
        generated_file="runtime/voice_outputs/test.wav",
        synthesis_mode="mock_demo_tts_stub",
        alignment_ratio=0.98,
        quality_score=0.77,
        confidence_score=0.81,
        metadata={"note": "unit"},
    )
    rows = services.voice_attempt_history.list_recent(pid, speaker_id="CHR_TEST", limit=20)
    assert rows
    assert rows[0]["speaker_id"] == "CHR_TEST"
    assert rows[0]["synthesis_mode"] == "mock_demo_tts_stub"

