# Codex Workspace Bootstrap (WorkFLOW)

This document defines the canonical startup flow for Codex on a new device.

## 1. Load workspace metadata
1. Read `workspace_config/workspace_manifest.json`.
2. Confirm `active_project_id` and `status_index` are consistent.
3. Read `workspace_config/codex_manifest.json`.

## 2. Resolve active project
Current active project:
- `shortform_core`
- path: `projects/wild_hunt_command_citadel/shortform_core`

Codex should prioritize this project for:
- analysis
- implementation
- verification
- runtime decisions

## 3. Read active project contracts
Read in this order:
1. `projects/wild_hunt_command_citadel/shortform_core/PROJECT_MANIFEST.json`
2. `projects/wild_hunt_command_citadel/shortform_core/README.md`
3. `projects/wild_hunt_command_citadel/shortform_core/CODEX.md`

## 4. Status isolation rules
- `active`: may receive primary engineering changes.
- `supporting`: changes only when explicitly requested or needed for integration.
- `experimental`: isolate from active runtime unless explicitly promoted.
- `archived`: read-only unless explicitly reactivated.
- `legacy`: avoid new features; maintain only compatibility/migration notes.

## 5. Bootstrap command (new device)
From repository root run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_workspace.ps1
```

Optional active-project setup:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_workspace.ps1 -SetupActive
```

## 6. Output artifacts
Bootstrap reports are written to:
- `runtime/workspace_bootstrap/bootstrap_report_<timestamp>.json`

Use this report to verify manifest consistency and project-path readiness.
