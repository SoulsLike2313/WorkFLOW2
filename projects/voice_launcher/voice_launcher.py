import ctypes
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

import pystray
import speech_recognition as sr
from PIL import Image, ImageDraw
from voice_launcher_app.app.controller import AppController, ListenerDeps
from voice_launcher_app.actions.launcher_runner import LauncherRunnerDeps, run_launcher_play
from voice_launcher_app.actions.target_launcher import TargetLauncher, TargetLauncherDeps, TargetLauncherState
from voice_launcher_app.core.command_manager import save_command_definition
from voice_launcher_app.core.launch_policy import (
    LaunchGate,
    ProcessScanner,
    find_running_process_for_entry as core_find_running_process_for_entry,
)
from voice_launcher_app.core.matching import find_best_command as modular_find_best_command
from voice_launcher_app.diagnostics.bundle import collect_diagnostics
from voice_launcher_app.profiles.profile_io import export_profile, import_profile
from voice_launcher_app.asr.audio_devices import AudioDeviceService
from voice_launcher_app.ui.controller import UiController, UiControllerDeps
from voice_launcher_app.ui.wizard import CommandWizardDeps, open_command_wizard
from voice_launcher_app.ui.theme import (
    PREMIUM_PALETTE,
    THEME_FONTS,
    paint_hero_gradient as draw_hero_gradient,
    premium_glow_colors,
    setup_styles as apply_theme_styles,
)
try:
    import audioop
except Exception:
    try:
        import audioop_lts as audioop  # type: ignore
    except Exception:
        audioop = None
try:
    import pyaudio
except Exception:
    pyaudio = None
try:
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None
try:
    import numpy as np
except Exception:
    np = None
try:
    from pywinauto import Desktop
    from pywinauto import mouse as pywinauto_mouse
    from pywinauto.keyboard import send_keys
except Exception:
    Desktop = None
    pywinauto_mouse = None
    send_keys = None


def get_storage_dir():
    # Runtime-данные всегда в AppData (и для исходников, и для exe).
    # При необходимости можно переопределить через VOICE_LAUNCHER_STORAGE_DIR.
    env_override = os.getenv("VOICE_LAUNCHER_STORAGE_DIR", "").strip()
    if env_override:
        base = env_override
    else:
        base = os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), "VoiceLauncher")
    os.makedirs(base, exist_ok=True)
    return base


STORAGE_DIR = get_storage_dir()
COMMANDS_FILE = os.path.join(STORAGE_DIR, "commands.json")
SETTINGS_FILE = os.path.join(STORAGE_DIR, "settings.json")
LOGS_DIR = os.path.join(STORAGE_DIR, "logs")
BACKUPS_DIR = os.path.join(STORAGE_DIR, "backups")
SNAPSHOTS_DIR = os.path.join(STORAGE_DIR, "snapshots")
for _folder in (LOGS_DIR, BACKUPS_DIR, SNAPSHOTS_DIR):
    os.makedirs(_folder, exist_ok=True)
LAUNCHER_LOG_FILE = os.path.join(LOGS_DIR, "launcher_automation.log")
RUNTIME_LOG_FILE = os.path.join(LOGS_DIR, "runtime.log")
ASR_LOG_FILE = os.path.join(LOGS_DIR, "asr_events.log")
SESSION_SNAPSHOT_FILE = os.path.join(SNAPSHOTS_DIR, "dev_session_snapshot.json")

PALETTE = dict(PREMIUM_PALETTE)
UI_FONT_SCRIPT = THEME_FONTS.get("title", "Bahnschrift SemiBold")
UI_FONT_SOFT = THEME_FONTS.get("body", "Segoe UI Semibold")

DEFAULT_SETTINGS = {
    "settings_version": 6,
    "asr_engine": "whisper",
    "whisper_model_size": "small",
    "microphone_name": "",
    "microphone_id": -1,
    "output_name": "",
    "output_id": -1,
    "dynamic_energy": True,
    "energy_threshold": 110,
    "fuzzy_threshold": 0.72,
    "listen_timeout": 1.8,
    "listen_phrase_limit": 5.0,
    "mic_gain": 1.4,
    "monitor_gain": 1.0,
    "simple_mode": True,
}

LEGACY_PRESET = {
    "dynamic_energy": False,
    "energy_threshold": 160,
    "fuzzy_threshold": 0.84,
    "listen_timeout": 1.0,
    "listen_phrase_limit": 3.4,
    "mic_gain": 2.0,
}

VOICE_CAPTURE_TIMEOUT = 5
VOICE_CAPTURE_LIMIT = 4
DEVICE_CACHE_TTL = 2.5

commands = {}
settings = DEFAULT_SETTINGS.copy()

stop_event = threading.Event()
pause_listen_event = threading.Event()
restart_listen_event = threading.Event()
monitor_active_event = threading.Event()
tray_icon = None
monitor_thread = None
whisper_model = None
whisper_model_lock = threading.Lock()
whisper_warmup_in_progress = False
last_asr_error_ts = 0.0
single_instance_mutex = None
device_options_cache = {"ts": 0.0, "inputs": [], "outputs": []}
audio_device_service = None

last_launch_phrase = ""
last_launch_time = 0.0
target_launcher_executor = None
launcher_log_lock = threading.Lock()
runtime_log_lock = threading.Lock()
command_launch_gate = {}
process_list_cache = {"ts": 0.0, "names": set()}
launch_gate_service = None
process_scanner_service = None
last_voice_trigger = {"phrase": "", "ts": 0.0}
recent_heard_phrases = []
recent_actions = []
ui_controller = None


# ======================= Utils =======================
def focus_existing_app_window():
    if Desktop is None:
        return
    try:
        for win in Desktop(backend="uia").windows():
            try:
                title = normalize_phrase(win.window_text() or "")
            except Exception:
                title = ""
            if not title:
                continue
            if "голосовой запускатор" in title or "voice launcher" in title:
                try:
                    if hasattr(win, "is_minimized") and win.is_minimized():
                        win.restore()
                except Exception:
                    pass
                try:
                    win.set_focus()
                except Exception:
                    pass
                return
    except Exception:
        return


def ensure_single_instance():
    global single_instance_mutex
    if os.name != "nt":
        return True

    try:
        mutex_name = "Global\\VoiceLauncherSingleInstance"
        handle = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
        if not handle:
            return True
        single_instance_mutex = handle
        already_exists = ctypes.windll.kernel32.GetLastError() == 183  # ERROR_ALREADY_EXISTS
        if already_exists:
            focus_existing_app_window()
            return False
        return True
    except Exception:
        return True


def hide_console_window():
    if os.name != "nt":
        return
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass


def normalize_phrase(text):
    return " ".join(text.strip().lower().split())


def set_status(text):
    root.after(0, lambda: status_var.set(text))


def push_history_value(buffer, value, limit=20):
    value = str(value or "").strip()
    if not value:
        return
    buffer.append(value)
    if len(buffer) > limit:
        del buffer[:-limit]


def set_last_phrase(text):
    if ui_controller is not None:
        ui_controller.push_last_phrase(text)
        return
    push_history_value(recent_heard_phrases, text, limit=30)
    if "last_phrase_var" in globals():
        root.after(0, lambda: last_phrase_var.set(f"Последняя фраза: {text}"))
    if "refresh_events_panel" in globals():
        root.after(0, refresh_events_panel)


def set_last_action(text):
    if ui_controller is not None:
        ui_controller.push_last_action(text)
        return
    push_history_value(recent_actions, text, limit=30)
    if "last_action_var" in globals():
        root.after(0, lambda: last_action_var.set(f"Последнее действие: {text}"))
    if "refresh_events_panel" in globals():
        root.after(0, refresh_events_panel)


def set_asr_status(text):
    if "asr_status_var" in globals():
        root.after(0, lambda: asr_status_var.set(str(text)))


def log_launcher(text):
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"{stamp} | {text}\n"
        with launcher_log_lock:
            with open(LAUNCHER_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line)
    except Exception:
        pass


def append_rotating_log(path, text, lock, max_bytes=1_800_000, backups=4):
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"{stamp} | {text}\n"
        with lock:
            try:
                if os.path.exists(path) and os.path.getsize(path) > max_bytes:
                    # Простейшая ротация: runtime.log -> runtime.log.1 -> ... -> runtime.log.4
                    oldest = f"{path}.{backups}"
                    if os.path.exists(oldest):
                        os.remove(oldest)
                    for idx in range(backups - 1, 0, -1):
                        src = f"{path}.{idx}"
                        dst = f"{path}.{idx + 1}"
                        if os.path.exists(src):
                            os.replace(src, dst)
                    os.replace(path, f"{path}.1")
            except Exception:
                pass

            with open(path, "a", encoding="utf-8") as f:
                f.write(line)
    except Exception:
        pass


def log_runtime(text):
    append_rotating_log(RUNTIME_LOG_FILE, text, runtime_log_lock)


def log_asr(text):
    append_rotating_log(ASR_LOG_FILE, text, runtime_log_lock)


def write_session_snapshot(trigger="manual"):
    try:
        snapshot = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "trigger": str(trigger),
            "cwd": os.getcwd(),
            "storage_dir": STORAGE_DIR,
            "python_executable": sys.executable,
            "python_version": sys.version.split()[0],
            "commands_count": len(commands),
            "asr_engine": str(settings.get("asr_engine", "whisper")),
            "whisper_model_size": str(settings.get("whisper_model_size", "small")),
            "dynamic_energy": bool(settings.get("dynamic_energy", True)),
            "energy_threshold": int(settings.get("energy_threshold", 110)),
            "mic_gain": float(settings.get("mic_gain", 1.0)),
            "fuzzy_threshold": float(settings.get("fuzzy_threshold", 0.72)),
            "listen_timeout": float(settings.get("listen_timeout", 1.8)),
            "listen_phrase_limit": float(settings.get("listen_phrase_limit", 5.0)),
            "microphone_id": int(settings.get("microphone_id", -1)),
            "microphone_name": maybe_fix_mojibake(str(settings.get("microphone_name", ""))),
            "output_id": int(settings.get("output_id", -1)),
            "output_name": maybe_fix_mojibake(str(settings.get("output_name", ""))),
            "files": {
                "commands": COMMANDS_FILE,
                "settings": SETTINGS_FILE,
                "launcher_log": LAUNCHER_LOG_FILE,
                "runtime_log": RUNTIME_LOG_FILE,
                "asr_log": ASR_LOG_FILE,
            },
        }
        save_json(SESSION_SNAPSHOT_FILE, snapshot)
    except Exception:
        pass


def show_info(title, text):
    root.after(0, lambda: messagebox.showinfo(title, text))


def show_warning(title, text):
    root.after(0, lambda: messagebox.showwarning(title, text))


def audio_rms(raw_data, sample_width):
    if not raw_data:
        return 0
    if audioop is not None:
        try:
            return int(audioop.rms(raw_data, sample_width))
        except Exception:
            pass
    if np is not None and sample_width == 2:
        try:
            arr = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)
            if arr.size == 0:
                return 0
            return int(np.sqrt(np.mean(arr * arr)))
        except Exception:
            return 0
    return 0


def audio_peak(raw_data, sample_width):
    if not raw_data:
        return 0
    if audioop is not None:
        try:
            return int(audioop.max(raw_data, sample_width))
        except Exception:
            pass
    if np is not None and sample_width == 2:
        try:
            arr = np.frombuffer(raw_data, dtype=np.int16)
            if arr.size == 0:
                return 0
            return int(np.max(np.abs(arr)))
        except Exception:
            return 0
    return 0


def audio_mul(raw_data, sample_width, gain):
    if not raw_data:
        return raw_data
    if audioop is not None:
        try:
            return audioop.mul(raw_data, sample_width, gain)
        except Exception:
            pass
    if np is not None and sample_width == 2:
        try:
            arr = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)
            arr *= float(gain)
            arr = np.clip(arr, -32768, 32767).astype(np.int16)
            return arr.tobytes()
        except Exception:
            return raw_data
    return raw_data


def audio_to_stereo(raw_data, sample_width):
    if not raw_data:
        return raw_data
    if audioop is not None:
        try:
            return audioop.tostereo(raw_data, sample_width, 1, 1)
        except Exception:
            pass
    if np is not None and sample_width == 2:
        try:
            mono = np.frombuffer(raw_data, dtype=np.int16)
            if mono.size == 0:
                return raw_data
            stereo = np.repeat(mono[:, None], 2, axis=1).reshape(-1)
            return stereo.astype(np.int16).tobytes()
        except Exception:
            return raw_data
    return raw_data


def get_audio_level_percent(audio):
    try:
        raw = audio.get_raw_data()
        rms = audio_rms(raw, audio.sample_width)
        max_val = float((1 << (8 * audio.sample_width - 1)) - 1)
        return int(max(0, min(100, (rms / max_val) * 350)))
    except Exception:
        return 0


def apply_safe_gain(raw_data, sample_width, gain):
    if gain <= 1.01:
        return raw_data

    try:
        peak = audio_peak(raw_data, sample_width)
        if peak <= 0:
            return raw_data
        max_val = float((1 << (8 * sample_width - 1)) - 1)
        safe_gain = min(float(gain), max_val / float(peak))
        if safe_gain <= 1.01:
            return raw_data
        return audio_mul(raw_data, sample_width, safe_gain)
    except Exception:
        return raw_data


def apply_mic_gain(audio):
    gain = float(settings.get("mic_gain", 1.0))
    raw = audio.get_raw_data()
    boosted = apply_safe_gain(raw, audio.sample_width, gain)
    return sr.AudioData(boosted, audio.sample_rate, audio.sample_width)


def normalize_audio_for_asr(audio):
    # Держим уровень входа в "рабочем" диапазоне: не тихо, но и без клиппинга.
    processed = apply_mic_gain(audio)
    raw16 = processed.get_raw_data(convert_width=2)

    try:
        rms = audio_rms(raw16, 2)
        if rms > 0:
            target_rms = 4400  # примерно 13% от full-scale для int16
            auto_gain = min(3.2, max(1.0, target_rms / float(rms)))
            raw16 = apply_safe_gain(raw16, 2, auto_gain)
    except Exception:
        pass

    return sr.AudioData(raw16, processed.sample_rate, 2)


def build_commands_prompt(max_chars=260):
    if not commands:
        return ""

    ordered = sorted((normalize_phrase(k) for k in commands.keys()), key=len)
    picked = []
    current_len = 0
    for phrase in ordered:
        if not phrase:
            continue
        token = phrase if not picked else f", {phrase}"
        if current_len + len(token) > max_chars:
            break
        picked.append(phrase)
        current_len += len(token)

    if not picked:
        return ""
    return "Ключевые команды: " + ", ".join(picked)


def get_whisper_audio_source(audio):
    processed = normalize_audio_for_asr(audio)
    temp_path = ""

    if np is not None:
        try:
            raw = processed.get_raw_data(convert_rate=16000, convert_width=2)
            pcm = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
            if pcm.size > 0:
                return pcm, temp_path
        except Exception:
            pass

    wav_data = processed.get_wav_data(convert_rate=16000, convert_width=2)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(wav_data)
        temp_path = tmp.name
    return temp_path, temp_path


def maybe_fix_mojibake(text):
    # Исправляет типичные случаи "РџС..." (UTF-8, ошибочно прочитанный как cp1251/latin1).
    if not isinstance(text, str):
        return str(text)
    if not any(marker in text for marker in ("Р", "С", "Ð", "Ñ")):
        return text

    def score(candidate):
        if not candidate:
            return 0.0
        cyr = sum(1 for ch in candidate if "а" <= ch.lower() <= "я" or ch in "ёЁ")
        bad = (
            candidate.count("Р")
            + candidate.count("С")
            + candidate.count("Ð")
            + candidate.count("Ñ")
        )
        qmarks = candidate.count("?")
        controls = sum(1 for ch in candidate if ord(ch) < 32 and ch not in "\r\n\t")
        return cyr * 2.2 - bad * 3.0 - qmarks * 2.0 - controls * 5.0

    best = text
    best_score = score(text)

    for enc in ("cp1251", "latin1"):
        try:
            fixed = text.encode(enc).decode("utf-8")
        except Exception:
            continue
        fixed_score = score(fixed)
        if fixed_score > best_score + 0.1:
            best = fixed
            best_score = fixed_score

    return best


def get_audio_device_service():
    global audio_device_service
    if audio_device_service is None:
        audio_device_service = AudioDeviceService(
            settings=settings,
            maybe_fix_mojibake=maybe_fix_mojibake,
            pyaudio_mod=pyaudio,
            cache_ttl=DEVICE_CACHE_TTL,
            cache=device_options_cache,
        )
    audio_device_service.settings = settings
    audio_device_service.pyaudio_mod = pyaudio
    audio_device_service.cache_ttl = DEVICE_CACHE_TTL
    return audio_device_service


def sort_device_options(options, kind="input", preferred_output_name=""):
    return get_audio_device_service().sort_device_options(
        options,
        kind=kind,
        preferred_output_name=preferred_output_name,
    )


def get_device_options(force_refresh=False):
    global device_options_cache
    service = get_audio_device_service()
    inputs, outputs = service.get_device_options(force_refresh=force_refresh)
    device_options_cache = dict(service.cache)
    return inputs, outputs


def resolve_selected_index(options, id_key, name_key):
    return get_audio_device_service().resolve_selected_index(options, id_key, name_key)


def get_selected_mic_index():
    return get_audio_device_service().get_selected_mic_index()


def get_selected_output_index():
    return get_audio_device_service().get_selected_output_index()


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def load_json(path):
    if not os.path.exists(path):
        return None
    # utf-8-sig безопасно читает и обычный UTF-8, и UTF-8 с BOM.
    try:
        with open(path, "r", encoding="utf-8-sig") as file:
            return json.load(file)
    except json.JSONDecodeError:
        # Если JSON поврежден, сохраняем копию и не падаем.
        try:
            stamp = time.strftime("%Y%m%d_%H%M%S")
            base_name = os.path.basename(path)
            backup_path = os.path.join(BACKUPS_DIR, f"{base_name}.corrupt_{stamp}.bak")
            shutil.copy2(path, backup_path)
        except Exception:
            pass
        return None
    except Exception:
        return None


# ======================= Data =======================
def load_settings():
    global settings
    loaded = load_json(SETTINGS_FILE)
    if isinstance(loaded, dict):
        changed = False
        merged = DEFAULT_SETTINGS.copy()
        for key in merged:
            if key in loaded:
                merged[key] = loaded[key]

        # Мягкая миграция со старого "агрессивного по обрезанию" профиля.
        if int(merged.get("settings_version", 0)) < 2:
            legacy_match = all(merged.get(k) == v for k, v in LEGACY_PRESET.items())
            if legacy_match:
                merged["dynamic_energy"] = DEFAULT_SETTINGS["dynamic_energy"]
                merged["energy_threshold"] = DEFAULT_SETTINGS["energy_threshold"]
                merged["fuzzy_threshold"] = DEFAULT_SETTINGS["fuzzy_threshold"]
                merged["listen_timeout"] = DEFAULT_SETTINGS["listen_timeout"]
                merged["listen_phrase_limit"] = DEFAULT_SETTINGS["listen_phrase_limit"]
                merged["mic_gain"] = DEFAULT_SETTINGS["mic_gain"]
            merged["settings_version"] = 2
            changed = True

        # Миграция anti-clipping: слишком высокий gain снижает разборчивость.
        if int(merged.get("settings_version", 0)) < 3:
            if float(merged.get("mic_gain", 1.4)) > 1.8:
                merged["mic_gain"] = 1.4
                changed = True
            if float(merged.get("monitor_gain", 1.0)) > 1.4:
                merged["monitor_gain"] = 1.0
                changed = True
            merged["settings_version"] = 3
            changed = True

        # Миграция 4: убираем слишком "жесткие" параметры, которые режут короткие фразы.
        if int(merged.get("settings_version", 0)) < 4:
            if float(merged.get("listen_timeout", 1.8)) < 1.0:
                merged["listen_timeout"] = 1.1
                changed = True
            if float(merged.get("listen_phrase_limit", 5.0)) < 3.0:
                merged["listen_phrase_limit"] = 3.2
                changed = True
            if float(merged.get("fuzzy_threshold", 0.72)) > 0.8:
                merged["fuzzy_threshold"] = 0.78
                changed = True
            merged["settings_version"] = 4
            changed = True

        # Миграция 5: добавлен safe launcher режим (dry-run/highlight) и структурные каталоги.
        if int(merged.get("settings_version", 0)) < 5:
            merged["settings_version"] = 5
            changed = True

        # Миграция 6: режим интерфейса (simple/advanced).
        if int(merged.get("settings_version", 0)) < 6:
            merged["simple_mode"] = bool(merged.get("simple_mode", True))
            merged["settings_version"] = 6
            changed = True

        # Санитизация значений (совместимость и устойчивость).
        fixed_mic_name = maybe_fix_mojibake(str(merged.get("microphone_name", ""))).strip()
        if fixed_mic_name != str(merged.get("microphone_name", "")):
            merged["microphone_name"] = fixed_mic_name
            changed = True

        fixed_out_name = maybe_fix_mojibake(str(merged.get("output_name", ""))).strip()
        if fixed_out_name != str(merged.get("output_name", "")):
            merged["output_name"] = fixed_out_name
            changed = True

        fixed_engine = str(merged.get("asr_engine", "whisper")).strip().lower()
        if fixed_engine not in ("whisper", "google"):
            fixed_engine = "whisper"
            changed = True
        merged["asr_engine"] = fixed_engine

        fixed_model = str(merged.get("whisper_model_size", "small")).strip().lower() or "small"
        if fixed_model not in ("tiny", "base", "small", "medium", "large-v2", "large-v3", "distil-large-v3"):
            fixed_model = "small"
            changed = True
        merged["whisper_model_size"] = fixed_model

        dynamic_value = merged.get("dynamic_energy", DEFAULT_SETTINGS["dynamic_energy"])
        if isinstance(dynamic_value, str):
            fixed_dynamic = dynamic_value.strip().lower() in ("1", "true", "yes", "on")
        else:
            fixed_dynamic = bool(dynamic_value)
        if fixed_dynamic != dynamic_value:
            changed = True
        merged["dynamic_energy"] = fixed_dynamic
        simple_value = merged.get("simple_mode", DEFAULT_SETTINGS.get("simple_mode", True))
        if isinstance(simple_value, str):
            fixed_simple = simple_value.strip().lower() in ("1", "true", "yes", "on")
        else:
            fixed_simple = bool(simple_value)
        merged["simple_mode"] = fixed_simple

        def clamp_number(key, lo, hi, cast=float):
            nonlocal changed
            try:
                value = cast(merged.get(key, DEFAULT_SETTINGS[key]))
            except Exception:
                value = cast(DEFAULT_SETTINGS[key])
                changed = True
            clamped = max(lo, min(hi, value))
            if clamped != value:
                changed = True
            merged[key] = clamped

        clamp_number("microphone_id", -1, 9999, int)
        clamp_number("output_id", -1, 9999, int)
        clamp_number("energy_threshold", 40, 800, int)
        clamp_number("fuzzy_threshold", 0.55, 0.98, float)
        clamp_number("listen_timeout", 0.5, 6.0, float)
        clamp_number("listen_phrase_limit", 1.5, 8.0, float)
        clamp_number("mic_gain", 1.0, 4.0, float)
        clamp_number("monitor_gain", 0.8, 2.5, float)

        settings = merged
        if changed:
            try:
                if os.path.exists(SETTINGS_FILE):
                    stamp = time.strftime("%Y%m%d_%H%M%S")
                    backup_path = os.path.join(BACKUPS_DIR, f"settings.migrate_{stamp}.bak.json")
                    shutil.copy2(SETTINGS_FILE, backup_path)
            except Exception:
                pass
            save_json(SETTINGS_FILE, settings)
            log_runtime("Settings migrated/sanitized and saved")
    else:
        settings = DEFAULT_SETTINGS.copy()
        log_runtime("Settings file missing/corrupt, using defaults")

    try:
        log_runtime(
            "Settings loaded: "
            f"engine={settings.get('asr_engine')} "
            f"model={settings.get('whisper_model_size')} "
            f"dynamic={settings.get('dynamic_energy')} "
            f"thr={settings.get('energy_threshold')}"
        )
    except Exception:
        pass


def save_settings():
    save_json(SETTINGS_FILE, settings)
    log_runtime("Settings saved")
    write_session_snapshot("save_settings")


def build_task_name(path):
    base = os.path.splitext(os.path.basename(path))[0]
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", base).strip("_")
    if not safe:
        safe = "App"
    digest = hashlib.md5(path.encode("utf-8")).hexdigest()[:8]
    return f"VoiceLauncher\\{safe}_{digest}"


def normalize_command_entry(value):
    if isinstance(value, str):
        path = maybe_fix_mojibake(value).strip()
        if path:
            return {
                "mode": "normal",
                "path": path,
                "task_name": "",
                "play_text": "Играть",
                "window_title": "",
                "wait_timeout": 240,
                "single_instance": True,
                "debounce_seconds": 2.8,
                "launcher_dry_run": False,
                "launcher_highlight": False,
                "min_window_confidence": 0.90,
            }
        return None

    if not isinstance(value, dict):
        return None

    mode = maybe_fix_mojibake(str(value.get("mode", "normal"))).strip() or "normal"
    path = maybe_fix_mojibake(str(value.get("path", ""))).strip()
    task_name = maybe_fix_mojibake(str(value.get("task_name", ""))).strip()
    play_text = maybe_fix_mojibake(str(value.get("play_text", "Играть"))).strip() or "Играть"
    window_title = maybe_fix_mojibake(str(value.get("window_title", ""))).strip()
    try:
        wait_timeout = int(value.get("wait_timeout", 240))
    except Exception:
        wait_timeout = 240
    single_instance_raw = value.get("single_instance", True)
    if isinstance(single_instance_raw, str):
        single_instance = single_instance_raw.strip().lower() in ("1", "true", "yes", "on")
    else:
        single_instance = bool(single_instance_raw)
    try:
        debounce_seconds = float(value.get("debounce_seconds", 2.8))
    except Exception:
        debounce_seconds = 2.8
    dry_run_raw = value.get("launcher_dry_run", False)
    highlight_raw = value.get("launcher_highlight", False)
    min_conf_raw = value.get("min_window_confidence", 0.90)
    launcher_dry_run = bool(dry_run_raw) if not isinstance(dry_run_raw, str) else dry_run_raw.strip().lower() in ("1", "true", "yes", "on")
    launcher_highlight = bool(highlight_raw) if not isinstance(highlight_raw, str) else highlight_raw.strip().lower() in ("1", "true", "yes", "on")
    try:
        min_window_confidence = float(min_conf_raw)
    except Exception:
        min_window_confidence = 0.90

    if not path:
        return None
    if mode not in ("admin_task", "launcher_play"):
        mode = "normal"
    if play_text.lower() == "грать":
        play_text = "Играть"
    wait_timeout = max(30, min(900, wait_timeout))
    debounce_seconds = max(0.8, min(30.0, debounce_seconds))
    min_window_confidence = max(0.65, min(0.99, min_window_confidence))

    return {
        "mode": mode,
        "path": path,
        "task_name": task_name,
        "play_text": play_text,
        "window_title": window_title,
        "wait_timeout": wait_timeout,
        "single_instance": single_instance,
        "debounce_seconds": debounce_seconds,
        "launcher_dry_run": launcher_dry_run,
        "launcher_highlight": launcher_highlight,
        "min_window_confidence": min_window_confidence,
    }


def get_entry_mode_label(entry):
    if isinstance(entry, dict) and entry.get("mode") == "admin_task":
        return "Админ-запуск"
    if isinstance(entry, dict) and entry.get("mode") == "launcher_play":
        if bool(entry.get("launcher_highlight", False)):
            return "Лаунчер (preview)"
        if bool(entry.get("launcher_dry_run", False)):
            return "Лаунчер (dry-run)"
        return "Лаунчер + Play"
    return "Обычный"


def run_schtasks(args):
    create_flags = 0
    if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW"):
        create_flags = subprocess.CREATE_NO_WINDOW
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        creationflags=create_flags,
    )


def extract_error_text(result):
    return (result.stderr or result.stdout or "").strip()


def ensure_admin_task(entry):
    path = entry.get("path", "").strip()
    if not path:
        return False, "Пустой путь к файлу"

    task_name = entry.get("task_name", "").strip()
    if not task_name:
        task_name = build_task_name(path)
        entry["task_name"] = task_name

    command = [
        "schtasks",
        "/create",
        "/tn",
        task_name,
        "/tr",
        f'"{path}"',
        "/sc",
        "once",
        "/st",
        "00:00",
        "/rl",
        "highest",
        "/f",
    ]
    result = run_schtasks(command)
    if result.returncode != 0:
        return False, extract_error_text(result) or "Не удалось создать задачу"
    return True, ""


def run_admin_task(entry):
    task_name = entry.get("task_name", "").strip()
    if not task_name:
        ok, error = ensure_admin_task(entry)
        if not ok:
            set_status("Админ-запуск не настроен")
            if error:
                print("Админ-запуск:", error)
            return
        task_name = entry.get("task_name", "").strip()

    run_result = run_schtasks(["schtasks", "/run", "/tn", task_name])
    if run_result.returncode == 0:
        set_status(f"Запущено как админ: {os.path.basename(entry.get('path', ''))}")
        set_last_action(f"Админ-запуск: {os.path.basename(entry.get('path', ''))}")
        return

    # Фолбэк: если задача отсутствует, пересоздаем и пробуем еще раз.
    ok, error = ensure_admin_task(entry)
    if not ok:
        set_status("Не удалось создать админ-задачу")
        if error:
            print("Админ-запуск:", error)
        return

    retry_result = run_schtasks(["schtasks", "/run", "/tn", entry["task_name"]])
    if retry_result.returncode == 0:
        set_status(f"Запущено как админ: {os.path.basename(entry.get('path', ''))}")
        set_last_action(f"Админ-запуск: {os.path.basename(entry.get('path', ''))}")
        return

    err_text = extract_error_text(retry_result) or "Не удалось запустить задачу"
    set_status("Ошибка админ-запуска (см. консоль)")
    set_last_action("Ошибка админ-запуска")
    print("Админ-запуск:", err_text)


def load_commands():
    commands.clear()
    loaded = load_json(COMMANDS_FILE)
    if isinstance(loaded, dict):
        changed = False
        for phrase, raw_entry in loaded.items():
            raw_phrase = str(phrase)
            phrase = normalize_phrase(maybe_fix_mojibake(raw_phrase))
            if not phrase:
                continue
            entry = normalize_command_entry(raw_entry)
            if entry:
                commands[phrase] = entry
                if phrase != normalize_phrase(raw_phrase):
                    changed = True
                elif isinstance(raw_entry, dict) and raw_entry != entry:
                    changed = True

        if changed:
            save_commands()
            log_runtime("Commands normalized and rewritten")
    log_runtime(f"Commands loaded: {len(commands)} entries")


def save_commands():
    save_json(COMMANDS_FILE, commands)
    log_runtime(f"Commands saved: {len(commands)} entries")
    write_session_snapshot("save_commands")


def open_logs_folder():
    try:
        if os.name == "nt":
            os.startfile(LOGS_DIR)
        else:
            subprocess.Popen(["xdg-open", LOGS_DIR])  # noqa: S603,S607
        set_status("Открыта папка логов")
    except Exception as exc:
        show_warning("Логи", f"Не удалось открыть папку логов:\n{exc}")


def export_profile_dialog():
    default_name = f"voice_launcher_profile_{time.strftime('%Y%m%d_%H%M%S')}.json"
    path = filedialog.asksaveasfilename(
        title="Экспорт профиля",
        defaultextension=".json",
        initialdir=SNAPSHOTS_DIR,
        initialfile=default_name,
        filetypes=[("JSON", "*.json"), ("Все файлы", "*.*")],
    )
    if not path:
        return
    try:
        export_profile(Path(path), commands=commands, settings=settings)
        set_status("Профиль экспортирован")
        set_last_action(f"Экспорт профиля: {path}")
        show_info("Экспорт профиля", f"Профиль сохранен:\n{path}")
    except Exception as exc:
        show_warning("Экспорт профиля", f"Ошибка экспорта:\n{exc}")


def import_profile_dialog():
    path = filedialog.askopenfilename(
        title="Импорт профиля",
        filetypes=[("JSON", "*.json"), ("Все файлы", "*.*")],
    )
    if not path:
        return
    try:
        imported_commands, imported_settings = import_profile(Path(path))
    except Exception as exc:
        show_warning("Импорт профиля", f"Ошибка чтения профиля:\n{exc}")
        return

    replace_mode = messagebox.askyesno(
        "Импорт профиля",
        "Полностью заменить текущие команды импортированными?\n\n"
        "Да = заменить все\nНет = объединить",
    )
    apply_settings = messagebox.askyesno(
        "Импорт профиля",
        "Применить аудио/ASR настройки из профиля?",
    )

    if replace_mode:
        commands.clear()
    for phrase, payload in imported_commands.items():
        normalized = normalize_command_entry(payload)
        if not normalized:
            continue
        commands[normalize_phrase(phrase)] = normalized

    if apply_settings:
        merged = DEFAULT_SETTINGS.copy()
        merged.update(imported_settings or {})
        settings.update(merged)
        save_settings()
        restart_listen_event.set()

    save_commands()
    refresh_table()
    set_status(f"Импорт завершен: {len(imported_commands)} команд")
    set_last_action(f"Импорт профиля: {path}")
    show_info("Импорт профиля", f"Импортировано команд: {len(imported_commands)}")


def collect_diagnostics_dialog():
    out_dir = filedialog.askdirectory(title="Куда сохранить диагностику?", initialdir=STORAGE_DIR)
    if not out_dir:
        return
    try:
        bundle_path = collect_diagnostics(
            out_dir=Path(out_dir),
            app_paths={
                "commands": Path(COMMANDS_FILE),
                "settings": Path(SETTINGS_FILE),
                "logs": Path(LOGS_DIR),
            },
            app_version="1.1.0-dev",
        )
        set_status("Диагностика собрана")
        set_last_action(f"Диагностика: {bundle_path}")
        show_info("Диагностика", f"Диагностический пакет создан:\n{bundle_path}")
    except Exception as exc:
        show_warning("Диагностика", f"Ошибка сбора диагностики:\n{exc}")


def refresh_table():
    for item in tree.get_children():
        tree.delete(item)
    for phrase, entry in sorted(commands.items()):
        normalized = normalize_command_entry(entry)
        if not normalized:
            continue
        display_phrase = maybe_fix_mojibake(phrase)
        display_path = maybe_fix_mojibake(normalized["path"])
        tree.insert(
            "",
            "end",
            iid=phrase,
            values=(display_phrase, display_path, get_entry_mode_label(normalized)),
        )


# ======================= Recognition =======================
def asr_engine():
    preferred = str(settings.get("asr_engine", "whisper")).strip().lower()
    if preferred == "whisper" and WhisperModel is not None:
        return "whisper"
    return "google"


def get_whisper_model():
    global whisper_model
    if WhisperModel is None:
        raise RuntimeError("Whisper модуль не установлен")

    if whisper_model is not None:
        return whisper_model

    with whisper_model_lock:
        if whisper_model is not None:
            return whisper_model

        model_size = str(settings.get("whisper_model_size", "small")).strip() or "small"
        set_status(f"Загрузка Whisper ({model_size})... первый запуск может занять время")
        whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
        set_status("Whisper готов")
        return whisper_model


def whisper_decode(model, source, prompt="", use_vad=True, beam_size=4, best_of=4):
    kwargs = {
        "language": "ru",
        "beam_size": beam_size,
        "best_of": best_of,
        "condition_on_previous_text": False,
        "temperature": 0.0,
        "vad_filter": bool(use_vad),
    }
    if use_vad:
        kwargs["vad_parameters"] = {"min_silence_duration_ms": 170}
    if prompt:
        kwargs["initial_prompt"] = prompt

    segments, _info = model.transcribe(source, **kwargs)
    return normalize_phrase(" ".join(seg.text for seg in segments))


def recognize_with_whisper(audio, command_hint=False):
    model = get_whisper_model()
    source, temp_path = get_whisper_audio_source(audio)
    prompt = build_commands_prompt() if command_hint else ""
    candidates = []

    try:
        primary = whisper_decode(
            model,
            source,
            prompt=prompt,
            use_vad=True,
            beam_size=5 if command_hint else 4,
            best_of=5 if command_hint else 4,
        )
        if primary:
            candidates.append(primary)

        # Если распознано слишком коротко ("т", "то"), делаем вторую попытку без VAD.
        if not primary or len(primary) <= 2:
            retry = whisper_decode(
                model,
                source,
                prompt=prompt,
                use_vad=False,
                beam_size=5,
                best_of=5,
            )
            if retry and retry not in candidates:
                candidates.append(retry)

        return candidates
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


def recognize_with_google(recognizer, audio):
    boosted = normalize_audio_for_asr(audio)
    candidates = []

    # Сначала берем список альтернатив распознавания.
    try:
        payload = recognizer.recognize_google(boosted, language="ru-RU", show_all=True)
        if isinstance(payload, dict):
            for alt in payload.get("alternative", []):
                text = normalize_phrase(alt.get("transcript", ""))
                if text and text not in candidates:
                    candidates.append(text)
    except sr.UnknownValueError:
        return []
    except Exception:
        pass

    # Фолбэк на обычный режим, если альтернатив не пришло.
    if not candidates:
        try:
            text = normalize_phrase(recognizer.recognize_google(boosted, language="ru-RU"))
            if text:
                candidates.append(text)
        except sr.UnknownValueError:
            return []
        except Exception:
            return []

    return candidates


def warmup_asr_async():
    global whisper_warmup_in_progress
    if asr_engine() != "whisper":
        return
    if whisper_model is not None or whisper_warmup_in_progress:
        return

    def worker():
        global whisper_warmup_in_progress
        whisper_warmup_in_progress = True
        try:
            get_whisper_model()
        except Exception as exc:
            set_status(f"Whisper не загрузился, используется Google ({exc})")
        finally:
            whisper_warmup_in_progress = False

    threading.Thread(target=worker, daemon=True).start()


def build_recognizer():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = bool(settings.get("dynamic_energy", True))
    recognizer.energy_threshold = int(settings.get("energy_threshold", 110))
    recognizer.dynamic_energy_adjustment_damping = 0.08
    recognizer.dynamic_energy_ratio = 1.35
    recognizer.pause_threshold = 0.75
    recognizer.non_speaking_duration = 0.35
    recognizer.phrase_threshold = 0.15
    return recognizer


def merge_candidates(*candidate_lists):
    merged = []
    for items in candidate_lists:
        if not items:
            continue
        for item in items:
            text = normalize_phrase(str(item))
            if text and text not in merged:
                merged.append(text)
    return merged


def rank_candidates_for_choice(candidates):
    if not candidates:
        return []
    long_first = [c for c in candidates if len(c) > 2]
    short_tail = [c for c in candidates if len(c) <= 2]
    return long_first + short_tail if long_first else candidates


def recognize_candidates(recognizer, audio, command_hint=False, prefer_all_engines=False):
    global last_asr_error_ts
    engine = asr_engine()
    whisper_candidates = []
    google_candidates = []

    # Холодный старт Whisper не должен "вешать" первые команды.
    if engine == "whisper" and whisper_model is None and not prefer_all_engines:
        if not whisper_warmup_in_progress:
            warmup_asr_async()
        google_candidates = recognize_with_google(recognizer, audio)
        if google_candidates:
            log_asr("cold-start fallback: used Google while Whisper warms up")
            set_asr_status("ASR: Google (Whisper прогревается)")
            return google_candidates
        if whisper_warmup_in_progress:
            set_asr_status("ASR: ожидание Whisper...")
            return []

    # Основной движок.
    if engine == "whisper" or prefer_all_engines:
        try:
            whisper_candidates = recognize_with_whisper(audio, command_hint=command_hint)
            if whisper_candidates and not prefer_all_engines:
                set_asr_status("ASR: Whisper")
                return whisper_candidates
        except Exception as exc:
            now = time.time()
            if now - last_asr_error_ts > 3.0:
                set_status(f"Whisper недоступен, fallback на Google ({exc})")
                last_asr_error_ts = now
            set_asr_status("ASR: Google (fallback после ошибки Whisper)")

    google_candidates = recognize_with_google(recognizer, audio)
    if google_candidates and engine == "google" and not prefer_all_engines:
        set_asr_status("ASR: Google")
        return google_candidates

    merged = merge_candidates(whisper_candidates, google_candidates)
    if merged:
        if whisper_candidates:
            set_asr_status("ASR: Whisper + Google")
        else:
            set_asr_status("ASR: Google")
    return rank_candidates_for_choice(merged)


def consonant_skeleton(text):
    vowels = set("аеёиоуыэюяьъ ")
    return "".join(ch for ch in text if ch not in vowels)


def command_match_score(candidate, key):
    candidate = normalize_phrase(candidate)
    key = normalize_phrase(key)
    if not candidate or not key:
        return 0.0
    if candidate == key:
        return 1.0

    score = difflib.SequenceMatcher(None, candidate, key).ratio()
    min_len = min(len(candidate), len(key))
    max_len = max(len(candidate), len(key))
    overlap = min_len / max(1, max_len)

    if key.startswith(candidate):
        score = max(score, 0.72 + 0.28 * overlap)
    if candidate.startswith(key):
        score = max(score, 0.74 + 0.26 * overlap)
    if candidate in key or key in candidate:
        score = max(score, 0.60 + 0.34 * overlap)

    # Для случаев "та" -> "танки", "з" -> "запрет".
    if len(candidate) <= 2 and key.startswith(candidate):
        score = max(score, 0.78)
    elif len(candidate) <= 2 and candidate in key:
        score = max(score, 0.66)

    # Фонетический фолбэк по "скелету" согласных.
    c_skel = consonant_skeleton(candidate)
    k_skel = consonant_skeleton(key)
    if c_skel and k_skel:
        skel_ratio = difflib.SequenceMatcher(None, c_skel, k_skel).ratio()
        score = max(score, 0.55 + 0.30 * skel_ratio)
        if len(c_skel) <= 2 and k_skel.startswith(c_skel):
            score = max(score, 0.74)

    # Для очень коротких кусков усиливаем штраф, если первая буква не совпадает.
    if candidate and key and len(candidate) <= 2 and candidate[0] != key[0]:
        score *= 0.62

    return min(1.0, score)


def find_best_command(candidates):
    result = modular_find_best_command(
        candidates=candidates or [],
        commands=commands,
        base_threshold=float(settings.get("fuzzy_threshold", 0.72)),
    )
    return result.phrase, result.entry, result.score, result.heard, result.margin


# ======================= Command actions =======================
def save_mapping(
    phrase,
    path,
    use_admin=False,
    launcher_play=False,
    play_text="Играть",
    window_title="",
    wait_timeout=240,
    single_instance=True,
    debounce_seconds=2.8,
    launcher_dry_run=False,
    launcher_highlight=False,
    min_window_confidence=0.90,
    replacing_phrase="",
):
    result = save_command_definition(
        commands=commands,
        phrase=phrase,
        path=path,
        use_admin=use_admin,
        launcher_play=launcher_play,
        play_text=play_text,
        window_title=window_title,
        wait_timeout=int(wait_timeout) if str(wait_timeout).strip() else 240,
        single_instance=bool(single_instance),
        debounce_seconds=max(0.8, min(30.0, float(debounce_seconds))),
        launcher_dry_run=bool(launcher_dry_run),
        launcher_highlight=bool(launcher_highlight),
        min_window_confidence=float(min_window_confidence),
        build_task_name=build_task_name,
        score_func=command_match_score,
        path_exists=os.path.exists,
        ignore_phrase=replacing_phrase,
    )
    if not result.ok:
        if result.code == "phrase_conflict":
            messagebox.showwarning("Похожая команда", result.message)
        elif result.code in ("empty_phrase", "empty_path"):
            messagebox.showinfo("Сохранение команды", result.message)
        else:
            messagebox.showwarning("Сохранение команды", result.message)
        return False

    entry = result.entry or {}
    phrase = result.phrase or normalize_phrase(phrase)
    if entry.get("mode") == "admin_task":
        ok, error = ensure_admin_task(entry)
        if not ok:
            messagebox.showwarning(
                "Админ-запуск",
                "Не удалось создать задачу с повышенными правами.\n"
                "Запустите лаунчер от имени администратора и повторите.\n\n"
                f"{error}",
            )
            if phrase in commands:
                del commands[phrase]
            return False

    save_commands()
    refresh_table()
    set_status(f"Сохранено: '{phrase}' ({get_entry_mode_label(entry)})")
    set_last_action(f"Сохранена команда: {phrase}")
    log_runtime(f"Command added/updated: phrase='{phrase}' mode={entry.get('mode')} path='{path}'")
    return True


def add_file_manual():
    path = filedialog.askopenfilename(title="Выберите файл")
    if not path:
        return

    phrase = simpledialog.askstring("Фраза", "Введите ключевую фразу:")
    if phrase is None:
        return

    use_admin = messagebox.askyesno(
        "Режим запуска",
        "Запускать эту команду как администратор (через Планировщик задач)?",
    )

    launcher_play = False
    play_text = "Играть"
    window_title = ""
    wait_timeout = 240
    launcher_dry_run = False
    launcher_highlight = False
    min_window_confidence = 0.90

    if not use_admin:
        launcher_play = messagebox.askyesno(
            "Лаунчер игры",
            "Это лаунчер? Ждать активную кнопку 'Играть' и нажимать автоматически?",
        )
        if launcher_play:
            custom_play = simpledialog.askstring(
                "Текст кнопки",
                "Текст кнопки запуска в лаунчере:",
                initialvalue="Играть",
            )
            if custom_play and custom_play.strip():
                play_text = custom_play.strip()

            custom_title = simpledialog.askstring(
                "Окно лаунчера",
                "Часть заголовка окна (необязательно, для точности):",
                initialvalue="",
            )
            if custom_title:
                window_title = custom_title.strip()

            custom_wait = simpledialog.askinteger(
                "Ожидание (сек)",
                "Сколько максимум ждать активации кнопки?",
                initialvalue=240,
                minvalue=30,
                maxvalue=900,
            )
            if custom_wait:
                wait_timeout = int(custom_wait)

            launcher_dry_run = messagebox.askyesno(
                "Безопасный режим",
                "Включить dry-run (проверка без клика) для этой команды?",
            )
            launcher_highlight = messagebox.askyesno(
                "Подсветка",
                "Включить режим подсветки окна/кнопки вместо клика?",
            )

    save_mapping(
        phrase,
        path,
        use_admin=use_admin,
        launcher_play=launcher_play,
        play_text=play_text,
        window_title=window_title,
        wait_timeout=wait_timeout,
        launcher_dry_run=launcher_dry_run,
        launcher_highlight=launcher_highlight,
        min_window_confidence=min_window_confidence,
    )


def remove_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("Удаление", "Выберите запись в таблице.")
        return

    phrase = selected[0]
    if phrase not in commands:
        phrase = tree.item(selected[0], "values")[0]
    if phrase in commands:
        del commands[phrase]
        save_commands()
        refresh_table()
        set_status(f"Удалено: '{phrase}'")
        set_last_action(f"Удалена команда: {phrase}")
        log_runtime(f"Command removed: phrase='{phrase}'")


def run_tasklist_command(args):
    create_flags = 0
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        create_flags = subprocess.CREATE_NO_WINDOW
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        creationflags=create_flags,
    )


def get_process_scanner():
    global process_scanner_service
    if process_scanner_service is None:
        process_scanner_service = ProcessScanner(
            runner=run_tasklist_command,
            logger=log_runtime,
            platform_name=os.name,
            now=time.time,
            cache_ttl=1.2,
            cache=process_list_cache,
        )
    return process_scanner_service


def get_launch_gate():
    global launch_gate_service
    if launch_gate_service is None:
        launch_gate_service = LaunchGate(
            gate=command_launch_gate,
            now=time.time,
        )
    return launch_gate_service


def get_running_process_names(force_refresh=False):
    scanner = get_process_scanner()
    names = scanner.get_running_process_names(force_refresh=force_refresh)
    try:
        process_list_cache.update(scanner.cache)
    except Exception:
        pass
    return names


def find_running_process_for_entry(entry):
    running_names = get_running_process_names()
    return core_find_running_process_for_entry(
        entry=entry,
        running_names=running_names,
        normalize_phrase=normalize_phrase,
    )


def can_launch_entry(entry):
    decision = get_launch_gate().can_launch_entry(
        entry=entry,
        find_running_process=find_running_process_for_entry,
    )
    return decision.can_launch, decision.reason, decision.payload


def get_target_launcher():
    global target_launcher_executor
    if target_launcher_executor is None:
        state = TargetLauncherState(
            last_path=last_launch_phrase,
            last_time=last_launch_time,
        )
        deps = TargetLauncherDeps(
            path_exists=os.path.exists,
            status=set_status,
            last_action=set_last_action,
            runtime_log=log_runtime,
            time_now=time.time,
            platform_name=os.name,
            os_startfile=getattr(os, "startfile", None),
            popen=subprocess.Popen,
        )
        target_launcher_executor = TargetLauncher(deps=deps, state=state)
    return target_launcher_executor


def launch_target(path, duplicate_guard_seconds=1.0):
    global last_launch_time, last_launch_phrase
    launcher = get_target_launcher()
    ok = launcher.launch_target(path, duplicate_guard_seconds=duplicate_guard_seconds)
    last_launch_time = float(launcher.state.last_time)
    last_launch_phrase = str(launcher.state.last_path)
    return ok


def get_path_stem(path):
    try:
        return os.path.splitext(os.path.basename(path))[0].strip().lower()
    except Exception:
        return ""


def get_path_folder(path):
    try:
        folder = os.path.basename(os.path.dirname(path or ""))
    except Exception:
        folder = ""
    return normalize_phrase(folder or "")


def get_window_title(window_wrapper):
    try:
        return normalize_phrase(window_wrapper.window_text() or "")
    except Exception:
        return ""


def get_window_handle(window_wrapper):
    for attr_name in ("handle", "hwnd"):
        try:
            value = getattr(window_wrapper, attr_name)
            if value:
                return int(value)
        except Exception:
            continue
    return None


def get_window_pid(hwnd):
    if os.name != "nt":
        return 0
    try:
        pid = ctypes.c_ulong(0)
        ctypes.windll.user32.GetWindowThreadProcessId(int(hwnd), ctypes.byref(pid))
        return int(pid.value or 0)
    except Exception:
        return 0


def get_process_path_by_pid(pid):
    if os.name != "nt" or not pid:
        return ""
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    handle = None
    try:
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if not handle:
            return ""
        size = ctypes.c_ulong(4096)
        buffer = ctypes.create_unicode_buffer(4096)
        ok = ctypes.windll.kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size))
        if ok:
            return os.path.abspath(buffer.value)
    except Exception:
        return ""
    finally:
        try:
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
        except Exception:
            pass
    return ""


def resolve_process_for_window_handle(hwnd):
    pid = get_window_pid(hwnd)
    proc_path = get_process_path_by_pid(pid)
    proc_name = os.path.basename(proc_path).lower() if proc_path else ""
    return proc_name, proc_path


def build_hint_variants(text):
    raw = str(text or "").strip()
    variants = []

    def add(item):
        value = normalize_phrase(item or "")
        if value and value not in variants:
            variants.append(value)

    if not raw:
        return variants

    add(raw)
    spaced = re.sub(r"([a-zа-я0-9])([A-ZА-Я])", r"\1 \2", raw)
    spaced = re.sub(r"[_\-]+", " ", spaced)
    add(spaced)
    compact = normalize_phrase(spaced).replace(" ", "")
    if compact and compact not in variants:
        variants.append(compact)
    return variants


def build_window_hints(path, window_title_hint=""):
    hints = []
    for part in (window_title_hint or "", get_path_stem(path), get_path_folder(path)):
        for variant in build_hint_variants(part):
            if variant and variant not in hints:
                hints.append(variant)

    generic = {"launcher", "launch", "client", "updater", "start"}
    prioritized = [h for h in hints if h not in generic]
    fallback = [h for h in hints if h in generic]
    return prioritized + fallback


def activate_window(window_wrapper):
    try:
        if hasattr(window_wrapper, "is_minimized") and window_wrapper.is_minimized():
            try:
                window_wrapper.restore()
            except Exception:
                pass
        window_wrapper.set_focus()
        return True
    except Exception:
        return False


def find_play_control(window_wrapper, play_text):
    target = normalize_phrase((play_text or "Играть").strip())
    if not target:
        target = "играть"

    tokens = [token for token in target.split() if len(token) >= 2]
    best = None
    best_score = 0.0

    control_types = ("Button", "Hyperlink", "Custom", "Text")
    for ctype in control_types:
        try:
            controls = window_wrapper.descendants(control_type=ctype)
        except Exception:
            continue
        for ctrl in controls:
            try:
                caption = normalize_phrase(ctrl.window_text())
            except Exception:
                caption = ""
            if not caption:
                try:
                    caption = normalize_phrase(getattr(ctrl.element_info, "name", "") or "")
                except Exception:
                    caption = ""

            score = 0.0
            if caption:
                if target in caption:
                    score = 1.0
                else:
                    ratio = difflib.SequenceMatcher(None, target, caption).ratio()
                    if ratio >= 0.68:
                        score = ratio
                    elif any(token in caption for token in tokens):
                        score = 0.72

            if score <= 0:
                continue

            if ctype == "Button":
                score += 0.30
            elif ctype == "Hyperlink":
                score += 0.20
            elif ctype == "Custom":
                score += 0.10
            else:
                score -= 0.10

            try:
                if ctrl.is_enabled():
                    score += 0.08
            except Exception:
                pass

            if score > best_score:
                best_score = score
                best = (ctrl, caption, ctype, score)

    return best


def is_control_enabled(control):
    try:
        return bool(control.is_enabled())
    except Exception:
        return True


def iter_control_chain(control, max_depth=5):
    chain = []
    seen = set()
    current = control
    for _ in range(max_depth):
        if current is None:
            break
        key = id(current)
        if key in seen:
            break
        seen.add(key)
        chain.append(current)
        try:
            current = current.parent()
        except Exception:
            break
    return chain


def click_play_control(control, window_wrapper):
    chain = iter_control_chain(control)

    for item in chain:
        try:
            if hasattr(item, "invoke"):
                item.invoke()
                return True, "invoke"
        except Exception:
            pass
        try:
            iface = getattr(item, "iface_invoke", None)
            if iface is not None:
                iface.Invoke()
                return True, "iface_invoke"
        except Exception:
            pass

    for item in chain:
        try:
            item.click_input()
            return True, "click_input"
        except Exception:
            pass
        try:
            item.click()
            return True, "click"
        except Exception:
            pass

    if pywinauto_mouse is not None:
        for item in chain:
            try:
                rect = item.rectangle()
                width = int(rect.right) - int(rect.left)
                height = int(rect.bottom) - int(rect.top)
                if width < 4 or height < 4:
                    continue
                cx = int((int(rect.left) + int(rect.right)) / 2)
                cy = int((int(rect.top) + int(rect.bottom)) / 2)
                pywinauto_mouse.click(button="left", coords=(cx, cy))
                return True, "mouse_center"
            except Exception:
                continue

    try:
        activate_window(window_wrapper)
        if send_keys is not None:
            send_keys("{ENTER}")
            return True, "enter"
    except Exception:
        pass

    try:
        activate_window(window_wrapper)
        if send_keys is not None:
            send_keys(" ")
            return True, "space"
    except Exception:
        pass

    return False, "none"


def play_control_is_ready(window_wrapper, play_text):
    found = find_play_control(window_wrapper, play_text)
    if not found:
        return False
    control, _, _, _ = found
    return is_control_enabled(control)


def launch_with_launcher_play(entry):
    if Desktop is None:
        set_status("Режим лаунчера: установите pywinauto (`pip install pywinauto`)")
        launch_target(entry.get("path", ""))
        return

    def worker():
        deps = LauncherRunnerDeps(
            desktop_factory=lambda: Desktop(backend="uia"),
            process_resolver=resolve_process_for_window_handle,
            find_running_process=find_running_process_for_entry,
            launch_target=lambda target_path: launch_target(target_path, duplicate_guard_seconds=0.0),
            find_play_control=find_play_control,
            is_control_enabled=is_control_enabled,
            click_play_control=click_play_control,
            play_control_is_ready=play_control_is_ready,
            activate_window=activate_window,
            build_window_hints=build_window_hints,
            normalize_phrase=normalize_phrase,
            logger=log_launcher,
            runtime_logger=log_runtime,
            set_status=set_status,
            set_last_action=set_last_action,
        )
        run_launcher_play(entry=entry, deps=deps)

    threading.Thread(target=worker, daemon=True).start()


def launch_command(entry):
    normalized = normalize_command_entry(entry)
    if not normalized:
        set_status("Некорректная команда")
        return

    can_launch, reason, payload = can_launch_entry(normalized)
    if not can_launch:
        if reason == "cooldown":
            set_status(f"Антидубль: подождите {float(payload):.1f} сек")
            log_runtime(
                f"Launch blocked by cooldown: path='{normalized.get('path', '')}' wait={float(payload):.2f}s"
            )
        elif reason == "already_running":
            set_status(f"Уже запущено: {payload}")
            log_runtime(
                f"Launch blocked because process is running: path='{normalized.get('path', '')}' proc='{payload}'"
            )
        return

    if normalized.get("mode") == "admin_task":
        run_admin_task(normalized)
        return
    if normalized.get("mode") == "launcher_play":
        launch_with_launcher_play(normalized)
        return

    launch_target(normalized.get("path", ""))


def test_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("Проверка", "Выберите запись в таблице.")
        return
    phrase = selected[0]
    if phrase not in commands:
        phrase = tree.item(selected[0], "values")[0]
    launch_command(commands.get(phrase))


def check_microphone():
    if monitor_active_event.is_set():
        set_status("Сначала выключите мониторинг")
        show_warning("Проверка микрофона", "Сначала выключите мониторинг и попробуйте снова.")
        return

    set_status("Проверка микрофона...")
    pause_listen_event.set()
    restart_listen_event.set()

    def worker():
        try:
            set_status("Тишина 1 сек для авто-настройки...")
            recognizer = build_recognizer()
            mic_index = get_selected_mic_index()
            with sr.Microphone(device_index=mic_index) as source:
                recognizer.adjust_for_ambient_noise(source, duration=1.0)
                calibrated_threshold = int(recognizer.energy_threshold)
                settings["energy_threshold"] = calibrated_threshold
                root.after(0, lambda: energy_var.set(calibrated_threshold))
                set_status("Скажите любую фразу...")
                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=max(4.5, float(settings.get("listen_phrase_limit", 5.0))),
                )

            level = get_audio_level_percent(audio)
            candidates = recognize_candidates(recognizer, audio)
            if candidates:
                preview = " / ".join(candidates[:3])
                quality = "Нормально"
                if level < 18:
                    quality = "Слишком тихо, поднимите Mic Gain или уровень микрофона в Windows"
                elif level > 92:
                    quality = "Слишком громко, есть риск искажений. Снизьте Mic Gain"

                save_settings()
                restart_listen_event.set()
                set_status(f"Проверка OK | Уровень {level}% | '{candidates[0]}'")
                show_info(
                    "Проверка микрофона",
                    f"Уровень сигнала: {level}%\n"
                    f"Порог после авто-настройки: {settings['energy_threshold']}\n"
                    f"Распознано: {preview}\n\n"
                    f"Рекомендация: {quality}",
                )
            else:
                save_settings()
                restart_listen_event.set()
                set_status(f"Проверка: не распознано | Уровень {level}%")
                show_warning(
                    "Проверка микрофона",
                    f"Речь не распознана.\n"
                    f"Уровень сигнала: {level}%\n"
                    f"Порог: {settings['energy_threshold']}\n\n"
                    "Попробуйте выбрать другой микрофон или увеличить Mic Gain до 1.4-1.8.",
                )
        except sr.WaitTimeoutError:
            set_status("Проверка: тишина, попробуйте еще раз")
            show_warning("Проверка микрофона", "Не услышал речь в течение ожидания.")
        except Exception as exc:
            set_status(f"Проверка: ошибка ({exc})")
            show_warning("Проверка микрофона", f"Ошибка микрофона:\n{exc}")
        finally:
            pause_listen_event.clear()

    threading.Thread(target=worker, daemon=True).start()


def calibrate_mic():
    # Оставлено для совместимости со старыми привязками кнопок.
    check_microphone()


def test_recognition_once():
    # Оставлено для совместимости со старыми привязками кнопок.
    check_microphone()


def stop_monitoring():
    monitor_active_event.clear()
    pause_listen_event.clear()
    restart_listen_event.set()
    if "monitor_button_text" in globals():
        monitor_button_text.set("Монитор: OFF")
    set_status("Мониторинг остановлен")


def monitor_open_streams(pa, in_index, out_index):
    rates = (48000, 44100, 32000, 24000, 22050, 16000)
    frames = 256
    last_exc = None

    for rate in rates:
        try:
            in_stream = pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=rate,
                input=True,
                input_device_index=in_index,
                frames_per_buffer=frames,
            )
            out_channels = 1
            out_stream = None
            try:
                out_info = pa.get_device_info_by_index(out_index)
                max_out = int(out_info.get("maxOutputChannels", 1))
                preferred_channels = [2, 1] if max_out >= 2 else [1]
            except Exception:
                preferred_channels = [1]

            try:
                for ch in preferred_channels:
                    out_stream = pa.open(
                        format=pyaudio.paInt16,
                        channels=ch,
                        rate=rate,
                        output=True,
                        output_device_index=out_index,
                        frames_per_buffer=frames,
                    )
                    out_channels = ch
                    break
                if out_stream is None:
                    raise RuntimeError("Не удалось открыть выходной поток")
            except Exception:
                in_stream.stop_stream()
                in_stream.close()
                raise
            return in_stream, out_stream, frames, rate, out_channels
        except Exception as exc:
            last_exc = exc
            continue

    raise RuntimeError(f"Не удалось открыть мониторинг аудио: {last_exc}")


def apply_monitor_cleanup(data):
    # Мягкая обработка для уменьшения "эхо-хвостов" в реальном времени.
    try:
        rms = audio_rms(data, 2)
        gate = max(120, int(float(settings.get("energy_threshold", 110)) * 1.7))
        if rms < gate:
            return audio_mul(data, 2, 0.45)
        return data
    except Exception:
        return data


def toggle_monitoring():
    global monitor_thread

    if monitor_active_event.is_set():
        stop_monitoring()
        if "monitor_button_text" in globals():
            monitor_button_text.set("Монитор: OFF")
        return

    if pyaudio is None:
        set_status("PyAudio недоступен для мониторинга")
        return

    if "monitor_button_text" in globals():
        monitor_button_text.set("Монитор: запуск...")

    def monitor_worker():
        pa = None
        in_stream = None
        out_stream = None
        try:
            pause_listen_event.set()
            restart_listen_event.set()
            time.sleep(0.25)

            in_index = get_selected_mic_index()
            out_index = get_selected_output_index()
            if in_index is None:
                set_status("Нет выбранного микрофона для мониторинга")
                return

            pa = pyaudio.PyAudio()
            in_stream, out_stream, frames, rate, out_channels = monitor_open_streams(pa, in_index, out_index)

            monitor_active_event.set()
            if "monitor_button_text" in globals():
                monitor_button_text.set("Монитор: ON")
            set_status(f"Мониторинг ON: реальное прослушивание ({rate} Hz)")

            gain = float(settings.get("monitor_gain", 1.2))
            last_status = 0.0
            while monitor_active_event.is_set():
                data = in_stream.read(frames, exception_on_overflow=False)
                data = apply_monitor_cleanup(data)
                if gain > 1.01:
                    data = apply_safe_gain(data, 2, gain)
                out_data = data
                if out_channels == 2:
                    out_data = audio_to_stereo(data, 2)
                out_stream.write(out_data)
                now = time.time()
                if now - last_status >= 1.0:
                    level = int(max(0, min(100, (audio_rms(data, 2) / 32767.0) * 350)))
                    set_status(f"Мониторинг ON | Уровень: {level}%")
                    last_status = now
        except Exception as exc:
            set_status(f"Мониторинг ошибка: {exc}")
        finally:
            monitor_active_event.clear()
            pause_listen_event.clear()
            restart_listen_event.set()
            if "monitor_button_text" in globals():
                monitor_button_text.set("Монитор: OFF")
            try:
                if in_stream is not None:
                    in_stream.stop_stream()
                    in_stream.close()
                if out_stream is not None:
                    out_stream.stop_stream()
                    out_stream.close()
                if pa is not None:
                    pa.terminate()
            except Exception:
                pass

    monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
    monitor_thread.start()


# ======================= Voice capture dialog =======================
def open_voice_capture_dialog():
    open_command_wizard(
        CommandWizardDeps(
            root=root,
            card_color=PALETTE["card"],
            monitor_active_event=monitor_active_event,
            pause_listen_event=pause_listen_event,
            build_recognizer=build_recognizer,
            get_selected_mic_index=get_selected_mic_index,
            microphone_factory=sr.Microphone,
            wait_timeout_error=sr.WaitTimeoutError,
            voice_capture_timeout=VOICE_CAPTURE_TIMEOUT,
            settings_provider=lambda: settings,
            get_audio_level_percent=get_audio_level_percent,
            recognize_candidates=recognize_candidates,
            save_mapping=save_mapping,
            launch_with_launcher_play=launch_with_launcher_play,
            path_exists=os.path.exists,
        )
    )


# ======================= Listener =======================
def listen_loop():
    global last_voice_trigger
    deps = ListenerDeps(
        stop_event=stop_event,
        pause_listen_event=pause_listen_event,
        monitor_active_event=monitor_active_event,
        restart_listen_event=restart_listen_event,
        build_recognizer=build_recognizer,
        get_selected_mic_index=get_selected_mic_index,
        microphone_factory=sr.Microphone,
        settings_provider=lambda: settings,
        recognize_candidates=lambda recognizer, audio: recognize_candidates(recognizer, audio),
        match_command=find_best_command,
        launch_command=launch_command,
        set_status=set_status,
        set_last_phrase=set_last_phrase,
        log_runtime=log_runtime,
        log_asr=log_asr,
        wait_timeout_error=sr.WaitTimeoutError,
    )
    controller = AppController(deps=deps, last_voice_trigger=last_voice_trigger)
    last_voice_trigger = controller.run_listen_loop()


# ======================= Tray & UI =======================
def hide_window(icon=None, item=None):
    root.withdraw()


def show_window(icon=None, item=None):
    root.deiconify()
    root.after(0, root.lift)


def quit_app(icon=None, item=None):
    log_runtime("Quit requested from tray/UI")
    write_session_snapshot("quit")
    stop_event.set()
    monitor_active_event.clear()
    if tray_icon:
        tray_icon.stop()
    root.after(0, root.destroy)


def on_closing():
    hide_window()


def create_tray_icon():
    global tray_icon
    if tray_icon is not None:
        return

    image = Image.new("RGB", (64, 64), color=PALETTE["card"])
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((6, 6, 58, 58), radius=14, fill=PALETTE["hero_left"])
    draw.ellipse((20, 14, 50, 44), fill=PALETTE["accent"])
    draw.rounded_rectangle((16, 40, 48, 52), radius=5, fill=PALETTE["border"])

    menu = pystray.Menu(
        pystray.MenuItem("Открыть настройки", show_window),
        pystray.MenuItem("Скрыть", hide_window),
        pystray.MenuItem("Выход", quit_app),
    )
    tray_icon = pystray.Icon("voice_launcher", image, "Voice Launcher", menu)
    try:
        tray_icon.run_detached()
    except Exception as exc:
        set_status(f"Трей недоступен: {exc}")


def setup_styles():
    style = ttk.Style()
    apply_theme_styles(style=style, palette=PALETTE, title_font=UI_FONT_SCRIPT, body_font=UI_FONT_SOFT)


def paint_hero_gradient(canvas):
    draw_hero_gradient(
        canvas=canvas,
        palette=PALETTE,
        title_font=UI_FONT_SCRIPT,
        body_font=UI_FONT_SOFT,
        title_text="Voice Launcher",
    )


if not ensure_single_instance():
    log_runtime("Second instance detected, exiting")
    raise SystemExit(0)

hide_console_window()
log_runtime(
    f"App startup: pid={os.getpid()} frozen={bool(getattr(sys, 'frozen', False))} storage='{STORAGE_DIR}'"
)
load_settings()
write_session_snapshot("startup_after_settings")

root = tk.Tk()
root.title("Голосовой запускатор")
root.geometry("1280x820")
root.minsize(1080, 700)
root.configure(bg=PALETTE["bg"])
root.attributes("-alpha", 0.0)

setup_styles()

main = ttk.Frame(root, style="Root.TFrame", padding=18)
main.pack(fill="both", expand=True)

card = ttk.Frame(main, style="Card.TFrame", padding=14)
card.pack(fill="both", expand=True)

hero = tk.Canvas(card, height=112, highlightthickness=0, bd=0, bg=PALETTE["hero_left"])
hero.pack(fill="x", pady=(0, 10))
paint_hero_gradient(hero)

tab_glow = tk.Canvas(card, height=4, highlightthickness=0, bg=PALETTE["card"], bd=0)
tab_glow.pack(fill="x", pady=(2, 10))
tab_glow_rect = tab_glow.create_rectangle(0, 0, 0, 4, outline="", fill=PALETTE["accent"])

mode_strip = ttk.Frame(card, style="Card.TFrame")
mode_strip.pack(fill="x", pady=(0, 8))

notebook = ttk.Notebook(card, style="Futuristic.TNotebook")
commands_tab = ttk.Frame(notebook, style="Card.TFrame", padding=10)
audio_tab = ttk.Frame(notebook, style="Card.TFrame", padding=10)
notebook.add(commands_tab, text="Команды")
notebook.add(audio_tab, text="Расширенный")
notebook.pack(fill="both", expand=True, pady=(0, 10))

settings_box = ttk.Frame(audio_tab, style="Panel.TFrame", padding=12)
settings_box.pack(fill="x", pady=(0, 10))

mic_options, output_options = get_device_options()
mic_labels = [opt["label"] for opt in mic_options]
output_labels = [opt["label"] for opt in output_options]


def get_default_label(options, id_key, name_key, kind="input", preferred_output_name=""):
    if not options:
        return ""
    saved_id_local = int(settings.get(id_key, -1))
    if saved_id_local >= 0:
        for opt in options:
            if opt["id"] == saved_id_local:
                return opt["label"]
    saved_name_local = settings.get(name_key, "")
    if saved_name_local:
        for opt in options:
            if opt["raw"] == saved_name_local or opt["name"] == saved_name_local:
                return opt["label"]
    ordered = sort_device_options(options, kind=kind, preferred_output_name=preferred_output_name)
    return ordered[0]["label"] if ordered else options[0]["label"]


default_out_label = get_default_label(output_options, "output_id", "output_name", kind="output")
default_out_name = ""
if default_out_label:
    selected_out_opt = next((o for o in output_options if o["label"] == default_out_label), None)
    if selected_out_opt:
        default_out_name = selected_out_opt["name"]

out_var = tk.StringVar(value=default_out_label)
mic_var = tk.StringVar(
    value=get_default_label(
        mic_options,
        "microphone_id",
        "microphone_name",
        kind="input",
        preferred_output_name=default_out_name,
    )
)
dynamic_var = tk.BooleanVar(value=bool(settings.get("dynamic_energy", True)))
energy_var = tk.IntVar(value=int(settings.get("energy_threshold", 110)))
fuzzy_var = tk.DoubleVar(value=float(settings.get("fuzzy_threshold", 0.72)))
gain_var = tk.DoubleVar(value=float(settings.get("mic_gain", 1.4)))
monitor_gain_var = tk.DoubleVar(value=float(settings.get("monitor_gain", 1.0)))
monitor_button_text = tk.StringVar(value="Монитор: OFF")
simple_mode_text = tk.StringVar(value="")
ui_controller = UiController(
    UiControllerDeps(
        root=root,
        settings=settings,
        save_settings=save_settings,
        set_status=set_status,
        heard_history=recent_heard_phrases,
        action_history=recent_actions,
    )
)
ui_controller.bind_mode_controls(notebook=notebook, advanced_tab=audio_tab, mode_text_var=simple_mode_text)


def apply_ui_mode():
    if ui_controller is None:
        return
    ui_controller.apply_mode()


def toggle_ui_mode():
    if ui_controller is None:
        return
    ui_controller.toggle_mode()


ttk.Button(mode_strip, textvariable=simple_mode_text, command=toggle_ui_mode, style="Soft.TButton").pack(
    side="right"
)

# Если пользователь еще не сохранял устройства, фиксируем автоматически лучшие кандидаты.
if int(settings.get("microphone_id", -1)) < 0 or int(settings.get("output_id", -1)) < 0:
    selected_mic_auto = next((opt for opt in mic_options if opt["label"] == mic_var.get()), None)
    selected_out_auto = next((opt for opt in output_options if opt["label"] == out_var.get()), None)
    if selected_mic_auto:
        settings["microphone_id"] = selected_mic_auto["id"]
        settings["microphone_name"] = selected_mic_auto["name"]
    if selected_out_auto:
        settings["output_id"] = selected_out_auto["id"]
        settings["output_name"] = selected_out_auto["name"]
    if selected_mic_auto or selected_out_auto:
        save_settings()
        restart_listen_event.set()

row1 = ttk.Frame(settings_box, style="Panel.TFrame")
row1.pack(fill="x", pady=(0, 8))

row2 = ttk.Frame(settings_box, style="Panel.TFrame")
row2.pack(fill="x", pady=(0, 8))

row3 = ttk.Frame(settings_box, style="Panel.TFrame")
row3.pack(fill="x")

ttk.Label(row1, text="Микрофон:", style="PanelLabel.TLabel").pack(side="left")
mic_combo = ttk.Combobox(row1, state="readonly", width=44, values=mic_labels, textvariable=mic_var)
mic_combo.pack(side="left", padx=(6, 6))

ttk.Label(row1, text="Вывод:", style="PanelLabel.TLabel").pack(side="left")
out_combo = ttk.Combobox(row1, state="readonly", width=30, values=output_labels, textvariable=out_var)
out_combo.pack(side="left", padx=(6, 6))


def refresh_mics():
    global mic_options, output_options
    mic_options, output_options = get_device_options(force_refresh=True)
    mic_labels_local = [opt["label"] for opt in mic_options]
    out_labels_local = [opt["label"] for opt in output_options]

    mic_combo.configure(values=mic_labels_local)
    out_combo.configure(values=out_labels_local)

    preferred_out_name = ""
    if out_labels_local:
        if out_var.get() not in out_labels_local:
            out_var.set(out_labels_local[0])
        selected_out = next((opt for opt in output_options if opt["label"] == out_var.get()), None)
        if selected_out:
            preferred_out_name = selected_out["name"]
    else:
        out_var.set("")

    if mic_labels_local:
        if mic_var.get() not in mic_labels_local:
            ordered_mics = sort_device_options(
                mic_options,
                kind="input",
                preferred_output_name=preferred_out_name,
            )
            mic_var.set((ordered_mics[0]["label"] if ordered_mics else mic_labels_local[0]))
    else:
        mic_var.set("")

    set_status(f"Устройства обновлены: Mic {len(mic_labels_local)}, Out {len(out_labels_local)}")



def apply_audio_settings():
    selected_mic_label = mic_var.get().strip()
    selected_mic = next((opt for opt in mic_options if opt["label"] == selected_mic_label), None)
    if selected_mic:
        settings["microphone_name"] = selected_mic["name"]
        settings["microphone_id"] = selected_mic["id"]
    else:
        settings["microphone_name"] = ""
        settings["microphone_id"] = -1

    selected_out_label = out_var.get().strip()
    selected_out = next((opt for opt in output_options if opt["label"] == selected_out_label), None)
    if selected_out:
        settings["output_name"] = selected_out["name"]
        settings["output_id"] = selected_out["id"]
    else:
        settings["output_name"] = ""
        settings["output_id"] = -1

    settings["dynamic_energy"] = bool(dynamic_var.get())
    settings["energy_threshold"] = int(energy_var.get())
    settings["fuzzy_threshold"] = round(float(fuzzy_var.get()), 2)
    settings["mic_gain"] = round(float(gain_var.get()), 2)
    settings["monitor_gain"] = round(float(monitor_gain_var.get()), 2)
    save_settings()
    restart_listen_event.set()
    set_status("Настройки аудио сохранены")



ttk.Button(row2, text="Обновить устройства", command=refresh_mics, style="Soft.TButton").pack(side="left")
ttk.Button(row2, text="Проверка микрофона", command=check_microphone, style="Soft.TButton").pack(side="left", padx=6)
ttk.Button(row2, textvariable=monitor_button_text, command=toggle_monitoring, style="Soft.TButton").pack(side="left", padx=6)
ttk.Button(row2, text="Сохранить аудио", command=apply_audio_settings, style="Primary.TButton").pack(side="left")


ttk.Checkbutton(
    row3,
    text="Авто-порог",
    variable=dynamic_var,
    onvalue=True,
    offvalue=False,
    style="Futuristic.TCheckbutton",
).pack(side="left")

ttk.Label(row3, text="Порог:", style="PanelLabel.TLabel").pack(side="left", padx=(10, 4))
energy_scale = ttk.Scale(row3, from_=40, to=800, variable=energy_var, orient="horizontal", length=170)
energy_scale.pack(side="left")
energy_label = ttk.Label(row3, textvariable=energy_var, style="PanelLabel.TLabel", width=4)
energy_label.pack(side="left", padx=(4, 10))

ttk.Label(row3, text="Точность:", style="PanelLabel.TLabel").pack(side="left", padx=(8, 4))
fuzzy_scale = ttk.Scale(row3, from_=0.55, to=0.98, variable=fuzzy_var, orient="horizontal", length=150)
fuzzy_scale.pack(side="left")
fuzzy_label = ttk.Label(row3, text="", style="PanelLabel.TLabel", width=4)
fuzzy_label.pack(side="left", padx=(4, 0))

ttk.Label(row3, text="Mic Gain:", style="PanelLabel.TLabel").pack(side="left", padx=(10, 4))
gain_scale = ttk.Scale(row3, from_=1.0, to=4.0, variable=gain_var, orient="horizontal", length=120)
gain_scale.pack(side="left")
gain_label = ttk.Label(row3, text="", style="PanelLabel.TLabel", width=4)
gain_label.pack(side="left", padx=(4, 0))

ttk.Label(row3, text="Monitor Gain:", style="PanelLabel.TLabel").pack(side="left", padx=(10, 4))
monitor_gain_scale = ttk.Scale(row3, from_=0.8, to=2.5, variable=monitor_gain_var, orient="horizontal", length=115)
monitor_gain_scale.pack(side="left")
monitor_gain_label = ttk.Label(row3, text="", style="PanelLabel.TLabel", width=4)
monitor_gain_label.pack(side="left", padx=(4, 0))


def update_fuzzy_label(*_args):
    fuzzy_label.configure(text=f"{float(fuzzy_var.get()):.2f}")


fuzzy_var.trace_add("write", update_fuzzy_label)
update_fuzzy_label()


def update_gain_label(*_args):
    gain_label.configure(text=f"{float(gain_var.get()):.1f}x")


gain_var.trace_add("write", update_gain_label)
update_gain_label()


def update_monitor_gain_label(*_args):
    monitor_gain_label.configure(text=f"{float(monitor_gain_var.get()):.1f}x")


monitor_gain_var.trace_add("write", update_monitor_gain_label)
update_monitor_gain_label()

diagnostics_box = ttk.Frame(audio_tab, style="Panel.TFrame", padding=12)
diagnostics_box.pack(fill="both", expand=True, pady=(6, 0))
ttk.Label(diagnostics_box, text="Последние события", style="PanelLabel.TLabel").pack(anchor="w", pady=(0, 6))
events_list = tk.Listbox(
    diagnostics_box,
    height=10,
    bg=PALETTE["card"],
    fg=PALETTE["text"],
    selectbackground=PALETTE["accent_deep"],
    selectforeground=PALETTE["text"],
    borderwidth=1,
    relief="solid",
)
events_list.pack(fill="both", expand=True)


def refresh_events_panel():
    if ui_controller is None:
        return
    ui_controller.refresh_events_panel()


ttk.Button(diagnostics_box, text="Обновить события", command=refresh_events_panel, style="Soft.TButton").pack(
    anchor="e", pady=(6, 0)
)
apply_ui_mode()

toolbar = ttk.Frame(commands_tab, style="Card.TFrame")
toolbar.pack(fill="x", pady=(2, 10), padx=6)

ttk.Button(toolbar, text="Добавить вручную", command=add_file_manual, style="Primary.TButton").pack(side="left")
ttk.Button(toolbar, text="Добавить голосом", command=open_voice_capture_dialog, style="Soft.TButton").pack(side="left", padx=8)
ttk.Button(toolbar, text="Проверить", command=test_selected, style="Soft.TButton").pack(side="left")
ttk.Button(toolbar, text="Проверить микрофон", command=check_microphone, style="Soft.TButton").pack(side="left", padx=(8, 0))
ttk.Button(toolbar, text="Тест распознавания", command=test_recognition_once, style="Soft.TButton").pack(side="left", padx=(8, 0))
ttk.Button(toolbar, text="Открыть логи", command=open_logs_folder, style="Soft.TButton").pack(side="left", padx=(8, 0))
ttk.Button(toolbar, text="Экспорт профиля", command=export_profile_dialog, style="Soft.TButton").pack(side="left", padx=(8, 0))
ttk.Button(toolbar, text="Импорт профиля", command=import_profile_dialog, style="Soft.TButton").pack(side="left", padx=(8, 0))
ttk.Button(toolbar, text="Диагностика", command=collect_diagnostics_dialog, style="Soft.TButton").pack(side="left", padx=(8, 0))
ttk.Button(toolbar, text="Удалить", command=remove_selected, style="Danger.TButton").pack(side="right", padx=(8, 0))

table_wrap = ttk.Frame(commands_tab, style="Panel.TFrame", padding=6)
table_wrap.pack(fill="both", expand=True)

tree = ttk.Treeview(
    table_wrap,
    columns=("phrase", "path", "mode"),
    show="headings",
    height=14,
    style="Custom.Treeview",
)
tree.heading("phrase", text="Ключевая фраза")
tree.heading("path", text="Файл")
tree.heading("mode", text="Режим запуска")
tree.column("phrase", width=330, anchor="w", stretch=False)
tree.column("path", width=590, anchor="w", stretch=False)
tree.column("mode", width=250, anchor="w", stretch=False)
tree.pack(side="left", fill="both", expand=True)

scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=tree.yview)
scroll.pack(side="right", fill="y")
tree.configure(yscrollcommand=scroll.set)


def fit_tree_columns(_event=None):
    # Держим колонки ровными и читаемыми на любом размере окна.
    total = table_wrap.winfo_width() - scroll.winfo_width() - 14
    if total < 720:
        total = 720

    phrase_w = max(260, int(total * 0.28))
    mode_w = max(250, int(total * 0.22))
    path_w = max(260, total - phrase_w - mode_w)

    tree.column("phrase", width=phrase_w)
    tree.column("path", width=path_w)
    tree.column("mode", width=mode_w)


table_wrap.bind("<Configure>", fit_tree_columns)

status_var = tk.StringVar(value="Готово")
status = ttk.Label(card, textvariable=status_var, style="Status.TLabel", anchor="w")
status.pack(fill="x", pady=(10, 0))
asr_status_var = tk.StringVar(value=f"ASR: {asr_engine().capitalize()}")
ttk.Label(card, textvariable=asr_status_var, style="Sub.TLabel", anchor="w").pack(fill="x", pady=(4, 0))

hint = ttk.Label(
    card,
    text="Режим ASR: Whisper (точнее). Проверка микрофона покажет уровень и распознанный текст.",
    style="Sub.TLabel",
    anchor="w",
)
hint.pack(fill="x", pady=(6, 0))

last_phrase_var = tk.StringVar(value="Последняя фраза: —")
last_action_var = tk.StringVar(value="Последнее действие: —")
ttk.Label(card, textvariable=last_phrase_var, style="Sub.TLabel", anchor="w").pack(fill="x", pady=(4, 0))
ttk.Label(card, textvariable=last_action_var, style="Sub.TLabel", anchor="w").pack(fill="x", pady=(2, 0))
if ui_controller is not None:
    ui_controller.bind_history_widgets(
        events_listbox=events_list,
        last_phrase_var=last_phrase_var,
        last_action_var=last_action_var,
    )


def animate_window_fade(alpha=0.0):
    if alpha >= 1.0:
        root.attributes("-alpha", 1.0)
        return
    root.attributes("-alpha", alpha)
    root.after(18, animate_window_fade, alpha + 0.07)


def animate_tab_glow(step=0):
    colors = list(premium_glow_colors())
    width = max(20, tab_glow.winfo_width())
    pulse = 0.20 + 0.70 * (step / max(1, len(colors) - 1))
    tab_glow.coords(tab_glow_rect, 0, 0, int(width * pulse), 4)
    tab_glow.itemconfigure(tab_glow_rect, fill=colors[min(step, len(colors) - 1)])
    if step < len(colors) - 1:
        root.after(22, animate_tab_glow, step + 1)


def on_tab_changed(_event=None):
    active = notebook.tab(notebook.select(), "text")
    set_status(f"Открыта вкладка: {active}")
    animate_tab_glow(0)


notebook.bind("<<NotebookTabChanged>>", on_tab_changed)


def on_hero_resize(event):
    if event.widget is hero:
        paint_hero_gradient(hero)


hero.bind("<Configure>", on_hero_resize)

root.protocol("WM_DELETE_WINDOW", on_closing)

load_commands()
refresh_table()
log_runtime(f"UI ready. Commands in table: {len(commands)}")
log_asr("ASR log initialized")
write_session_snapshot("startup_ui_ready")

threading.Thread(target=listen_loop, daemon=True).start()
create_tray_icon()
warmup_asr_async()
log_runtime("Background services started: listener + tray + warmup")

root.after(40, animate_window_fade)
root.after(80, animate_tab_glow, 0)
root.after(120, fit_tree_columns)

log_runtime("Entering Tk mainloop")
root.mainloop()

