# WorkFLOW Repository

## Overview
This repository is a multi-project workspace. The primary engineering focus is one module: `shortform_core`.

The repository is maintained around a strict machine verification discipline:
- major changes are validated by a canonical verification pipeline;
- manual testing is allowed only after a `PASS` gate status;
- update and patch workflows are tracked with machine-readable artifacts.

## Current active module
Active module path:
- `projects/wild_hunt_command_citadel/shortform_core`

This module is the main product in active development and the source of truth for:
- runtime architecture,
- user/developer launch modes,
- verification and readiness checks,
- update/patch flow.

## Repository structure
Top-level structure:
- `projects/wild_hunt_command_citadel/shortform_core` — active core module
- `projects/voice_launcher` — secondary project
- `projects/adaptive_trading` — secondary project
- `scripts` — repository-level automation and sync scripts

## Active vs legacy components
Active component:
- `shortform_core` is the only active engineering core for current workflow decisions and verification standards.

Secondary / legacy / experimental components:
- `voice_launcher`
- `adaptive_trading`

These components remain in the repo, but they are not the primary reference for current platform architecture.

## How to use the active module
All operational commands should be run from:
- `projects/wild_hunt_command_citadel/shortform_core`

User mode:
- Windows helper script: `run_user.ps1`
- Direct launcher command: `python -m app.launcher user`

Developer mode:
- Windows helper script: `run_developer.ps1`
- API backend: `python -m app.launcher developer backend --host 127.0.0.1 --port 8000`
- Desktop UI only: `python -m app.launcher developer ui --api-base-url http://127.0.0.1:8000`

Setup helper:
- `run_setup.ps1` prepares environment and can run gate checks before launch.

## Verification and readiness
Canonical verification entrypoint:
- `python -m app.verify`

Machine Verification Gate statuses:
- `PASS`
- `PASS_WITH_WARNINGS`
- `FAIL`

Manual testing policy:
- manual testing is allowed only when gate status is `PASS`.

Verification artifacts are generated in:
- `runtime/verification/<run_id>/`

Required artifacts:
- `verification_summary.json`
- `verification_summary.md`
- `readiness_summary.json`
- `consolidated_status.json`
- `diagnostics_manifest.json`

Additional update/report artifacts:
- `patch_application_summary.json`
- `update_audit_summary.json`

## Update / patch flow
User-facing local flow (no manual API calls required):
- `run_update.ps1 -Mode check -ManifestPath <manifest.json>`
- `run_update.ps1 -Mode apply -BundlePath <patch_bundle.zip> -TargetVersion <version>`
- `run_update.ps1 -Mode post-verify`

Developer API flow (for integration/debug scenarios):
- start backend via developer mode;
- use `/updates/check`, `/updates/apply-local`, `/updates/post-verify` endpoints.

## Notes about legacy projects
Legacy/secondary modules are kept for continuity, reference, and separate workflows, but they do not replace the active `shortform_core` flow.

If there is a conflict between legacy docs and active module docs, follow `shortform_core` documentation and verification outputs.
