# Machine Readability Audit

- run_id: `full-platform-audit-20260312T221421Z`
- generated_at_utc: `2026-03-12T22:14:21.535248+00:00`
- status: `PASS`

## Required Platform Files

| path | exists | size_bytes |
|---|---|---|
| `workspace_config/GITHUB_SYNC_POLICY.md` | True | 1030 |
| `workspace_config/COMPLETION_GATE_RULES.md` | True | 701 |
| `workspace_config/TASK_RULES.md` | True | 2641 |
| `workspace_config/AGENT_EXECUTION_POLICY.md` | True | 2343 |
| `workspace_config/MACHINE_REPO_READING_RULES.md` | True | 3308 |
| `docs/INSTRUCTION_INDEX.md` | True | 4478 |
| `docs/review_artifacts/MACHINE_INSTRUCTION_AUDIT.md` | True | 4671 |
| `workspace_config/shared_systems_registry.json` | True | 10128 |
| `workspace_config/workspace_manifest.json` | True | 12946 |
| `workspace_config/codex_manifest.json` | True | 4782 |

## Machine Parsing Checks

| check | status |
|---|---|
| `active_project_declared_in_workspace_manifest` | PASS |
| `active_project_exists_in_registry` | PASS |
| `active_project_root_path_exists` | PASS |
| `shared_systems_registry_exists` | PASS |
| `shared_systems_root_exists` | PASS |
| `codex_manifest_onboarding_sequence_has_required_rules` | PASS |
| `readme_mentions_active_project_slug` | PASS |
| `instruction_index_references_task_rules` | PASS |

## Findings

- gaps_count: `0`
