from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class DashboardSnapshot:
    rows: List[Tuple[str, str]] = field(default_factory=list)
    likes_series: List[float] = field(default_factory=list)
    followers_series: List[float] = field(default_factory=list)
    plan_priority_series: List[float] = field(default_factory=list)


def _safe_read_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _parse_jsonl(path: Path) -> List[dict]:
    if not path.exists():
        return []
    items: List[dict] = []
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        if isinstance(payload, dict):
            items.append(payload)
    return items


def _parse_compact_number(value: object) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip().replace(" ", "").replace(",", ".")
    if not text:
        return None

    match = re.match(r"^([0-9]+(?:\.[0-9]+)?)([KMB]?)$", text, flags=re.IGNORECASE)
    if not match:
        digits = re.sub(r"[^0-9.]", "", text)
        if not digits:
            return None
        try:
            return float(digits)
        except ValueError:
            return None

    number = float(match.group(1))
    suffix = match.group(2).upper()
    if suffix == "K":
        number *= 1000
    elif suffix == "M":
        number *= 1_000_000
    elif suffix == "B":
        number *= 1_000_000_000
    return number


def load_dashboard_snapshot(output_dir: Path, core_root: Path, limit: int = 24) -> DashboardSnapshot:
    output_dir = Path(output_dir)
    core_root = Path(core_root)
    stats_items = _parse_jsonl(output_dir / "session_stats.jsonl")
    event_items = _parse_jsonl(output_dir / "session_events.jsonl")
    plan_payload = _safe_read_json(core_root / "runtime" / "output" / "plan_bundle.json")
    analytics_payload = _safe_read_json(core_root / "runtime" / "output" / "analytics_report.json")

    likes_series: List[float] = []
    followers_series: List[float] = []
    watch_count = 0
    comment_count = 0
    profile_visits = 0
    uploads = 0

    for event in event_items:
        event_name = str(event.get("event", "")).lower()
        if event_name == "watch_feed":
            watch_count += 1
        elif event_name == "comment":
            comment_count += 1
        elif event_name == "visit_profile":
            profile_visits += 1
        elif event_name == "upload":
            uploads += 1

    for stat in stats_items:
        likes = _parse_compact_number(stat.get("likes"))
        followers = _parse_compact_number(stat.get("followers"))
        if likes is not None:
            likes_series.append(likes)
        if followers is not None:
            followers_series.append(followers)

        video_stats = stat.get("video_stats")
        if isinstance(video_stats, dict):
            v_likes = _parse_compact_number(video_stats.get("likes"))
            if v_likes is not None:
                likes_series.append(v_likes)

    likes_series = likes_series[-limit:]
    followers_series = followers_series[-limit:]

    plan_steps = []
    plan_priority_series: List[float] = []
    if isinstance(plan_payload, dict):
        plan_steps = list(plan_payload.get("steps", []))
        priority_map = {"high": 3, "medium": 2, "low": 1}
        for step in plan_steps[:limit]:
            if not isinstance(step, dict):
                continue
            priority = str(step.get("priority", "")).lower()
            plan_priority_series.append(float(priority_map.get(priority, 0)))

    health_score = "-"
    if isinstance(analytics_payload, dict):
        assessment = analytics_payload.get("account_assessment", {})
        if isinstance(assessment, dict):
            score_value = assessment.get("health_score")
            if score_value is not None:
                health_score = str(score_value)

    rows = [
        ("Видео просмотрено", str(watch_count)),
        ("Комментариев отправлено", str(comment_count)),
        ("Профилей посещено", str(profile_visits)),
        ("Загрузок видео", str(uploads)),
        ("Записей stats", str(len(stats_items))),
        ("Шагов в плане core", str(len(plan_steps))),
        ("Health score core", health_score),
    ]

    return DashboardSnapshot(
        rows=rows,
        likes_series=likes_series,
        followers_series=followers_series,
        plan_priority_series=plan_priority_series,
    )
