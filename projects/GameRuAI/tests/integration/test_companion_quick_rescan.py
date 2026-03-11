from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path


def test_create_companion_session_and_quick_rescan(services, tmp_path: Path) -> None:
    game_root = tmp_path / "mini_game"
    texts_dir = game_root / "texts"
    texts_dir.mkdir(parents=True, exist_ok=True)
    file_path = texts_dir / "tutorial.txt"
    file_path.write_text("L1|NPC_A|tutorial||tutorial|Press [E] now.\n", encoding="utf-8")

    project = services.ensure_project("Companion Mini Game", game_root)
    pid = int(project["id"])
    services.scan(pid, game_root)
    services.extract(pid, game_root)
    before = services.repo.list_entries(pid, limit=100)
    assert before

    session = services.launch_companion(
        project_id=pid,
        executable_path=Path(sys.executable),
        watched_path=game_root,
        args=["-c", "import time; time.sleep(20)"],
    )
    session_id = str(session["session_id"])

    time.sleep(0.05)
    file_path.write_text(
        "L1|NPC_A|tutorial||tutorial|Press [E] now.\nL2|NPC_A|tutorial||tutorial|Hold [E] for quick action.\n",
        encoding="utf-8",
    )
    polled = services.poll_companion(project_id=pid, session_id=session_id, game_root=game_root)
    assert polled["events"]
    assert polled["quick_reindexed_entries"] >= 1

    after = services.repo.list_entries(pid, limit=200)
    assert len(after) >= len(before)

    services.stop_companion(project_id=pid, session_id=session_id)
