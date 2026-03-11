from __future__ import annotations

import time
from pathlib import Path


def test_file_watch_event_capture(services, demo_project, tmp_path: Path) -> None:
    pid = int(demo_project["id"])
    watched = tmp_path / "watched"
    watched.mkdir(parents=True, exist_ok=True)
    session_id = "test-session-watch"

    services.file_watch_service.start_watch(project_id=pid, session_id=session_id, watched_path=watched)
    target = watched / "dialogue.txt"
    target.write_text("hello", encoding="utf-8")
    time.sleep(0.02)
    target.write_text("hello updated", encoding="utf-8")

    events = services.file_watch_service.poll(session_id)
    event_types = {event["event_type"] for event in events}
    assert event_types.intersection({"created", "modified"})

    stored = services.repo.list_watched_file_events(pid, session_id=session_id)
    assert stored
