from __future__ import annotations

import pytest

from app.workspace.errors import LimitExceededError
from app.workspace.models import ConnectionType, ManagementMode, Platform
from app.workspace.runtime import build_workspace_runtime


def test_profile_limit(tmp_path):
    rt = build_workspace_runtime(
        max_profiles=2,
        log_dir=tmp_path / "logs",
        debug_logs=True,
        persistence_path=tmp_path / "workspace_state.db",
    )
    rt.profiles.create_profile(
        display_name="One",
        platform=Platform.TIKTOK,
        connection_type=ConnectionType.CDP,
        management_mode=ManagementMode.MANUAL,
    )
    rt.profiles.create_profile(
        display_name="Two",
        platform=Platform.TIKTOK,
        connection_type=ConnectionType.DEVICE,
        management_mode=ManagementMode.GUIDED,
    )
    with pytest.raises(LimitExceededError):
        rt.profiles.create_profile(
            display_name="Three",
            platform=Platform.TIKTOK,
            connection_type=ConnectionType.OFFICIAL_AUTH,
            management_mode=ManagementMode.MANAGED,
        )

