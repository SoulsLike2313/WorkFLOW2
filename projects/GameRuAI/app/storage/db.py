from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

from app.core.exceptions import StorageError


class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")

    def close(self) -> None:
        self._conn.close()

    def init_schema(self, schema_path: Path) -> None:
        try:
            script = schema_path.read_text(encoding="utf-8")
            self._conn.executescript(script)
            self._apply_migrations()
            self._conn.commit()
        except Exception as exc:  # pragma: no cover - catastrophic path
            raise StorageError(f"Failed to initialize schema: {exc}") from exc

    def _apply_migrations(self) -> None:
        self._ensure_column("translations", "fallback_backend", "TEXT")
        self._ensure_column("translations", "context_used", "INTEGER NOT NULL DEFAULT 0")

    def _ensure_column(self, table: str, column: str, definition: str) -> None:
        rows = self.query(f"PRAGMA table_info({table})")
        existing = {str(row["name"]) for row in rows}
        if column in existing:
            return
        self._conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    @contextmanager
    def transaction(self):
        cursor = self._conn.cursor()
        try:
            yield cursor
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cursor.close()

    def execute(self, sql: str, params: Iterable[object] | tuple[()] = ()) -> int:
        with self.transaction() as cursor:
            cursor.execute(sql, tuple(params))
            return int(cursor.lastrowid)

    def executemany(self, sql: str, seq_of_params: list[tuple[object, ...]]) -> None:
        with self.transaction() as cursor:
            cursor.executemany(sql, seq_of_params)

    def query(self, sql: str, params: Iterable[object] | tuple[()] = ()) -> list[sqlite3.Row]:
        cursor = self._conn.cursor()
        try:
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()

    def query_one(self, sql: str, params: Iterable[object] | tuple[()] = ()) -> sqlite3.Row | None:
        rows = self.query(sql, params)
        return rows[0] if rows else None
