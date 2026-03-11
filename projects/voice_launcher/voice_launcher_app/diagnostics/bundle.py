from __future__ import annotations

import json
import platform
import shutil
import subprocess
import time
import ctypes
from importlib import import_module
from pathlib import Path
from typing import Dict


def run_cmd(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True)
        return result.returncode, (result.stdout or result.stderr or "").strip()
    except Exception as exc:
        return 1, str(exc)


def collect_diagnostics(
    out_dir: Path,
    app_paths: Dict[str, Path],
    app_version: str = "dev",
    history: Dict[str, object] | None = None,
) -> Path:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    target = out_dir / f"diagnostics_{stamp}"
    target.mkdir(parents=True, exist_ok=True)

    include = [
        app_paths.get("commands"),
        app_paths.get("settings"),
    ]
    for item in include:
        if item and item.exists():
            shutil.copy2(item, target / item.name)

    logs_dir = app_paths.get("logs")
    if logs_dir and logs_dir.exists():
        for file in logs_dir.glob("*.log*"):
            try:
                shutil.copy2(file, target / file.name)
            except Exception:
                pass

    code, pyver = run_cmd(["python", "--version"])
    code2, pip_freeze = run_cmd(["python", "-m", "pip", "freeze"])
    code3, devices = run_cmd(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_SoundDevice | Select-Object Name | Format-Table -HideTableHeaders"])

    commands_payload = {}
    commands_file = app_paths.get("commands")
    if commands_file and commands_file.exists():
        try:
            commands_payload = json.loads(commands_file.read_text(encoding="utf-8-sig"))
        except Exception:
            commands_payload = {}

    paths_check = {}
    for phrase, entry in (commands_payload or {}).items():
        if isinstance(entry, dict):
            path = str(entry.get("path", "")).strip()
        else:
            path = str(entry).strip()
        if path:
            paths_check[phrase] = Path(path).exists()

    try:
        is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        is_admin = False

    def module_ok(name: str) -> bool:
        try:
            import_module(name)
            return True
        except Exception:
            return False

    report = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "app_version": app_version,
        "platform": platform.platform(),
        "python_version": pyver if code == 0 else "unavailable",
        "pip_freeze": pip_freeze if code2 == 0 else "unavailable",
        "audio_devices": devices if code3 == 0 else "unavailable",
        "self_check": {
            "settings_exists": bool(app_paths.get("settings") and app_paths["settings"].exists()),
            "commands_exists": bool(app_paths.get("commands") and app_paths["commands"].exists()),
            "logs_exists": bool(logs_dir and logs_dir.exists()),
            "is_admin": is_admin,
            "deps": {
                "speech_recognition": module_ok("speech_recognition"),
                "pyaudio": module_ok("pyaudio"),
                "pywinauto": module_ok("pywinauto"),
                "faster_whisper": module_ok("faster_whisper"),
            },
            "command_paths_ok": paths_check,
        },
        "recent_history": history or {},
    }
    with (target / "diagnostics.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return target
