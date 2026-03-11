# WorkFLOW Multi-Project Repository

## Overview
This repository is a structured multi-project workspace.

Current engineering priority is one active product module:
- `projects/wild_hunt_command_citadel/shortform_core`

Root documentation is a navigation map. Implementation details belong to each project directory.

## Active Module
Primary active module:
- `projects/wild_hunt_command_citadel/shortform_core`

Primary references:
- `projects/wild_hunt_command_citadel/shortform_core/README.md`
- `projects/wild_hunt_command_citadel/shortform_core/PROJECT_MANIFEST.json`

## Root-Level Structure
Top-level purpose:
- `docs/`: repository-level documentation and review artifacts.
- `projects/`: project source roots (active + secondary/legacy scopes).
- `scripts/`: workspace bootstrap, validation, startup, and utility scripts.
- `workspace_config/`: machine-readable workspace governance and templates.
- `runtime/`: generated runtime and diagnostics artifacts.

## Project Priority and Status
Status source of truth:
- `workspace_config/workspace_manifest.json`

Current priority model:
- `active`: `shortform_core`
- `supporting`: `voice_launcher`
- `experimental`: `adaptive_trading`
- `legacy`: `tiktok_automation_app`

Interpretation:
- `shortform_core` is the main current product module.
- Other projects are secondary scopes and should be handled only when a task explicitly targets them.

## Workspace Manifests and Contracts
Workspace-level contracts:
- `workspace_config/workspace_manifest.json`
- `workspace_config/codex_manifest.json`
- `workspace_config/PROJECT_RULES.md`
- `workspace_config/codex_bootstrap.md`

Project-level contracts:
- `projects/<project>/PROJECT_MANIFEST.json`

Use manifests for scope, status, and entrypoints instead of guessing from folder names.

## Root Entrypoints for the Active Module
Run from repository root (`.`):

User mode:
```powershell
python scripts/project_startup.py run --project-slug shortform_core --entrypoint user --startup-kind user --port-mode fixed
```

Developer mode:
```powershell
python scripts/project_startup.py run --project-slug shortform_core --entrypoint developer --startup-kind developer --port-mode fixed
```

Verification:
```powershell
python scripts/project_startup.py run --project-slug shortform_core --entrypoint verify --startup-kind verify --port-mode fixed
```

Update flow:
```powershell
python scripts/project_startup.py run --project-slug shortform_core --entrypoint update --startup-kind update --port-mode fixed
```

Manual test policy:
- manual testing is allowed only after verification gate `PASS`.

## Supporting Files and Notes
Supporting files in root:
- `.gitignore`
- workspace-level scripts in `scripts/`
- workspace governance in `workspace_config/`

Operator default flow:
1. Validate scope in `workspace_manifest.json`.
2. Work in `shortform_core` unless another project is explicitly requested.
3. Use project-level README and PROJECT_MANIFEST for implementation details.
