import pytest

from voice_launcher_app.profiles.profile_io import export_profile, import_profile, validate_profile


def test_profile_export_import_roundtrip(tmp_path):
    target = tmp_path / "profile.json"
    commands = {"танки": {"mode": "normal", "path": "C:/Games/launcher.exe"}}
    settings = {"asr_engine": "whisper", "settings_version": 6}

    export_profile(target, commands, settings)
    imported_commands, imported_settings = import_profile(target)

    assert "танки" in imported_commands
    assert imported_settings["asr_engine"] == "whisper"


def test_profile_validation_rejects_invalid_payload():
    ok, error = validate_profile({"profile_version": 1, "commands": [], "settings": {}})
    assert ok is False
    assert "commands" in error


def test_import_profile_raises_on_invalid_file(tmp_path):
    target = tmp_path / "bad.json"
    target.write_text('{"profile_version": 0}', encoding="utf-8")
    with pytest.raises(ValueError):
        import_profile(target)
