from __future__ import annotations

import os
import threading
import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog, messagebox, ttk
from typing import Any, Callable, Dict, Sequence


def build_launcher_preview(
    *,
    path: str,
    play_text: str,
    window_title: str,
    wait_timeout: int,
    post_launch_cooldown: int = 110,
    highlight: bool,
    min_window_confidence: float,
) -> Dict[str, Any]:
    return {
        "mode": "launcher_play",
        "path": str(path or "").strip(),
        "play_text": str(play_text or "Играть").strip() or "Играть",
        "window_title": str(window_title or "").strip(),
        "wait_timeout": int(wait_timeout or 240),
        "post_launch_cooldown": int(post_launch_cooldown or 110),
        "launcher_dry_run": True,
        "launcher_highlight": bool(highlight),
        "min_window_confidence": float(min_window_confidence or 0.90),
    }


@dataclass
class CommandWizardDeps:
    root: Any
    card_color: str
    monitor_active_event: Any
    pause_listen_event: Any
    build_recognizer: Callable[[], Any]
    get_selected_mic_index: Callable[[], int | None]
    microphone_factory: Callable[..., Any]
    wait_timeout_error: type[BaseException]
    voice_capture_timeout: int
    settings_provider: Callable[[], Dict[str, Any]]
    get_audio_level_percent: Callable[[Any], int]
    recognize_candidates: Callable[..., Sequence[str]]
    save_mapping: Callable[..., bool]
    launch_with_launcher_play: Callable[[dict], None]
    path_exists: Callable[[str], bool]


def open_command_wizard(deps: CommandWizardDeps) -> None:
    dialog = tk.Toplevel(deps.root)
    dialog.title("Мастер добавления команды")
    dialog.geometry("700x500")
    dialog.minsize(640, 440)
    dialog.configure(bg=deps.card_color)
    dialog.transient(deps.root)
    dialog.grab_set()

    path_var = tk.StringVar(value="")
    phrase_var = tk.StringVar(value="")
    admin_var = tk.BooleanVar(value=False)
    launcher_play_var = tk.BooleanVar(value=False)
    play_text_var = tk.StringVar(value="Играть")
    window_title_var = tk.StringVar(value="")
    wait_timeout_var = tk.IntVar(value=240)
    post_launch_cooldown_var = tk.IntVar(value=110)
    dry_run_var = tk.BooleanVar(value=False)
    highlight_var = tk.BooleanVar(value=False)
    min_confidence_var = tk.DoubleVar(value=0.90)
    status_local = tk.StringVar(value="1) Выберите файл  2) Запишите фразу")
    candidates_var = tk.StringVar(value=[])

    body = ttk.Frame(dialog, style="Card.TFrame", padding=12)
    body.pack(fill="both", expand=True)

    ttk.Label(body, text="Шаг 1/5. Выберите файл", style="Sub.TLabel").pack(anchor="w")
    row = ttk.Frame(body, style="Card.TFrame")
    row.pack(fill="x", pady=(2, 8))
    ttk.Entry(row, textvariable=path_var).pack(side="left", fill="x", expand=True)

    def choose_file():
        path = filedialog.askopenfilename(title="Выберите файл", parent=dialog)
        if path:
            path_var.set(path)

    ttk.Button(row, text="Выбрать", command=choose_file, style="Soft.TButton").pack(side="left", padx=(8, 0))

    ttk.Label(body, text="Шаг 2/5. Введите или запишите ключевую фразу", style="Sub.TLabel").pack(anchor="w")
    ttk.Entry(body, textvariable=phrase_var).pack(fill="x", pady=(2, 8))

    ttk.Label(body, text="Варианты распознавания", style="Sub.TLabel").pack(anchor="w")
    options = ttk.Combobox(body, textvariable=candidates_var, state="readonly")
    options.pack(fill="x", pady=(2, 8))

    def on_pick(_event=None):
        value = options.get().strip()
        if value:
            phrase_var.set(value)

    options.bind("<<ComboboxSelected>>", on_pick)

    ttk.Label(body, text="Шаг 3/5. Выберите тип действия", style="Sub.TLabel").pack(anchor="w", pady=(4, 4))
    ttk.Checkbutton(
        body,
        text="Запускать как админ (через Планировщик задач)",
        variable=admin_var,
        onvalue=True,
        offvalue=False,
    ).pack(anchor="w", pady=(0, 8))

    launcher_row = ttk.Frame(body, style="Card.TFrame")
    launcher_row.pack(fill="x", pady=(0, 4))
    ttk.Checkbutton(
        launcher_row,
        text="Режим лаунчера: автонажатие кнопки",
        variable=launcher_play_var,
        onvalue=True,
        offvalue=False,
    ).pack(side="left")

    launcher_details = ttk.Frame(body, style="Card.TFrame")
    ttk.Label(launcher_details, text="Шаг 4/5. Настройка launcher_play", style="Sub.TLabel").pack(anchor="w")
    ttk.Label(launcher_details, text="Текст кнопки:", style="Sub.TLabel").pack(anchor="w")
    ttk.Entry(launcher_details, textvariable=play_text_var).pack(fill="x", pady=(2, 6))
    ttk.Label(launcher_details, text="Фильтр окна (необязательно):", style="Sub.TLabel").pack(anchor="w")
    ttk.Entry(launcher_details, textvariable=window_title_var).pack(fill="x", pady=(2, 6))

    wait_row = ttk.Frame(launcher_details, style="Card.TFrame")
    wait_row.pack(fill="x", pady=(0, 8))
    ttk.Label(wait_row, text="Ожидание кнопки (сек):", style="Sub.TLabel").pack(side="left")
    ttk.Spinbox(wait_row, from_=30, to=900, textvariable=wait_timeout_var, width=8).pack(side="left", padx=(8, 0))
    ttk.Label(wait_row, text="Пауза после старта (сек):", style="Sub.TLabel").pack(side="left", padx=(12, 4))
    ttk.Spinbox(wait_row, from_=5, to=900, textvariable=post_launch_cooldown_var, width=8).pack(side="left")

    safety_row = ttk.Frame(launcher_details, style="Card.TFrame")
    safety_row.pack(fill="x", pady=(0, 8))
    ttk.Checkbutton(
        safety_row,
        text="Dry-run (без клика)",
        variable=dry_run_var,
        onvalue=True,
        offvalue=False,
    ).pack(side="left")
    ttk.Checkbutton(
        safety_row,
        text="Только подсветка",
        variable=highlight_var,
        onvalue=True,
        offvalue=False,
    ).pack(side="left", padx=(10, 0))
    ttk.Label(safety_row, text="Уверенность окна:", style="Sub.TLabel").pack(side="left", padx=(14, 4))
    ttk.Spinbox(
        safety_row,
        from_=0.65,
        to=0.99,
        increment=0.01,
        textvariable=min_confidence_var,
        width=6,
    ).pack(side="left")

    def sync_mode(*_args):
        if admin_var.get() and launcher_play_var.get():
            launcher_play_var.set(False)
        if admin_var.get():
            status_local.set("Админ-режим: автонажатие лаунчера отключено")
        elif launcher_play_var.get():
            launcher_details.pack(fill="x", pady=(0, 8))
            status_local.set("Режим лаунчера: безопасная верификация окна и кнопки")
        else:
            launcher_details.pack_forget()
            status_local.set("1) Выберите файл  2) Запишите фразу")

    admin_var.trace_add("write", sync_mode)
    launcher_play_var.trace_add("write", sync_mode)
    sync_mode()

    ttk.Label(body, text="Шаг 5/5. Тест и сохранение", style="Sub.TLabel").pack(anchor="w", pady=(4, 2))
    ttk.Label(body, textvariable=status_local, style="Sub.TLabel").pack(anchor="w", pady=(0, 10))

    controls = ttk.Frame(body, style="Card.TFrame")
    controls.pack(fill="x")

    def do_record():
        def ui(text):
            dialog.after(0, lambda: status_local.set(text))

        if deps.monitor_active_event.is_set():
            ui("Сначала выключите мониторинг")
            return

        deps.pause_listen_event.set()
        try:
            ui("Подготовка микрофона... 1 сек тишины")
            recognizer = deps.build_recognizer()
            recognizer.pause_threshold = 1.0
            recognizer.non_speaking_duration = 0.45
            mic_index = deps.get_selected_mic_index()
            with deps.microphone_factory(device_index=mic_index) as source:
                recognizer.adjust_for_ambient_noise(source, duration=1.0)
                ui("Слушаю... произнесите фразу четко один раз")
                settings = deps.settings_provider() or {}
                audio = recognizer.listen(
                    source,
                    timeout=deps.voice_capture_timeout,
                    phrase_time_limit=max(5.2, float(settings.get("listen_phrase_limit", 5.0))),
                )

            level = deps.get_audio_level_percent(audio)
            candidates = list(
                deps.recognize_candidates(recognizer, audio, prefer_all_engines=True) or []
            )
            if not candidates:
                ui(f"Не распознано. Уровень сигнала: {level}%. Повторите запись.")
                return

            candidates = candidates[:8]
            dialog.after(0, lambda: options.configure(values=candidates))
            dialog.after(0, lambda: options.set(candidates[0]))
            dialog.after(0, lambda: phrase_var.set(candidates[0]))
            ui(f"Фраза записана. Уровень сигнала: {level}%")
        except deps.wait_timeout_error:
            ui("Тишина. Нажмите 'Записать' еще раз.")
        except Exception as exc:
            ui(f"Ошибка записи: {exc}")
        finally:
            deps.pause_listen_event.clear()

    def start_record():
        threading.Thread(target=do_record, daemon=True).start()

    def save_voice_mapping():
        path = path_var.get().strip()
        phrase = phrase_var.get().strip()
        if not path:
            messagebox.showinfo("Файл", "Выберите файл.", parent=dialog)
            return
        if not phrase:
            messagebox.showinfo("Фраза", "Сначала запишите или введите фразу.", parent=dialog)
            return
        saved = deps.save_mapping(
            phrase,
            path,
            use_admin=bool(admin_var.get()),
            launcher_play=bool(launcher_play_var.get()),
            play_text=play_text_var.get().strip() or "Играть",
            window_title=window_title_var.get().strip(),
            wait_timeout=int(wait_timeout_var.get() or 240),
            post_launch_cooldown=int(post_launch_cooldown_var.get() or 110),
            launcher_dry_run=bool(dry_run_var.get()),
            launcher_highlight=bool(highlight_var.get()),
            min_window_confidence=float(min_confidence_var.get() or 0.90),
        )
        if saved:
            dialog.destroy()

    def safe_preview():
        preview_entry = build_launcher_preview(
            path=path_var.get().strip(),
            play_text=play_text_var.get().strip() or "Играть",
            window_title=window_title_var.get().strip(),
            wait_timeout=int(wait_timeout_var.get() or 240),
            post_launch_cooldown=int(post_launch_cooldown_var.get() or 110),
            highlight=bool(highlight_var.get()),
            min_window_confidence=float(min_confidence_var.get() or 0.90),
        )
        if not preview_entry["path"]:
            messagebox.showwarning("Безопасный тест", "Сначала выберите файл.", parent=dialog)
            return
        if not deps.path_exists(preview_entry["path"]):
            messagebox.showwarning("Безопасный тест", "Указанный файл не найден.", parent=dialog)
            return
        deps.launch_with_launcher_play(preview_entry)
        status_local.set("Запущен безопасный тест launcher_play (без клика)")

    ttk.Button(controls, text="Записать", command=start_record, style="Primary.TButton").pack(side="left")
    ttk.Button(controls, text="Безопасный тест", command=safe_preview, style="Soft.TButton").pack(side="left", padx=8)
    ttk.Button(controls, text="Сохранить", command=save_voice_mapping, style="Soft.TButton").pack(side="left", padx=8)
    ttk.Button(controls, text="Отмена", command=dialog.destroy, style="Soft.TButton").pack(side="right")
