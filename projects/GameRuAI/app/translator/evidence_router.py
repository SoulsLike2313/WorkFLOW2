from __future__ import annotations

from app.core.models import TranslationPackage


class EvidenceRouter:
    """Builds a transparent translation package from orchestrator outputs."""

    def build_package(
        self,
        *,
        entry_id: int,
        source_text: str,
        source_lang: str,
        context_summary: dict,
        chosen_backend: str,
        fallback_used: bool,
        glossary_hits: list[dict],
        tm_hits: list[dict],
        alternatives: list[dict],
        quality_score: float,
        uncertainty: float,
        final_translation: str,
        reference_checks: list[dict] | None = None,
    ) -> TranslationPackage:
        warnings: list[str] = []
        if uncertainty >= 0.28:
            warnings.append("high_uncertainty")
        if fallback_used:
            warnings.append("fallback_used")
        if source_lang in {"unknown", "mixed"}:
            warnings.append("uncertain_source_language")
        if quality_score < 0.55:
            warnings.append("low_quality_candidate")

        confidence = round(max(0.01, min(0.99, 1.0 - uncertainty)), 4)
        return TranslationPackage(
            entry_id=entry_id,
            source_text=source_text,
            source_lang=source_lang,
            context_summary=context_summary,
            chosen_backend=chosen_backend,
            fallback_used=fallback_used,
            glossary_hits=glossary_hits,
            tm_hits=tm_hits,
            alternatives=alternatives,
            confidence=confidence,
            quality_score=quality_score,
            warnings=warnings,
            final_translation=final_translation,
            reference_checks=reference_checks or [],
        )

