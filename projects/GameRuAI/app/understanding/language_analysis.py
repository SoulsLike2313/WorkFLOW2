from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.language.detector import LanguageDetector


@dataclass(slots=True)
class LanguageInsight:
    language: str
    confidence: float
    uncertain: bool
    ambiguous: bool
    details: dict[str, Any]


class LanguageAnalysisService:
    def __init__(self, detector: LanguageDetector):
        self.detector = detector

    def analyze(self, text: str) -> LanguageInsight:
        result = self.detector.detect(text)
        details = dict(result.details or {})
        ranked = sorted(details.items(), key=lambda item: item[1], reverse=True)
        ambiguous = len(ranked) > 1 and abs(float(ranked[0][1]) - float(ranked[1][1])) < 0.08
        uncertain = result.language in {"unknown", "mixed"} or result.confidence < 0.75
        return LanguageInsight(
            language=result.language,
            confidence=float(result.confidence),
            uncertain=uncertain,
            ambiguous=ambiguous,
            details=details,
        )

