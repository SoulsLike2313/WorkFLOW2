from __future__ import annotations


def test_build_speaker_groups_and_voice_attempt_history(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)
    services.extract(pid, root)
    services.detect_languages(pid)
    services.translate(pid, backend_name="local_mock", style="radio")

    summary = services.voice_attempts(pid, root)
    assert summary["voice_attempts"] > 0
    assert summary["speaker_groups"] > 0

    groups = services.repo.list_speaker_groups(pid)
    assert groups
    assert all("speaker_id" in row for row in groups)

    history = services.repo.list_voice_attempt_history(project_id=pid, limit=200)
    assert history
    assert history[0]["synthesis_mode"] == "mock_demo_tts_stub"


def test_preview_player_path_handling_for_voice_attempt(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)
    services.extract(pid, root)
    services.detect_languages(pid)
    services.translate(pid, backend_name="local_mock")
    services.voice_attempts(pid, root)

    snapshot = services.voice_snapshot(pid, game_root=root)
    attempt = snapshot["attempts"][0]
    payload = services.voice_preview(
        str(attempt.get("source_voice_path") or ""),
        str(attempt.get("output_voice_path") or ""),
        game_root=root,
    )
    assert "source" in payload and "generated" in payload
    assert payload["generated"]["status"] in {"ready", "not_found"}

