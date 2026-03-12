from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from .config import AppConfig, load_config
from .readiness import ReadinessService
from .workspace.diagnostics import configure_diagnostics, diag_log
from .workspace.runtime import WorkspaceRuntime, build_workspace_runtime


@dataclass
class StartupContext:
    config: AppConfig
    workspace_runtime: WorkspaceRuntime
    readiness: dict[str, Any]


class StartupManager:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()
        self.readiness_service = ReadinessService()
        self._backend_proc: subprocess.Popen[str] | None = None

    def initialize_local_runtime(self) -> StartupContext:
        configure_diagnostics(self.config.storage.logs_dir, debug=self.config.workspace.debug_logs)
        runtime = build_workspace_runtime(
            max_profiles=self.config.workspace.max_profiles,
            analytics_weights=self.config.workspace.analytics_weights.model_dump(),
            log_dir=self.config.storage.logs_dir,
            debug_logs=self.config.workspace.debug_logs,
            persistence_path=self.config.storage.workspace_state_path,
        )
        readiness = self.readiness_service.evaluate_local(config=self.config, workspace_runtime=runtime)
        diag_log("runtime_logs", "startup_initialized", payload={"mode": self.config.mode, "readiness": readiness})
        return StartupContext(config=self.config, workspace_runtime=runtime, readiness=readiness)

    def start_internal_backend(self, *, host: str | None = None, port: int | None = None) -> int:
        bind_host = host or self.config.api_host
        bind_port = int(port or self.config.api_port)
        env = os.environ.copy()
        env["SFCO_MODE"] = "user"
        env["SFCO_API_HOST"] = bind_host
        env["SFCO_API_PORT"] = str(bind_port)
        env["SFCO_LOGS_DIR"] = str(self.config.storage.logs_dir)
        env["SFCO_WORKSPACE_STATE_PATH"] = str(self.config.storage.workspace_state_path)
        env["SFCO_DATABASE_PATH"] = str(self.config.storage.database_path)

        creation_flags = 0
        if os.name == "nt":
            creation_flags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]

        self._backend_proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.api:app",
                "--host",
                bind_host,
                "--port",
                str(bind_port),
            ],
            cwd=self.config.storage.project_root,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            creationflags=creation_flags,
        )
        diag_log("runtime_logs", "internal_backend_started", payload={"pid": self._backend_proc.pid, "host": bind_host, "port": bind_port})
        return int(self._backend_proc.pid or 0)

    def wait_backend_ready(self, *, timeout_seconds: float = 25.0) -> bool:
        base = f"http://{self.config.api_host}:{self.config.api_port}"
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            try:
                with httpx.Client(timeout=2.0) as client:
                    response = client.get(f"{base}/workspace/health")
                if response.status_code == 200:
                    diag_log("runtime_logs", "internal_backend_ready", payload={"base_url": base})
                    return True
            except Exception:
                time.sleep(0.4)
        diag_log("runtime_logs", "internal_backend_not_ready", level="ERROR", payload={"base_url": base})
        return False

    def stop_internal_backend(self) -> None:
        if self._backend_proc is None:
            return
        if self._backend_proc.poll() is None:
            self._backend_proc.terminate()
            try:
                self._backend_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._backend_proc.kill()
        diag_log("shutdown_logs", "internal_backend_stopped", payload={"returncode": self._backend_proc.returncode})
        self._backend_proc = None

