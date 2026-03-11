from __future__ import annotations

import sys
from pathlib import Path


def test_translation_pipeline_still_runs(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)
    services.extract(pid, root)
    services.detect_languages(pid)
    result = services.translate(pid, backend_name="local_mock")
    assert result["translated"] >= 300


def test_companion_mode_still_runs(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    session = services.launch_companion(
        project_id=pid,
        executable_path=Path(sys.executable),
        watched_path=root,
        args=["-c", "import time; time.sleep(2)"],
    )
    session_id = str(session["session_id"])
    polled = services.poll_companion(project_id=pid, session_id=session_id, game_root=root)
    assert "status" in polled
    services.stop_companion(project_id=pid, session_id=session_id)

