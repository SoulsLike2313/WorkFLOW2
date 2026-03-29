from __future__ import annotations

from types import SimpleNamespace

from app.user_mode_orchestrator import UserModeOrchestrator


class _FakeProbe:
    def __init__(self, ready: bool, reason: str = "none", recovery: str = "none") -> None:
        self.ready = ready
        self.failure_reason = reason
        self.recovery_signal = recovery

    def as_dict(self):
        return {
            "ready": self.ready,
            "failure_reason": self.failure_reason,
            "recovery_signal": self.recovery_signal,
        }


class _FakeManager:
    def __init__(self, *, readiness_ok: bool = True, probe_ready: bool = True) -> None:
        self.config = SimpleNamespace(api_host="127.0.0.1", api_port=8123, mode="developer")
        self._readiness_ok = readiness_ok
        self._probe_ready = probe_ready
        self.start_called = False
        self.stop_called = False

    def initialize_local_runtime(self):
        return SimpleNamespace(readiness={"overall_ready": self._readiness_ok})

    def start_internal_backend(self):
        self.start_called = True
        return 1

    def probe_backend_readiness(self):
        if self._probe_ready:
            return _FakeProbe(ready=True)
        return _FakeProbe(ready=False, reason="backend_timeout", recovery="inspect_backend_logs")

    def stop_internal_backend(self):
        self.stop_called = True


def test_orchestrator_stops_when_gate_fails():
    manager = _FakeManager(readiness_ok=True, probe_ready=True)
    orchestrator = UserModeOrchestrator(
        startup_manager=manager,
        gate_runner=lambda: 1,
        window_runner=lambda _api: 0,
    )
    code = orchestrator.run(skip_gate_check=False)
    assert code == 1
    assert manager.start_called is False


def test_orchestrator_returns_failure_when_probe_not_ready():
    manager = _FakeManager(readiness_ok=True, probe_ready=False)
    orchestrator = UserModeOrchestrator(
        startup_manager=manager,
        gate_runner=lambda: 0,
        window_runner=lambda _api: 0,
    )
    code = orchestrator.run(skip_gate_check=False)
    assert code == 1
    assert manager.start_called is True
    assert manager.stop_called is True


def test_orchestrator_runs_window_with_api_base():
    manager = _FakeManager(readiness_ok=True, probe_ready=True)
    seen: dict[str, str] = {}

    def _window(api_base: str) -> int:
        seen["api_base"] = api_base
        return 0

    orchestrator = UserModeOrchestrator(
        startup_manager=manager,
        gate_runner=lambda: 0,
        window_runner=_window,
    )
    code = orchestrator.run(skip_gate_check=False)
    assert code == 0
    assert seen["api_base"] == "http://127.0.0.1:8123"
    assert manager.stop_called is True
