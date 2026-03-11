from __future__ import annotations

from pathlib import Path


def test_pipeline_end_to_end(services) -> None:
    game_root = services.config.paths.fixtures_root
    summary = services.pipeline_end_to_end("Integration Demo", game_root)
    pid = int(summary["project"]["id"])

    assert summary["scan"]["files_total"] >= 15
    assert summary["extract"]["entries_extracted"] >= 300
    assert summary["detect"]["detected"] >= 300
    assert summary["translate"]["translated"] >= 300
    assert summary["voice"]["voice_attempts"] >= 100
    assert summary["export"]["translated_entries"] >= 300

    manifest = Path(summary["export"]["manifest"])
    diff_report = Path(summary["export"]["diff_report"])
    assert manifest.exists()
    assert diff_report.exists()

    # Feedback loop: correction should improve repeat translation via TM.
    entries = services.repo.list_entries(pid, limit=50)
    target = next((e for e in entries if e.get("detected_lang") == "en"), entries[0])
    entry_id = int(target["id"])
    services.apply_correction(pid, entry_id, "Исправленный перевод для TM", user_note="integration test")
    services.translate(pid, backend_name="local_mock")
    refreshed = services.repo.get_entry(entry_id)
    assert "Исправленный перевод" in (refreshed.get("translated_text") or "")
