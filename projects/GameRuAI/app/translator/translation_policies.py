from __future__ import annotations

from dataclasses import dataclass

from app.core.context_models import TranslationContext


@dataclass(slots=True)
class TranslationPolicyDecision:
    backend_preference: list[str]
    reasons: list[str]
    strict_quality_mode: bool


class TranslationPolicies:
    def select(self, *, source_lang: str, context: TranslationContext | None) -> TranslationPolicyDecision:
        reasons: list[str] = []
        preference = ["local_mock", "dummy"]
        strict_quality_mode = False

        if source_lang in {"ja", "ko", "zh"}:
            preference = ["transformers", "local_nllb", "local_mock", "dummy"]
            reasons.append("cjk_language_preferred_advanced_backend")
            strict_quality_mode = True
        elif source_lang in {"fr", "de", "es", "it", "pt", "pl", "tr", "en"}:
            preference = ["argos", "transformers", "local_mock", "dummy"]
            reasons.append("latin_language_prefers_argos_or_transformers")

        if context and context.line_type in {"ui", "system"}:
            reasons.append("ui_system_text_needs_deterministic_style")
            preference = [name for name in preference if name != "cloud_adapter"] + ["cloud_adapter"]

        if context and context.style_preset in {"dramatic", "radio"}:
            reasons.append("style_sensitive_context")
            strict_quality_mode = True

        return TranslationPolicyDecision(
            backend_preference=preference,
            reasons=reasons or ["default_policy"],
            strict_quality_mode=strict_quality_mode,
        )

