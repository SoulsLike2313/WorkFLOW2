from __future__ import annotations

from app.core.context_models import TranslationContext
from app.translator.base import BackendUnavailableError, TranslationBackend


class TransformersBackend(TranslationBackend):
    name = "transformers"

    def __init__(self) -> None:
        self._available = False
        try:
            import transformers  # type: ignore

            self._available = bool(transformers)
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
            raise BackendUnavailableError("Transformers backend is not available in this environment.")
        scene_tag = f" scene={context.scene_id}" if context and context.scene_id else ""
        return f"[TFM::{source_lang}] {text}{scene_tag}"
