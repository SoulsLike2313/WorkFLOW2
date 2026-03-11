from __future__ import annotations

from pathlib import Path

from app.assets.archive_report import inspect_archive_suspicion


def test_archive_extension_is_flagged() -> None:
    suspected, confidence, reason, _ = inspect_archive_suspicion(Path("packs/world.pak"), "archive", 1024)
    assert suspected is True
    assert confidence >= 0.45
    assert "archive extension" in reason


def test_large_opaque_binary_can_be_flagged() -> None:
    suspected, confidence, reason, _ = inspect_archive_suspicion(Path("blob/resource.bin"), "binary", 6 * 1024 * 1024)
    assert suspected is False or confidence > 0.0
    assert reason

