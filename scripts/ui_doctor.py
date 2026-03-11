from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    target = repo_root / "projects" / "wild_hunt_command_citadel" / "shortform_core" / "scripts" / "ui_doctor.py"
    if not target.exists():
        print(f"Target script not found: {target}")
        return 2

    sys.argv = [str(target), *sys.argv[1:]]
    try:
        runpy.run_path(str(target), run_name="__main__")
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
