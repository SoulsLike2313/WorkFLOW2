from __future__ import annotations

from pathlib import Path

from app.workspace.models import ConnectionType, ManagementMode, Platform
from app.workspace.runtime import build_workspace_runtime


def test_workspace_repository_persistence_roundtrip(tmp_path: Path):
    db_path = tmp_path / "workspace_state.db"
    rt1 = build_workspace_runtime(
        max_profiles=10,
        log_dir=tmp_path / "logs_a",
        debug_logs=True,
        persistence_path=db_path,
    )
    profile = rt1.profiles.create_profile(
        display_name="Persisted",
        platform=Platform.TIKTOK,
        connection_type=ConnectionType.CDP,
        management_mode=ManagementMode.GUIDED,
    )

    rt2 = build_workspace_runtime(
        max_profiles=10,
        log_dir=tmp_path / "logs_b",
        debug_logs=True,
        persistence_path=db_path,
    )
    loaded = rt2.profiles.get_profile(profile.id)
    assert loaded.display_name == "Persisted"

