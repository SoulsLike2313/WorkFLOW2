# Platform Audit Report

- run_id: `platform-audit-20260312T192732Z`
- timestamp: `2026-03-12T19:27:32.627704+00:00`

## Platform Assessment
- overall_status: `PASS_WITH_WARNINGS`
- audited_projects: `tiktok_agent_platform, game_ru_ai`
- shared_systems_checked: `ui_qa_toolkit, verification_toolkit, reporting_toolkit, localization_toolkit, audit_observability_toolkit, update_patch_toolkit, security_baseline`

## Checks Passed
- `tiktok_agent_platform` `verification`: PASS
- `tiktok_agent_platform` `readiness`: PASS
- `tiktok_agent_platform` `ui_qa`: PASS
- `tiktok_agent_platform` `reporting`: PASS
- `tiktok_agent_platform` `localization`: PASS
- `tiktok_agent_platform` `audit`: PASS
- `tiktok_agent_platform` `manifest_integrity`: PASS
- `tiktok_agent_platform` `runtime_diagnostics_paths`: PASS
- `tiktok_agent_platform` `machine_docs_consistency`: PASS
- `tiktok_agent_platform` `source_of_truth_integrity`: PASS
- `game_ru_ai` `verification`: PASS
- `game_ru_ai` `readiness`: PASS
- `game_ru_ai` `reporting`: PASS
- `game_ru_ai` `localization`: PASS
- `game_ru_ai` `audit`: PASS
- `game_ru_ai` `manifest_integrity`: PASS
- `game_ru_ai` `runtime_diagnostics_paths`: PASS
- `game_ru_ai` `machine_docs_consistency`: PASS
- `game_ru_ai` `source_of_truth_integrity`: PASS

## Checks Not Passed
- `tiktok_agent_platform` `install_remove_compatibility`: PASS_WITH_WARNINGS
- `game_ru_ai` `ui_qa`: PASS_WITH_WARNINGS
- `game_ru_ai` `install_remove_compatibility`: PASS_WITH_WARNINGS

## Critical Gaps
- none

## Major Gaps
- `ui_qa_toolkit`
- `verification_toolkit`
- `reporting_toolkit`
- `localization_toolkit`
- `audit_observability_toolkit`
- `update_patch_toolkit`
- `security_baseline`

## Partial Stub
- ui_qa_toolkit: no_executable_module_tests
- verification_toolkit: no_executable_module_tests
- reporting_toolkit: no_executable_module_tests
- localization_toolkit: no_executable_module_tests
- audit_observability_toolkit: no_executable_module_tests
- update_patch_toolkit: not_integrated_in_target_projects, no_executable_module_tests
- security_baseline: not_integrated_in_target_projects, no_executable_module_tests

## Machine Readability
- workspace_validation_status: `PASS`
- machine_readable_status: `PASS`

## GitHub Sync Readiness
- github_sync_ready_status: `PASS`
- repo_sync_gate_run_id: `repo-sync-20260312T193149Z`

## Install Remove Architecture
- install_remove_working_status: `PASS`
