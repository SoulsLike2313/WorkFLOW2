# Quickstart

## 1) Install
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

## 2) Generate demo game world
```powershell
python scripts/generate_demo_assets.py --project-root .
```

## 3) Launch app
```powershell
python -m app.main
```

## 4) Run first pipeline
1. `Project` tab -> choose fixture path -> `Create/Select Project`
2. Quick path: `Run Full Demo Pipeline` button in `Project` tab
3. Manual path: `Scan` -> `Extract Strings` -> `Detect Language` -> `Translate to Russian` -> `Generate Demo Voice Attempts` -> `Run QA Checks` -> `Export Patch Output`

## 5) Live mode
- Open `Live Demo` tab
- Choose scene
- Click `Start Live Demo`
