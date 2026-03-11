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
2. Run `Scan` (or one-click `Run Full Demo Pipeline`)

## 5) Use Asset Research Mode
1. Open `Asset Explorer` tab.
2. Click `Refresh Asset Index`.
3. Select resource in tree.
4. Check:
   - `File metadata` panel
   - `Texture preview` widget (supported image formats only)
   - `Audio preview` widget (WAV preview)
   - `Archive/container report` section

## 6) Metadata-only fallback
- Select unsupported/unknown binary file.
- `preview_status` will be `metadata_only` and metadata is shown without fake render.

## 7) Translation + companion flows still available
- Translation flow: `Scan -> Extract -> Detect -> Translate`.
- Companion flow: `Companion` tab -> launch -> poll events -> quick re-index.

## 8) Tests
```powershell
pytest -q
```
