from __future__ import annotations

from app.startup_manager import StartupManager


def test_startup_manager_local_init():
    manager = StartupManager()
    context = manager.initialize_local_runtime()
    assert context.workspace_runtime.repository is not None
    assert "overall_ready" in context.readiness

