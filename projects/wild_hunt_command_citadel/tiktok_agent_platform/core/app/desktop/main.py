from __future__ import annotations

import argparse
import sys

from PySide6.QtWidgets import QApplication

from .user_window import UserWorkspaceWindow


def run_user_window(*, api_base_url: str) -> int:
    app = QApplication(sys.argv)
    window = UserWorkspaceWindow(api_base_url=api_base_url)
    window.show()
    return app.exec()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Shortform desktop user workspace")
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args(argv)
    return run_user_window(api_base_url=args.api_base_url)


if __name__ == "__main__":
    raise SystemExit(main())

