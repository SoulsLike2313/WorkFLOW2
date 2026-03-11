from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, Optional


@dataclass
class UiControllerDeps:
    root: Any
    settings: dict
    save_settings: Callable[[], None]
    set_status: Callable[[str], None]
    heard_history: List[str]
    action_history: List[str]


class UiController:
    def __init__(self, deps: UiControllerDeps):
        self.deps = deps
        self.notebook = None
        self.advanced_tab = None
        self.mode_text_var = None
        self.events_listbox = None
        self.last_phrase_var = None
        self.last_action_var = None

    def bind_mode_controls(self, notebook, advanced_tab, mode_text_var) -> None:
        self.notebook = notebook
        self.advanced_tab = advanced_tab
        self.mode_text_var = mode_text_var

    def bind_history_widgets(self, events_listbox=None, last_phrase_var=None, last_action_var=None) -> None:
        self.events_listbox = events_listbox
        self.last_phrase_var = last_phrase_var
        self.last_action_var = last_action_var

    def _run_on_ui(self, fn: Callable[[], None]) -> None:
        try:
            self.deps.root.after(0, fn)
        except Exception:
            fn()

    @staticmethod
    def _push_history(buffer: List[str], value: str, limit: int = 30) -> None:
        text = str(value or "").strip()
        if not text:
            return
        buffer.append(text)
        if len(buffer) > limit:
            del buffer[:-limit]

    def apply_mode(self) -> None:
        simple_mode = bool(self.deps.settings.get("simple_mode", True))
        if simple_mode:
            try:
                self.notebook.hide(self.advanced_tab)
            except Exception:
                pass
            if self.mode_text_var is not None:
                self.mode_text_var.set("Режим: Простой (переключить на расширенный)")
        else:
            try:
                self.notebook.add(self.advanced_tab, text="Расширенный")
            except Exception:
                pass
            if self.mode_text_var is not None:
                self.mode_text_var.set("Режим: Расширенный (переключить на простой)")

    def toggle_mode(self) -> None:
        self.deps.settings["simple_mode"] = not bool(self.deps.settings.get("simple_mode", True))
        self.deps.save_settings()
        self.apply_mode()
        self.deps.set_status("Режим интерфейса сохранен")

    def refresh_events_panel(self) -> None:
        if self.events_listbox is None:
            return
        try:
            self.events_listbox.delete(0, "end")
            for phrase in self.deps.heard_history[-8:]:
                self.events_listbox.insert("end", f"Фраза: {phrase}")
            for action in self.deps.action_history[-8:]:
                self.events_listbox.insert("end", f"Действие: {action}")
        except Exception:
            pass

    def push_last_phrase(self, text: str) -> None:
        self._push_history(self.deps.heard_history, text, limit=30)
        if self.last_phrase_var is not None:
            self._run_on_ui(lambda: self.last_phrase_var.set(f"Последняя фраза: {text}"))
        self._run_on_ui(self.refresh_events_panel)

    def push_last_action(self, text: str) -> None:
        self._push_history(self.deps.action_history, text, limit=30)
        if self.last_action_var is not None:
            self._run_on_ui(lambda: self.last_action_var.set(f"Последнее действие: {text}"))
        self._run_on_ui(self.refresh_events_panel)
