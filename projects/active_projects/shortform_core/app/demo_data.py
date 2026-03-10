from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .io_utils import read_jsonl
from .models import (
    AccountState,
    CoreBundle,
    CreativeAsset,
    CreativeStatus,
    ExternalEvent,
    Hypothesis,
    MetricSnapshot,
    Platform,
    TaskItem,
    TaskStatus,
    utc_now,
)


def _parse_counter(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(max(0, value))

    text = str(value).strip().replace(" ", "").replace("\u00a0", "")
    if not text:
        return 0

    if re.fullmatch(r"\d{1,3}(,\d{3})+", text):
        return int(text.replace(",", ""))
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", text):
        return int(text.replace(".", ""))

    normalized = text.replace(",", ".")
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)([kmbKMB]?)", normalized)
    if not match:
        digits = re.sub(r"[^\d]", "", normalized)
        return int(digits) if digits else 0

    number = float(match.group(1))
    suffix = match.group(2).lower()
    multiplier = 1
    if suffix == "k":
        multiplier = 1_000
    elif suffix == "m":
        multiplier = 1_000_000
    elif suffix == "b":
        multiplier = 1_000_000_000
    return int(max(0, number * multiplier))


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    if isinstance(value, str) and value.strip():
        raw = value.strip().replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(raw).astimezone(timezone.utc)
        except ValueError:
            pass
    return utc_now()


def _extract_creative_id(url: str | None) -> str | None:
    if not url:
        return None
    match = re.search(r"/video/(\d+)", url)
    if match:
        return f"tt-{match.group(1)}"
    return None


def _handle_from_url(url: str | None) -> str | None:
    if not url:
        return None
    match = re.search(r"tiktok\.com/(@[A-Za-z0-9_.-]+)", url)
    if match:
        return match.group(1)
    return None


def _load_tiktok_snapshot(
    snapshot_dir: Path,
    account_id: str,
) -> tuple[list[MetricSnapshot], list[ExternalEvent], dict[str, int], str | None]:
    stats_path = snapshot_dir / "output" / "session_stats.jsonl"
    events_path = snapshot_dir / "output" / "session_events.jsonl"
    stats_rows = read_jsonl(stats_path)
    event_rows = read_jsonl(events_path)

    metrics: list[MetricSnapshot] = []
    events: list[ExternalEvent] = []
    profile_counters: dict[str, int] = {"followers": 0, "following": 0, "likes": 0}
    inferred_handle: str | None = None

    for row in stats_rows:
        creative_id = _extract_creative_id(row.get("url"))
        metrics.append(
            MetricSnapshot(
                account_id=account_id,
                platform=Platform.TIKTOK,
                creative_id=creative_id,
                captured_at=_parse_timestamp(row.get("timestamp")),
                views=_parse_counter(row.get("views")),
                likes=_parse_counter(row.get("likes")),
                comments=_parse_counter(row.get("comments")),
                shares=_parse_counter(row.get("shares")),
                saves=_parse_counter(row.get("saves")),
                source="tiktok_snapshot_stats",
                metadata={
                    "url": row.get("url"),
                    "author": row.get("author"),
                    "description": row.get("description"),
                },
            )
        )

    for row in event_rows:
        event_type = str(row.get("event") or "unknown")
        event_time = _parse_timestamp(row.get("timestamp"))
        profile_url = row.get("profile_url")
        inferred_handle = inferred_handle or _handle_from_url(profile_url)

        events.append(
            ExternalEvent(
                account_id=account_id,
                source="tiktok_snapshot_events",
                event_type=event_type,
                event_time=event_time,
                payload=row,
            )
        )

        if event_type == "profile_metrics":
            profile_counters["followers"] = _parse_counter(row.get("followers"))
            profile_counters["following"] = _parse_counter(row.get("following"))
            profile_counters["likes"] = _parse_counter(row.get("likes"))

            views_total = 0
            posts = row.get("posts") or []
            if isinstance(posts, list):
                for post in posts:
                    if not isinstance(post, dict):
                        continue
                    views_total += _parse_counter(post.get("views"))
            metrics.append(
                MetricSnapshot(
                    account_id=account_id,
                    platform=Platform.TIKTOK,
                    captured_at=event_time,
                    views=max(views_total, 0),
                    likes=profile_counters["likes"],
                    comments=0,
                    shares=0,
                    saves=0,
                    source="tiktok_snapshot_profile",
                    metadata={"profile_url": profile_url, "posts_count": len(posts) if isinstance(posts, list) else 0},
                )
            )

    return metrics, events, profile_counters, inferred_handle


def _default_bundle(account_id: str, handle: str) -> CoreBundle:
    account = AccountState(
        account_id=account_id,
        platform=Platform.TIKTOK,
        handle=handle,
        followers=0,
        following=0,
        total_likes=0,
    )

    creatives = [
        CreativeAsset(
            creative_id="cr-witcher-hook-01",
            account_id=account_id,
            platform=Platform.TIKTOK,
            title="Хук Ведьмака: подготовка зелья в 3 кадрах",
            topic="фэнтези",
            hook="Сможет ли Геральт выжить без знаков?",
            cta="Напиши в комментарии свою школу",
            status=CreativeStatus.TESTING,
            tags=["тест-хука", "фэнтези"],
        ),
        CreativeAsset(
            creative_id="cr-build-breakdown-02",
            account_id=account_id,
            platform=Platform.TIKTOK,
            title="Разбор билда: снаряжение мечника",
            topic="игры",
            hook="Самый сильный бюджетный билд",
            cta="Сохрани, чтобы не потерять",
            status=CreativeStatus.TESTING,
            tags=["обучение", "билды"],
        ),
        CreativeAsset(
            creative_id="cr-story-clip-03",
            account_id=account_id,
            platform=Platform.TIKTOK,
            title="Сюжетный клип: самый тяжелый контракт",
            topic="лор",
            hook="Этот контракт изменил всё",
            cta="Подпишись на вторую часть",
            status=CreativeStatus.ACTIVE,
            tags=["сторителлинг"],
        ),
    ]

    hypotheses = [
        Hypothesis(
            hypothesis_id="hp-hook-emotion",
            account_id=account_id,
            statement="Эмоциональные хуки дают более высокий engagement, чем нейтральные вступления.",
            success_criteria="Средний engagement rate >= 8% на 3+ креативах",
            related_creative_ids=[creative.creative_id for creative in creatives[:2]],
        )
    ]

    tasks = [
        TaskItem(
            task_id="ts-refresh-thumbnails",
            account_id=account_id,
            title="Обновить обложки для двух самых слабых креативов",
            description="Использовать более высокий контраст и один ключевой заголовок на обложке.",
            priority=2,
            status=TaskStatus.TODO,
            tags=["дизайн", "быстрый-результат"],
        ),
        TaskItem(
            task_id="ts-comment-framework",
            account_id=account_id,
            title="Подготовить переиспользуемый шаблон ответов на комментарии",
            description="Собрать 5 форматов ответов для быстрого комьюнити-менеджмента.",
            priority=3,
            status=TaskStatus.TODO,
            tags=["сообщество"],
        ),
    ]

    metrics = [
        MetricSnapshot(
            snapshot_id="ms-demo-001",
            account_id=account_id,
            platform=Platform.TIKTOK,
            creative_id="cr-witcher-hook-01",
            views=3200,
            likes=265,
            comments=47,
            shares=21,
            saves=16,
            source="demo_seed",
        ),
        MetricSnapshot(
            snapshot_id="ms-demo-002",
            account_id=account_id,
            platform=Platform.TIKTOK,
            creative_id="cr-build-breakdown-02",
            views=1900,
            likes=82,
            comments=13,
            shares=9,
            saves=5,
            source="demo_seed",
        ),
        MetricSnapshot(
            snapshot_id="ms-demo-003",
            account_id=account_id,
            platform=Platform.TIKTOK,
            creative_id="cr-story-clip-03",
            views=4100,
            likes=332,
            comments=58,
            shares=37,
            saves=26,
            source="demo_seed",
        ),
    ]

    events = [
        ExternalEvent(
            account_id=account_id,
            source="demo_seed",
            event_type="seed_generated",
            event_time=utc_now(),
            payload={"reason": "Не найден tiktok snapshot output; используется безопасный demo seed"},
        )
    ]
    return CoreBundle(
        account=account,
        creatives=creatives,
        hypotheses=hypotheses,
        tasks=tasks,
        metrics=metrics,
        events=events,
    )


def build_demo_bundle(snapshot_dir: Path) -> CoreBundle:
    account_id = "acc-main"
    fallback_handle = "@creator"
    bundle = _default_bundle(account_id=account_id, handle=fallback_handle)

    metrics, events, profile_counters, inferred_handle = _load_tiktok_snapshot(snapshot_dir, account_id)
    if not metrics and not events:
        return bundle

    account = bundle.account.model_copy(
        update={
            "handle": inferred_handle or bundle.account.handle,
            "followers": profile_counters.get("followers", 0),
            "following": profile_counters.get("following", 0),
            "total_likes": profile_counters.get("likes", 0),
        }
    )

    known_ids = {creative.creative_id for creative in bundle.creatives}
    discovered_ids = {metric.creative_id for metric in metrics if metric.creative_id}

    for creative_id in sorted(discovered_ids):
        if creative_id in known_ids:
            continue
        bundle.creatives.append(
            CreativeAsset(
                creative_id=creative_id,
                account_id=account_id,
                platform=Platform.TIKTOK,
                title=f"Импортированный креатив {creative_id}",
                topic="импорт",
                hook="Импортировано из tiktok_automation snapshot",
                cta="Проверь и доработай",
                status=CreativeStatus.TESTING,
                tags=["импорт", "tiktok_snapshot"],
                metadata={"source": "external_data/tiktok_automation_snapshot"},
            )
        )

    if metrics:
        bundle.metrics = metrics
    if events:
        bundle.events = events
    bundle.account = account
    return bundle
