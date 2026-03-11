# WorkFLOW Repository

## Overview
This repository is organized as a **multi-project workspace** with one active product module and several secondary modules.

The active engineering focus is:
- `projects/wild_hunt_command_citadel/shortform_core`

Root-level documentation is a workspace map. Project-level implementation details live inside each project folder.

## Current Active Module
- **Active module:** `projects/wild_hunt_command_citadel/shortform_core`
- **Project README:** `projects/wild_hunt_command_citadel/shortform_core/README.md`
- **Project manifest:** `projects/wild_hunt_command_citadel/shortform_core/PROJECT_MANIFEST.json`

If you are starting work in this repository, begin with this module unless the task explicitly says otherwise.

## Repository Structure
Top-level directories:
- `docs/`: cross-repo documentation and review artifacts.
- `projects/`: project source roots (active + secondary/legacy).
- `scripts/`: workspace-level bootstrap, validation, startup, and maintenance scripts.
- `workspace_config/`: machine-readable workspace governance (`workspace_manifest`, `codex_manifest`, rules, templates).
- `runtime/`: generated runtime and verification artifacts.

## Active vs Secondary Modules
Source of truth: `workspace_config/workspace_manifest.json` (`project_registry` + `project_status_index`).

Current status model:
- `active`: `shortform_core`
- `supporting`: `voice_launcher`
- `experimental`: `adaptive_trading`
- `legacy`: `tiktok_automation_app`

Interpretation:
- `shortform_core` is the primary product module.
- Other projects are maintained as secondary scopes and should not be treated as equal current priority unless requested.

## Workspace Manifests and Rules
Workspace control files:
- `workspace_config/workspace_manifest.json`
- `workspace_config/codex_manifest.json`
- `workspace_config/PROJECT_RULES.md`
- `workspace_config/codex_bootstrap.md`

Project-level machine-readable contract:
- `projects/<project>/PROJECT_MANIFEST.json`

Use manifests as authoritative source for project status, entrypoints, and scope.

## How To Use the Active Module
From repository root (`.`):

User mode:
```powershell
python scripts/project_startup.py run --project-slug shortform_core --entrypoint user --startup-kind user --port-mode fixed
```

Developer mode:
```powershell
python scripts/project_startup.py run --project-slug shortform_core --entrypoint developer --startup-kind developer --port-mode fixed
```

## Verification and Readiness
Canonical verify flow:
```powershell
python scripts/project_startup.py run --project-slug shortform_core --entrypoint verify --startup-kind verify --port-mode fixed
```

Alternative direct verify (inside the project):
```powershell
cd projects/wild_hunt_command_citadel/shortform_core
python -m app.verify
```

Manual testing policy:
- manual testing is allowed only when verification gate is `PASS`.

## Update / Patch Flow
User-facing update flow for active module:
```powershell
python scripts/project_startup.py run --project-slug shortform_core --entrypoint update --startup-kind update --port-mode fixed
```

Developer update endpoints and deeper update diagnostics are documented in:
- `projects/wild_hunt_command_citadel/shortform_core/README.md`

## Notes About Secondary Modules
Secondary modules remain in the workspace for supporting, experimental, or legacy purposes.

Default operator workflow:
1. Start with `shortform_core`.
2. Switch to another project only if the task explicitly targets that project.
3. Validate scope against manifests before making changes.
