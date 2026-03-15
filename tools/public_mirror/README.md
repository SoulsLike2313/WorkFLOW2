# Public Mirror Toolkit

## Canonical Paths

- source repo: `E:\CVVCODEX`
- mirror root: `E:\_public_repo_mirror\WorkFLOW`
- mirror is outside source repo and outside `tools/`
- GitHub is not source of truth for this mirror workflow

## Stage Model (FAST_RESUME_STAGED)

1. `STAGE_A_USABLE`
- syncs key engineering paths first: `README*`, `docs`, `workspace_config`, `scripts`, `projects`, `setup_reports`, `shared_systems`
- emits `PUBLIC_REPO_STATE.*`, `PUBLIC_SYNC_STATUS.*`, `PUBLIC_ENTRYPOINTS.md`

2. `STAGE_B_INCREMENTAL`
- incremental whole-tree sync from existing mirror baseline
- reflects deletions
- does not require full rebuild

3. `STAGE_C_HEAVY_TAIL` (optional)
- deferred heavy paths (`runtime`, `setup_assets`)
- not required for engineering-ready state

## ENGINEERING READY Gate

Mirror is engineering-ready when all are true:
- `README/docs/workspace_config/scripts/projects` exist in mirror
- `PUBLIC_REPO_STATE.*`, `PUBLIC_SYNC_STATUS.*`, `PUBLIC_ENTRYPOINTS.md` exist
- excludes are applied
- `.git/.env/keys/tokens/secrets` are not exposed

## Entrypoints

- fast resume (recommended):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\fast_resume_public_mirror.ps1 `
  -SourceRepoPath E:\CVVCODEX `
  -MirrorPath E:\_public_repo_mirror\WorkFLOW `
  -ExcludesFilePath E:\CVVCODEX\setup_reports\public_mirror_excludes.txt `
  -StageATimeBudgetSeconds 180 `
  -StageBTimeBudgetSeconds 180
```

- safe resume from checkpoint/mirror:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\resume_public_mirror.ps1 `
  -SourceRepoPath E:\CVVCODEX
```

- manual single-pass sync (legacy helper):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\sync_repo_to_public_mirror.ps1 `
  -SourceRepoPath E:\CVVCODEX `
  -MirrorPath E:\_public_repo_mirror\WorkFLOW `
  -ExcludesFilePath E:\CVVCODEX\setup_reports\public_mirror_excludes.txt
```

- watch mode:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\start_public_mirror_watch.ps1 `
  -SourceRepoPath E:\CVVCODEX `
  -MirrorPath E:\_public_repo_mirror\WorkFLOW `
  -ExcludesFilePath E:\CVVCODEX\setup_reports\public_mirror_excludes.txt
```

- local web start:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\start_public_mirror_web.ps1 `
  -SourceRepoPath E:\CVVCODEX `
  -MirrorPath E:\_public_repo_mirror\WorkFLOW `
  -Port 18080
```

- local web stop:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\stop_public_mirror_web.ps1 `
  -SourceRepoPath E:\CVVCODEX
```

- local web check:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\check_public_mirror_web.ps1 `
  -SourceRepoPath E:\CVVCODEX
```

- public access start (localhost.run tunnel):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\start_public_mirror_public_access.ps1 `
  -SourceRepoPath E:\CVVCODEX `
  -Port 18080
```

- public access check:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\check_public_mirror_public_access.ps1 `
  -SourceRepoPath E:\CVVCODEX
```

- end-to-end validation:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\validate_public_mirror.ps1 `
  -SourceRepoPath E:\CVVCODEX `
  -MirrorPath E:\_public_repo_mirror\WorkFLOW `
  -ExcludesFilePath E:\CVVCODEX\setup_reports\public_mirror_excludes.txt
```

## Excludes

- source file: `setup_reports/public_mirror_excludes.txt`
- policy doc: `setup_reports/public_mirror_excludes.md`

Minimum sensitive excludes:
- `.git/`
- `.env`, `.env.*`
- `*.pem`, `*.key`, `*.pfx`, `*.p12`
- `id_rsa`, `id_ed25519`
- `secrets.*`, `token*`, `credentials*`
- `.venv/`, `venv/`, `__pycache__/`

## Runtime/State Files

- source runtime state: `setup_reports/public_runtime_state.json`
- progress: `setup_reports/public_mirror_progress_status.json` and `.md`
- validation: `setup_reports/public_repo_access_validation.json` and `.md`
- web check: `setup_reports/public_mirror_web_check.json` and `.md`
- public check: `setup_reports/public_access_check.json` and `.md`

Mirror root files:
- `PUBLIC_REPO_STATE.json/.md`
- `PUBLIC_SYNC_STATUS.json/.md`
- `PUBLIC_ENTRYPOINTS.md`
