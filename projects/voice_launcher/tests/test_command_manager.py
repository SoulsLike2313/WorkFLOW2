from voice_launcher_app.core.command_manager import (
    detect_phrase_conflict,
    save_command_definition,
)
from voice_launcher_app.core.matching import command_match_score


def test_detect_phrase_conflict():
    commands = {"танки": {"path": "x"}, "запрет": {"path": "y"}}
    phrase, score = detect_phrase_conflict(commands, "танк", command_match_score)
    assert phrase == "танки"
    assert score > 0.7


def test_save_command_definition_rejects_missing_path():
    result = save_command_definition(
        commands={},
        phrase="танки",
        path="C:/missing.exe",
        use_admin=False,
        launcher_play=False,
        play_text="Играть",
        window_title="",
        wait_timeout=240,
        single_instance=True,
        debounce_seconds=2.8,
        launcher_dry_run=False,
        launcher_highlight=False,
        min_window_confidence=0.9,
        build_task_name=lambda p: f"task:{p}",
        score_func=command_match_score,
        path_exists=lambda _p: False,
    )
    assert result.ok is False
    assert result.code == "missing_path"


def test_save_command_definition_ok_launcher_mode():
    store = {}
    result = save_command_definition(
        commands=store,
        phrase="включи игру",
        path="E:/WarThunder/launcher.exe",
        use_admin=False,
        launcher_play=True,
        play_text="Играть",
        window_title="war thunder",
        wait_timeout=240,
        single_instance=True,
        debounce_seconds=12.0,
        launcher_dry_run=True,
        launcher_highlight=False,
        min_window_confidence=0.92,
        build_task_name=lambda p: f"task:{p}",
        score_func=command_match_score,
        path_exists=lambda _p: True,
    )
    assert result.ok is True
    assert result.entry["mode"] == "launcher_play"
    assert "включи игру" in store
