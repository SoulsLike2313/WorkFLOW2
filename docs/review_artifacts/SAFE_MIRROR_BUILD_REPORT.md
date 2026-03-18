# SAFE MIRROR Build Report

- generated_at: `2026-03-18T01:51:50.736589+00:00`
- local_source_root: `E:\CVVCODEX`
- repo_name: `WorkFLOW2`
- evidence_contract_version: `2.0.0`
- evidence_mode: `tracked_evidence_refresh_commit`
- basis_head_sha: `68cb366c216a6edc2f21c53239219ee14b04ecff`
- evidence_generated_at: `2026-03-18T01:51:50.736589+00:00`
- evidence_commit_note: `post-targeted-proof-closure-reports`
- active_project: `platform_test_agent`
- branch: `main`
- head_sha (basis): `68cb366c216a6edc2f21c53239219ee14b04ecff`
- tracking_branch: `safe_mirror/main`
- ahead/behind: `0/0`
- worktree_clean: `True`
- tracked_files_count: `1212`
- sync_verdict: `PASS`
- publication_safe_verdict: `FAIL`

## Evidence Contract
- tracked evidence artifacts describe `basis_head_sha` commit.
- for `tracked_evidence_refresh_commit` mode, current `HEAD` can be an evidence refresh commit on top of basis.

## Included Roots
- `docs`
- `integration`
- `projects`
- `scripts`
- `shared_systems`
- `tasks`
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
- disallowed_tracked_paths: `2`
- allowlist_violations: `2`
- secret_hits: `0`
- failure_reasons:
  - disallowed tracked paths detected
  - tracked files outside allowlist roots

## Verdict
- publication_safe_verdict: `FAIL`
- sync_verdict: `PASS`
