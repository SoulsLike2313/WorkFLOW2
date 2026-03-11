from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from app.storage.repositories import RepositoryHub


@dataclass(slots=True)
class _WatchState:
    project_id: int
    session_id: str
    watched_path: Path
    snapshot: dict[str, float] = field(default_factory=dict)


class FileWatchService:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo
        self._states: dict[str, _WatchState] = {}

    def start_watch(self, *, project_id: int, session_id: str, watched_path: Path) -> None:
        state = _WatchState(
            project_id=project_id,
            session_id=session_id,
            watched_path=watched_path,
            snapshot=self._snapshot(watched_path),
        )
        self._states[session_id] = state

    def stop_watch(self, session_id: str) -> None:
        self._states.pop(session_id, None)

    def poll(self, session_id: str) -> list[dict]:
        state = self._states.get(session_id)
        if not state:
            return []
        current = self._snapshot(state.watched_path)
        events: list[dict] = []

        old_keys = set(state.snapshot)
        new_keys = set(current)
        created = sorted(new_keys - old_keys)
        deleted = sorted(old_keys - new_keys)
        common = sorted(old_keys & new_keys)

        for rel in created:
            events.append(self._emit(state, "created", rel))
        for rel in deleted:
            events.append(self._emit(state, "deleted", rel))
        for rel in common:
            if current[rel] != state.snapshot[rel]:
                events.append(self._emit(state, "modified", rel))

        state.snapshot = current
        return events

    @staticmethod
    def _snapshot(root: Path) -> dict[str, float]:
        if not root.exists():
            return {}
        snapshot: dict[str, float] = {}
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part.startswith(".") for part in path.parts):
                continue
            rel = path.relative_to(root).as_posix()
            snapshot[rel] = path.stat().st_mtime
        return snapshot

    def _emit(self, state: _WatchState, event_type: str, rel_file: str) -> dict:
        event = {
            "project_id": state.project_id,
            "session_id": state.session_id,
            "watched_path": str(state.watched_path),
            "event_type": event_type,
            "file_path": rel_file,
        }
        self.repo.add_watched_file_event(
            project_id=state.project_id,
            session_id=state.session_id,
            watched_path=str(state.watched_path),
            event_type=event_type,
            file_path=rel_file,
        )
        return event
