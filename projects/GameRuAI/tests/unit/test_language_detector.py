from __future__ import annotations

from app.language.detector import LanguageDetector


def test_detect_japanese_script() -> None:
    detector = LanguageDetector()
    result = detector.detect("任務はセクターで開始します。")
    assert result.language == "ja"
    assert result.confidence > 0.9


def test_detect_spanish_latin() -> None:
    detector = LanguageDetector()
    result = detector.detect("Hola, la mision empieza ahora.")
    assert result.language in {"es", "unknown"}


def test_detect_unknown() -> None:
    detector = LanguageDetector()
    result = detector.detect("12345 !!!")
    assert result.language == "unknown"
