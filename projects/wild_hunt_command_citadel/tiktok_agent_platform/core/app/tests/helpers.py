from __future__ import annotations

from pathlib import Path

from app.workspace.demo_seed import seed_workspace_runtime
from app.workspace.runtime import WorkspaceRuntime, build_workspace_runtime


def build_runtime(*, max_profiles: int = 10, log_dir: Path | None = None) -> WorkspaceRuntime:
    return build_workspace_runtime(max_profiles=max_profiles, log_dir=log_dir, debug_logs=True)


def build_seeded_runtime(*, max_profiles: int = 10, log_dir: Path | None = None) -> tuple[WorkspaceRuntime, dict]:
    runtime = build_runtime(max_profiles=max_profiles, log_dir=log_dir)
    seed_summary = seed_workspace_runtime(runtime)
    return runtime, seed_summary

