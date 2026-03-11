from __future__ import annotations

from pathlib import Path

from app.extractors.registry import ExtractorRegistry


def test_registry_supports_expected_extensions() -> None:
    registry = ExtractorRegistry()
    assert {"txt", "json", "xml", "csv", "ini", "yaml", "yml"}.issubset(registry.supported_extensions())


def test_registry_returns_extractor() -> None:
    registry = ExtractorRegistry()
    assert registry.get_for_path(Path("sample.json")) is not None
    assert registry.get_for_path(Path("sample.csv")) is not None
    assert registry.get_for_path(Path("sample.unknown")) is None
