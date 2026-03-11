# GameRuAI (Desktop MVP Demo)

GameRuAI is a local desktop demo app for game localization experiments.
It scans fixture game data, extracts multilingual text, detects source language, translates to Russian, runs mock voice attempts, and shows transparent learning signals (TM, glossary, corrections).

## Stack
- Python 3.11+
- PySide6
- SQLite
- pytest
- structured logging
- pathlib

## What Is Working In This Sprint
- Translation backend router with graceful fallback:
  - `local_mock` (default, always available)
  - `dummy` (always available)
  - `argos` (optional)
  - `transformers` (optional)
- Context-aware translation pipeline:
  - context fields: speaker, scene, neighbor lines, line type, file group, style preset
  - context is passed to orchestrator/backend and persisted (`context_used`)
- Translation transparency:
  - active backend, fallback, latency, quality, uncertainty
  - glossary/TM usage and context usage in decision data
- Safe Companion Mode (sidecar only):
  - launch executable
  - bind session to project
  - watch file changes
  - quick re-index for changed text/config files
  - no runtime injection / memory hacking / binary patching

## Install
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

## Generate Demo Assets
```powershell
python scripts/generate_demo_assets.py --project-root .
```

## Run App
```powershell
python scripts/run_dev.py
```

Or directly:
```powershell
python -m app.main
```

## Open Demo Project
1. Open `Project` tab.
2. Use `Use Demo Fixture` or set `fixtures/demo_game_world`.
3. Click `Create/Select Project`.
4. Run `Run Full Demo Pipeline` or run steps manually.

## See Active Backend And Context
1. Open `Translation` tab.
2. Select backend (`local_mock` / `dummy` / `argos` / `transformers`).
3. Click `Translate to Russian`.
4. Check Backend Status block:
   - active backend
   - fallback used count
   - context used count
5. In translation table check columns: `Backend`, `Fallback`, `Context`, `Latency`, `Uncertainty`.
6. In `Entries` tab check `Context` column per row.

## Companion Mode (Working MVP)
1. Open `Companion` tab.
2. Set executable path (for demo you can use `python.exe`).
3. Set watched path (game folder).
4. Optional args example:
   ```
   -c "import time; time.sleep(60)"
   ```
5. Click `Launch Companion Session`.
6. Edit a text file inside watched path.
7. Click `Poll Status / Watch`.
8. Observe:
   - session status widget
   - quick re-index count
   - watched file events table

## Tests
Run all:
```powershell
pytest -q
```

Run sprint-specific tests:
```powershell
pytest -q tests/unit/test_context_builder.py tests/unit/test_backend_router_fallback.py tests/unit/test_companion_launcher_lifecycle.py tests/unit/test_file_watch_service.py tests/integration/test_translation_context_and_fallback.py tests/integration/test_companion_quick_rescan.py
```

## Build
```powershell
python scripts/build_app.py
```

Optional one-file:
```powershell
python scripts/build_app.py --onefile
```

## Honest Limits (Current Sprint)
- `argos`/`transformers` backends are optional adapters; if dependency is missing, fallback is used automatically.
- Voice generation is mock/stub (no real cloning model in this sprint).
- Companion quick re-index currently targets changed text/config assets only.
- No asset explorer, texture preview, or 3D preview in this sprint.
