from voice_launcher_app.storage.repository import (
    ensure_layout,
    load_commands,
    load_settings,
    migrate_settings,
    normalize_command_entry,
    save_commands,
    save_settings,
)


def test_normalize_command_entry_accepts_launcher_safety_fields():
    raw = {
        "mode": "launcher_play",
        "path": "C:/Games/launcher.exe",
        "play_text": "Играть",
        "launcher_dry_run": True,
        "launcher_highlight": False,
        "min_window_confidence": 0.97,
    }
    entry = normalize_command_entry(raw)
    assert entry is not None
    assert entry.mode == "launcher_play"
    assert entry.launcher_dry_run is True
    assert 0.65 <= entry.min_window_confidence <= 0.99


def test_migrate_settings_to_v6_sets_simple_mode(tmp_path):
    backups = tmp_path / "backups"
    backups.mkdir()
    migrated, changed = migrate_settings({"settings_version": 3, "asr_engine": "whisper"}, backups)
    assert changed is True
    assert migrated.settings_version == 6
    assert isinstance(migrated.simple_mode, bool)


def test_load_and_save_commands_roundtrip(tmp_path):
    paths = ensure_layout(tmp_path)
    commands = {
        "  Танки  ": {
            "mode": "launcher_play",
            "path": "C:/Games/launcher.exe",
            "play_text": "Играть",
        }
    }
    save_commands(paths, commands)
    loaded = load_commands(paths)
    assert "танки" in loaded
    assert loaded["танки"]["mode"] == "launcher_play"


def test_load_and_save_settings_roundtrip(tmp_path):
    paths = ensure_layout(tmp_path)
    settings = load_settings(paths)
    settings.energy_threshold = 200
    settings.simple_mode = False
    save_settings(paths, settings)
    restored = load_settings(paths)
    assert restored.energy_threshold == 200
    assert restored.simple_mode is False
