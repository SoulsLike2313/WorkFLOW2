import json
from pathlib import Path

from voice_launcher_app.diagnostics import bundle


def test_collect_diagnostics_includes_history_and_recent_files(tmp_path, monkeypatch):
    base = tmp_path / "runtime"
    out = tmp_path / "out"
    logs = base / "logs"
    backups = base / "backups"
    snapshots = base / "snapshots"
    for folder in (logs, backups, snapshots):
        folder.mkdir(parents=True, exist_ok=True)

    commands = base / "commands.json"
    settings = base / "settings.json"
    commands.write_text(
        json.dumps(
            {
                "включи игру": {
                    "mode": "launcher_play",
                    "path": "C:/Games/launcher.exe",
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    settings.write_text(json.dumps({"settings_version": 6}), encoding="utf-8")
    (logs / "runtime.log").write_text("ok", encoding="utf-8")
    (backups / "settings.bak.json").write_text("bak", encoding="utf-8")
    (snapshots / "session.json").write_text("snap", encoding="utf-8")

    monkeypatch.setattr(bundle, "run_cmd", lambda _args: (0, "ok"))
    monkeypatch.setattr(bundle, "module_version", lambda _name: "test-ver")

    target = bundle.collect_diagnostics(
        out_dir=out,
        app_paths={
            "commands": commands,
            "settings": settings,
            "logs": logs,
            "backups": backups,
            "snapshots": snapshots,
        },
        app_version="test",
        history={"heard": ["включи игру"], "actions": ["launch"]},
    )

    report = json.loads((target / "diagnostics.json").read_text(encoding="utf-8"))
    assert report["app_version"] == "test"
    assert report["recent_history"]["heard"] == ["включи игру"]
    assert report["self_check"]["command_modes"]["launcher_play"] == 1
    assert "runtime.log" in report["bundle_files"]["logs"]
    assert "settings.bak.json" in report["bundle_files"]["backups"]
    assert "session.json" in report["bundle_files"]["snapshots"]
