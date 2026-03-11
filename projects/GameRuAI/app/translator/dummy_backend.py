from __future__ import annotations

from app.core.context_models import TranslationContext

from .base import TranslationBackend


class DummyBackend(TranslationBackend):
    name = "dummy"

    def translate(
        self,
        text: str,
        *,
        source_lang: str,
        target_lang: str = "ru",
        style: str = "neutral",
        context: TranslationContext | None = None,
    ) -> str:
        return f"[RU::{source_lang}] {text}"
