from __future__ import annotations

from app.workspace.ai_providers import (
    StubCreativeProvider,
    StubGenerationAdapter,
    StubLearningScorer,
    StubPerceptionProvider,
    StubReasoningProvider,
)


def test_ai_provider_capabilities_smoke():
    assert StubPerceptionProvider().get_capabilities()["analyze_frame"] is True
    assert StubReasoningProvider().get_capabilities()["generate_recommendations"] is True
    assert StubCreativeProvider().get_capabilities()["evaluate_content"] is True
    assert StubGenerationAdapter().get_capabilities()["prepare_assets"] is True
    assert StubLearningScorer().get_capabilities()["score_outcome"] is True

