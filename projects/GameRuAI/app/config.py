from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .core.paths import PathSet


@dataclass(frozen=True, slots=True)
class AppConfig:
    app_name: str
    project_root: Path
    paths: PathSet
    default_project_name: str = "Demo GameRuAI Project"

    @classmethod
    def load(cls) -> "AppConfig":
        project_root = Path(__file__).resolve().parents[1]
        paths = PathSet.from_project_root(project_root)
        return cls(app_name="GameRuAI", project_root=project_root, paths=paths)
