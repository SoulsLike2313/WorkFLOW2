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
- `python scripts/project_startup.py run --project-slug tiktok_agent_platform --entrypoint update --startup-kind update --port-mode fixed`
- `python scripts/project_startup.py prepare --project-slug tiktok_agent_platform --startup-kind user --port-mode fixed`
- `python scripts/project_startup.py prepare --project-slug tiktok_agent_platform --startup-kind developer --port-mode fixed`

Latest recorded outcomes:

- workspace manifest integrity: `PASS` (`workspace-validate-20260312T154614Z`)
- verify pipeline: `PASS` (`verify-20260312T154621Z`)
- verify startup preflight: `READY` (`tiktok_agent_platform-startup-20260312T154620Z`)
- UI-QA validation (from verify run): `PASS` (`validate_20260312_184639`)
- update/patch entrypoint dry check: `PASS` (`tiktok_agent_platform-startup-20260312T155116Z`)
- user/developer preflight: `READY` (`tiktok_agent_platform-startup-20260312T153501Z`)

Primary generated artifacts from latest verify run:

- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/verification/verify-20260312T154621Z/verification_summary.json`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/verification/verify-20260312T154621Z/verification_summary.md`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/verification/verify-20260312T154621Z/readiness_summary.json`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/verification/verify-20260312T154621Z/consolidated_status.json`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/verification/verify-20260312T154621Z/diagnostics_manifest.json`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/verification/verify-20260312T154621Z/test_results.json`

Primary generated artifacts from latest UI-QA run:

- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/ui_validation/validate_20260312_184639/ui_validation_summary.json`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/ui_validation/validate_20260312_184639/ui_validation_summary.md`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/ui_validation/validate_20260312_184639/ui_screenshots_manifest.json`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/ui_validation/validate_20260312_184639/ui_walkthrough_trace.json`

## Rebinding Fixes Applied During Migration

- update entrypoint placeholder removed from machine-run manifests (root and core layer) so update flow can execute without literal `<manifest.json>`.
- workspace UI proxy scripts switched to execute core scripts through `core/.venv` (with fallback), preventing dependency drift.
- core runtime DB default renamed to `runtime/tiktok_agent_platform_core.db` and synced with env contracts.
- legacy user-facing strings in runtime launch scripts/docs updated from old split project path to unified `tiktok_agent_platform` path.

## Transient Issues (Resolved)

- update flow initially failed because `project_startup` executed a literal placeholder in update command; resolved by normalizing `update_entrypoint`.
- root `scripts/ui_validate.py` initially failed because it executed with the wrong interpreter; resolved by delegating to core virtual environment.

## Sensitive Follow-Ups

- Local workstation path `projects/wild_hunt_command_citadel/shortform_core` remains as non-tracked residue; this session could not remove it automatically because destructive removal command was blocked by policy. Repository-level tracked structure is fully migrated.
- Manual smoke of full desktop user-mode UI remains recommended after gate PASS.
