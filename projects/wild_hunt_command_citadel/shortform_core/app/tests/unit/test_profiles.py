from __future__ import annotations

import unittest

from app.tests.helpers import build_runtime
from app.workspace.errors import LimitExceededError
from app.workspace.models import (
    ConnectionStatus,
    ConnectionType,
    ManagementMode,
    Platform,
    ProfileStatus,
)


class ProfileServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = build_runtime(max_profiles=2)

    def test_create_profile_and_get(self) -> None:
        created = self.runtime.profiles.create_profile(
            display_name="Alpha",
            platform=Platform.TIKTOK,
            connection_type=ConnectionType.CDP,
            management_mode=ManagementMode.MANUAL,
            notes="demo",
            tags=["a"],
        )

        fetched = self.runtime.profiles.get_profile(created.id)
        connection = self.runtime.profiles.get_connection(created.id)
        self.assertEqual(fetched.display_name, "Alpha")
        self.assertEqual(fetched.status, ProfileStatus.DISCONNECTED)
        self.assertEqual(connection.profile_id, created.id)

    def test_max_profiles_limit(self) -> None:
        self.runtime.profiles.create_profile(
            display_name="One",
            platform=Platform.TIKTOK,
            connection_type=ConnectionType.CDP,
            management_mode=ManagementMode.MANUAL,
        )
        self.runtime.profiles.create_profile(
            display_name="Two",
            platform=Platform.TIKTOK,
            connection_type=ConnectionType.DEVICE,
            management_mode=ManagementMode.MANUAL,
        )

        with self.assertRaises(LimitExceededError):
            self.runtime.profiles.create_profile(
                display_name="Three",
                platform=Platform.TIKTOK,
                connection_type=ConnectionType.OFFICIAL_AUTH,
                management_mode=ManagementMode.MANUAL,
            )

    def test_set_management_mode(self) -> None:
        profile = self.runtime.profiles.create_profile(
            display_name="ModeTest",
            platform=Platform.TIKTOK,
            connection_type=ConnectionType.CDP,
            management_mode=ManagementMode.MANUAL,
        )
        updated = self.runtime.profiles.set_management_mode(profile.id, ManagementMode.GUIDED)
        self.assertEqual(updated.management_mode, ManagementMode.GUIDED)

    def test_connect_profile_updates_connection(self) -> None:
        profile = self.runtime.profiles.create_profile(
            display_name="ConnectTest",
            platform=Platform.TIKTOK,
            connection_type=ConnectionType.CDP,
            management_mode=ManagementMode.MANUAL,
        )
        connection = self.runtime.profiles.connect_profile(
            profile.id,
            cdp_url="ws://127.0.0.1:9222/devtools/browser/demo",
            confirmed=True,
        )
        self.assertIn(connection.connection_status, {ConnectionStatus.CONNECTED, ConnectionStatus.ERROR})
        self.assertEqual(connection.cdp_url, "ws://127.0.0.1:9222/devtools/browser/demo")


if __name__ == "__main__":
    unittest.main()

