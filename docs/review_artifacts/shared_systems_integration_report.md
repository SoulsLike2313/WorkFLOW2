# Shared Systems Integration Report

- run_id: `shared-systems-check-20260312T175132Z`
- timestamp: `2026-03-12T17:51:32.316306+00:00`

## Project Scope
- TikTok Agent: `projects/wild_hunt_command_citadel/tiktok_agent_platform`
- Russifier: `projects/GameRuAI`

## Installed Systems (Both Projects)
- `ui_qa_toolkit`
- `verification_toolkit`
- `reporting_toolkit`
- `localization_toolkit`
- `audit_observability_toolkit`

## Per-Project Runs
### tiktok_agent_platform
- output_dir: `runtime/projects/tiktok_agent_platform/shared_systems_checks/shared-systems-check-20260312T175132Z`
- verification_run_id: `verify-20260312T170537Z` (`PASS`)
- readiness_run_id: `tiktok_agent_platform-startup-20260312T170554Z` (`READY`)
- ui_run_id: `20260312_200601` (`PASS`)
- ui_run_dir: `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/ui_validation/validate_20260312_200601`
### game_ru_ai
- output_dir: `runtime/projects/game_ru_ai/shared_systems_checks/shared-systems-check-20260312T175132Z`
- verification_run_id: `verify-game_ru_ai-20260312T175132Z` (`PASS`)
- readiness_run_id: `game_ru_ai-startup-20260312T174820Z` (`READY`)
- ui_run_id: `20260312_173011` (`PASS_WITH_WARNINGS`)
- ui_run_dir: `projects/GameRuAI/runtime/ui_validation/validate_20260312_173011`

## Validation Notes
- install/remove flow dry-run checks executed successfully.
- workspace manifest and project manifests are consistent for installed_systems registry.
- update_patch_toolkit and security_baseline are present in library but not installed in these two projects (by scope).
