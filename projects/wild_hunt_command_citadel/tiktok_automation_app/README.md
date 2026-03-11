# Witcher Command Deck (Unified App)

This app now lives inside:

- `E:\CVVCODEX\projects\wild_hunt_command_citadel\tiktok_automation_app`

Integrated core lives in:

- `E:\CVVCODEX\projects\wild_hunt_command_citadel\shortform_core`

## Features

- Unified Russian Witcher UI.
- First-run wizard (`venv`, deps, Playwright Chromium).
- Config profiles (save/apply/update/delete).
- Scheduler by weekday/time + execution queue.
- In-app dashboard (metrics table + charts).
- Resilient automation engine:
  - retries
  - action/selector timeouts
  - selector diagnostics (`selector_diagnostics.jsonl`)
  - profile health-check
- Core integration:
  - bootstrap
  - analytics + plan
  - plan summary in UI log

## Run

```powershell
cd E:\CVVCODEX\projects\wild_hunt_command_citadel\tiktok_automation_app
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode developer -PortMode fixed
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode user -PortMode fixed
```

`auto` mode allows fallback only inside project range `8300-8399`.

Run without console:

- `run.bat`
- `run_silent.vbs`

## Build EXE

```powershell
cd E:\CVVCODEX\projects\wild_hunt_command_citadel\tiktok_automation_app
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1 -Clean
```

Output:

- `dist\WitcherCommandDeck.exe`
