from __future__ import annotations

import unittest

from app.tests.helpers import build_runtime
from app.workspace.models import (
    ConnectionType,
    ContentItem,
    ContentStatus,
    ManagementMode,
    Platform,
    ValidationState,
)


class ContentServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = build_runtime()
        self.profile = self.runtime.profiles.create_profile(
            display_name="ContentProfile",
            platform=Platform.TIKTOK,
            connection_type=ConnectionType.CDP,
            management_mode=ManagementMode.GUIDED,
        )

    def test_validate_and_queue_content(self) -> None:
        item = self.runtime.content.add_content_item(
            ContentItem(
                profile_id=self.profile.id,
                local_path="demo_assets/video_a.mp4",
                title="Demo video",
                caption="caption",
                duration=22,
                format_label="talking_head",
                topic_label="strategy",
                hook_label="stop_scrolling",
                cta_label="save",
            )
        )
        result = self.runtime.content.validate_content_item(item.id)
        self.assertIn(result["validation_state"], {"valid", "warning"})

        queued = self.runtime.content.queue_content_item(item.id, confirmed=True)
        self.assertEqual(queued.status, ContentStatus.QUEUED)

    def test_invalid_content_moves_to_failed_on_queue(self) -> None:
        item = self.runtime.content.add_content_item(
            ContentItem(
                profile_id=self.profile.id,
                local_path="",
                title="",
            )
        )
        result = self.runtime.content.validate_content_item(item.id)
        self.assertEqual(result["validation_state"], ValidationState.INVALID.value)
        queued = self.runtime.content.queue_content_item(item.id, confirmed=True)
        self.assertEqual(queued.status, ContentStatus.FAILED)


if __name__ == "__main__":
    unittest.main()

