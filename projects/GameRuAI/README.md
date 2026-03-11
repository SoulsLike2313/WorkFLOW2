# GameRuAI (Desktop MVP Demo)

GameRuAI is a local desktop demo app for game localization and safe game-resource research.
Current MVP includes scan/extract/detect/translate/learning loop, companion sidecar mode, and lightweight asset research mode.

## Stack
- Python 3.11+
- PySide6
- SQLite
- pytest
- structured logging
- pathlib

## Working Features (Current Sprint)
- Translation pipeline with backend router and fallback (`local_mock`, `dummy`, optional `argos`/`transformers`).
- Context-aware translation with transparent decision data (backend, fallback, latency, uncertainty, TM/glossary/context usage).
- Learning loop (manual correction -> TM/glossary/adaptation visibility).
- Companion mode (safe sidecar): launch process, monitor session, watch file changes, quick re-index.
- Asset Research Mode:
  - asset indexing (`asset_type`, `preview_type`, `preview_status`, relevance, suspected container flag)
  - asset explorer tree in UI
  - texture preview for supported image files
  - audio preview for supported WAV files
  - metadata-only fallback for unsupported/binary formats
  - archive/container suspicion report

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
2. Set `fixtures/demo_game_world` (or click `Use Demo Fixture`).
3. Click `Create/Select Project`.
4. Run `Scan` (or one-click `Run Full Demo Pipeline`).

## Asset Explorer
1. Open `Asset Explorer` tab.
2. Click `Refresh Asset Index` after scan.
3. Browse `Resource` tree.
4. Select file to inspect:
   - metadata panel
   - texture preview widget (if supported)
   - audio preview widget (if supported WAV)
   - archive/container report table

## Companion Mode
1. Open `Companion` tab.
2. Set executable + watched path.
3. Launch session.
4. Modify files in watched folder.
5. Poll session to see file events and quick re-index.

## Tests
Run all:
```powershell
pytest -q
```

Run sprint-specific asset tests:
```powershell
pytest -q tests/unit/test_asset_classifier.py tests/unit/test_asset_preview_eligibility.py tests/unit/test_archive_suspicion_heuristics.py tests/integration/test_asset_research_mode.py
```

## Build
```powershell
python scripts/build_app.py
```

Optional one-file:
```powershell
python scripts/build_app.py --onefile
```

## Honest Limits
- Texture preview is limited to lightweight supported image formats handled locally.
- Audio preview is fully supported for WAV metadata preview; other audio formats are metadata-only.
- Unknown/binary resources are shown as metadata-only (no fake preview).
- No 3D preview, mesh editor, scene reconstruction, runtime scene capture, or memory inspection in this sprint.
