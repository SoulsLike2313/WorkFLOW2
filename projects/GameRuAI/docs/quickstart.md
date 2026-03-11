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
1. `Project` tab -> set `fixtures/demo_game_world` -> `Create/Select Project`
2. Run either:
   - one click: `Run Full Demo Pipeline`
   - manual: `Scan` -> `Extract Strings` -> `Detect Language` -> `Translate to Russian` -> `Generate Demo Voice Attempts`

## 5) Check backend transparency
1. `Translation` tab -> select backend.
2. Click `Translate to Russian`.
3. Confirm:
   - Backend Status labels (`active`, `fallback`, `context used`)
   - translation table columns (`Backend`, `Fallback`, `Context`, `Latency`, `Uncertainty`)

## 6) Check context-aware behavior
1. In `Entries` tab ensure `Context` column shows `yes` for translated lines.
2. In `Jobs / Logs` inspect backend run records (`context_used`, `fallback_used`, `backend_name`).

## 7) Run Companion Mode
1. Open `Companion` tab.
2. Set executable + watched path.
3. Launch session.
4. Modify file in watched folder.
5. Poll session.
6. Confirm watched events list and quick re-index counter update.

## 8) Learning loop visibility
1. In `Translation` tab pick `Entry ID` and apply manual correction.
2. Re-run translation for similar lines.
3. In `Learning` tab check correction/adaptation history.

## 9) Tests
```powershell
pytest -q
```
