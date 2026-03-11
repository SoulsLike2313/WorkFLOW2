from __future__ import annotations

from app.language.detector import LanguageDetector


def test_language_detection_stability_samples() -> None:
    detector = LanguageDetector()
    samples = [
        ("Hello mission ready", "en"),
        ("Bonjour la mission", "fr"),
        ("Hallo mission", "de"),
        ("Hola mision", "es"),
        ("任務を開始します", "ja"),
        ("任务开始", "zh"),
    ]
    for text, expected in samples:
        result = detector.detect(text)
        if expected in {"en", "fr", "de", "es"}:
            assert result.language in {expected, "unknown"}
        else:
            assert result.language == expected
