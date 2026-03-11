from __future__ import annotations


def test_voice_linker_returns_entries_with_voice(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)
    services.extract(pid, root)
    entries = services.voice_linker.get_voiced_entries(pid)
    assert entries
    assert all(item.get("voice_link") for item in entries[:20])
