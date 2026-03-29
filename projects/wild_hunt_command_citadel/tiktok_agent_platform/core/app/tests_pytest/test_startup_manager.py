from __future__ import annotations

from app.startup_manager import StartupManager


def test_startup_manager_local_init():
    manager = StartupManager()
    context = manager.initialize_local_runtime()
    assert context.workspace_runtime.repository is not None
    assert "overall_ready" in context.readiness


def test_startup_manager_probe_has_explicit_failure_reason():
    manager = StartupManager()

    class ExitedProc:
        returncode = 17

        def poll(self):
            return self.returncode

    manager._backend_proc = ExitedProc()  # type: ignore[assignment]
    probe = manager.probe_backend_readiness(timeout_seconds=0.1, host="127.0.0.1", port=8123)
    assert probe.ready is False
    assert probe.failure_reason == "backend_process_exited_before_ready"
    assert probe.recovery_signal == "restart_backend_and_validate_port_binding"
    assert manager.get_last_backend_probe().get("failure_reason") == "backend_process_exited_before_ready"
