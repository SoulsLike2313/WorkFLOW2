from __future__ import annotations

import json
from pathlib import Path

from .db import connect_sqlite, init_db
from .models import (
    AccountState,
    CoreBundle,
    CreativeAsset,
    ExternalEvent,
    Hypothesis,
    MetricSnapshot,
    PlanBundle,
    TaskItem,
)


def _dump_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def _load_json(value: str | None, default: object) -> object:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


class SQLiteRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def init_schema(self) -> None:
        with connect_sqlite(self.db_path) as conn:
            init_db(conn)

    def upsert_account(self, account: AccountState) -> None:
        payload = account.model_dump(mode="json")
        with connect_sqlite(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO accounts (
                    account_id, platform, handle, followers, following, total_likes, last_sync_at, tags_json
                ) VALUES (
                    :account_id, :platform, :handle, :followers, :following, :total_likes, :last_sync_at, :tags_json
                )
                ON CONFLICT(account_id) DO UPDATE SET
                    platform=excluded.platform,
                    handle=excluded.handle,
                    followers=excluded.followers,
                    following=excluded.following,
                    total_likes=excluded.total_likes,
                    last_sync_at=excluded.last_sync_at,
                    tags_json=excluded.tags_json
                """,
                {
                    "account_id": payload["account_id"],
                    "platform": payload["platform"],
                    "handle": payload["handle"],
                    "followers": payload["followers"],
                    "following": payload["following"],
                    "total_likes": payload["total_likes"],
                    "last_sync_at": payload["last_sync_at"],
                    "tags_json": _dump_json(payload["tags"]),
                },
            )
            conn.commit()

    def upsert_creative(self, creative: CreativeAsset) -> None:
        payload = creative.model_dump(mode="json")
        with connect_sqlite(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO creatives (
                    creative_id, account_id, platform, title, topic, hook, cta, hypothesis_id,
                    status, tags_json, created_at, metadata_json
                ) VALUES (
                    :creative_id, :account_id, :platform, :title, :topic, :hook, :cta, :hypothesis_id,
                    :status, :tags_json, :created_at, :metadata_json
                )
                ON CONFLICT(creative_id) DO UPDATE SET
                    account_id=excluded.account_id,
                    platform=excluded.platform,
                    title=excluded.title,
                    topic=excluded.topic,
                    hook=excluded.hook,
                    cta=excluded.cta,
                    hypothesis_id=excluded.hypothesis_id,
                    status=excluded.status,
                    tags_json=excluded.tags_json,
                    created_at=excluded.created_at,
                    metadata_json=excluded.metadata_json
                """,
                {
                    "creative_id": payload["creative_id"],
                    "account_id": payload["account_id"],
                    "platform": payload["platform"],
                    "title": payload["title"],
                    "topic": payload["topic"],
                    "hook": payload["hook"],
                    "cta": payload["cta"],
                    "hypothesis_id": payload["hypothesis_id"],
                    "status": payload["status"],
                    "tags_json": _dump_json(payload["tags"]),
                    "created_at": payload["created_at"],
                    "metadata_json": _dump_json(payload["metadata"]),
                },
            )
            conn.commit()

    def upsert_hypothesis(self, hypothesis: Hypothesis) -> None:
        payload = hypothesis.model_dump(mode="json")
        with connect_sqlite(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO hypotheses (
                    hypothesis_id, account_id, statement, success_criteria, status,
                    related_creative_ids_json, created_at, owner
                ) VALUES (
                    :hypothesis_id, :account_id, :statement, :success_criteria, :status,
                    :related_creative_ids_json, :created_at, :owner
                )
                ON CONFLICT(hypothesis_id) DO UPDATE SET
                    account_id=excluded.account_id,
                    statement=excluded.statement,
                    success_criteria=excluded.success_criteria,
                    status=excluded.status,
                    related_creative_ids_json=excluded.related_creative_ids_json,
                    created_at=excluded.created_at,
                    owner=excluded.owner
                """,
                {
                    "hypothesis_id": payload["hypothesis_id"],
                    "account_id": payload["account_id"],
                    "statement": payload["statement"],
                    "success_criteria": payload["success_criteria"],
                    "status": payload["status"],
                    "related_creative_ids_json": _dump_json(payload["related_creative_ids"]),
                    "created_at": payload["created_at"],
                    "owner": payload["owner"],
                },
            )
            conn.commit()

    def upsert_task(self, task: TaskItem) -> None:
        payload = task.model_dump(mode="json")
        with connect_sqlite(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    task_id, account_id, title, description, status, priority, due_at, tags_json, metadata_json
                ) VALUES (
                    :task_id, :account_id, :title, :description, :status, :priority, :due_at, :tags_json, :metadata_json
                )
                ON CONFLICT(task_id) DO UPDATE SET
                    account_id=excluded.account_id,
                    title=excluded.title,
                    description=excluded.description,
                    status=excluded.status,
                    priority=excluded.priority,
                    due_at=excluded.due_at,
                    tags_json=excluded.tags_json,
                    metadata_json=excluded.metadata_json
                """,
                {
                    "task_id": payload["task_id"],
                    "account_id": payload["account_id"],
                    "title": payload["title"],
                    "description": payload["description"],
                    "status": payload["status"],
                    "priority": payload["priority"],
                    "due_at": payload["due_at"],
                    "tags_json": _dump_json(payload["tags"]),
                    "metadata_json": _dump_json(payload["metadata"]),
                },
            )
            conn.commit()

    def add_metric(self, metric: MetricSnapshot) -> None:
        payload = metric.model_dump(mode="json")
        with connect_sqlite(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO metrics (
                    snapshot_id, account_id, platform, creative_id, captured_at, views, likes, comments, shares, saves,
                    watch_time_seconds, source, metadata_json
                ) VALUES (
                    :snapshot_id, :account_id, :platform, :creative_id, :captured_at, :views, :likes, :comments, :shares,
                    :saves, :watch_time_seconds, :source, :metadata_json
                )
                """,
                {
                    "snapshot_id": payload["snapshot_id"],
                    "account_id": payload["account_id"],
                    "platform": payload["platform"],
                    "creative_id": payload["creative_id"],
                    "captured_at": payload["captured_at"],
                    "views": payload["views"],
                    "likes": payload["likes"],
                    "comments": payload["comments"],
                    "shares": payload["shares"],
                    "saves": payload["saves"],
                    "watch_time_seconds": payload["watch_time_seconds"],
                    "source": payload["source"],
                    "metadata_json": _dump_json(payload["metadata"]),
                },
            )
            conn.commit()

    def add_event(self, event: ExternalEvent) -> None:
        payload = event.model_dump(mode="json")
        with connect_sqlite(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO events (
                    event_id, account_id, source, event_type, event_time, payload_json
                ) VALUES (
                    :event_id, :account_id, :source, :event_type, :event_time, :payload_json
                )
                """,
                {
                    "event_id": payload["event_id"],
                    "account_id": payload["account_id"],
                    "source": payload["source"],
                    "event_type": payload["event_type"],
                    "event_time": payload["event_time"],
                    "payload_json": _dump_json(payload["payload"]),
                },
            )
            conn.commit()

    def store_plan(self, plan: PlanBundle) -> None:
        payload = plan.model_dump(mode="json")
        with connect_sqlite(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO plans (bundle_id, account_id, generated_at, summary, steps_json)
                VALUES (:bundle_id, :account_id, :generated_at, :summary, :steps_json)
                """,
                {
                    "bundle_id": payload["bundle_id"],
                    "account_id": payload["account_id"],
                    "generated_at": payload["generated_at"],
                    "summary": payload["summary"],
                    "steps_json": _dump_json(payload["steps"]),
                },
            )
            conn.commit()

    def save_bundle(self, bundle: CoreBundle) -> None:
        self.upsert_account(bundle.account)
        for creative in bundle.creatives:
            self.upsert_creative(creative)
        for hypothesis in bundle.hypotheses:
            self.upsert_hypothesis(hypothesis)
        for task in bundle.tasks:
            self.upsert_task(task)
        for metric in bundle.metrics:
            self.add_metric(metric)
        for event in bundle.events:
            self.add_event(event)

    def get_account(self, account_id: str) -> AccountState | None:
        with connect_sqlite(self.db_path) as conn:
            row = conn.execute("SELECT * FROM accounts WHERE account_id = ?", (account_id,)).fetchone()
        if row is None:
            return None
        payload = dict(row)
        payload["tags"] = _load_json(payload.pop("tags_json"), [])
        return AccountState.model_validate(payload)

    def list_creatives(self, account_id: str) -> list[CreativeAsset]:
        with connect_sqlite(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM creatives WHERE account_id = ? ORDER BY created_at DESC",
                (account_id,),
            ).fetchall()
        creatives: list[CreativeAsset] = []
        for row in rows:
            payload = dict(row)
            payload["tags"] = _load_json(payload.pop("tags_json"), [])
            payload["metadata"] = _load_json(payload.pop("metadata_json"), {})
            creatives.append(CreativeAsset.model_validate(payload))
        return creatives

    def list_tasks(self, account_id: str) -> list[TaskItem]:
        with connect_sqlite(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE account_id = ? ORDER BY priority ASC, task_id ASC",
                (account_id,),
            ).fetchall()
        tasks: list[TaskItem] = []
        for row in rows:
            payload = dict(row)
            payload["tags"] = _load_json(payload.pop("tags_json"), [])
            payload["metadata"] = _load_json(payload.pop("metadata_json"), {})
            tasks.append(TaskItem.model_validate(payload))
        return tasks

    def list_metrics(self, account_id: str, limit: int = 200) -> list[MetricSnapshot]:
        with connect_sqlite(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM metrics
                WHERE account_id = ?
                ORDER BY captured_at DESC
                LIMIT ?
                """,
                (account_id, limit),
            ).fetchall()
        metrics: list[MetricSnapshot] = []
        for row in rows:
            payload = dict(row)
            payload["metadata"] = _load_json(payload.pop("metadata_json"), {})
            metrics.append(MetricSnapshot.model_validate(payload))
        return metrics

    def get_latest_plan(self, account_id: str) -> PlanBundle | None:
        with connect_sqlite(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT * FROM plans
                WHERE account_id = ?
                ORDER BY generated_at DESC
                LIMIT 1
                """,
                (account_id,),
            ).fetchone()
        if row is None:
            return None
        payload = dict(row)
        payload["steps"] = _load_json(payload.pop("steps_json"), [])
        return PlanBundle.model_validate(payload)
