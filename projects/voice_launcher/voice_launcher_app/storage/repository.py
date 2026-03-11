from __future__ import annotations

import json
import os
import shutil
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from .models import (
    ACTION_ADMIN_TASK,
    ACTION_LAUNCHER_PLAY,
    ACTION_NORMAL,
    SUPPORTED_ACTIONS,
    CommandEntry,
    SettingsData,
)


def default_storage_dir() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(os.getenv("APPDATA", str(Path.home()))) / "VoiceLauncher"
    else:
        base = Path(__file__).resolve().parents[2]
    base.mkdir(parents=True, exist_ok=True)
    return base


def ensure_layout(base_dir: Path) -> Dict[str, Path]:
    logs = base_dir / "logs"
    backups = base_dir / "backups"
    snapshots = base_dir / "snapshots"
    for folder in (logs, backups, snapshots):
        folder.mkdir(parents=True, exist_ok=True)
    return {
        "base": base_dir,
        "commands": base_dir / "commands.json",
        "settings": base_dir / "settings.json",
        "logs": logs,
        "backups": backups,
        "snapshots": snapshots,
    }


def _save_json_atomic(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _load_json(path: Path) -> Optional[Any]:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return None


def maybe_fix_mojibake(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    if not any(ch in text for ch in ("Р", "С", "Ð", "Ñ")):
        return text

    def score(candidate: str) -> float:
        cyr = sum(1 for ch in candidate if ("а" <= ch.lower() <= "я") or ch in "ёЁ")
        bad = candidate.count("Р") + candidate.count("С") + candidate.count("Ð") + candidate.count("Ñ")
        return cyr * 2.0 - bad * 2.8

    best = text
    best_score = score(text)
    for enc in ("cp1251", "latin1"):
        try:
            fixed = text.encode(enc).decode("utf-8")
        except Exception:
            continue
        fixed_score = score(fixed)
        if fixed_score > best_score:
            best = fixed
            best_score = fixed_score
    return best


def normalize_phrase(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def normalize_command_entry(raw: Any) -> Optional[CommandEntry]:
    if isinstance(raw, str):
        path = maybe_fix_mojibake(raw).strip()
        if not path:
            return None
        return CommandEntry(path=path)
    if not isinstance(raw, dict):
        return None

    entry = CommandEntry.from_mapping(raw)
    entry.path = maybe_fix_mojibake(entry.path).strip()
    entry.task_name = maybe_fix_mojibake(entry.task_name).strip()
    entry.play_text = maybe_fix_mojibake(entry.play_text).strip() or "Играть"
    entry.window_title = maybe_fix_mojibake(entry.window_title).strip()
    entry.mode = entry.mode if entry.mode in SUPPORTED_ACTIONS else ACTION_NORMAL
    entry.wait_timeout = max(30, min(900, int(entry.wait_timeout)))
    entry.debounce_seconds = max(0.8, min(30.0, float(entry.debounce_seconds)))
    if entry.mode == ACTION_LAUNCHER_PLAY:
        entry.debounce_seconds = max(12.0, entry.debounce_seconds)
    if not entry.path:
        return None
    return entry


def default_settings() -> SettingsData:
    return SettingsData()


def migrate_settings(raw: Dict[str, Any], backups_dir: Path) -> Tuple[SettingsData, bool]:
    changed = False
    src = dict(raw)

    if int(src.get("settings_version", 0)) < 5:
        src["settings_version"] = 5
        changed = True

    data = default_settings()
    merged = data.to_dict()
    merged.update(src)

    merged["asr_engine"] = str(merged.get("asr_engine", "whisper")).strip().lower()
    if merged["asr_engine"] not in ("whisper", "google"):
        merged["asr_engine"] = "whisper"
        changed = True

    merged["whisper_model_size"] = str(merged.get("whisper_model_size", "small")).strip().lower() or "small"
    if merged["whisper_model_size"] not in ("tiny", "base", "small", "medium", "large-v2", "large-v3", "distil-large-v3"):
        merged["whisper_model_size"] = "small"
        changed = True

    def clamp(key: str, lo: float, hi: float, cast: Callable[[Any], Any]) -> None:
        nonlocal changed
        try:
            value = cast(merged.get(key))
        except Exception:
            value = cast(default_settings().to_dict()[key])
            changed = True
        clamped = max(lo, min(hi, value))
        if clamped != value:
            changed = True
        merged[key] = clamped

    clamp("microphone_id", -1, 9999, int)
    clamp("output_id", -1, 9999, int)
    clamp("energy_threshold", 40, 800, int)
    clamp("fuzzy_threshold", 0.55, 0.98, float)
    clamp("listen_timeout", 0.5, 6.0, float)
    clamp("listen_phrase_limit", 1.5, 8.0, float)
    clamp("mic_gain", 1.0, 4.0, float)
    clamp("monitor_gain", 0.8, 2.5, float)
    merged["dynamic_energy"] = bool(merged.get("dynamic_energy", True))

    settings = SettingsData(
        settings_version=int(merged["settings_version"]),
        asr_engine=str(merged["asr_engine"]),
        whisper_model_size=str(merged["whisper_model_size"]),
        microphone_name=maybe_fix_mojibake(str(merged.get("microphone_name", ""))).strip(),
        microphone_id=int(merged["microphone_id"]),
        output_name=maybe_fix_mojibake(str(merged.get("output_name", ""))).strip(),
        output_id=int(merged["output_id"]),
        dynamic_energy=bool(merged["dynamic_energy"]),
        energy_threshold=int(merged["energy_threshold"]),
        fuzzy_threshold=float(merged["fuzzy_threshold"]),
        listen_timeout=float(merged["listen_timeout"]),
        listen_phrase_limit=float(merged["listen_phrase_limit"]),
        mic_gain=float(merged["mic_gain"]),
        monitor_gain=float(merged["monitor_gain"]),
        extra={},
    )
    return settings, changed


def load_settings(paths: Dict[str, Path]) -> SettingsData:
    raw = _load_json(paths["settings"])
    if not isinstance(raw, dict):
        return default_settings()
    settings, changed = migrate_settings(raw, paths["backups"])
    if changed:
        stamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = paths["backups"] / f"settings.migrate_{stamp}.bak.json"
        try:
            shutil.copy2(paths["settings"], backup_path)
        except Exception:
            pass
        save_settings(paths, settings)
    return settings


def save_settings(paths: Dict[str, Path], settings: SettingsData) -> None:
    _save_json_atomic(paths["settings"], settings.to_dict())


def load_commands(paths: Dict[str, Path]) -> Dict[str, Dict[str, Any]]:
    loaded = _load_json(paths["commands"])
    if not isinstance(loaded, dict):
        return {}

    out: Dict[str, Dict[str, Any]] = {}
    changed = False
    for phrase_raw, payload_raw in loaded.items():
        phrase = normalize_phrase(maybe_fix_mojibake(str(phrase_raw)))
        if not phrase:
            changed = True
            continue
        normalized = normalize_command_entry(payload_raw)
        if not normalized:
            changed = True
            continue
        out[phrase] = normalized.to_dict()
        if phrase != str(phrase_raw):
            changed = True
    if changed:
        save_commands(paths, out)
    return out


def save_commands(paths: Dict[str, Path], commands: Dict[str, Dict[str, Any]]) -> None:
    _save_json_atomic(paths["commands"], commands)


def save_snapshot(paths: Dict[str, Path], name: str, payload: Dict[str, Any]) -> Path:
    stamp = time.strftime("%Y%m%d_%H%M%S")
    target = paths["snapshots"] / f"{name}_{stamp}.json"
    _save_json_atomic(target, payload)
    return target

