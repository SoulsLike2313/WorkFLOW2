from __future__ import annotations

import asyncio
import os
import subprocess
import threading
import traceback
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from automation_engine import TikTokAutomationEngine
from settings import BotSettings


class BotWorker(QThread):
    log_signal = Signal(str)
    done_signal = Signal(bool, str)

    def __init__(self, settings: BotSettings):
        super().__init__()
        self.settings = settings
        self.stop_event = threading.Event()

    def run(self) -> None:
        try:
            engine = TikTokAutomationEngine(self.settings, self.stop_event, self._emit_log)
            asyncio.run(engine.run())
            self.done_signal.emit(True, "Сценарий завершен.")
        except Exception as error:
            details = "".join(traceback.format_exception(error))
            self.done_signal.emit(False, details)

    def stop(self) -> None:
        self.stop_event.set()

    def _emit_log(self, message: str) -> None:
        self.log_signal.emit(message)


class CoreWorker(QThread):
    log_signal = Signal(str)
    done_signal = Signal(bool, str)

    def __init__(self, core_root: Path, action: str, snapshot_dir: Path | None = None):
        super().__init__()
        self.core_root = Path(core_root)
        self.action = action
        self.snapshot_dir = Path(snapshot_dir) if snapshot_dir else None

    def run(self) -> None:
        try:
            python_exe = self.core_root / ".venv" / "Scripts" / "python.exe"
            if not python_exe.exists():
                self.done_signal.emit(
                    False,
                    (
                        "Core venv не найден. Сначала выполни setup:\n"
                        f"powershell -ExecutionPolicy Bypass -File {self.core_root / 'run_setup.ps1'}"
                    ),
                )
                return

            command = [str(python_exe), "-m", "app.main"]
            if self.action == "bootstrap":
                command = [str(python_exe), "-m", "app.bootstrap_v2"]

            env = os.environ.copy()
            if self.snapshot_dir:
                env["SFCO_TIKTOK_SNAPSHOT_DIR"] = str(self.snapshot_dir)

            self.log_signal.emit(f"[CORE] действие={self.action} cwd={self.core_root}")
            if self.snapshot_dir:
                self.log_signal.emit(f"[CORE] snapshot_dir={self.snapshot_dir}")

            process = subprocess.Popen(
                command,
                cwd=str(self.core_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
            assert process.stdout is not None
            for line in process.stdout:
                text = line.rstrip()
                if text:
                    self.log_signal.emit(text)
            return_code = process.wait()
            if return_code != 0:
                self.done_signal.emit(False, f"Core-команда завершилась с кодом {return_code}")
                return

            self.done_signal.emit(True, "Core-команда выполнена успешно.")
        except Exception as error:
            details = "".join(traceback.format_exception(error))
            self.done_signal.emit(False, details)

