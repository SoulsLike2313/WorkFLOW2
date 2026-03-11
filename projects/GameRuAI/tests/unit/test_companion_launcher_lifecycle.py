from __future__ import annotations

import sys
from pathlib import Path


def test_companion_session_lifecycle(services, demo_project, tmp_path: Path) -> None:
    pid = int(demo_project["id"])
    watched = services.config.paths.fixtures_root
    session = services.launch_companion(
        project_id=pid,
        executable_path=Path(sys.executable),
        watched_path=watched,
        args=["-c", "import time; time.sleep(20)"],
    )

    session_id = str(session["session_id"])
    polled = services.poll_companion(project_id=pid, session_id=session_id, game_root=watched)
    assert "status" in polled
    assert polled["session"] is not None

    stopped = services.stop_companion(project_id=pid, session_id=session_id)
    assert "stopped" in str(stopped.get("process_status", "")) or "exited" in str(stopped.get("process_status", ""))
