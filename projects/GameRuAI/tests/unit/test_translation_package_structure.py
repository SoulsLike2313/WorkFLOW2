from __future__ import annotations

from app.translator.evidence_router import EvidenceRouter
from app.translator.reference_compare import compare_with_references
from app.translator.translation_policies import TranslationPolicies


def test_evidence_router_builds_translation_package() -> None:
    package = EvidenceRouter().build_package(
        entry_id=10,
        source_text="Mission ready",
        source_lang="en",
        context_summary={"scene_id": "s1"},
        chosen_backend="local_mock",
        fallback_used=False,
        glossary_hits=[{"source": "mission", "target": "миссия"}],
        tm_hits=[],
        alternatives=[{"backend": "argos"}],
        quality_score=0.72,
        uncertainty=0.14,
        final_translation="Миссия готова",
        reference_checks=[],
    )
    assert package.entry_id == 10
    assert package.final_translation
    assert package.confidence > 0


def test_reference_compare_and_policy() -> None:
    checks = compare_with_references("Миссия готова", ["Миссия готова", "Задание начато"])
    assert len(checks) == 2
    policy = TranslationPolicies().select(source_lang="ja", context=None)
    assert policy.backend_preference

