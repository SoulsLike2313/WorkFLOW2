from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from app.tests.helpers import build_runtime
from app.workspace.models import (
    ConnectionType,
    ContentItem,
    ContentMetricsSnapshot,
    ManagementMode,
    MetricsSourceType,
    OutcomeLabel,
    Platform,
    RecommendationFeedbackStatus,
    SourceType,
)


class AnalyticsAndAITests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = build_runtime()
        self.profile = self.runtime.profiles.create_profile(
            display_name="AnalyticsAI",
            platform=Platform.TIKTOK,
            connection_type=ConnectionType.CDP,
            management_mode=ManagementMode.GUIDED,
        )
        self.content = self.runtime.content.add_content_item(
            ContentItem(
                profile_id=self.profile.id,
                local_path="demo_assets/ai_video.mp4",
                title="AI content",
                caption="demo",
                duration=25,
                format_label="talking_head",
                topic_label="analytics",
                hook_label="mistake_hook",
                cta_label="follow",
            )
        )
        self.runtime.content.validate_content_item(self.content.id)
        self.runtime.content.queue_content_item(self.content.id, confirmed=True)

    def test_metrics_and_action_plan(self) -> None:
        now = datetime.now(timezone.utc)
        snapshot = ContentMetricsSnapshot(
            profile_id=self.profile.id,
            content_id=self.content.id,
            source_type=MetricsSourceType.MANUAL,
            views=1000,
            likes=120,
            comments_count=20,
            shares=10,
            favorites=8,
            avg_watch_time=13.1,
            completion_rate=0.45,
            publish_time=now - timedelta(days=2),
            collected_at=now,
        )
        created = self.runtime.metrics.ingest_metrics_snapshot(snapshot)
        self.assertGreater(created.engagement_rate, 0.0)
        self.assertGreater(created.weighted_engagement_score, 0.0)

        top = self.runtime.top_content.get_top_content(self.profile.id, window="30d", limit=5)
        self.assertGreaterEqual(len(top), 1)
        plan = self.runtime.planning.generate_next_content_plan(self.profile.id, window="30d")
        self.assertGreaterEqual(len(plan.next_actions), 1)

    def test_ai_perception_recommendation_learning_and_brief(self) -> None:
        frame = self.runtime.ai_perception.analyze_frame(
            profile_id=self.profile.id,
            source_kind=SourceType.SCREENSHOT,
            source_ref="hook_overlay_demo.png",
        )
        self.assertEqual(frame.profile_id, self.profile.id)

        recs = self.runtime.ai_recommendation.generate_explainable_recommendations(self.profile.id, limit=5)
        self.assertGreaterEqual(len(recs), 1)
        self.assertTrue(recs[0].rationale)

        feedback = self.runtime.ai_learning.ingest_user_feedback(
            profile_id=self.profile.id,
            recommendation_id=recs[0].id,
            feedback_status=RecommendationFeedbackStatus.ACCEPTED,
            manual_score=0.8,
        )
        self.assertEqual(feedback.feedback_status, RecommendationFeedbackStatus.ACCEPTED)

        outcome = self.runtime.ai_learning.ingest_content_performance_feedback(
            profile_id=self.profile.id,
            recommendation_id=recs[0].id,
            content_id=self.content.id,
            metrics_snapshot_ids=[],
            outcome_label=OutcomeLabel.SUCCESS,
            outcome_summary="good outcome",
        )
        self.assertEqual(outcome.outcome_label, OutcomeLabel.SUCCESS)

        summary = self.runtime.ai_learning.summarize_learnings(self.profile.id)
        self.assertGreaterEqual(summary.get("total_records", 0), 0)

        brief = self.runtime.generation_prep.generate_video_brief(
            profile_id=self.profile.id,
            content_goal="Improve retention",
            creative_angle="tactical minimal",
            hook="Most creators lose viewers at second 3",
            format_target="9:16",
            duration_target="20-30s",
        )
        self.assertEqual(brief.profile_id, self.profile.id)
        bundle = self.runtime.generation_prep.build_generation_bundle(
            profile_id=self.profile.id,
            content_goal="Improve retention",
            creative_angle="tactical minimal",
            format_target="9:16",
            duration_target="20-30s",
        )
        self.assertTrue(bundle.generation_ready_flag)


if __name__ == "__main__":
    unittest.main()

