from __future__ import annotations

import re

from app.core.context_models import TranslationContext

from .base import TranslationBackend


TOKEN_MAP = {
    "en": {"mission": "миссия", "ready": "готово", "danger": "опасность", "shop": "магазин", "quest": "задание"},
    "fr": {"mission": "миссия", "bonjour": "привет", "alerte": "тревога", "marchand": "торговец"},
    "de": {"mission": "миссия", "hallo": "привет", "achtung": "внимание", "handel": "торговля"},
    "es": {"mision": "миссия", "hola": "привет", "peligro": "опасность", "tienda": "магазин"},
    "it": {"missione": "миссия", "ciao": "привет", "pericolo": "опасность", "negozio": "магазин"},
    "pt": {"missao": "миссия", "ola": "привет", "perigo": "опасность", "loja": "магазин"},
    "pl": {"misja": "миссия", "czesc": "привет", "niebezpieczenstwo": "опасность", "sklep": "магазин"},
    "tr": {"gorev": "миссия", "merhaba": "привет", "tehlike": "опасность", "dukkan": "магазин"},
}


class LocalMockBackend(TranslationBackend):
    name = "local_mock"

    def translate(
        self,
        text: str,
        *,
        source_lang: str,
        target_lang: str = "ru",
        style: str = "neutral",
        context: TranslationContext | None = None,
    ) -> str:
        if source_lang in {"ja", "ko", "zh"}:
            prefix = {"ja": "яп", "ko": "кор", "zh": "кит"}[source_lang]
            suffix = f" [ctx:{context.line_type}]" if context and context.used() else ""
            return f"[{prefix}] {text}{suffix}"

        mapping = TOKEN_MAP.get(source_lang, {})
        tokens = re.findall(r"\w+|\W+", text, flags=re.UNICODE)
        out = []
        for token in tokens:
            replacement = mapping.get(token.lower())
            out.append(replacement if replacement else token)
        base = "".join(out)

        style_suffix = {
            "neutral": "",
            "dramatic": "!",
            "calm": ".",
            "radio": " [радио-канал]",
        }.get(style, "")
        if context and context.scene_id:
            style_suffix += f" [scene:{context.scene_id}]"
        return f"{base}{style_suffix}"
