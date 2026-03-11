from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from .config import AppConfig
from .workspace.runtime import WorkspaceRuntime


@dataclass(frozen=True)
class ReadinessItem:
    name: str
    ready: bool
    reason: str = ""
    details: dict[str, Any] | None = None


class ReadinessService:
    """
    Aggregates service readiness for startup and verification gates.
    """

    def evaluate_local(
        self,
        *,
        config: AppConfig,
        workspace_runtime: WorkspaceRuntime | None = None,
    ) -> dict[str, Any]:
        items: list[ReadinessItem] = [
            self._config_ready(config),
            self._db_ready(config.storage.database_path),
            self._workspace_state_ready(config.storage.workspace_state_path),
            self._logs_dir_ready(config.storage.logs_dir),
            self._patch_dir_ready(config.storage.patch_dir),
        ]

        if workspace_runtime is not None:
            items.extend(
                [
                    self._repository_ready(workspace_runtime),
                    self._workspace_ready(workspace_runtime),
                    self._analytics_ready(workspace_runtime),
                    self._ai_ready(workspace_runtime),
                    self._update_ready(config),
                    self._ui_bridge_ready(),
                ]
            )

        overall = all(item.ready for item in items)
        return {
            "overall_ready": overall,
            "status": "ready" if overall else "degraded",
            "items": [
                {
                    "name": item.name,
                    "ready": item.ready,
                    "reason": item.reason,
                    "details": item.details or {},
                }
                for item in items
            ],
        }

    def evaluate_api(self, *, base_url: str, timeout_seconds: float = 3.0) -> ReadinessItem:
        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                response = client.get(f"{base_url}/workspace/health")
            if response.status_code == 200:
                return ReadinessItem(name="api_ready", ready=True, reason="ok")
            return ReadinessItem(
                name="api_ready",
                ready=False,
                reason=f"unexpected status {response.status_code}",
            )
        except Exception as exc:
            return ReadinessItem(name="api_ready", ready=False, reason=str(exc))

    @staticmethod
    def _config_ready(config: AppConfig) -> ReadinessItem:
        ok = bool(config.api_host) and int(config.api_port) > 0
        return ReadinessItem(name="config_ready", ready=ok, reason="" if ok else "invalid host/port config")

    @staticmethod
    def _db_ready(db_path: Path) -> ReadinessItem:
        exists = db_path.parent.exists()
        return ReadinessItem(name="db_ready", ready=exists, reason="" if exists else "database directory missing")

    @staticmethod
    def _workspace_state_ready(workspace_state_path: Path) -> ReadinessItem:
        exists = workspace_state_path.parent.exists()
        return ReadinessItem(
            name="workspace_state_ready",
            ready=exists,
            reason="" if exists else "workspace state directory missing",
        )

    @staticmethod
    def _logs_dir_ready(logs_dir: Path) -> ReadinessItem:
        return ReadinessItem(name="logs_ready", ready=logs_dir.exists(), reason="" if logs_dir.exists() else "logs dir missing")

    @staticmethod
    def _patch_dir_ready(patch_dir: Path) -> ReadinessItem:
        return ReadinessItem(name="update_ready", ready=patch_dir.exists(), reason="" if patch_dir.exists() else "patch dir missing")

    @staticmethod
    def _repository_ready(workspace_runtime: WorkspaceRuntime) -> ReadinessItem:
        ok = workspace_runtime.repository is not None
        return ReadinessItem(name="repository_ready", ready=ok, reason="" if ok else "repository missing")

    @staticmethod
    def _workspace_ready(workspace_runtime: WorkspaceRuntime) -> ReadinessItem:
        ok = workspace_runtime.profiles is not None and workspace_runtime.sessions is not None
        return ReadinessItem(name="workspace_ready", ready=ok, reason="" if ok else "workspace services missing")

    @staticmethod
    def _analytics_ready(workspace_runtime: WorkspaceRuntime) -> ReadinessItem:
        ok = workspace_runtime.metrics is not None and workspace_runtime.formulas is not None
        return ReadinessItem(name="analytics_ready", ready=ok, reason="" if ok else "analytics services missing")

    @staticmethod
    def _ai_ready(workspace_runtime: WorkspaceRuntime) -> ReadinessItem:
        ok = workspace_runtime.ai_perception is not None and workspace_runtime.ai_recommendation is not None
        return ReadinessItem(name="ai_ready", ready=ok, reason="" if ok else "ai services missing")

    @staticmethod
    def _update_ready(config: AppConfig) -> ReadinessItem:
        ok = config.storage.patch_dir.exists()
        return ReadinessItem(name="update_ready", ready=ok, reason="" if ok else "patch directory unavailable")

    @staticmethod
    def _ui_bridge_ready() -> ReadinessItem:
        return ReadinessItem(name="ui_bridge_ready", ready=True, reason="desktop bridge available")

