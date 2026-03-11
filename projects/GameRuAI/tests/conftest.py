from __future__ import annotations

import sys
from pathlib import Path

import pytest

from app.bootstrap import AppServices
from app.config import AppConfig
from app.core.paths import PathSet


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def ensure_demo_assets(project_root: Path) -> None:
    scripts_dir = project_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from generate_demo_assets import generate_demo_assets

    generate_demo_assets(project_root)


@pytest.fixture
def services(tmp_path: Path, project_root: Path) -> AppServices:
    base = AppConfig.load()
    runtime_root = tmp_path / "runtime"
    logs_dir = runtime_root / "logs"
    data_dir = runtime_root / "data"
    diagnostics_dir = runtime_root / "diagnostics"
    exports_dir = tmp_path / "exports"
    db_path = tmp_path / "db" / "test.db"
    fixtures_root = project_root / "fixtures" / "demo_game_world"

    for folder in (runtime_root, logs_dir, data_dir, diagnostics_dir, exports_dir, db_path.parent):
        folder.mkdir(parents=True, exist_ok=True)

    paths = PathSet(
        repo_root=base.paths.repo_root,
        project_root=project_root,
        runtime_root=runtime_root,
        logs_dir=logs_dir,
        data_dir=data_dir,
        diagnostics_dir=diagnostics_dir,
        exports_dir=exports_dir,
        db_path=db_path,
        fixtures_root=fixtures_root,
    )
    config = AppConfig(app_name="GameRuAI-Test", project_root=project_root, paths=paths)
    svc = AppServices(config)
    try:
        yield svc
    finally:
        svc.close()


@pytest.fixture
def demo_project(services: AppServices) -> dict:
    return services.ensure_project("Pytest Demo", services.config.paths.fixtures_root)
