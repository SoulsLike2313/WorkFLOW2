from __future__ import annotations


def test_extraction_snapshot_stability(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)
    first = services.extract(pid, root)["entries_extracted"]
    services.scan(pid, root)
    second = services.extract(pid, root)["entries_extracted"]

    assert first == second
    assert first >= 300
