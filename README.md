# WorkFLOW Repository

Monorepo with several projects.  
Current priority product: `shortform_core`.

## Current Structure

- `projects/wild_hunt_command_citadel/shortform_core`
- `projects/adaptive_trading`
- `projects/voice_launcher`

## Canonical Verification Entrypoint

Use exactly one canonical command:

```powershell
cd projects/wild_hunt_command_citadel/shortform_core
.\.venv\Scripts\python.exe -m app.verify
```

Machine gate statuses:

- `PASS`
- `PASS_WITH_WARNINGS`
- `FAIL`

Manual testing is allowed only when gate is `PASS`.

## Required Verification Artifacts

After `python -m app.verify`, these files must exist in:

`projects/wild_hunt_command_citadel/shortform_core/runtime/verification/<run_id>/`

- `verification_summary.json`
- `verification_summary.md`
- `readiness_summary.json`
- `consolidated_status.json`
- `patch_application_summary.json`
- `update_audit_summary.json`
- `diagnostics_manifest.json`

## User Mode

From `projects/wild_hunt_command_citadel/shortform_core`:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_user.ps1
```

Expected behavior:

- gate check runs first
- user mode starts only on `PASS`
- desktop window opens
- internal backend is managed automatically (no manual server startup)

## User Update / Patch Flow

From `projects/wild_hunt_command_citadel/shortform_core`:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_update.ps1 -Mode check -ManifestPath .\runtime\verification\<run_id>\manifest.json
powershell -ExecutionPolicy Bypass -File .\run_update.ps1 -Mode apply -BundlePath .\runtime\verification\<run_id>\patch_bundle.zip -TargetVersion 0.4.1
powershell -ExecutionPolicy Bypass -File .\run_update.ps1 -Mode post-verify
```

This is user-facing flow and does not require manual `uvicorn` or `/updates/*` API calls.

## Developer Mode

From `projects/wild_hunt_command_citadel/shortform_core`:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_developer.ps1
```

Developer API update flow remains available via backend endpoints when needed.

## GitHub Auto Sync Scripts

- `scripts/auto_sync.ps1`
- `scripts/check_repo_sync.ps1`
- `scripts/sync_and_check.ps1`
- `scripts/register_auto_sync_task.ps1`
- `scripts/unregister_auto_sync_task.ps1`

## Full Sync + Match Check (Windows)

After each major update run:

```powershell
cd <repo-root>
powershell -ExecutionPolicy Bypass -File .\scripts\sync_and_check.ps1 -Branch main -CommitMessage "sync: major update"
```

Strict check only (without commit/push):

```powershell
cd <repo-root>
powershell -ExecutionPolicy Bypass -File .\scripts\check_repo_sync.ps1 -Branch main
```
