from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .exceptions import ConfigurationError


def find_repo_root(start: Path) -> Path:
    cursor = start.resolve()
    for node in [cursor, *cursor.parents]:
        if (node / "workspace_config" / "workspace_manifest.json").exists():
            return node
    raise ConfigurationError("Cannot locate repository root from project path.")


@dataclass(frozen=True, slots=True)
class PathSet:
    repo_root: Path
    project_root: Path
    runtime_root: Path
    logs_dir: Path
    data_dir: Path
    diagnostics_dir: Path
    exports_dir: Path
    db_path: Path
    fixtures_root: Path

    @classmethod
    def from_project_root(cls, project_root: Path) -> "PathSet":
        repo_root = find_repo_root(project_root)
        manifest_path = project_root / "PROJECT_MANIFEST.json"
        if not manifest_path.exists():
            raise ConfigurationError(f"Missing PROJECT_MANIFEST.json at {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        runtime_paths = manifest.get("runtime_paths", {})
        state_paths = manifest.get("state_paths", {})

        runtime_root = repo_root / str(runtime_paths.get("runtime_dir", "runtime/projects/game_ru_ai"))
        logs_dir = repo_root / str(runtime_paths.get("log_dir", runtime_root / "logs"))
        data_dir = repo_root / str(runtime_paths.get("data_dir", runtime_root / "data"))
        diagnostics_dir = repo_root / str(runtime_paths.get("diagnostics_dir", runtime_root / "diagnostics"))
        db_path = repo_root / str(state_paths.get("db_path", runtime_root / "db/game_ru_ai.db"))
        exports_dir = project_root / "runtime" / "exports"
        fixtures_root = project_root / "fixtures" / "demo_game_world"

        for folder in (runtime_root, logs_dir, data_dir, diagnostics_dir, db_path.parent, exports_dir, fixtures_root):
            folder.mkdir(parents=True, exist_ok=True)

        return cls(
            repo_root=repo_root,
            project_root=project_root,
            runtime_root=runtime_root,
            logs_dir=logs_dir,
            data_dir=data_dir,
            diagnostics_dir=diagnostics_dir,
            exports_dir=exports_dir,
            db_path=db_path,
            fixtures_root=fixtures_root,
        )
