from __future__ import annotations

import pytest


def test_job_manager_marks_failure_and_resume(services) -> None:
    manager = services.job_manager

    with pytest.raises(RuntimeError):
        manager.run_job("scan", lambda: (_ for _ in ()).throw(RuntimeError("boom")))

    state = manager.get_job_state("scan")
    assert state is not None
    assert state["status"] == "failed"

    manager.run_job("scan", lambda: {"ok": True})
    resumed = manager.get_job_state("scan")
    assert resumed is not None
    assert resumed["status"] == "done"


def test_mark_interrupted_jobs(services) -> None:
    services.repo.set_setting(
        "job_state::translate",
        {"name": "translate", "status": "running", "started_at": "now", "finished_at": None, "error": None},
    )
    interrupted = services.job_manager.mark_interrupted_jobs()
    assert interrupted
    assert interrupted[0]["status"] == "interrupted"
