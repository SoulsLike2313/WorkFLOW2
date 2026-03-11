from __future__ import annotations

from typing import Any

from .ai_contracts import (
    BaseCreativeProvider,
    BaseGenerationAdapter,
    BaseLearningScorer,
    BasePerceptionProvider,
    BaseReasoningProvider,
)


class StubPerceptionProvider(BasePerceptionProvider):
    provider_name = "stub_perception_provider"

    def analyze_frame(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "stub",
            "provider": self.provider_name,
            "detected_objects": payload.get("detected_objects", []),
            "detected_text": payload.get("detected_text", []),
            "confidence": 0.5,
        }

    def get_capabilities(self) -> dict[str, Any]:
        return {"analyze_frame": True, "real_model": False}


class StubReasoningProvider(BaseReasoningProvider):
    provider_name = "stub_reasoning_provider"

    def generate_recommendations(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        return payload.get("recommendations", [])

    def get_capabilities(self) -> dict[str, Any]:
        return {"generate_recommendations": True, "real_model": False}


class StubCreativeProvider(BaseCreativeProvider):
    provider_name = "stub_creative_provider"

    def evaluate_content(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"status": "stub", "provider": self.provider_name, "result": payload}

    def generate_brief(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"status": "stub", "provider": self.provider_name, "brief": payload}

    def get_capabilities(self) -> dict[str, Any]:
        return {"evaluate_content": True, "generate_brief": True, "real_model": False}


class StubGenerationAdapter(BaseGenerationAdapter):
    adapter_name = "stub_generation_adapter"

    def prepare_assets(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"status": "stub", "adapter": self.adapter_name, "payload": payload}

    def get_capabilities(self) -> dict[str, Any]:
        return {"prepare_assets": True, "real_generation": False}


class StubLearningScorer(BaseLearningScorer):
    scorer_name = "stub_learning_scorer"

    def score_outcome(self, payload: dict[str, Any]) -> dict[str, Any]:
        expected = float(payload.get("expected_score", 0.5))
        actual = float(payload.get("actual_score", expected))
        delta = actual - expected
        return {"status": "ok", "scorer": self.scorer_name, "confidence_delta": delta}

    def get_capabilities(self) -> dict[str, Any]:
        return {"score_outcome": True, "adaptive_learning": False}
