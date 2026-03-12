# GitHub Sync Compliance Report

- run_id: `full-platform-audit-20260312T221421Z`
- generated_at_utc: `2026-03-12T22:14:21.535248+00:00`
- branch: `main`
- local_head: `e1733fe93cd815e4da98f4faaa44c6172ca5c365`
- origin_main_head: `e1733fe93cd815e4da98f4faaa44c6172ca5c365`
- sync_status: `SYNCED`
- compliance_status: `FAIL`
- latest_repo_sync_run_id: `missing`

## Sync Checks

| check | status |
|---|---|
| `branch_main` | PASS |
| `head_matches_origin_main` | PASS |
| `worktree_clean` | FAIL |
| `required_sync_policy_files_exist` | PASS |
| `repo_sync_check_run_available` | FAIL |

## Findings

- worktree_clean: `False`
- git_status_short_present: `True`
- status_short_lines:
  - `M projects/GameRuAI/ui_screenshots_manifest.json`
  - ` M projects/GameRuAI/ui_validation_summary.json`
  - ` M projects/GameRuAI/ui_validation_summary.md`
  - ` M projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/ui_snapshots/latest_run.json`
  - ` M projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/ui_snapshots/latest_run.txt`
  - ` M projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/ui_validation/latest_run.json`
  - ` M projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/ui_validation/latest_run.txt`
  - ` M projects/wild_hunt_command_citadel/tiktok_agent_platform/core/ui_screenshots_manifest.json`
  - ` M projects/wild_hunt_command_citadel/tiktok_agent_platform/core/ui_validation_summary.json`
  - ` M projects/wild_hunt_command_citadel/tiktok_agent_platform/core/ui_validation_summary.md`
  - ` M projects/wild_hunt_command_citadel/tiktok_agent_platform/core/ui_walkthrough_trace.json`
- gaps_count: `2`
- gap: `worktree_clean`
- gap: `repo_sync_check_run_available`
