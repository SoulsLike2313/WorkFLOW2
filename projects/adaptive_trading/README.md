# Adaptive Trading

## Overview
Experimental trading project with script and GUI prototypes.

## Scope
- research and prototyping
- not part of active workspace release gate
- can be promoted only via workspace status update

## Entry points
```powershell
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode user -PortMode fixed
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode developer -PortMode fixed
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode train -PortMode fixed
```

`auto` mode allows fallback only inside project range `8200-8299`.

## Dependencies
```powershell
pip install -r trading_requirements.txt
```

## Manifest
Machine-readable descriptor:
- `projects/adaptive_trading/PROJECT_MANIFEST.json`
