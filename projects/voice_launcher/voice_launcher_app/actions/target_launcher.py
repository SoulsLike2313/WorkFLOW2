from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class TargetLauncherState:
    last_path: str = ""
    last_time: float = 0.0


@dataclass
class TargetLauncherDeps:
    path_exists: Callable[[str], bool]
    status: Callable[[str], None]
    last_action: Callable[[str], None]
    runtime_log: Callable[[str], None]
    time_now: Callable[[], float] = time.time
    platform_name: str = os.name
    os_startfile: Optional[Callable[[str], None]] = getattr(os, "startfile", None)
    popen: Callable[[list[str]], subprocess.Popen] = subprocess.Popen


class TargetLauncher:
    def __init__(self, deps: TargetLauncherDeps, state: Optional[TargetLauncherState] = None):
        self.deps = deps
        self.state = state or TargetLauncherState()

    def launch_target(self, path: str, duplicate_guard_seconds: float = 1.0) -> bool:
        now = self.deps.time_now()
        if (
            duplicate_guard_seconds > 0
            and now - float(self.state.last_time) < float(duplicate_guard_seconds)
            and path == self.state.last_path
        ):
            self.deps.runtime_log(f"Launch skipped by duplicate-guard: {path}")
            return False

        if not self.deps.path_exists(path):
            self.deps.status("Файл не найден")
            self.deps.runtime_log(f"Launch failed (missing path): {path}")
            return False

        try:
            if self.deps.platform_name == "nt" and self.deps.os_startfile is not None:
                self.deps.os_startfile(path)  # noqa: S606,S607
            else:
                self.deps.popen([path])  # noqa: S603

            self.state.last_time = now
            self.state.last_path = path
            file_name = os.path.basename(path)
            self.deps.status(f"Запущено: {file_name}")
            self.deps.last_action(f"Запущено: {file_name}")
            self.deps.runtime_log(f"Launch target started: {path}")
            return True
        except Exception as exc:
            self.deps.status(f"Ошибка запуска: {exc}")
            self.deps.last_action(f"Ошибка запуска: {exc}")
            self.deps.runtime_log(f"Launch target error: {path} | {exc}")
            return False
