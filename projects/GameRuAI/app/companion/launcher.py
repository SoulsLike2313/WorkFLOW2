from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from .process_monitor import ProcessMonitor
from .session_registry import CompanionSession, SessionRegistry


class CompanionLauncher:
    def __init__(self, session_registry: SessionRegistry, process_monitor: ProcessMonitor):
        self.session_registry = session_registry
        self.process_monitor = process_monitor

    def launch(
        self,
        *,
        project_id: int,
        executable_path: Path,
        watched_path: Path,
        args: list[str] | None = None,
        cwd: Path | None = None,
    ) -> CompanionSession:
        command = [str(executable_path)] + (args or [])
        process = subprocess.Popen(
            command,
            cwd=str(cwd) if cwd else str(executable_path.parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        session = self.session_registry.create(
            project_id=project_id,
            executable_path=str(executable_path),
            watched_path=str(watched_path),
            process_status="running",
            process_pid=process.pid,
        )
        self.process_monitor.register(session.session_id, process)
        return session
