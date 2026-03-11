from __future__ import annotations

from dataclasses import dataclass

from .backends.argos_backend import ArgosBackend
from .backends.transformers_backend import TransformersBackend
from .base import TranslationBackend
from .dummy_backend import DummyBackend
from .local_mock_backend import LocalMockBackend


@dataclass(slots=True)
class BackendResolution:
    requested_backend: str
    active_backend: str
    fallback_backend: str | None
    fallback_used: bool
    reason: str


class TranslatorRouter:
    def __init__(self):
        self.backends: dict[str, TranslationBackend] = {
            "local_mock": LocalMockBackend(),
            "dummy": DummyBackend(),
            "argos": ArgosBackend(),
            "transformers": TransformersBackend(),
        }
        self.default_backend = "local_mock"

    def get(self, backend_name: str) -> TranslationBackend:
        return self.backends.get(backend_name, self.backends[self.default_backend])

    def available_backends(self) -> list[str]:
        return [name for name, backend in self.backends.items() if backend.is_available()]

    def resolve(self, requested_backend: str) -> tuple[TranslationBackend, BackendResolution]:
        requested = self.backends.get(requested_backend)
        if requested and requested.is_available():
            return requested, BackendResolution(
                requested_backend=requested_backend,
                active_backend=requested.name,
                fallback_backend=None,
                fallback_used=False,
                reason="requested backend available",
            )

        fallback = self.backends.get(self.default_backend) or self.backends["dummy"]
        fallback_reason = "requested backend unavailable" if requested else "requested backend unknown"
        return fallback, BackendResolution(
            requested_backend=requested_backend,
            active_backend=fallback.name,
            fallback_backend=fallback.name,
            fallback_used=True,
            reason=fallback_reason,
        )
