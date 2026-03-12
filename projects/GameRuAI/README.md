# GameRuAI (Desktop MVP Demo)

GameRuAI is a local desktop demo app for game localization workflows.
Current MVP includes translation + learning loop, companion mode, asset research, voice preparation, and project diagnostics.

## Stack
- Python 3.11+
- PySide6
- SQLite
- pytest
- structured logging
- pathlib

## Working Modules
- Product HUD (top status shell):
  - project/game path context
  - active backend + fallback visibility
  - pipeline stage status (`scan/extract/detect/translate/voice/export/reports/diagnostics`)
  - companion session visibility
  - translation/language/QA/voice summary metrics
  - language bottlenecks summary
  - quick actions (`Scan`, `Detect`, `Translate`, `Voice`, `Export`, `Reports`)
- Language Hub panel:
  - language overview
  - language queue
  - backend status block
  - uncertain/mixed review block
  - localization stress block
  - language flow summary
  - action buttons to jump to uncertain/stress entries and translation workbench
- Translation pipeline with backend fallback and context visibility.
- Learning loop (manual correction -> TM/glossary reuse).
- Companion mode (safe sidecar, file watch, quick re-index).
- Asset Research Mode (index + preview where supported + metadata fallback).
- Voice Preparation Layer (speaker grouping, sample bank, duration planning, attempt history).
- Reports and Diagnostics layer:
  - translation metrics and backend diagnostics
  - language distribution and uncertainty report
  - voice/QA/companion quality summaries

## Honest Status
- Voice synthesis in current MVP is `mock_demo_tts_stub` (demo/mock preparation layer).
- Reports are based on actual stored pipeline data.
- No production-grade dubbing claims.

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
1. `Project` tab -> set `fixtures/demo_game_world` -> `Create/Select Project`.
2. Run `Scan` (or one-click `Run Full Demo Pipeline`).
3. Check top `Project HUD` for current stage and next action.
4. Open `Language Hub` for language map, queue, uncertain lines, and localization stress.

## Reports And Diagnostics UI
1. Open `Reports` tab -> click `Generate Reports`.
2. Open `Diagnostics` tab for backend and quality history.
3. Use widgets/tables to track translation quality, companion event health, and voice prep readiness.

## UI QA Automation
Run the full UI audit loop (doctor + snapshots + consolidated artifacts):
```powershell
python scripts/ui_validate.py
```

Run snapshot harvesting only:
```powershell
python scripts/ui_snapshot_runner.py
```

Run structural UI diagnostics only:
```powershell
python scripts/ui_doctor.py
```

Validation outputs:
- `ui_validation_summary.json`
- `ui_validation_summary.md`
- `ui_screenshots_manifest.json`
- `runtime/ui_validation/latest_run.txt`

## Tests
Run all:
```powershell
pytest -q
```

## Build
```powershell
python scripts/build_app.py
```

Optional one-file:
```powershell
python scripts/build_app.py --onefile
```

## Current Limits
- Voice pipeline remains preparation-layer quality (not final dubbing).
- Asset unsupported formats remain metadata-only.
- No 3D runtime capture, memory inspection, or production speech cloning.
