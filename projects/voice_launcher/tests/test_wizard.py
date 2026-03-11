from voice_launcher_app.ui.wizard import build_launcher_preview


def test_build_launcher_preview_defaults():
    payload = build_launcher_preview(
        path="E:/WarThunder/launcher.exe",
        play_text="",
        window_title="War Thunder",
        wait_timeout=0,
        highlight=True,
        min_window_confidence=0.0,
    )
    assert payload["mode"] == "launcher_play"
    assert payload["launcher_dry_run"] is True
    assert payload["launcher_highlight"] is True
    assert payload["play_text"] == "Играть"
    assert payload["post_launch_cooldown"] == 110
    assert payload["path"] == "E:/WarThunder/launcher.exe"
