from __future__ import annotations

from app.core.context_models import TranslationContext
from app.translator.base import BackendUnavailableError, TranslationBackend


class ArgosBackend(TranslationBackend):
    name = "argos"

    def __init__(self) -> None:
        self._available = False
        try:
            import argostranslate.translate as _  # type: ignore

            self._available = True
        except Exception:
            self._available = False

    def is_available(self) -> bool:
        return self._available

    def translate(
        self,
        text: str,
        *,
        source_lang: str,
        target_lang: str = "ru",
        style: str = "neutral",
        context: TranslationContext | None = None,
    ) -> str:
        if not self._available:
            raise BackendUnavailableError("Argos backend is not available in this environment.")
        # Lightweight demo behavior to avoid heavy model bootstrap in MVP.
        context_tag = f" [ctx:{context.line_type}]" if context and context.used() else ""
        return f"[ARGOS::{source_lang}] {text}{context_tag}"
