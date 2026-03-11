from __future__ import annotations


def test_feedback_updates_history_and_tm(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)
    services.extract(pid, root)
    services.detect_languages(pid)
    services.translate(pid, backend_name="local_mock")

    entries = services.repo.list_entries(pid, limit=5)
    entry = entries[0]
    services.apply_correction(pid, int(entry["id"]), "Пользовательская правка", user_note="test correction")

    corrections = services.repo.list_corrections(pid)
    assert corrections
    assert corrections[0]["after_text"] == "Пользовательская правка"

    tm_rows = services.repo.list_translation_memory(pid)
    assert any("Пользовательская правка" == row["target_text"] for row in tm_rows)
