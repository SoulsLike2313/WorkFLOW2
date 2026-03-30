# SAFE MIRROR Build Report

- generated_at: `2026-03-30T00:13:16.021199+00:00`
- local_source_root: `E:\CVVCODEX`
- repo_name: `WorkFLOW2`
- evidence_contract_version: `2.0.0`
- evidence_mode: `tracked_evidence_refresh_commit`
- basis_head_sha: `de1bcabb8dba8d463c3ccdd0e89225839414547b`
- evidence_generated_at: `2026-03-30T00:13:16.021199+00:00`
- evidence_commit_note: `imperium_mode1_policy_gate_closure_delta_20260330T000729Z`
- active_project: `platform_test_agent`
- branch: `main`
- head_sha (basis): `de1bcabb8dba8d463c3ccdd0e89225839414547b`
- tracking_branch: `safe_mirror/main`
- ahead/behind: `0/0`
- worktree_clean: `True`
- tracked_files_count: `1630`
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
- `runtime/repo_control_center/constitution_status.json`
- `runtime/repo_control_center/constitution_status.md`

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
- allowlist_violations: `12`
- secret_hits: `0`
- failure_reasons:
  - tracked files outside allowlist roots

## Verdict
- publication_safe_verdict: `FAIL`
- sync_verdict: `PASS`
