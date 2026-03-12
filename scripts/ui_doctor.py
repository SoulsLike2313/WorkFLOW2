from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    core_root = (
        repo_root
        / "projects"
        / "wild_hunt_command_citadel"
        / "tiktok_agent_platform"
        / "core"
    )
    target = (
        core_root
        / "scripts"
        / "ui_doctor.py"
    )
    if not target.exists():
        print(f"Target script not found: {target}")
        return 2

    venv_python = core_root / ".venv" / "Scripts" / "python.exe"
    python_exe = str(venv_python) if venv_python.exists() else (sys.executable or "python")
    completed = subprocess.run([python_exe, str(target), *sys.argv[1:]], cwd=core_root, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
