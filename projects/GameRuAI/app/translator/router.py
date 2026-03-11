from __future__ import annotations

from .base import TranslationBackend
from .dummy_backend import DummyBackend
from .local_mock_backend import LocalMockBackend


class TranslatorRouter:
    def __init__(self):
        self.backends: dict[str, TranslationBackend] = {
            "dummy": DummyBackend(),
            "local_mock": LocalMockBackend(),
        }

    def get(self, backend_name: str) -> TranslationBackend:
        return self.backends.get(backend_name, self.backends["local_mock"])
