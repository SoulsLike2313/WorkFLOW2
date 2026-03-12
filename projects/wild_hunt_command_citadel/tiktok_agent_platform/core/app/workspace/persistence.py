from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


LATEST_SCHEMA_VERSION = 1


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SQLiteWorkspacePersistence:
    """
    Lightweight persistence layer for workspace repository snapshots.

    Uses a single-state document model for predictable migrations and safe restore.
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()
        self.migrate()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            yield conn
        finally:
            conn.close()

    def init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS workspace_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS workspace_state (
                    state_id TEXT PRIMARY KEY,
                    schema_version INTEGER NOT NULL,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            current = conn.execute(
                "SELECT value FROM workspace_meta WHERE key = 'schema_version'"
            ).fetchone()
            if current is None:
                conn.execute(
                    "INSERT INTO workspace_meta (key, value) VALUES ('schema_version', ?)",
                    (str(LATEST_SCHEMA_VERSION),),
                )
            conn.commit()

    def get_schema_version(self) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM workspace_meta WHERE key = 'schema_version'"
            ).fetchone()
        if row is None:
            return 0
        try:
            return int(row["value"])
        except (TypeError, ValueError):
            return 0

    def migrate(self) -> None:
        """
        Reserved migration path for future schema changes.
        """
        version = self.get_schema_version()
        if version >= LATEST_SCHEMA_VERSION:
            return
        with self._connect() as conn:
            conn.execute(
                "UPDATE workspace_meta SET value = ? WHERE key = 'schema_version'",
                (str(LATEST_SCHEMA_VERSION),),
            )
            conn.commit()

    def load_state(self) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload_json FROM workspace_state WHERE state_id = 'default' LIMIT 1"
            ).fetchone()
        if row is None:
            return None
        try:
            payload = json.loads(row["payload_json"])
        except json.JSONDecodeError:
            return None
        return payload if isinstance(payload, dict) else None

    def save_state(self, state: dict[str, Any]) -> None:
        payload_json = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO workspace_state (state_id, schema_version, payload_json, updated_at)
                VALUES ('default', ?, ?, ?)
                ON CONFLICT(state_id) DO UPDATE SET
                    schema_version = excluded.schema_version,
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                """,
                (LATEST_SCHEMA_VERSION, payload_json, _utc_now_iso()),
            )
            conn.commit()

    def backup_to(self, target_path: Path) -> Path:
        target = Path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            backup = sqlite3.connect(target)
            try:
                conn.backup(backup)
            finally:
                backup.close()
        return target

    def health_check(self) -> dict[str, Any]:
        version = self.get_schema_version()
        state = self.load_state()
        return {
            "db_path": str(self.db_path),
            "schema_version": version,
            "state_present": state is not None,
            "status": "ok",
        }

