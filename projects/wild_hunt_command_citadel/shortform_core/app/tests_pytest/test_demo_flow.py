from __future__ import annotations

from app.workspace.demo_seed import seed_workspace_runtime


def test_demo_seed_flow(runtime):
    summary = seed_workspace_runtime(runtime)
    assert summary["profile_id"]
    assert len(summary["content_ids"]) >= 2
    assert "generation" in summary

