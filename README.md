# WorkFLOW Multi-Project Workspace

## Overview
This repository is organized as a normalized multi-project workspace.

Core principles:
- each project is isolated and independently scoped;
- one project is explicitly marked as active;
- project statuses are machine-readable;
- Codex/device bootstrap does not rely on guessing from free-form text.

## Workspace control layer
Canonical workspace control files:
- `workspace_config/workspace_manifest.json`
- `workspace_config/codex_manifest.json`
- `workspace_config/codex_bootstrap.md`
- `scripts/bootstrap_workspace.ps1`

These files define project statuses, active target, analysis order, and bootstrap checks.

## Project status map
Status categories used in this workspace:
- `active`
- `supporting`
- `experimental`
- `archived`
- `legacy`

Current registry:

| Project ID | Path | Status | Manifest |
|---|---|---|---|
| `shortform_core` | `projects/wild_hunt_command_citadel/shortform_core` | `active` | `projects/wild_hunt_command_citadel/shortform_core/PROJECT_MANIFEST.json` |
| `voice_launcher` | `projects/voice_launcher` | `supporting` | `projects/voice_launcher/PROJECT_MANIFEST.json` |
| `adaptive_trading` | `projects/adaptive_trading` | `experimental` | `projects/adaptive_trading/PROJECT_MANIFEST.json` |
| `tiktok_automation_app` | `projects/wild_hunt_command_citadel/tiktok_automation_app` | `legacy` | `projects/wild_hunt_command_citadel/tiktok_automation_app/PROJECT_MANIFEST.json` |

Notes:
- archived bucket exists in the model and is currently empty.
- only the active project is used as default engineering target.

## Active project (source of truth)
Active project:
- `projects/wild_hunt_command_citadel/shortform_core`

Primary docs for active runtime and engineering contracts:
- `projects/wild_hunt_command_citadel/shortform_core/README.md`
- `projects/wild_hunt_command_citadel/shortform_core/CODEX.md`

User mode / developer mode / verification / update flow are maintained in the active project scope.

## Bootstrap on a new device
From repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_workspace.ps1
```

Optional active-project environment setup:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_workspace.ps1 -SetupActive
```

Bootstrap outputs:
- `runtime/workspace_bootstrap/bootstrap_report_<timestamp>.json`

## How Codex should start analysis
Codex bootstrap order:
1. read `workspace_config/workspace_manifest.json`
2. resolve `active_project_id`
3. read active `PROJECT_MANIFEST.json`
4. read active project docs (`README.md`, `CODEX.md`)
5. work inside active scope unless user explicitly requests another project

Detailed flow is documented in:
- `workspace_config/codex_bootstrap.md`

## Project isolation rules
- project-level implementation details stay inside each project folder.
- root README is a workspace map, not a full technical spec for every module.
- status changes must be reflected in both:
  - `workspace_config/workspace_manifest.json`
  - target `PROJECT_MANIFEST.json`

## Manifest maintenance
When adding or reclassifying a project:
1. create/update project `PROJECT_MANIFEST.json`
2. update `workspace_config/workspace_manifest.json`
3. if analysis priority changes, update `workspace_config/codex_manifest.json`
4. run bootstrap check script and confirm report status is `PASS` or `PASS_WITH_WARNINGS`
