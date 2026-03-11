from __future__ import annotations

import unittest

from app.tests.helpers import build_seeded_runtime


class WorkspaceFlowIntegrationTests(unittest.TestCase):
    def test_seeded_runtime_full_flow(self) -> None:
        runtime, seed_summary = build_seeded_runtime()
        profile_id = seed_summary["profile_id"]

        workspace_summary = runtime.repository.build_summary()
        self.assertGreaterEqual(workspace_summary.profile_count, 1)
        self.assertGreaterEqual(workspace_summary.queued_content_items, 1)
        self.assertGreaterEqual(workspace_summary.open_session_windows, 1)

        patterns = runtime.intelligence.extract_patterns(profile_id, window="30d")
        self.assertGreaterEqual(len(patterns), 1)

        top_content = runtime.top_content.get_top_content(profile_id, window="30d", limit=5)
        self.assertGreaterEqual(len(top_content), 1)

        learnings = runtime.ai_learning.summarize_learnings(profile_id)
        self.assertGreaterEqual(learnings.get("feedback_count", 0), 1)

        bundles = runtime.generation_prep.list_generation_bundles(profile_id, limit=10)
        self.assertGreaterEqual(len(bundles), 1)


if __name__ == "__main__":
    unittest.main()

