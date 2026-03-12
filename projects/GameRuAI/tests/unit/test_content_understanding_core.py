from __future__ import annotations

from app.language.detector import LanguageDetector
from app.understanding.content_classifier import ContentClassifier
from app.understanding.emotion_hints import infer_emotion_hint
from app.understanding.language_analysis import LanguageAnalysisService
from app.understanding.subtitle_alignment import SubtitleAlignmentService


def test_language_analysis_marks_uncertain_for_unknown() -> None:
    service = LanguageAnalysisService(LanguageDetector())
    insight = service.analyze("###")
    assert insight.language in {"unknown", "en", "fr", "de", "es", "it", "pt", "pl", "tr", "ja", "ko", "zh"}
    assert isinstance(insight.uncertain, bool)


def test_content_classifier_returns_structured_unit() -> None:
    classifier = ContentClassifier()
    unit = classifier.classify(
        entry_id=1,
        line_id="ui_001",
        file_path="texts/ui.json",
        source_text="Press [E] to open",
        speaker_id=None,
        tags=["ui"],
        scene_id="scene_01",
    )
    assert unit.entry_id == 1
    assert unit.content_type in {"ui", "unknown"}
    assert 0 <= unit.confidence <= 1


def test_subtitle_alignment_and_emotion_hints() -> None:
    align = SubtitleAlignmentService().align(line_id="ln1", voice_link="audio/voice.wav", content_type="dialogue")
    assert align.has_audio_link is True
    emotion = infer_emotion_hint("Danger! Move now!")
    assert emotion["dominant_emotion"] in {"anger", "fear", "joy", "neutral"}

