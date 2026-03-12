# TikTok Agent Platform

Unified product project for TikTok agent operations.

This project is intentionally structured as one product with two explicit layers:

- `core/` - platform and intelligence/runtime core (verification, readiness, update/patch, UI-QA).
- `agent/` - product-facing TikTok desktop agent application.

## Why This Structure

Previous layout had two sibling folders that behaved like separate projects.
Now both layers are consolidated under one project root with one product manifest and one project slug:

- `tiktok_agent_platform`

This keeps machine-readable contracts and startup/verification flows coherent at workspace level.

## Product Structure

```text
projects/wild_hunt_command_citadel/tiktok_agent_platform/
  PROJECT_MANIFEST.json
  README.md
  CODEX.md
  run_project.ps1
  core/
    app/
    scripts/
    runtime/
    PROJECT_MANIFEST.json
    run_user.ps1
    run_developer.ps1
    run_verify.ps1
    run_update.ps1
  agent/
    app.py
    ui_main.py
    automation_engine.py
    run_project.ps1
    PROJECT_MANIFEST.json
    runtime/
```

## Entrypoints

Run from the product root:

```powershell
cd projects/wild_hunt_command_citadel/tiktok_agent_platform
```

User mode (agent layer):

```powershell
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode user -PortMode fixed
```

Developer mode (agent layer):

```powershell
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode developer -PortMode fixed
```

Unified verification:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode verify -PortMode fixed
```

Update/patch flow (core layer):

```powershell
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode update -PortMode fixed -ManifestPath <manifest.json>
```

## Layer-Specific Modes

Core only:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode core-user -PortMode fixed
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode core-developer -PortMode fixed
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode core-verify -PortMode fixed
```

Agent only:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode agent-user -PortMode fixed
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode agent-developer -PortMode fixed
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode agent-verify -PortMode fixed
```
