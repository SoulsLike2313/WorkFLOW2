from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
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


@dataclass
class BackendProbeResult:
    ready: bool
    failure_reason: str
    recovery_signal: str
    base_url: str
    health_endpoint: str
    endpoint_statuses: dict[str, Any]
    attempts: list[dict[str, Any]]
    process_exit_detected: bool
    process_exit_code: int | None
    duration_seconds: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "ready": self.ready,
            "failure_reason": self.failure_reason,
            "recovery_signal": self.recovery_signal,
            "base_url": self.base_url,
            "health_endpoint": self.health_endpoint,
            "endpoint_statuses": self.endpoint_statuses,
            "attempts": self.attempts,
            "process_exit_detected": self.process_exit_detected,
            "process_exit_code": self.process_exit_code,
            "duration_seconds": self.duration_seconds,
        }


class StartupManager:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()
        self.readiness_service = ReadinessService()
        self._backend_proc: subprocess.Popen[str] | None = None
        self._last_backend_probe: BackendProbeResult | None = None

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

    def wait_backend_ready(
        self,
        *,
        timeout_seconds: float = 25.0,
        host: str | None = None,
        port: int | None = None,
    ) -> bool:
        probe = self.probe_backend_readiness(timeout_seconds=timeout_seconds, host=host, port=port)
        self._last_backend_probe = probe
        return probe.ready

    def probe_backend_readiness(
        self,
        *,
        timeout_seconds: float = 25.0,
        host: str | None = None,
        port: int | None = None,
    ) -> BackendProbeResult:
        bind_host = host or self.config.api_host
        bind_port = int(port or self.config.api_port)
        base = f"http://{bind_host}:{bind_port}"
        health_endpoint = "/workspace/health"
        observable_endpoints = (
            "/workspace/health",
            "/workspace/readiness",
            "/workspace/profiles",
            "/workspace/prompt-lineage",
        )
        deadline = time.time() + timeout_seconds
        started_at = time.time()
        last_error = "timeout_without_health_200"
        attempts: list[dict[str, Any]] = []

        while time.time() < deadline:
            if self._backend_proc is not None and self._backend_proc.poll() is not None:
                result = BackendProbeResult(
                    ready=False,
                    failure_reason="backend_process_exited_before_ready",
                    recovery_signal="restart_backend_and_validate_port_binding",
                    base_url=base,
                    health_endpoint=health_endpoint,
                    endpoint_statuses={},
                    attempts=attempts,
                    process_exit_detected=True,
                    process_exit_code=self._backend_proc.returncode,
                    duration_seconds=round(time.time() - started_at, 3),
                )
                self._last_backend_probe = result
                diag_log(
                    "runtime_logs",
                    "internal_backend_exited_before_ready",
                    level="ERROR",
                    payload=result.as_dict(),
                )
                return result
            try:
                with httpx.Client(timeout=2.0, trust_env=False) as client:
                    health_response = client.get(f"{base}{health_endpoint}")
                    attempt = {
                        "at_utc": datetime.now(timezone.utc).isoformat(),
                        "health_status_code": health_response.status_code,
                    }
                    if health_response.status_code == 200:
                        endpoint_statuses: dict[str, Any] = {health_endpoint: 200}
                        for endpoint in observable_endpoints[1:]:
                            try:
                                endpoint_resp = client.get(f"{base}{endpoint}")
                                endpoint_statuses[endpoint] = endpoint_resp.status_code
                            except Exception as endpoint_exc:
                                endpoint_statuses[endpoint] = f"error:{type(endpoint_exc).__name__}"
                        attempt["endpoint_statuses"] = endpoint_statuses
                        attempts.append(attempt)
                        result = BackendProbeResult(
                            ready=True,
                            failure_reason="none",
                            recovery_signal="none",
                            base_url=base,
                            health_endpoint=health_endpoint,
                            endpoint_statuses=endpoint_statuses,
                            attempts=attempts,
                            process_exit_detected=False,
                            process_exit_code=None,
                            duration_seconds=round(time.time() - started_at, 3),
                        )
                        self._last_backend_probe = result
                        diag_log(
                            "runtime_logs",
                            "internal_backend_ready",
                            payload=result.as_dict(),
                        )
                        return result
                    last_error = f"health_status_code_{health_response.status_code}"
                    attempt["error"] = last_error
                    attempts.append(attempt)
                    time.sleep(0.25)
            except Exception as exc:
                last_error = f"http_client_error:{type(exc).__name__}"
                attempts.append(
                    {
                        "at_utc": datetime.now(timezone.utc).isoformat(),
                        "error": str(exc),
                    }
                )
                time.sleep(0.4)

        result = BackendProbeResult(
            ready=False,
            failure_reason=last_error,
            recovery_signal="inspect_backend_logs_and_localhost_connectivity",
            base_url=base,
            health_endpoint=health_endpoint,
            endpoint_statuses={},
            attempts=attempts[-12:],
            process_exit_detected=False,
            process_exit_code=None,
            duration_seconds=round(time.time() - started_at, 3),
        )
        self._last_backend_probe = result
        diag_log(
            "runtime_logs",
            "internal_backend_not_ready",
            level="ERROR",
            payload=result.as_dict(),
        )
        return result

    def get_last_backend_probe(self) -> dict[str, Any]:
        if self._last_backend_probe is None:
            return {}
        return self._last_backend_probe.as_dict()

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
