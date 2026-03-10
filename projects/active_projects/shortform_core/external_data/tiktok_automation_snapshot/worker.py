from __future__ import annotations

import asyncio
import threading
import traceback

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
