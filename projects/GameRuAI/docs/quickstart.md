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

## 5) Translation / companion / asset flows
- Translation: `Scan -> Extract -> Detect -> Translate`
- Companion: `Companion` tab -> launch session -> edit file -> poll status
- Asset research: `Asset Explorer` -> `Refresh Asset Index` -> inspect file

## 6) Voice preparation flow
1. Run translation first (voice attempts use translated RU text).
2. Open `Voice` tab.
3. Click `Generate Demo Voice Attempts`.
4. Inspect sections:
   - `Speaker groups`
   - `Voice attempt history`
   - `Voice Preview panel`
   - `Duration Plan widget`
   - `Voice quality/confidence`

## 7) Demo/mock clarity
- Synthesis mode in this sprint is `mock_demo_tts_stub`.
- UI and metadata explicitly mark it as demo/mock preparation layer.

## 8) Tests
```powershell
pytest -q
```
