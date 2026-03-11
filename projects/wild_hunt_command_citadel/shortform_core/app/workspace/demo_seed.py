from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .models import (
    AttachedSourceType,
    ConnectionType,
    ContentItem,
    ContentMetricsSnapshot,
    ManagementMode,
    MetricsSourceType,
    OutcomeLabel,
    Platform,
    RecommendationFeedbackStatus,
    SourceType,
    ViewportPreset,
)
from .runtime import WorkspaceRuntime


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def seed_workspace_runtime(runtime: WorkspaceRuntime) -> dict[str, Any]:
    now = _utc_now()

    profile = runtime.profiles.create_profile(
        display_name="Demo Profile Alpha",
        platform=Platform.TIKTOK,
        connection_type=ConnectionType.CDP,
        management_mode=ManagementMode.GUIDED,
        notes="Demo profile for verification pipeline.",
        tags=["demo", "verification"],
    )
    runtime.profiles.connect_profile(
        profile.id,
        cdp_url="ws://127.0.0.1:9222/devtools/browser/demo",
        confirmed=True,
    )
    runtime.sessions.open_session_window(
        profile.id,
        viewport_preset=ViewportPreset.SMARTPHONE_DEFAULT,
        attached_source_type=AttachedSourceType.CDP,
        attached_source_id="demo-cdp-source",
        confirmed=True,
    )

    content_a = runtime.content.add_content_item(
        ContentItem(
            profile_id=profile.id,
            local_path="demo_assets/alpha_scene_a.mp4",
            title="Hook test A",
            caption="Fast hook with tactical tip.",
            hashtags=["shorts", "demo"],
            duration=24,
            format_label="talking_head",
            topic_label="content_strategy",
            hook_label="mistake_hook",
            cta_label="save_and_follow",
        )
    )
    content_b = runtime.content.add_content_item(
        ContentItem(
            profile_id=profile.id,
            local_path="demo_assets/alpha_scene_b.mp4",
            title="Hook test B",
            caption="Alternative format with social proof.",
            hashtags=["shorts", "experiment"],
            duration=29,
            format_label="visual_demo",
            topic_label="content_strategy",
            hook_label="proof_hook",
            cta_label="comment_prompt",
        )
    )

    runtime.content.validate_content_item(content_a.id)
    runtime.content.validate_content_item(content_b.id)
    runtime.content.queue_content_item(content_a.id, confirmed=True)
    runtime.content.queue_content_item(content_b.id, confirmed=True)

    snapshot_a = runtime.metrics.ingest_metrics_snapshot(
        ContentMetricsSnapshot(
            profile_id=profile.id,
            content_id=content_a.id,
            source_type=MetricsSourceType.DEMO,
            views=3200,
            likes=260,
            comments_count=42,
            shares=28,
            favorites=16,
            avg_watch_time=15.2,
            completion_rate=0.42,
            publish_time=now - timedelta(days=2),
            collected_at=now - timedelta(days=1),
        )
    )
    snapshot_b = runtime.metrics.ingest_metrics_snapshot(
        ContentMetricsSnapshot(
            profile_id=profile.id,
            content_id=content_b.id,
            source_type=MetricsSourceType.DEMO,
            views=4700,
            likes=510,
            comments_count=88,
            shares=72,
            favorites=39,
            avg_watch_time=19.4,
            completion_rate=0.55,
            publish_time=now - timedelta(days=4),
            collected_at=now - timedelta(days=1, hours=3),
        )
    )

    performance = runtime.metrics.get_profile_performance_summary(profile.id, window="30d")
    action_plan = runtime.planning.generate_next_content_plan(profile.id, window="30d")

    frame = runtime.ai_perception.analyze_frame(
        profile_id=profile.id,
        source_kind=SourceType.SCREENSHOT,
        source_ref="demo_frame_hook_overlay_caption.png",
    )
    asset_review = runtime.ai_perception.analyze_asset_preview(
        profile_id=profile.id,
        source_ref="demo_asset_preview_variant_a.png",
    )
    content_eval = runtime.ai_creative.evaluate_content_item(content_a.id)
    recommendations = runtime.ai_recommendation.generate_explainable_recommendations(profile.id, limit=5)
    recommendation_id = recommendations[0].id

    feedback = runtime.ai_learning.ingest_user_feedback(
        profile_id=profile.id,
        recommendation_id=recommendation_id,
        feedback_status=RecommendationFeedbackStatus.ACCEPTED,
        user_notes="Applied to next script draft.",
        manual_score=0.82,
    )
    outcome = runtime.ai_learning.ingest_content_performance_feedback(
        profile_id=profile.id,
        recommendation_id=recommendation_id,
        content_id=content_b.id,
        metrics_snapshot_ids=[snapshot_b.id],
        outcome_label=OutcomeLabel.SUCCESS,
        outcome_summary="Retention and engagement improved.",
    )
    learning_summary = runtime.ai_learning.summarize_learnings(profile.id)

    video_brief = runtime.generation_prep.generate_video_brief(
        profile_id=profile.id,
        content_goal="Improve hook retention",
        creative_angle="cinematic tactical breakdown",
        hook="Most creators lose viewers in second 3",
        format_target="9:16 short-form",
        duration_target="25-35s",
    )
    audio_brief = runtime.generation_prep.generate_audio_brief(
        profile_id=profile.id,
        content_goal="Improve hook retention",
        music_mood="dark pulse",
        voice_style="clear strategic",
    )
    script_brief = runtime.generation_prep.generate_script_brief(
        profile_id=profile.id,
        content_goal="Improve hook retention",
        hook="Most creators lose viewers in second 3",
        cta="Save and test this structure",
    )
    text_brief = runtime.generation_prep.generate_text_brief(
        profile_id=profile.id,
        content_goal="Improve hook retention",
        cta_options=["Save this format", "Try on your next post"],
    )
    bundle = runtime.generation_prep.build_generation_bundle(
        profile_id=profile.id,
        content_goal="Improve hook retention",
        creative_angle="cinematic tactical breakdown",
        format_target="9:16 short-form",
        duration_target="25-35s",
    )

    return {
        "profile_id": profile.id,
        "content_ids": [content_a.id, content_b.id],
        "metric_snapshot_ids": [snapshot_a.id, snapshot_b.id],
        "performance_snapshot_id": performance.id,
        "action_plan_id": action_plan.id,
        "ai": {
            "frame_id": frame.id,
            "asset_review_id": asset_review["asset_review"]["id"],
            "content_quality_score": content_eval["quality_score"],
            "recommendation_id": recommendation_id,
            "feedback_id": feedback.id,
            "outcome_link_id": outcome.id,
            "learning_records": learning_summary.get("total_records", 0),
        },
        "generation": {
            "video_brief_id": video_brief.id,
            "audio_brief_id": audio_brief.id,
            "script_brief_id": script_brief.id,
            "text_brief_id": text_brief.id,
            "bundle_id": bundle.id,
        },
    }
