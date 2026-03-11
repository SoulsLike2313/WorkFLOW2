from __future__ import annotations

from app.reports.project_summary import build_project_summary


def test_project_summary_aggregates_quality_and_qa() -> None:
    entries = [
        {"id": 1, "line_id": "L1", "detected_lang": "en", "language_confidence": 0.9, "context_type": "dialogue", "translation_status": "translated", "translated_text": "ru"},
        {"id": 2, "line_id": "L2", "detected_lang": "unknown", "language_confidence": 0.3, "context_type": "ui", "translation_status": "pending", "translated_text": ""},
    ]
    translations = [{"backend": "local_mock"}]
    translation_report = {
        "translation_coverage_rate": 0.5,
        "low_quality_count": 1,
        "uncertain_language_rate": 0.5,
        "backend_usage": {"local_mock": 1},
    }
    voice_attempts = [
        {"status": "generated", "quality_score": 0.8, "metadata_json": {"alignment": {"ratio": 1.02}, "synthesis_mode": "mock_demo_tts_stub"}}
    ]
    summary = build_project_summary(
        entries=entries,
        translations=translations,
        translation_report=translation_report,
        voice_attempts=voice_attempts,
        voice_history=[{"id": 1}],
        speaker_groups=[{"speaker_id": "S1", "line_count": 1, "linked_count": 1, "broken_links": 0, "avg_confidence": 0.9}],
        qa_findings=[{"severity": "warning", "check_name": "tags_mismatch", "details_json": {"line_id": "L1"}}],
        export_jobs=[],
        companion_sessions=[],
        watched_events=[],
        asset_index=[],
    )
    assert summary["quality_dashboard"]["translation_coverage_rate"] == 0.5
    assert summary["voice"]["attempts_total"] == 1
    assert summary["qa_dashboard"]["broken_tags"] == 1
    assert summary["language"]["uncertain_count"] == 1

