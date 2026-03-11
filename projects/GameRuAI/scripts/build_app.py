from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build GameRuAI desktop binary with PyInstaller.")
    parser.add_argument("--onefile", action="store_true", help="Build onefile executable.")
    parser.add_argument("--name", default="GameRuAI", help="Executable/app name.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    pyinstaller = shutil.which("pyinstaller")
    if not pyinstaller:
        print("[build_app] pyinstaller is not installed. Install requirements-dev first.")
        return 1

    cmd = [
        pyinstaller,
        "--noconfirm",
        "--name",
        args.name,
        "--windowed",
        "app/main.py",
    ]
    if args.onefile:
        cmd.append("--onefile")

    print("[build_app] running:", " ".join(cmd))
    return subprocess.call(cmd, cwd=str(project_root))


if __name__ == "__main__":
    raise SystemExit(main())
