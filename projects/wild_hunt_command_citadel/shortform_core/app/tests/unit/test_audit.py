from __future__ import annotations

import unittest

from app.tests.helpers import build_runtime
from app.workspace.errors import PolicyDeniedError
from app.workspace.models import ConnectionType, ContentItem, ManagementMode, Platform


class AuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = build_runtime()

    def test_audit_events_are_recorded(self) -> None:
        profile = self.runtime.profiles.create_profile(
            display_name="AuditProfile",
            platform=Platform.TIKTOK,
            connection_type=ConnectionType.CDP,
            management_mode=ManagementMode.GUIDED,
        )
        item = self.runtime.content.add_content_item(
            ContentItem(
                profile_id=profile.id,
                local_path="demo_assets/audit.mp4",
                title="audit",
                format_label="format",
                topic_label="topic",
                hook_label="hook",
                cta_label="cta",
            )
        )
        self.runtime.content.validate_content_item(item.id)
        self.runtime.content.queue_content_item(item.id, confirmed=True)

        audit_events = self.runtime.audit.list_audit(profile_id=profile.id, limit=20)
        self.assertGreaterEqual(len(audit_events), 3)

    def test_policy_denial_appears_in_error_log(self) -> None:
        profile = self.runtime.profiles.create_profile(
            display_name="PolicyProfile",
            platform=Platform.TIKTOK,
            connection_type=ConnectionType.CDP,
            management_mode=ManagementMode.MANUAL,
        )
        item = self.runtime.content.add_content_item(
            ContentItem(
                profile_id=profile.id,
                local_path="demo_assets/policy.mp4",
                title="policy",
            )
        )
        self.runtime.content.validate_content_item(item.id)

        with self.assertRaises(PolicyDeniedError):
            self.runtime.content.queue_content_item(item.id, confirmed=False)


if __name__ == "__main__":
    unittest.main()

