from __future__ import annotations

import unittest

from app.tests.helpers import build_runtime
from app.workspace.models import (
    AttachedSourceType,
    ConnectionType,
    ManagementMode,
    Platform,
    SessionRuntimeState,
    ViewportPreset,
)


class SessionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = build_runtime()
        self.profile = self.runtime.profiles.create_profile(
            display_name="SessionProfile",
            platform=Platform.TIKTOK,
            connection_type=ConnectionType.CDP,
            management_mode=ManagementMode.MANUAL,
        )

    def test_open_and_restore_session(self) -> None:
        session = self.runtime.sessions.open_session_window(
            self.profile.id,
            viewport_preset=ViewportPreset.SMARTPHONE_DEFAULT,
            attached_source_type=AttachedSourceType.CDP,
            attached_source_id="source-1",
            confirmed=True,
        )
        self.assertTrue(session.is_open)
        self.assertEqual(session.runtime_state, SessionRuntimeState.OPEN)
        self.assertEqual(session.aspect_ratio, "9:16")

        restored = self.runtime.sessions.restore_session_window(self.profile.id)
        self.assertTrue(restored.is_open)
        self.assertEqual(restored.attached_source_id, "source-1")

    def test_set_viewport_and_close(self) -> None:
        self.runtime.sessions.open_session_window(self.profile.id, confirmed=True)
        session = self.runtime.sessions.set_viewport_preset(
            self.profile.id,
            viewport_preset=ViewportPreset.IPHONE_LIKE,
        )
        self.assertEqual(session.viewport_preset, ViewportPreset.IPHONE_LIKE)
        self.assertGreater(session.width, 0)
        self.assertGreater(session.height, 0)

        closed = self.runtime.sessions.close_session_window(self.profile.id, confirmed=True)
        self.assertFalse(closed.is_open)
        self.assertEqual(closed.runtime_state, SessionRuntimeState.CLOSED)


if __name__ == "__main__":
    unittest.main()

