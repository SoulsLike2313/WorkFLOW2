from __future__ import annotations

import os

from app.core.context_models import TranslationContext
from app.translator.base import BackendUnavailableError, TranslationBackend


class CloudAdapterBackend(TranslationBackend):
    """
    Optional cloud adapter.
    Working mode in MVP: adapter shell only. Real cloud calls are disabled by default.
    """

    name = "cloud_adapter"

    def is_available(self) -> bool:
        return bool(os.getenv("GAMERUAI_ENABLE_CLOUD_ADAPTER", "").strip())

    def translate(
        self,
        text: str,
        *,
        source_lang: str,
        target_lang: str = "ru",
        style: str = "neutral",
        context: TranslationContext | None = None,
    ) -> str:
        if not self.is_available():
            raise BackendUnavailableError("Cloud adapter disabled. Set GAMERUAI_ENABLE_CLOUD_ADAPTER=1 to enable.")
        speaker = context.speaker_id if context else None
        speaker_tag = f" speaker={speaker}" if speaker else ""
        return f"[CLOUD::{source_lang}->{target_lang}] {text}{speaker_tag}"

