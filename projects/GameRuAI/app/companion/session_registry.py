from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.storage.repositories import RepositoryHub


@dataclass(slots=True)
class CompanionSession:
    project_id: int
    session_id: str
    executable_path: str
    watched_path: str
    process_status: str
    process_pid: int | None = None


class SessionRegistry:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def create(
        self,
        *,
        project_id: int,
        executable_path: str,
        watched_path: str,
        process_status: str,
        process_pid: int | None,
    ) -> CompanionSession:
        session_id = str(uuid.uuid4())
        self.repo.create_companion_session(
            project_id=project_id,
            session_id=session_id,
            executable_path=executable_path,
            watched_path=watched_path,
            process_status=process_status,
            process_pid=process_pid,
        )
        return CompanionSession(
            project_id=project_id,
            session_id=session_id,
            executable_path=executable_path,
            watched_path=watched_path,
            process_status=process_status,
            process_pid=process_pid,
        )

    def update(self, session_id: str, *, status: str, pid: int | None = None, ended: bool = False) -> None:
        self.repo.update_companion_session(session_id=session_id, process_status=status, process_pid=pid, ended=ended)

    def get(self, session_id: str) -> dict | None:
        return self.repo.get_companion_session(session_id)

    def list_by_project(self, project_id: int) -> list[dict]:
        return self.repo.list_companion_sessions(project_id)
