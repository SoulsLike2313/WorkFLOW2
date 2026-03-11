from __future__ import annotations

from .base import TranslationBackend


class DummyBackend(TranslationBackend):
    name = "dummy"

    def translate(self, text: str, *, source_lang: str, target_lang: str = "ru", style: str = "neutral") -> str:
        return f"[RU::{source_lang}] {text}"
