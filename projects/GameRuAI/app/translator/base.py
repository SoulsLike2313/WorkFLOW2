from __future__ import annotations

from abc import ABC, abstractmethod


class TranslationBackend(ABC):
    name = "base"

    @abstractmethod
    def translate(self, text: str, *, source_lang: str, target_lang: str = "ru", style: str = "neutral") -> str:
        raise NotImplementedError
