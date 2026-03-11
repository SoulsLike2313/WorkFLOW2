from __future__ import annotations

import re
from collections import Counter


LANGUAGE_HINTS: dict[str, set[str]] = {
    "en": {"the", "and", "you", "mission", "ready", "warning", "system"},
    "fr": {"le", "la", "bonjour", "mission", "avec", "pour", "vous"},
    "de": {"der", "die", "und", "hallo", "mission", "nicht", "bitte"},
    "es": {"el", "la", "hola", "mision", "gracias", "para", "vamos"},
    "it": {"ciao", "missione", "grazie", "con", "per", "non", "il"},
    "pt": {"ola", "missao", "obrigado", "com", "para", "nao", "voce"},
    "pl": {"czesc", "misja", "dziekuje", "jest", "nie", "to", "gracz"},
    "tr": {"merhaba", "gorev", "tesekkur", "icin", "degil", "oyuncu", "ve"},
}

CJK_RANGES = {
    "ja": re.compile(r"[\u3040-\u30ff\u31f0-\u31ff]"),
    "ko": re.compile(r"[\uac00-\ud7af]"),
    "zh": re.compile(r"[\u4e00-\u9fff]"),
}


def tokenize(text: str) -> list[str]:
    lowered = text.lower().replace("’", "'")
    words = re.findall(r"[a-zA-ZÀ-ÿ']+", lowered)
    return [word.strip("'") for word in words if word.strip("'")]


def detect_script_language(text: str) -> tuple[str | None, float]:
    for lang, pattern in CJK_RANGES.items():
        if pattern.search(text):
            return lang, 0.99
    return None, 0.0


def score_languages(tokens: list[str]) -> dict[str, float]:
    if not tokens:
        return {"unknown": 0.0}
    token_counts = Counter(tokens)
    scores: dict[str, float] = {}
    for lang, hints in LANGUAGE_HINTS.items():
        score = 0
        for token, count in token_counts.items():
            if token in hints:
                score += count
        scores[lang] = score / max(1, len(tokens))
    return scores
