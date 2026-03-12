# TikTok Agent Restructure Report

## Scope

Structural consolidation performed inside:

- `projects/wild_hunt_command_citadel/`

Goal:

- replace split sibling-project model with one unified product project:
  - `tiktok_agent_platform`
  - explicit `core` and `agent` layers

## Previous State

Before consolidation:

- `projects/wild_hunt_command_citadel/shortform_core`
- `projects/wild_hunt_command_citadel/tiktok_automation_app`

Problems:

- split product identity in workspace registry
- duplicated startup/verification boundaries
- weak machine-readable indication that these folders are one product
- legacy naming and lore-style branding in app docs

## New State

Unified product root:

- `projects/wild_hunt_command_citadel/tiktok_agent_platform`

Layer model:

- `core/` - platform runtime, verify/readiness/update/UI-QA foundations
- `agent/` - product-facing TikTok agent desktop layer

Unified contracts:

- root `PROJECT_MANIFEST.json`
- root `run_project.ps1`
- workspace active slug switched to `tiktok_agent_platform`

## Updated Contracts

- `workspace_config/workspace_manifest.json`
- `workspace_config/codex_manifest.json`
- `README.md`
- `scripts/ui_validate.py`
- `scripts/ui_snapshot_runner.py`
- `scripts/ui_doctor.py`
- `scripts/ui_compare_runs.py`

## Verification and Health Checks

Machine checks executed after restructure are listed in:

- `docs/review_artifacts/TIKTOK_AGENT_MIGRATION_NOTES.md`

## Status Summary

- consolidated structure: complete
- workspace registry migration: complete
- core/agent entrypoint rewiring: complete
- path/docs rewiring: complete
- residual sensitivity: local lock on old `shortform_core` folder in current workstation session (non-repo artifact)
