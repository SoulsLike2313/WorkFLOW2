from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable

from .startup_manager import StartupManager
from .workspace.diagnostics import diag_log


def run_default_machine_gate() -> int:
    return subprocess.call([sys.executable, "-m", "app.verify"])


class UserModeOrchestrator:
    def __init__(
        self,
        *,
        startup_manager: StartupManager | None = None,
        gate_runner: Callable[[], int] | None = None,
        window_runner: Callable[[str], int],
    ) -> None:
        self.startup_manager = startup_manager or StartupManager()
        self.gate_runner = gate_runner or run_default_machine_gate
        self.window_runner = window_runner

    def run(self, *, skip_gate_check: bool = False) -> int:
        if not skip_gate_check:
            verify_code = int(self.gate_runner())
            if verify_code != 0:
                print("Machine Verification Gate did not return PASS. User mode launch aborted.")
                return 1

        manager = self.startup_manager
        manager.config.mode = "user"
        context = manager.initialize_local_runtime()
        if not context.readiness.get("overall_ready", False):
            print("User mode startup failed: local readiness is degraded.")
            print(context.readiness)
            return 1

        manager.start_internal_backend()
        probe = manager.probe_backend_readiness()
        if not probe.ready:
            print("User mode startup failed: internal backend did not reach ready state.")
            print(
                {
                    "failure_reason": probe.failure_reason,
                    "recovery_signal": probe.recovery_signal,
                }
            )
            manager.stop_internal_backend()
            return 1

        api_base = f"http://{manager.config.api_host}:{manager.config.api_port}"
        diag_log(
            "runtime_logs",
            "user_mode_window_open",
            payload={"api_base": api_base, "backend_probe": probe.as_dict()},
        )
        try:
            code = self.window_runner(api_base)
        finally:
            manager.stop_internal_backend()
        return int(code)
