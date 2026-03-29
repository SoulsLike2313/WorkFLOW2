from __future__ import annotations

import unittest

try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
except ModuleNotFoundError:
    FastAPI = None
    TestClient = None

if FastAPI is not None and TestClient is not None:
    from app.workspace.api import build_workspace_router
else:
    build_workspace_router = None
from app.workspace.runtime import build_workspace_runtime


@unittest.skipUnless(
    FastAPI is not None and TestClient is not None and build_workspace_router is not None,
    "fastapi runtime dependency is required for API smoke tests",
)
class WorkspaceAPISmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        runtime = build_workspace_runtime(debug_logs=True)
        app = FastAPI()
        app.include_router(build_workspace_router(runtime))
        self.client = TestClient(app)

    def test_workspace_profile_session_content_analytics_flow(self) -> None:
        health = self.client.get("/workspace/health")
        self.assertEqual(health.status_code, 200)
        prompt_lineage = self.client.get("/workspace/prompt-lineage")
        self.assertEqual(prompt_lineage.status_code, 200)
        self.assertIn("lineage_id", prompt_lineage.json())
        runtime_observability = self.client.get("/workspace/runtime-observability")
        self.assertEqual(runtime_observability.status_code, 200)
        self.assertIn("process_state", runtime_observability.json())

        profile_resp = self.client.post(
            "/workspace/profiles",
            json={
                "display_name": "SmokeProfile",
                "platform": "tiktok",
                "connection_type": "cdp",
                "management_mode": "guided",
                "notes": "smoke",
                "tags": ["smoke"],
            },
        )
        self.assertEqual(profile_resp.status_code, 200)
        profile_id = profile_resp.json()["profile"]["id"]

        open_resp = self.client.post(
            f"/workspace/sessions/{profile_id}/open",
            json={"viewport_preset": "smartphone_default", "confirmed": True},
        )
        self.assertEqual(open_resp.status_code, 200)

        content_resp = self.client.post(
            "/workspace/content",
            json={
                "profile_id": profile_id,
                "local_path": "demo_assets/smoke.mp4",
                "title": "Smoke test video",
                "caption": "caption",
                "duration": 20,
                "content_type": "video",
                "format_label": "talking_head",
                "topic_label": "smoke",
                "hook_label": "hook",
                "cta_label": "cta",
            },
        )
        self.assertEqual(content_resp.status_code, 200)
        content_id = content_resp.json()["item"]["id"]

        validate_resp = self.client.post(f"/workspace/content/{content_id}/validate")
        self.assertEqual(validate_resp.status_code, 200)

        queue_resp = self.client.post(
            f"/workspace/content/{content_id}/queue",
            json={"confirmed": True},
        )
        self.assertEqual(queue_resp.status_code, 200)

        metrics_resp = self.client.post(
            "/workspace/metrics/ingest",
            json={
                "profile_id": profile_id,
                "content_id": content_id,
                "source_type": "manual_metrics_provider",
                "views": 1000,
                "likes": 120,
                "comments_count": 12,
                "shares": 8,
                "favorites": 6,
                "avg_watch_time": 11.2,
                "completion_rate": 0.41,
            },
        )
        self.assertEqual(metrics_resp.status_code, 200)

        perf_resp = self.client.get(f"/workspace/analytics/profiles/{profile_id}/performance")
        self.assertEqual(perf_resp.status_code, 200)

        plan_resp = self.client.post(
            f"/workspace/analytics/profiles/{profile_id}/action-plan",
            json={"window": "30d"},
        )
        self.assertEqual(plan_resp.status_code, 200)

    def test_workspace_ai_and_generation_endpoints(self) -> None:
        profile_resp = self.client.post(
            "/workspace/profiles",
            json={
                "display_name": "AISmokeProfile",
                "platform": "tiktok",
                "connection_type": "cdp",
                "management_mode": "guided",
                "notes": "",
                "tags": [],
            },
        )
        self.assertEqual(profile_resp.status_code, 200)
        profile_id = profile_resp.json()["profile"]["id"]

        content_resp = self.client.post(
            "/workspace/content",
            json={
                "profile_id": profile_id,
                "local_path": "demo_assets/ai_smoke.mp4",
                "title": "AI smoke video",
                "caption": "caption",
                "duration": 26,
                "content_type": "video",
                "format_label": "visual_demo",
                "topic_label": "ai",
                "hook_label": "hook",
                "cta_label": "cta",
            },
        )
        self.assertEqual(content_resp.status_code, 200)
        content_id = content_resp.json()["item"]["id"]

        frame_resp = self.client.post(
            "/workspace/ai/analyze/frame",
            json={"profile_id": profile_id, "source_kind": "screenshot", "source_ref": "frame_hook_caption.png"},
        )
        self.assertEqual(frame_resp.status_code, 200)

        asset_resp = self.client.post(
            "/workspace/ai/analyze/asset",
            json={"profile_id": profile_id, "source_ref": "asset_preview_variant.png"},
        )
        self.assertEqual(asset_resp.status_code, 200)

        eval_resp = self.client.post(
            "/workspace/ai/evaluate/content",
            json={"content_id": content_id},
        )
        self.assertEqual(eval_resp.status_code, 200)

        rec_resp = self.client.post(
            "/workspace/ai/recommendations/generate",
            json={"profile_id": profile_id, "limit": 5},
        )
        self.assertEqual(rec_resp.status_code, 200)
        recommendation_id = rec_resp.json()["items"][0]["id"]

        feedback_resp = self.client.post(
            "/workspace/ai/feedback/recommendation",
            json={
                "profile_id": profile_id,
                "recommendation_id": recommendation_id,
                "feedback_status": "accepted",
                "manual_score": 0.8,
            },
        )
        self.assertEqual(feedback_resp.status_code, 200)

        generic_feedback = self.client.post(
            "/workspace/ai/feedback/ingest",
            json={
                "profile_id": profile_id,
                "learning_type": "user_feedback",
                "input_ref": recommendation_id,
                "outcome_summary": "accepted",
                "adjustment_summary": "positive",
                "confidence_delta": 0.05,
            },
        )
        self.assertEqual(generic_feedback.status_code, 200)

        video_brief = self.client.post(
            f"/workspace/profiles/{profile_id}/generation/video-brief",
            json={
                "profile_id": profile_id,
                "source_recommendation_ids": [],
                "creative_goal": "Improve retention",
                "target_format": "9:16",
                "target_duration": "20-30s",
                "visual_style": "premium dark",
                "hook": "Most creators lose viewers in second 3",
                "cta": "Save this",
            },
        )
        self.assertEqual(video_brief.status_code, 200)

        audio_brief = self.client.post(
            f"/workspace/profiles/{profile_id}/generation/audio-brief",
            json={"content_goal": "Improve retention", "music_mood": "pulse", "voice_style": "clear"},
        )
        self.assertEqual(audio_brief.status_code, 200)

        script_brief = self.client.post(
            f"/workspace/profiles/{profile_id}/generation/script-brief",
            json={"content_goal": "Improve retention", "hook": "Hook", "cta": "Save"},
        )
        self.assertEqual(script_brief.status_code, 200)

        text_brief = self.client.post(
            f"/workspace/profiles/{profile_id}/generation/text-brief",
            json={"content_goal": "Improve retention", "cta_options": ["Save this"]},
        )
        self.assertEqual(text_brief.status_code, 200)

        bundle_build = self.client.post(
            f"/workspace/profiles/{profile_id}/generation/bundles/build",
            json={
                "content_goal": "Improve retention",
                "creative_angle": "tactical",
                "format_target": "9:16",
                "duration_target": "20-30s",
            },
        )
        self.assertEqual(bundle_build.status_code, 200)

        bundles = self.client.get(f"/workspace/profiles/{profile_id}/generation/bundles")
        self.assertEqual(bundles.status_code, 200)
        self.assertGreaterEqual(len(bundles.json()["items"]), 1)


if __name__ == "__main__":
    unittest.main()
