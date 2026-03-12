from __future__ import annotations


def test_multimodal_core_foundation_pipeline(services) -> None:
    game_root = services.config.paths.fixtures_root
    project = services.ensure_project("Multimodal Core Demo", game_root)
    pid = int(project["id"])

    scan = services.scan(pid, game_root)
    assert scan["files_total"] >= 15
    assert services.repo.list_asset_manifest(pid, limit=50)

    extract = services.extract(pid, game_root)
    assert extract["entries_extracted"] >= 300

    detect = services.detect_languages(pid)
    assert detect["detected"] >= 300
    assert detect["content_units"] >= 300
    assert services.repo.list_content_units(pid, limit=50)

    translate = services.translate(pid, backend_name="local_mock", style="neutral")
    assert translate["translated"] >= 300
    packages = services.repo.list_translation_packages(pid, limit=20)
    assert packages

    first_entry = services.repo.list_entries(pid, limit=1)[0]
    services.apply_correction(pid, int(first_entry["id"]), "Тестовая ручная правка", user_note="multimodal-core")
    evidence = services.repo.list_evidence_records(pid, limit=100)
    assert any(row["evidence_type"] == "user_correction" for row in evidence)

    voice = services.voice_attempts(pid, game_root)
    assert voice["voice_attempts"] >= 100
    assert services.repo.list_audio_analysis_results(pid, limit=10)
    assert services.repo.list_sync_plans(pid, limit=10)
    assert services.repo.list_transcript_segments(pid, limit=10)

    sources = services.repo.list_knowledge_sources(pid, limit=50)
    assert sources

