from __future__ import annotations

from app.reports.translation_report import build_translation_report


def test_translation_report_builder_calculates_rates() -> None:
    entries = [
        {"id": 1, "detected_lang": "en", "language_confidence": 0.9},
        {"id": 2, "detected_lang": "unknown", "language_confidence": 0.4},
    ]
    translations = [
        {
            "translated_text": "ru1",
            "glossary_hits_json": [{"term": "x"}],
            "tm_hits_json": [],
            "backend": "local_mock",
            "quality_score": 0.7,
            "uncertainty": 0.2,
            "latency_ms": 10,
        },
        {
            "translated_text": "ru2",
            "glossary_hits_json": [],
            "tm_hits_json": [{"score": 0.95}],
            "backend": "translation_memory",
            "quality_score": 0.5,
            "uncertainty": 0.35,
            "latency_ms": 20,
        },
    ]

    report = build_translation_report(entries, translations)
    assert report["entries_total"] == 2
    assert report["translated_count"] == 2
    assert report["glossary_hit_count"] == 1
    assert report["tm_hit_count"] >= 1
    assert report["low_quality_count"] == 1
    assert report["uncertain_language_count"] == 1

