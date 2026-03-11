from __future__ import annotations


def test_scan_manifest_stability(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    first = services.scan(pid, root)
    second = services.scan(pid, root)
    assert first["files_total"] == second["files_total"]
    assert first["by_type"] == second["by_type"]
