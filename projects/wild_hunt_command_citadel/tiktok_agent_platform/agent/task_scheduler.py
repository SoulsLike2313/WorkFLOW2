from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, QTimer, Signal

WEEKDAY_LABELS_RU = {
    0: "Пн",
    1: "Вт",
    2: "Ср",
    3: "Чт",
    4: "Пт",
    5: "Сб",
    6: "Вс",
}


@dataclass
class ScheduledTask:
    task_id: str
    name: str
    profile_name: str
    hour: int
    minute: int
    weekdays: List[int]
    enabled: bool = True
    created_at: str = ""
    last_run_on: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "profile_name": self.profile_name,
            "hour": self.hour,
            "minute": self.minute,
            "weekdays": self.weekdays,
            "enabled": self.enabled,
            "created_at": self.created_at,
            "last_run_on": self.last_run_on,
        }

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "ScheduledTask":
        now = datetime.utcnow().isoformat() + "Z"
        weekdays = [int(day) for day in raw.get("weekdays", []) if str(day).isdigit()]
        weekdays = [day for day in weekdays if 0 <= day <= 6]
        weekdays = sorted(set(weekdays)) or list(range(7))

        return cls(
            task_id=str(raw.get("task_id") or uuid.uuid4().hex),
            name=str(raw.get("name", "Задача")).strip() or "Задача",
            profile_name=str(raw.get("profile_name", "")).strip(),
            hour=max(0, min(23, int(raw.get("hour", 0)))),
            minute=max(0, min(59, int(raw.get("minute", 0)))),
            weekdays=weekdays,
            enabled=bool(raw.get("enabled", True)),
            created_at=str(raw.get("created_at", now)),
            last_run_on=str(raw.get("last_run_on", "")),
        )

    def schedule_label(self) -> str:
        days = ",".join(WEEKDAY_LABELS_RU.get(day, str(day)) for day in self.weekdays)
        return f"{days} {self.hour:02d}:{self.minute:02d}"


@dataclass
class QueueItem:
    queue_id: str
    source: str
    created_at: str
    payload: Dict[str, Any]


class SchedulerStore:
    def __init__(self, storage_path: Path) -> None:
        self.storage_path = Path(storage_path)

    def load(self) -> List[ScheduledTask]:
        if not self.storage_path.exists():
            return []

        try:
            raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except Exception:
            return []

        items = []
        if isinstance(raw, dict):
            tasks = raw.get("tasks", [])
            if isinstance(tasks, list):
                items = [item for item in tasks if isinstance(item, dict)]
        elif isinstance(raw, list):
            items = [item for item in raw if isinstance(item, dict)]

        return [ScheduledTask.from_dict(item) for item in items]

    def save(self, tasks: List[ScheduledTask]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "tasks": [task.to_dict() for task in tasks],
        }
        self.storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


class TaskScheduler(QObject):
    task_due = Signal(dict)

    def __init__(self, storage_path: Path, check_interval_ms: int = 15000) -> None:
        super().__init__()
        self.store = SchedulerStore(storage_path)
        self.tasks: List[ScheduledTask] = self.store.load()
        self.timer = QTimer(self)
        self.timer.setInterval(check_interval_ms)
        self.timer.timeout.connect(self._on_tick)

    def start(self) -> None:
        if not self.timer.isActive():
            self.timer.start()

    def stop(self) -> None:
        if self.timer.isActive():
            self.timer.stop()

    def add_task(
        self,
        *,
        name: str,
        profile_name: str,
        hour: int,
        minute: int,
        weekdays: List[int],
    ) -> ScheduledTask:
        now = datetime.utcnow().isoformat() + "Z"
        task = ScheduledTask(
            task_id=uuid.uuid4().hex,
            name=name.strip() or "Запуск",
            profile_name=profile_name.strip(),
            hour=max(0, min(23, int(hour))),
            minute=max(0, min(59, int(minute))),
            weekdays=sorted(set(day for day in weekdays if 0 <= int(day) <= 6)) or list(range(7)),
            enabled=True,
            created_at=now,
            last_run_on="",
        )
        self.tasks.append(task)
        self._persist()
        return task

    def remove_task(self, task_id: str) -> bool:
        initial = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.task_id != task_id]
        changed = len(self.tasks) != initial
        if changed:
            self._persist()
        return changed

    def set_task_enabled(self, task_id: str, enabled: bool) -> bool:
        for task in self.tasks:
            if task.task_id == task_id:
                task.enabled = enabled
                self._persist()
                return True
        return False

    def list_tasks(self) -> List[ScheduledTask]:
        return list(self.tasks)

    def describe_tasks(self) -> List[str]:
        lines: List[str] = []
        for task in self.tasks:
            state = "ON" if task.enabled else "OFF"
            profile = task.profile_name or "текущие настройки"
            lines.append(f"[{state}] {task.name} -> {task.schedule_label()} | профиль: {profile}")
        return lines

    def _persist(self) -> None:
        self.store.save(self.tasks)

    def _on_tick(self) -> None:
        now = datetime.now()
        today = now.date().isoformat()
        for task in self.tasks:
            if not task.enabled:
                continue
            if now.weekday() not in task.weekdays:
                continue
            if now.hour != task.hour or now.minute != task.minute:
                continue
            if task.last_run_on == today:
                continue

            task.last_run_on = today
            self._persist()
            self.task_due.emit(
                {
                    "task_id": task.task_id,
                    "name": task.name,
                    "profile_name": task.profile_name,
                    "scheduled_for": f"{now.strftime('%Y-%m-%d')} {task.hour:02d}:{task.minute:02d}",
                }
            )


class RunQueue:
    def __init__(self) -> None:
        self._items: List[QueueItem] = []

    def enqueue(self, source: str, payload: Dict[str, Any]) -> QueueItem:
        item = QueueItem(
            queue_id=uuid.uuid4().hex,
            source=source,
            created_at=datetime.utcnow().isoformat() + "Z",
            payload=dict(payload),
        )
        self._items.append(item)
        return item

    def pop(self) -> Optional[QueueItem]:
        if not self._items:
            return None
        return self._items.pop(0)

    def clear(self) -> None:
        self._items.clear()

    def items(self) -> List[QueueItem]:
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)
