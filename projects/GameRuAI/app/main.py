from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.bootstrap import AppServices
from app.config import AppConfig
from app.ui.main_window import MainWindow


def ensure_demo_assets(config: AppConfig) -> None:
    marker = config.paths.fixtures_root / "texts" / "ui.json"
    if marker.exists():
        return
    # Import lazily to avoid script dependency during tests.
    scripts_dir = config.project_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from generate_demo_assets import generate_demo_assets

    generate_demo_assets(config.project_root)


def main() -> int:
    config = AppConfig.load()
    ensure_demo_assets(config)
    services = AppServices(config)

    app = QApplication(sys.argv)
    window = MainWindow(services)
    window.show()
    exit_code = app.exec()
    services.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
