from __future__ import annotations

import importlib.util
from pathlib import Path


def run_legacy_entry() -> None:
    """Compatibility entrypoint.

    Keeps existing UI/runtime behavior while project is being migrated to modules.
    """
    root = Path(__file__).resolve().parents[3]
    legacy_file = root / "voice_launcher.py"
    if not legacy_file.exists():
        raise FileNotFoundError(f"Legacy entry file not found: {legacy_file}")
    spec = importlib.util.spec_from_file_location("voice_launcher_legacy_entry", legacy_file)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load legacy entrypoint")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def main() -> None:
    run_legacy_entry()


if __name__ == "__main__":
    main()

