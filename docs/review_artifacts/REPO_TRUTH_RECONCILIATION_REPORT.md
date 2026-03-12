# REPO TRUTH RECONCILIATION REPORT

## Scope Checked
- `README.md`
- `workspace_config/workspace_manifest.json`
- `workspace_config/codex_manifest.json`
- `projects/**/PROJECT_MANIFEST.json`
- Physical tree under `projects/`
- `scripts/project_startup.py`
- Existing review artifacts related to workspace/normalization/repo truth

## Discrepancies Found
1. Workspace verification/update entrypoints were stale at root level.
- `verification_entrypoints.active_project_verify` pointed to `python -m app.verify`.
- `update_entrypoints.active_user_update` pointed to `.\\run_update.ps1` (file not present at repository root).
- `update_entrypoints.active_developer_update_api` pointed to `python -m app.launcher developer backend` (not canonical root entrypoint).

2. Non-registry classification was incomplete.
- `projects/wild_hunt_command_citadel/shortform_core` was classified, but container path `projects/wild_hunt_command_citadel` was not explicitly classified.

3. Layer manifest classification was implicit, not machine-explicit in workspace manifest.
- Layer manifests existed physically:
  - `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/PROJECT_MANIFEST.json`
  - `projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/PROJECT_MANIFEST.json`
- They were excluded from project registry by behavior, but not explicitly indexed as layer manifests.

4. Legacy normalization artifacts contained stale active-module phrasing (`.../tiktok_agent_platform/core` as active project).

## Corrections Applied
1. Updated `workspace_config/workspace_manifest.json`:
- `verification_entrypoints.active_project_verify` -> canonical root verify command for `tiktok_agent_platform`.
- `update_entrypoints.active_user_update` -> canonical root update command for `tiktok_agent_platform`.
- `update_entrypoints.active_developer_update_api` -> canonical root update command for `tiktok_agent_platform`.
- Added `non_registry_paths` entry for `projects/wild_hunt_command_citadel` as `project_group_container`.
- Added `layer_manifest_registry` with explicit entries for:
  - `tiktok_agent_core_layer`
  - `tiktok_agent_app_layer`

2. Updated `README.md`:
- Explicit non-registry container path classification for `projects/wild_hunt_command_citadel`.
- Added source-of-truth precedence order.
- Added explicit canonical root user-mode entrypoint command.

3. Updated stale normalization artifacts to current canonical active project wording:
- `docs/review_artifacts/README_BEFORE_AFTER_SUMMARY.md`
- `docs/review_artifacts/README_NORMALIZATION_CHECKLIST.md`
- `docs/review_artifacts/README_REWRITE_RATIONALE.md`
- `docs/review_artifacts/ROOT_REPO_NORMALIZATION.md`

## Canonical Active Project
- slug: `tiktok_agent_platform`
- path: `projects/wild_hunt_command_citadel/tiktok_agent_platform`
- status: `active`

## Canonical Non-Registry Paths
- `projects/wild_hunt_command_citadel` (`project_group_container`)
- `projects/wild_hunt_command_citadel/shortform_core` (`legacy_internal_layer`)

## Canonical Layer Manifests (Not Workspace Projects)
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/PROJECT_MANIFEST.json` (`tiktok_agent_core_layer`)
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/PROJECT_MANIFEST.json` (`tiktok_agent_app_layer`)

## Root Entrypoint Validation
- command checked:
  - `python scripts/project_startup.py run --project-slug tiktok_agent_platform --entrypoint user --startup-kind user --port-mode fixed --dry-run`
- result: `PASS`
- run_id: `tiktok_agent_platform-startup-20260312T203150Z`

## Workspace Validation
- command: `python scripts/validate_workspace.py`
- result: `PASS`
- run_dir: `runtime/workspace_validation/workspace-validate-20260312T203506Z`

## Residual Risks
- Historical migration/restructure artifacts still contain legacy context by design; canonical interpretation order is now explicit in root README and workspace manifest.
