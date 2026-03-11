# GameRuAI (Desktop MVP Demo)

GameRuAI is a local desktop demo tool that scans a game-like fixture, extracts multilingual text lines, detects source language, translates to Russian, performs mock Russian voice attempts, and shows transparent learning/adaptation behavior through glossary, translation memory, and user corrections.

## Tech Stack
- Python 3.11+
- PySide6
- SQLite
- pytest
- structured logging
- pathlib
- modular architecture

## Project Layout
- `app/` main application modules (UI + services + pipeline)
- `fixtures/demo_game_world/` generated demo mini-game data
- `scripts/` utility scripts for dev run / build / fixture generation
- `tests/` unit, integration, regression tests
- `docs/` architecture and usage docs

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

## Run Dev Mode
```powershell
python scripts/run_dev.py
```

Or directly:
```powershell
python -m app.main
```

## Open Demo Project In UI
1. Open `Project` tab.
2. Use `Use Demo Fixture` or set path to `fixtures/demo_game_world`.
3. Click `Create/Select Project`.
4. Quick way: click `Run Full Demo Pipeline` (one-click end-to-end).
5. Manual way: `Scan` -> `Extract Strings` -> `Detect Language` -> `Translate to Russian` -> `Generate Demo Voice Attempts`.

## Live Demo Mode
1. Go to `Live Demo` tab.
2. Select a scene from `scene_id :: title`.
3. Click `Start Live Demo`.
4. Observe stream: source -> detected lang -> translated RU -> voice status -> uncertainty.

## Learning / Adaptation Visibility
- `Translation` tab:
  - apply manual correction per `Entry ID`;
  - optionally add glossary pair.
- `Learning` tab:
  - correction history;
  - adaptation events;
  - terms learned / TM entries summary.
- `Glossary` tab:
  - view and add glossary terms.

## Run Tests
```powershell
pytest
```

## Build App
```powershell
python scripts/build_app.py
```

Optional one-file:
```powershell
python scripts/build_app.py --onefile
```

## Notes
- Original fixture files are never modified during export.
- Export artifacts are written into selected output folder (`patch/`, `export_manifest.json`, `diff_report.md`).
- Voice synthesis in this demo is explicitly `MOCK/STUB` (technical WAV generation, no real voice cloning).
