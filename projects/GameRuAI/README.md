# GameRuAI (Desktop MVP Demo)

GameRuAI is a local desktop demo app for game localization workflows.
Current MVP combines translation + learning loop, safe companion mode, lightweight asset research, and a voice preparation layer.

## Stack
- Python 3.11+
- PySide6
- SQLite
- pytest
- structured logging
- pathlib

## Working Modules
- Translation pipeline with backend fallback and context visibility.
- Learning loop (manual correction -> TM/glossary reuse).
- Companion mode (safe sidecar, file watch, quick re-index).
- Asset Research Mode (index + preview where supported + metadata fallback).
- Voice Preparation Layer:
  - speaker grouping from voice-linked entries
  - voice sample bank (source file, duration, scene, speaker)
  - duration planning for mock synthesis
  - voice attempt history persistence
  - preview path resolution for source/generated files

## Honest Voice Status
- Voice synthesis in this sprint is explicitly `mock/demo` (`mock_demo_tts_stub`).
- This is preparation for future RU dubbing pipeline, not final production dubbing.
- No speech cloning, no lip-sync, no full phoneme forced alignment.

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

## Voice Sprint UI
1. Open `Voice` tab.
2. Click `Generate Demo Voice Attempts`.
3. Check:
   - `Speaker groups`
   - `Voice attempts`
   - `Voice attempt history`
   - `Voice Preview panel`
   - `Duration Plan widget`
   - `Voice quality/confidence`

## Tests
Run all:
```powershell
pytest -q
```

Voice sprint tests:
```powershell
pytest -q tests/unit/test_speaker_grouping.py tests/unit/test_voice_link_validation.py tests/unit/test_duration_planner.py tests/unit/test_voice_attempt_history.py tests/integration/test_voice_preparation_pipeline.py
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
- Unsupported/unknown assets still use metadata-only fallback.
- No 3D runtime capture or memory inspection.
