from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BasePerceptionProvider(ABC):
    provider_name: str

    @abstractmethod
    def analyze_frame(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_capabilities(self) -> dict[str, Any]:
        raise NotImplementedError


class BaseReasoningProvider(ABC):
    provider_name: str

    @abstractmethod
    def generate_recommendations(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_capabilities(self) -> dict[str, Any]:
        raise NotImplementedError


class BaseCreativeProvider(ABC):
    provider_name: str

    @abstractmethod
    def evaluate_content(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate_brief(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_capabilities(self) -> dict[str, Any]:
        raise NotImplementedError


class BaseGenerationAdapter(ABC):
    adapter_name: str

    @abstractmethod
    def prepare_assets(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_capabilities(self) -> dict[str, Any]:
        raise NotImplementedError


class BaseLearningScorer(ABC):
    scorer_name: str

    @abstractmethod
    def score_outcome(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_capabilities(self) -> dict[str, Any]:
        raise NotImplementedError
