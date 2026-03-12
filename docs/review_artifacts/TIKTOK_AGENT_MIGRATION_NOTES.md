# TikTok Agent Migration Notes

## Naming Decision

Selected product-grade name:

- **TikTok Agent Platform**
- slug: `tiktok_agent_platform`

Alternatives considered:

- `tiktok_ops_workspace`
- `shortform_agent_platform`
- `creator_ops_platform`
- `content_agent_workspace`

## Path Migration

### Core Layer

Moved from:

- `projects/wild_hunt_command_citadel/shortform_core`

Moved to:

- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core`

### Agent Layer

Moved from:

- `projects/wild_hunt_command_citadel/tiktok_automation_app`

Moved to:

- `projects/wild_hunt_command_citadel/tiktok_agent_platform/agent`

## Workspace Registry Migration

- active project switched from `shortform_core` to `tiktok_agent_platform`
- legacy `tiktok_automation_app` registry record removed
- active project files in codex manifest switched to unified root paths

## Entrypoint Rewiring

- Added product orchestrator:
  - `projects/wild_hunt_command_citadel/tiktok_agent_platform/run_project.ps1`
- Added core verification entrypoint:
  - `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/run_verify.ps1`
- Updated core and agent startup scripts to use `tiktok_agent_platform` preflight slug.
- Updated workspace UI proxy scripts to route into `tiktok_agent_platform/core/scripts/*`.

## Machine-Run Check Log

Executed checks and outputs are recorded in runtime and command outputs from:

- `python scripts/validate_workspace.py`
- `python scripts/project_startup.py run --project-slug tiktok_agent_platform --entrypoint verify --startup-kind verify --port-mode fixed`
- `powershell -ExecutionPolicy Bypass -File projects/wild_hunt_command_citadel/tiktok_agent_platform/run_project.ps1 -Mode verify -PortMode fixed`
- `python scripts/ui_validate.py`

## Sensitive Follow-Ups

- Local workstation session currently keeps a lock on the old `shortform_core` folder path (non-tracked local runtime/venv residue); repository-level tracked structure is fully migrated.
- Manual smoke of full desktop user-mode UI remains recommended after gate PASS.
