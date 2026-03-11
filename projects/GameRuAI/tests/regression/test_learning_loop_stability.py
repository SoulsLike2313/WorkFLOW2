from __future__ import annotations


def test_learning_snapshot_contains_adaptation_events(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)
    services.extract(pid, root)
    services.detect_languages(pid)
    services.translate(pid, backend_name="local_mock")

    entries = services.repo.list_entries(pid, limit=5)
    services.apply_correction(pid, int(entries[0]["id"]), "First correction", user_note="c1")
    services.apply_correction(pid, int(entries[1]["id"]), "Second correction", user_note="c2")

    snapshot = services.learning_snapshot(pid)
    assert snapshot["adaptation_summary"]["events_total"] >= 2
    assert len(snapshot["corrections"]) >= 2
