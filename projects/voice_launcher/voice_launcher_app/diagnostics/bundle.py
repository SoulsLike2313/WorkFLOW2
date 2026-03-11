from __future__ import annotations

import json
import platform
import shutil
import subprocess
import time
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
        },
    }
    with (target / "diagnostics.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return target

