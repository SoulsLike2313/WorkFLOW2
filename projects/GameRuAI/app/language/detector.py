from __future__ import annotations

from dataclasses import dataclass

from .heuristics import detect_script_language, score_languages, tokenize


@dataclass(slots=True)
class DetectionResult:
    language: str
    confidence: float
    details: dict[str, float]


class LanguageDetector:
    def detect(self, text: str) -> DetectionResult:
        scripted, scripted_conf = detect_script_language(text)
        if scripted:
            return DetectionResult(language=scripted, confidence=scripted_conf, details={scripted: scripted_conf})

        tokens = tokenize(text)
        scores = score_languages(tokens)
        if not scores:
            return DetectionResult(language="unknown", confidence=0.0, details={})

        lang = max(scores, key=scores.get)
        conf = float(scores[lang])
        if conf <= 0:
            lang = "unknown"
            conf = 0.15 if tokens else 0.0

        details = {k: round(v, 4) for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)}
        return DetectionResult(language=lang, confidence=round(min(0.99, conf + 0.2), 4), details=details)
