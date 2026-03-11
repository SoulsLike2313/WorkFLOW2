from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Tuple

from ..storage.repository import normalize_command_entry

PROFILE_VERSION = 1


def export_profile(path: Path, commands: Dict[str, dict], settings: Dict[str, object]) -> Path:
    payload = {
        "profile_version": PROFILE_VERSION,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "commands": commands,
        "settings": settings,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def validate_profile(payload: dict) -> Tuple[bool, str]:
    if not isinstance(payload, dict):
        return False, "Некорректный формат профиля (ожидался JSON-объект)"
    if int(payload.get("profile_version", 0)) <= 0:
        return False, "Неизвестная версия профиля"
    if not isinstance(payload.get("commands"), dict):
        return False, "В профиле нет валидного блока commands"
    if not isinstance(payload.get("settings"), dict):
        return False, "В профиле нет валидного блока settings"
    for phrase, raw in payload["commands"].items():
        if not str(phrase).strip():
            return False, "Найдена пустая фраза команды"
        if normalize_command_entry(raw) is None:
            return False, f"Команда '{phrase}' невалидна"
    return True, ""


def import_profile(path: Path) -> Tuple[Dict[str, dict], Dict[str, object]]:
    with path.open("r", encoding="utf-8-sig") as f:
        payload = json.load(f)
    ok, error = validate_profile(payload)
    if not ok:
        raise ValueError(error)
    return payload["commands"], payload["settings"]

