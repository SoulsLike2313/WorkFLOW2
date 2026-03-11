from __future__ import annotations

import json
import platform
import shutil
import subprocess
import time
import ctypes
from importlib import import_module, metadata
from pathlib import Path
from typing import Dict


def run_cmd(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True)
        return result.returncode, (result.stdout or result.stderr or "").strip()
    except Exception as exc:
        return 1, str(exc)


def copy_recent_files(source_dir: Path | None, target_dir: Path, patterns, limit: int = 24):
    if not source_dir or not source_dir.exists():
        return []

    copied = []
    candidates = []
    for pattern in patterns:
        candidates.extend(source_dir.glob(pattern))

    candidates = sorted(
        [p for p in candidates if p.is_file()],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    for file in candidates[: max(1, int(limit))]:
        try:
            dst = target_dir / file.name
            shutil.copy2(file, dst)
            copied.append(dst.name)
        except Exception:
            continue
    return copied


def module_version(name: str) -> str:
    try:
        return metadata.version(name)
    except Exception:
        return "not-installed"


def collect_diagnostics(
    out_dir: Path,
    app_paths: Dict[str, Path],
    app_version: str = "dev",
    history: Dict[str, object] | None = None,
) -> Path:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    target = out_dir / f"diagnostics_{stamp}"
    target.mkdir(parents=True, exist_ok=True)

    include = [app_paths.get("commands"), app_paths.get("settings")]
    for item in include:
        if item and item.exists():
            shutil.copy2(item, target / item.name)

    logs_dir = app_paths.get("logs")
    backups_dir = app_paths.get("backups")
    snapshots_dir = app_paths.get("snapshots")
    copied_logs = copy_recent_files(logs_dir, target, patterns=["*.log", "*.log.*"], limit=40)
    copied_backups = copy_recent_files(backups_dir, target, patterns=["*.json", "*.bak", "*.zip"], limit=16)
    copied_snapshots = copy_recent_files(snapshots_dir, target, patterns=["*.json", "*.zip"], limit=16)

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
    command_modes = {"normal": 0, "admin_task": 0, "launcher_play": 0}
    for phrase, entry in (commands_payload or {}).items():
        if isinstance(entry, dict):
            path = str(entry.get("path", "")).strip()
            mode = str(entry.get("mode", "normal") or "normal").strip().lower()
        else:
            path = str(entry).strip()
            mode = "normal"
        if path:
            paths_check[phrase] = Path(path).exists()
        if mode not in command_modes:
            mode = "normal"
        command_modes[mode] += 1

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
        "python_impl": platform.python_implementation(),
        "pip_freeze": pip_freeze if code2 == 0 else "unavailable",
        "audio_devices": devices if code3 == 0 else "unavailable",
        "dependencies": {
            "SpeechRecognition": module_version("SpeechRecognition"),
            "PyAudio": module_version("PyAudio"),
            "pywinauto": module_version("pywinauto"),
            "faster-whisper": module_version("faster-whisper"),
            "numpy": module_version("numpy"),
            "Pillow": module_version("Pillow"),
            "pystray": module_version("pystray"),
        },
        "bundle_files": {
            "logs": copied_logs,
            "backups": copied_backups,
            "snapshots": copied_snapshots,
        },
        "storage_paths": {key: str(value) for key, value in (app_paths or {}).items() if value},
        "self_check": {
            "settings_exists": bool(app_paths.get("settings") and app_paths["settings"].exists()),
            "commands_exists": bool(app_paths.get("commands") and app_paths["commands"].exists()),
            "logs_exists": bool(logs_dir and logs_dir.exists()),
            "backups_exists": bool(backups_dir and backups_dir.exists()),
            "snapshots_exists": bool(snapshots_dir and snapshots_dir.exists()),
            "is_admin": is_admin,
            "deps": {
                "speech_recognition": module_ok("speech_recognition"),
                "pyaudio": module_ok("pyaudio"),
                "pywinauto": module_ok("pywinauto"),
                "faster_whisper": module_ok("faster_whisper"),
            },
            "commands_count": len(commands_payload),
            "command_modes": command_modes,
            "command_paths_ok": paths_check,
        },
        "recent_history": history or {},
    }
    with (target / "diagnostics.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return target
