from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


ACTION_NORMAL = "normal"
ACTION_ADMIN_TASK = "admin_task"
ACTION_LAUNCHER_PLAY = "launcher_play"
SUPPORTED_ACTIONS = {ACTION_NORMAL, ACTION_ADMIN_TASK, ACTION_LAUNCHER_PLAY}


@dataclass
class CommandEntry:
    mode: str = ACTION_NORMAL
    path: str = ""
    task_name: str = ""
    play_text: str = "Играть"
    window_title: str = ""
    wait_timeout: int = 240
    single_instance: bool = True
    debounce_seconds: float = 2.8
    launcher_dry_run: bool = False
    launcher_highlight: bool = False
    min_window_confidence: float = 0.90
    post_launch_cooldown: int = 110

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "path": self.path,
            "task_name": self.task_name,
            "play_text": self.play_text,
            "window_title": self.window_title,
            "wait_timeout": int(self.wait_timeout),
            "single_instance": bool(self.single_instance),
            "debounce_seconds": float(self.debounce_seconds),
            "launcher_dry_run": bool(self.launcher_dry_run),
            "launcher_highlight": bool(self.launcher_highlight),
            "min_window_confidence": float(self.min_window_confidence),
            "post_launch_cooldown": int(self.post_launch_cooldown),
        }

    @classmethod
    def from_mapping(cls, value: Dict[str, Any]) -> "CommandEntry":
        return cls(
            mode=str(value.get("mode", ACTION_NORMAL) or ACTION_NORMAL),
            path=str(value.get("path", "") or ""),
            task_name=str(value.get("task_name", "") or ""),
            play_text=str(value.get("play_text", "Играть") or "Играть"),
            window_title=str(value.get("window_title", "") or ""),
            wait_timeout=int(value.get("wait_timeout", 240) or 240),
            single_instance=bool(value.get("single_instance", True)),
            debounce_seconds=float(value.get("debounce_seconds", 2.8) or 2.8),
            launcher_dry_run=bool(value.get("launcher_dry_run", False)),
            launcher_highlight=bool(value.get("launcher_highlight", False)),
            min_window_confidence=float(value.get("min_window_confidence", 0.90) or 0.90),
            post_launch_cooldown=int(value.get("post_launch_cooldown", 110) or 110),
        )


@dataclass
class SettingsData:
    settings_version: int = 6
    asr_engine: str = "whisper"
    whisper_model_size: str = "small"
    microphone_name: str = ""
    microphone_id: int = -1
    output_name: str = ""
    output_id: int = -1
    dynamic_energy: bool = True
    energy_threshold: int = 110
    fuzzy_threshold: float = 0.72
    listen_timeout: float = 1.8
    listen_phrase_limit: float = 5.0
    mic_gain: float = 1.4
    monitor_gain: float = 1.0
    simple_mode: bool = True
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        base = {
            "settings_version": int(self.settings_version),
            "asr_engine": self.asr_engine,
            "whisper_model_size": self.whisper_model_size,
            "microphone_name": self.microphone_name,
            "microphone_id": int(self.microphone_id),
            "output_name": self.output_name,
            "output_id": int(self.output_id),
            "dynamic_energy": bool(self.dynamic_energy),
            "energy_threshold": int(self.energy_threshold),
            "fuzzy_threshold": float(self.fuzzy_threshold),
            "listen_timeout": float(self.listen_timeout),
            "listen_phrase_limit": float(self.listen_phrase_limit),
            "mic_gain": float(self.mic_gain),
            "monitor_gain": float(self.monitor_gain),
            "simple_mode": bool(self.simple_mode),
        }
        base.update(self.extra)
        return base
