from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, TypeVar

from app.storage.repositories import RepositoryHub

T = TypeVar("T")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobManager:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def run_job(self, name: str, fn: Callable[[], T]) -> T:
        key = f"job_state::{name}"
        self.repo.set_setting(
            key,
            {
                "name": name,
                "status": "running",
                "started_at": _now(),
                "finished_at": None,
                "error": None,
            },
        )
        try:
            result = fn()
        except Exception as exc:
            self.repo.set_setting(
                key,
                {
                    "name": name,
                    "status": "failed",
                    "started_at": self.repo.get_setting(key).get("started_at") if self.repo.get_setting(key) else _now(),
                    "finished_at": _now(),
                    "error": str(exc),
                },
            )
            raise
        self.repo.set_setting(
            key,
            {
                "name": name,
                "status": "done",
                "started_at": self.repo.get_setting(key).get("started_at") if self.repo.get_setting(key) else _now(),
                "finished_at": _now(),
                "error": None,
            },
        )
        return result

    def mark_interrupted_jobs(self) -> list[dict[str, Any]]:
        interrupted: list[dict[str, Any]] = []
        for setting_key in ("job_state::scan", "job_state::extract", "job_state::translate", "job_state::voice", "job_state::export"):
            state = self.repo.get_setting(setting_key)
            if state and state.get("status") == "running":
                state["status"] = "interrupted"
                state["finished_at"] = _now()
                self.repo.set_setting(setting_key, state)
                interrupted.append(state)
        return interrupted

    def get_job_state(self, name: str) -> dict[str, Any] | None:
        return self.repo.get_setting(f"job_state::{name}")
