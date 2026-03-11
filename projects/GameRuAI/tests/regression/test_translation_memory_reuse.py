from __future__ import annotations


def test_translation_memory_reuse_after_correction(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)
    services.extract(pid, root)
    services.detect_languages(pid)
    services.translate(pid, backend_name="local_mock")

    entries = services.repo.list_entries(pid, limit=200)
    chosen = next((e for e in entries if e.get("detected_lang") in {"en", "fr", "de"}), entries[0])
    entry_id = int(chosen["id"])
    services.apply_correction(pid, entry_id, "TM-driven corrected translation", user_note="regression check")
    services.translate(pid, backend_name="local_mock")
    refreshed = services.repo.get_entry(entry_id)
    assert refreshed is not None
    assert "TM-driven corrected translation" in (refreshed.get("translated_text") or "")
