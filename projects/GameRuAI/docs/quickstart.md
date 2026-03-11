# Quickstart

## 1) Install
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

## 2) Generate demo fixture
```powershell
python scripts/generate_demo_assets.py --project-root .
```

## 3) Run app
```powershell
python -m app.main
```

## 4) Create/open demo project
1. `Project` tab -> `fixtures/demo_game_world` -> `Create/Select Project`
2. Run `Scan`

## 5) Translation / companion / asset / voice flows
- Translation: `Scan -> Extract -> Detect -> Translate`
- Companion: `Companion` tab -> launch session -> edit file -> poll status
- Asset research: `Asset Explorer` -> `Refresh Asset Index` -> inspect file
- Voice prep: `Voice` -> `Generate Demo Voice Attempts`

## 6) Reports and diagnostics
1. Open `Reports` tab -> click `Generate Reports`.
2. Read:
   - translation metrics
   - language distribution + uncertainty
   - QA and export integrity summary
   - compact quality widgets
3. Open `Diagnostics` tab for backend latency/fallback/context and quality snapshot history.

## 7) Demo/mock clarity
- Voice synthesis mode is `mock_demo_tts_stub`.
- Fallback/demo behavior is shown in UI and reports (not hidden).

## 8) Tests
```powershell
pytest -q
```

## 9) UI validation loop
```powershell
python scripts/ui_validate.py
```

Artifacts after run:
- `ui_validation_summary.json`
- `ui_validation_summary.md`
- `ui_screenshots_manifest.json`
- `runtime/ui_validation/latest_run.txt`
