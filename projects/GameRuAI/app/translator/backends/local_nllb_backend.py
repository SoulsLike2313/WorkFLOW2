from __future__ import annotations

from app.core.context_models import TranslationContext
from app.translator.base import BackendUnavailableError, TranslationBackend


class LocalNllbBackend(TranslationBackend):
    """Foundation backend adapter for local NLLB-like models."""

    name = "local_nllb"

    def __init__(self) -> None:
        self._available = False
        try:
            import sentencepiece  # type: ignore

            self._available = bool(sentencepiece)
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
            raise BackendUnavailableError("Local NLLB backend is unavailable (dependency not installed).")
        scene_tag = f" scene={context.scene_id}" if context and context.scene_id else ""
        return f"[NLLB::{source_lang}->{target_lang}] {text}{scene_tag}"

