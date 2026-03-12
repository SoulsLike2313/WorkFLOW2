from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS accounts (
  account_id TEXT PRIMARY KEY,
  platform TEXT NOT NULL,
  handle TEXT NOT NULL,
  followers INTEGER NOT NULL DEFAULT 0,
  following INTEGER NOT NULL DEFAULT 0,
  total_likes INTEGER NOT NULL DEFAULT 0,
  last_sync_at TEXT NOT NULL,
  tags_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS creatives (
  creative_id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  platform TEXT NOT NULL,
  title TEXT NOT NULL,
  topic TEXT NOT NULL,
  hook TEXT NOT NULL,
  cta TEXT NOT NULL,
  hypothesis_id TEXT,
  status TEXT NOT NULL,
  tags_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hypotheses (
  hypothesis_id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  statement TEXT NOT NULL,
  success_criteria TEXT NOT NULL,
  status TEXT NOT NULL,
  related_creative_ids_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  owner TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
  task_id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  status TEXT NOT NULL,
  priority INTEGER NOT NULL,
  due_at TEXT,
  tags_json TEXT NOT NULL,
  metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metrics (
  snapshot_id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  platform TEXT NOT NULL,
  creative_id TEXT,
  captured_at TEXT NOT NULL,
  views INTEGER NOT NULL,
  likes INTEGER NOT NULL,
  comments INTEGER NOT NULL,
  shares INTEGER NOT NULL,
  saves INTEGER NOT NULL,
  watch_time_seconds REAL,
  source TEXT NOT NULL,
  metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  source TEXT NOT NULL,
  event_type TEXT NOT NULL,
  event_time TEXT NOT NULL,
  payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plans (
  bundle_id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  generated_at TEXT NOT NULL,
  summary TEXT NOT NULL,
  steps_json TEXT NOT NULL
);
"""


def connect_sqlite(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()
