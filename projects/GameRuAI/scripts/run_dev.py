from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from generate_demo_assets import generate_demo_assets


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    summary = generate_demo_assets(project_root)
    print("[run_dev] demo assets ready:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    return subprocess.call([sys.executable, "-m", "app.main"], cwd=str(project_root), env=env)


if __name__ == "__main__":
    raise SystemExit(main())
