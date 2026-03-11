from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Sequence

from .desktop.main import run_user_window
from .startup_manager import StartupManager
from .workspace.diagnostics import diag_log


def _run_user_mode() -> int:
    manager = StartupManager()
    manager.config.mode = "user"
    context = manager.initialize_local_runtime()
    if not context.readiness.get("overall_ready", False):
        print("User mode startup failed: local readiness is degraded.")
        print(context.readiness)
        return 1

    manager.start_internal_backend()
    ready = manager.wait_backend_ready()
    if not ready:
        print("User mode startup failed: internal backend did not reach ready state.")
        manager.stop_internal_backend()
        return 1

    api_base = f"http://{manager.config.api_host}:{manager.config.api_port}"
    diag_log("runtime_logs", "user_mode_window_open", payload={"api_base": api_base})
    try:
        code = run_user_window(api_base_url=api_base)
    finally:
        manager.stop_internal_backend()
    return code


def _run_developer_backend(host: str, port: int) -> int:
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.api:app",
        "--host",
        host,
        "--port",
        str(port),
        "--reload",
    ]
    return subprocess.call(cmd)


def _run_developer_ui(api_base_url: str) -> int:
    return run_user_window(api_base_url=api_base_url)


def _run_developer_verify() -> int:
    return subprocess.call([sys.executable, "-m", "app.verify"])


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Shortform launcher")
    sub = parser.add_subparsers(dest="mode", required=True)

    sub.add_parser("user", help="User mode: desktop app with internal backend orchestration")

    dev = sub.add_parser("developer", help="Developer mode: explicit controls")
    dev_sub = dev.add_subparsers(dest="dev_cmd", required=True)

    dev_backend = dev_sub.add_parser("backend", help="Run backend API")
    dev_backend.add_argument("--host", default="127.0.0.1")
    dev_backend.add_argument("--port", type=int, default=8000)

    dev_ui = dev_sub.add_parser("ui", help="Run desktop UI only")
    dev_ui.add_argument("--api-base-url", default="http://127.0.0.1:8000")

    dev_sub.add_parser("verify", help="Run machine verification pipeline")

    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.mode == "user":
        return _run_user_mode()
    if args.mode == "developer":
        if args.dev_cmd == "backend":
            return _run_developer_backend(args.host, args.port)
        if args.dev_cmd == "ui":
            return _run_developer_ui(args.api_base_url)
        if args.dev_cmd == "verify":
            return _run_developer_verify()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
