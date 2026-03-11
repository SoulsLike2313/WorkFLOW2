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
2. `Scan` tab -> `Run Scan` -> `Extract Strings`
3. `Entries` tab -> `Detect Language`
4. `Translation` tab -> `Translate to Russian`
5. `Voice` tab -> `Generate Demo Voice Attempts`
6. `QA` tab -> `Run QA Checks`
7. `Export` tab -> `Export Patch Output`

## 5) Live mode
- Open `Live Demo` tab
- Choose scene
- Click `Start Live Demo`
