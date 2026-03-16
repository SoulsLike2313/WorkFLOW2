# SAFE MIRROR Build Report

- generated_at: `2026-03-16T21:50:47.080083+00:00`
- local_source_root: `E:\CVVCODEX`
- repo_name: `WorkFLOW2`
- evidence_contract_version: `2.0.0`
- evidence_mode: `tracked_evidence_refresh_commit`
- basis_head_sha: `5c020b666b66f568ce632722b6ebb69172b00d67`
- evidence_generated_at: `2026-03-16T21:50:47.080083+00:00`
- evidence_commit_note: `evidence refresh commit for audit baseline 5c020b6`
- active_project: `platform_test_agent`
- branch: `main`
- head_sha (basis): `5c020b666b66f568ce632722b6ebb69172b00d67`
- tracking_branch: `safe_mirror/main`
- ahead/behind: `0/0`
- worktree_clean: `True`
- tracked_files_count: `1056`
- sync_verdict: `PASS`
- publication_safe_verdict: `PASS`

## Evidence Contract
- tracked evidence artifacts describe `basis_head_sha` commit.
- for `tracked_evidence_refresh_commit` mode, current `HEAD` can be an evidence refresh commit on top of basis.

## Included Roots
- `docs`
- `projects`
- `scripts`
- `shared_systems`
- `workspace_config`
- `.gitignore`
- `MACHINE_CONTEXT.md`
- `README.md`
- `REPO_MAP.md`

## Excluded Categories
- .env files
- credentials and private keys
- runtime dumps and logs
- temporary/cache artifacts
- network diagnostics and publication leftovers
- legacy publication/tunnel artifacts
- local machine-only backups

## Required File Check
- missing_required_files: `0`

## Safety Check Findings
- disallowed_tracked_paths: `0`
- allowlist_violations: `0`
- secret_hits: `0`
- failure_reasons: none

## Verdict
- publication_safe_verdict: `PASS`
- sync_verdict: `PASS`
