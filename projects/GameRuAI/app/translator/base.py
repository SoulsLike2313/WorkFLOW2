from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.context_models import TranslationContext


class BackendUnavailableError(RuntimeError):
    """Raised when optional backend dependencies are missing."""


class TranslationBackend(ABC):
    name = "base"

    def is_available(self) -> bool:
        return True

    @abstractmethod
    def translate(
        self,
        text: str,
        *,
        source_lang: str,
        target_lang: str = "ru",
        style: str = "neutral",
        context: TranslationContext | None = None,
    ) -> str:
        raise NotImplementedError
