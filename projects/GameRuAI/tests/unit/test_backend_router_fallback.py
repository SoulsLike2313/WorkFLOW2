from __future__ import annotations

from app.translator.router import TranslatorRouter


def test_router_keeps_local_mock_available() -> None:
    router = TranslatorRouter()
    backend, resolution = router.resolve("local_mock")
    assert backend.name == "local_mock"
    assert resolution.fallback_used is False


def test_router_fallback_when_backend_missing() -> None:
    router = TranslatorRouter()
    backend, resolution = router.resolve("non_existing_backend")
    assert backend.name in {"local_mock", "dummy"}
    assert resolution.fallback_used is True


def test_router_fallback_for_optional_backend() -> None:
    router = TranslatorRouter()
    _, resolution = router.resolve("argos")
    # In CI/local env optional package may be absent; fallback must still be explicit and safe.
    if resolution.fallback_used:
        assert resolution.active_backend in {"local_mock", "dummy"}
