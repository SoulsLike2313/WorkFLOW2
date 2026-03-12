from __future__ import annotations

from datetime import datetime, timezone

from app.workspace.models import (
    ConnectionType,
    ContentItem,
    ContentMetricsSnapshot,
    ManagementMode,
    MetricsSourceType,
    Platform,
)


def test_action_plan_generation(runtime):
    profile = runtime.profiles.create_profile(
        display_name="Planner",
        platform=Platform.TIKTOK,
        connection_type=ConnectionType.CDP,
        management_mode=ManagementMode.GUIDED,
    )
    item = runtime.content.add_content_item(
        ContentItem(
            profile_id=profile.id,
            local_path="demo_assets/planner.mp4",
            title="Planner demo",
            duration=22,
            format_label="talking_head",
            topic_label="strategy",
            hook_label="hook",
            cta_label="cta",
        )
    )
    runtime.content.validate_content_item(item.id)
    runtime.content.queue_content_item(item.id, confirmed=True)
    runtime.metrics.ingest_metrics_snapshot(
        ContentMetricsSnapshot(
            profile_id=profile.id,
            content_id=item.id,
            source_type=MetricsSourceType.MANUAL,
            views=1500,
            likes=200,
            comments_count=30,
            shares=20,
            favorites=10,
            publish_time=datetime.now(timezone.utc),
            collected_at=datetime.now(timezone.utc),
        )
    )
    plan = runtime.planning.generate_next_content_plan(profile.id, window="30d")
    assert len(plan.next_actions) > 0

