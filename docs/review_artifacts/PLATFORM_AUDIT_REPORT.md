# Platform Audit Report

- run_id: `full-platform-audit-20260312T221721Z`
- generated_at_utc: `2026-03-12T22:17:21.943491+00:00`
- audited_projects: `tiktok_agent_platform, game_ru_ai`
- checked_shared_systems: `ui_qa_toolkit, verification_toolkit, reporting_toolkit, localization_toolkit, audit_observability_toolkit, update_patch_toolkit, security_baseline`
- overall_status: `FAIL`

## Platform Sections

| section | status | evidence_path_or_run |
|---|---|---|
| `workspace_governance` | PASS | `workspace_config/workspace_manifest.json` |
| `github_sync_policy` | PASS_WITH_WARNINGS | `runtime/repo_sync_checks/repo-sync-20260312T215553Z.json` |
| `machine_readability` | PASS | `workspace_config/workspace_manifest.json` |
| `shared_systems_registry` | PASS | `workspace_config/shared_systems_registry.json` |
| `install_remove_architecture` | PASS | `scripts/install_system.py; scripts/remove_system.py` |
| `module_maturity` | PASS_WITH_WARNINGS | `docs/review_artifacts/MODULE_MATURITY_MATRIX.md` |
| `instruction_layer` | PASS | `docs/review_artifacts/MACHINE_INSTRUCTION_AUDIT.md` |

## Project Findings

| project | verification | readiness | ui_qa | reporting | localization | audit_observability | manifest_integrity | installed_systems_integrity | runtime_health | diagnostics_summary | install_remove_compatibility | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `tiktok_agent_platform` | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| `game_ru_ai` | FAIL | PASS | FAIL | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | FAIL |

## Run References

- workspace_validate_run: `workspace-validate-20260312T215553Z`
- repo_sync_run: `repo-sync-20260312T215553Z`
- module_install_remove_run: `module-library-hardening-20260312T215356Z`
- tiktok_readiness_run: `tiktok_agent_platform-startup-20260312T215753Z`
- tiktok_verification_run: `verify-20260312T215801Z`
- game_readiness_run: `game_ru_ai-startup-20260312T215753Z`
- game_verification_run: `game_ru_ai-startup-20260312T215800Z`
- game_verification_result: `verification_command_timeout`
