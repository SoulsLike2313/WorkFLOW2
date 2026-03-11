from __future__ import annotations

import subprocess
from typing import Any


class ProcessMonitor:
    def __init__(self):
        self._processes: dict[str, subprocess.Popen[Any]] = {}

    def register(self, session_id: str, process: subprocess.Popen[Any]) -> None:
        self._processes[session_id] = process

    def pid(self, session_id: str) -> int | None:
        process = self._processes.get(session_id)
        return process.pid if process else None

    def status(self, session_id: str) -> str:
        process = self._processes.get(session_id)
        if not process:
            return "unknown"
        code = process.poll()
        if code is None:
            return "running"
        return f"exited({code})"

    def stop(self, session_id: str) -> str:
        process = self._processes.get(session_id)
        if not process:
            return "not_found"
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except Exception:
                process.kill()
                process.wait(timeout=5)
        return f"stopped({process.returncode})"

    def unregister(self, session_id: str) -> None:
        self._processes.pop(session_id, None)
