from __future__ import annotations

from pathlib import Path

import pytest

from app.workspace.runtime import WorkspaceRuntime, build_workspace_runtime


@pytest.fixture()
def runtime(tmp_path: Path) -> WorkspaceRuntime:
    logs = tmp_path / "logs"
    persistence = tmp_path / "workspace_state.db"
    return build_workspace_runtime(
        max_profiles=10,
        log_dir=logs,
        debug_logs=True,
        persistence_path=persistence,
    )

