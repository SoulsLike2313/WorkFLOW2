# Public Mirror Tools

## Source of Truth

- source repo: local working tree (`E:\CVVCODEX`)
- GitHub is not source of truth for this mirror workflow

## Mirror Path

- mirror root: `E:\_public_repo_mirror\WorkFLOW`
- mirror is outside source repo

## Fast Resume / Fast Sync

Primary entrypoint:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\fast_resume_public_mirror.ps1
```

Recommended fast run with explicit budgets:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\fast_resume_public_mirror.ps1 `
  -SourceRepoPath E:\CVVCODEX `
  -MirrorPath E:\_public_repo_mirror\WorkFLOW `
  -ExcludesFilePath E:\CVVCODEX\setup_reports\public_mirror_excludes.txt `
  -StageATimeBudgetSeconds 180 `
  -StageBTimeBudgetSeconds 180
```

Optional heavy tail completion:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\fast_resume_public_mirror.ps1 `
  -RunHeavyTail `
  -StageCTimeBudgetSeconds 600
```

## Stage Model

1. `STAGE_A_USABLE`
- fast sync of key engineering paths (`README*`, `docs`, `workspace_config`, `scripts`, `projects`, `setup_reports`, `shared_systems`)
- emits `PUBLIC_*` state files early

2. `STAGE_B_INCREMENTAL`
- incremental pass over source tree
- uses existing mirror baseline
- reflects deletions
- defers heavy tail by default

3. `STAGE_C_HEAVY_TAIL` (optional)
- explicit sync for deferred heavy paths
- does not block engineering-ready state

## Progress and Status Files

- `setup_reports/public_mirror_progress_status.json`
- `setup_reports/public_mirror_progress_status.md`
- mirror root:
  - `PUBLIC_REPO_STATE.json`
  - `PUBLIC_REPO_STATE.md`
  - `PUBLIC_SYNC_STATUS.json`
  - `PUBLIC_SYNC_STATUS.md`
  - `PUBLIC_ENTRYPOINTS.md`

## Security / Excludes

Excludes are defined in:

- `setup_reports/public_mirror_excludes.txt`
- `setup_reports/public_mirror_excludes.md`

Minimum blocked set:

- `.git/`
- `.env`, `.env.*`
- `*.pem`, `*.key`, `*.pfx`, `*.p12`
- `id_rsa`, `id_ed25519`
- `secrets.*`, `token*`, `credentials*`

Fast mode also excludes local heavy non-public trees:

- `.venv/`, `venv/`, `__pycache__/`
- `projects/wild_hunt_command_citadel/shortform_core/`

## Legacy Utilities

- `sync_repo_to_public_mirror.ps1` (single-pass sync)
- `start_public_mirror_watch.ps1` (watch mode)
- `validate_public_mirror.ps1` (validation)
- `stop_public_mirror_watch.ps1` (stop helper)
