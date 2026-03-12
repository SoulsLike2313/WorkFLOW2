# GitHub Sync Compliance Report

- run_id: `full-platform-audit-20260312T221721Z`
- generated_at_utc: `2026-03-12T22:17:21.943491+00:00`
- branch: `main`
- local_head: `0505d21292ab21d09dd84e74ba16ed4521fac68d`
- origin_main_head: `0505d21292ab21d09dd84e74ba16ed4521fac68d`
- sync_status: `SYNCED`
- compliance_status: `PASS_WITH_WARNINGS`
- latest_repo_sync_run_id: `repo-sync-20260312T215553Z`

## Sync Checks

| check | status |
|---|---|
| `branch_main` | PASS |
| `head_matches_origin_main` | PASS |
| `worktree_clean` | FAIL |
| `required_sync_policy_files_exist` | PASS |
| `repo_sync_check_run_available` | PASS |

## Findings

- worktree_clean: `False`
- git_status_short_present: `True`
- status_short_lines:
  - `M docs/review_artifacts/GITHUB_SYNC_COMPLIANCE_REPORT.md`
  - `M docs/review_artifacts/MACHINE_READABILITY_AUDIT.md`
  - `M docs/review_artifacts/MODULE_MATURITY_MATRIX.md`
  - `M docs/review_artifacts/PLATFORM_AUDIT_REPORT.md`
  - `M docs/review_artifacts/PROJECT_RUNTIME_HEALTH_MATRIX.md`
  - `M docs/review_artifacts/PROJECT_SYSTEM_COVERAGE.md`
- gaps_count: `1`
- gap: `worktree_clean`
