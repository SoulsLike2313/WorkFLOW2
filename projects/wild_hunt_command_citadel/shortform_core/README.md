# shortform_core

Modular Python workspace for short-form account operations:
- multi-profile management (configurable limit, default `MAX_PROFILES=10`)
- session windows with mobile viewport presets (9:16 concept)
- provider-based profile connections (`cdp`, `official_auth`, `device`)
- content desk (library, validation, queue)
- metrics ingestion and explainable analytics
- content intelligence and action-plan generation
- AI assist mode (perception, workflow guidance, learning, creative briefing)
- typed audit and error timeline

Important safety scope:
- this project is not anti-detect software
- no stealth or evasive behavior
- no hidden human-like mass automation
- no plaintext secret storage in code

## Project Root

Run all commands from:

`projects/wild_hunt_command_citadel/shortform_core`

## Current Structure

```text
app/
  api.py
  launcher.py
  readiness.py
  startup_manager.py
  verify.py
  version.py
  update/
    models.py
    services.py
  desktop/
    main.py
    user_window.py
  tests_pytest/
    *.py
  tests/
    unit/
    integration/
    smoke/
  analytics.py
  bootstrap_v2.py
  config.py
  db.py
  demo_data.py
  io_utils.py
  main.py
  models.py
  planner.py
  registry.py
  repository.py
  schemas.py
  workspace/
    persistence.py
    demo_seed.py
    diagnostics.py
    api.py
    ai_contracts.py
    ai_providers.py
    connectors.py
    contracts.py
    device_providers.py
    errors.py
    metrics_providers.py
    models.py
    policy.py
    repository.py
    runtime.py
    schemas.py
    video_generator.py
    services/
      ai_services.py
      analytics_services.py
      audit_service.py
      content_service.py
      generation_prep_service.py
      metrics_service.py
      profile_service.py
      session_service.py
      video_generation_service.py
CODEX.md
PROMPT_FOR_CODEX.txt
requirements.txt
run_setup.ps1
run_user.ps1
run_developer.ps1
run_update.ps1
```

## User Mode (Desktop)

```powershell
cd projects/wild_hunt_command_citadel/shortform_core
powershell -ExecutionPolicy Bypass -File .\run_user.ps1 -PortMode fixed
```

What happens:
- startup preflight is executed first (`scripts/project_startup.py prepare`)
- machine verification gate is executed first (`python -m app.verify`)
- if gate is `PASS`, desktop app opens
- backend API is started automatically in the background and managed by launcher
- user does not need to manually run `uvicorn` or open localhost
- direct command `python -m app.launcher user` also enforces gate before window startup

## Developer Mode

Setup and show developer commands:

```powershell
cd projects/wild_hunt_command_citadel/shortform_core
powershell -ExecutionPolicy Bypass -File .\run_developer.ps1 -PortMode fixed
```

Direct developer commands:

```powershell
.\.venv\Scripts\python.exe -m app.launcher developer backend --host 127.0.0.1 --port $env:SFCO_API_PORT
.\.venv\Scripts\python.exe -m app.launcher developer ui --api-base-url http://127.0.0.1:$env:SFCO_API_PORT
.\.venv\Scripts\python.exe -m app.verify
```

## Verification Workflow

Canonical verify entrypoint:

```powershell
.\.venv\Scripts\python.exe -m app.verify
```

Run full verification pipeline:

```powershell
cd projects/wild_hunt_command_citadel/shortform_core
.\.venv\Scripts\python.exe -m app.verify
```

What it does:
- checks environment and installs dependencies (`pip install -r requirements.txt`)
- validates config and startup prerequisites
- initializes verification SQLite + workspace persistence state
- applies schema/bootstrap and loads demo seeds
- runs `unittest` suites (`unit`, `integration`, `smoke`)
- runs `pytest` suites (`app/tests_pytest`)
- runs runtime readiness checks (backend start/ready)
- runs AI contract checks
- runs UI/backend connectivity checks
- runs update/patch checks with post-update verification
- collects structured diagnostics logs and test artifacts
- writes machine-readable report:
  - `runtime/verification/<run_id>/verification_summary.json`
  - `runtime/verification/<run_id>/verification_summary.md`
  - `runtime/verification/<run_id>/readiness_summary.json`
  - `runtime/verification/<run_id>/consolidated_status.json`
  - `runtime/verification/<run_id>/test_results.json`
  - `runtime/verification/<run_id>/patch_application_summary.json`
  - `runtime/verification/<run_id>/update_audit_summary.json`
  - `runtime/verification/<run_id>/diagnostics_manifest.json`

Verification gate status:
- `PASS`: manual user-mode testing is allowed
- `PASS_WITH_WARNINGS`: manual user-mode testing is blocked
- `FAIL`: manual user-mode testing is blocked

Optional direct test runs:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s app/tests/unit -t . -p "test_*.py"
.\.venv\Scripts\python.exe -m unittest discover -s app/tests/integration -t . -p "test_*.py"
.\.venv\Scripts\python.exe -m unittest discover -s app/tests/smoke -t . -p "test_*.py"
.\.venv\Scripts\python.exe -m pytest app/tests_pytest -q
```

## Update / Patch Mode

### User Update Flow (No Manual API/Ports)

Use script flow from project root:

```powershell
cd projects/wild_hunt_command_citadel/shortform_core
```

1) Check manifest compatibility:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_update.ps1 -Mode check -PortMode fixed -ManifestPath .\runtime\verification\<run_id>\manifest.json
```

2) Apply local patch bundle:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_update.ps1 -Mode apply -PortMode fixed -BundlePath .\runtime\verification\<run_id>\patch_bundle.zip -TargetVersion 0.4.1
```

3) Run post-update verification:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_update.ps1 -Mode post-verify -PortMode fixed
```

Script outputs:

- `runtime/output/update_check_result.json`
- `runtime/output/update_apply_result.json`
- `runtime/output/update_post_verify_result.json`

### Developer Update Flow (API)

Developer backend:

```powershell
.\.venv\Scripts\python.exe -m app.launcher developer backend --host 127.0.0.1 --port 8000
```

Manifest check:

```powershell
# then call:
# POST /updates/check?manifest_path=path\to\manifest.json
```

Local patch apply:

```powershell
# POST /updates/apply-local?bundle_path=path\to\bundle.zip&target_version=0.4.1
```

Post-update verification:

```powershell
# GET /updates/post-verify
```

## Runtime Artifacts Layout

```text
runtime/
  logs/
    runtime_logs.jsonl
    audit_logs.jsonl
    verification_logs.jsonl
    diagnostics_logs.jsonl (if enabled by flow)
    ai_learning_logs.jsonl
    update_logs.jsonl
    patch_logs.jsonl
  verification/
    verify-<timestamp>/
      verification_summary.json
      verification_summary.md
      readiness_summary.json
      consolidated_status.json
      test_results.json
      patch_application_summary.json
      update_audit_summary.json
      diagnostics_manifest.json
      logs/
      diagnostics/
      test_artifacts/
  patches/
```

## Config (Environment Variables)

- `SFCO_MAX_PROFILES` (default: `10`)
- `SFCO_API_HOST` (default: `127.0.0.1`)
- `SFCO_API_PORT` (selected from `shortform_core` range `8000-8099`, default `8000` in fixed mode)
- `SFCO_DATABASE_PATH`
- `SFCO_WORKSPACE_STATE_PATH`
- `SFCO_OUTPUT_DIR`
- `SFCO_LOGS_DIR`
- `SFCO_VERIFICATION_DIR`
- `SFCO_PATCH_DIR`
- `SFCO_DEBUG_LOGS` (`1/true/on` enables debug diagnostics)
- `SFCO_MODE` (`user` or `developer`)
- analytics weights:
  - `SFCO_VIEWS_WEIGHT`
  - `SFCO_LIKES_WEIGHT`
  - `SFCO_COMMENTS_WEIGHT`
  - `SFCO_SHARES_WEIGHT`
  - `SFCO_FAVORITES_WEIGHT`
  - `SFCO_WATCH_TIME_WEIGHT`
  - `SFCO_COMPLETION_WEIGHT`

## API Overview

Legacy core endpoints:
- `GET /health`
- `GET /readiness`
- `POST /bootstrap/load-demo`
- `GET /accounts/{account_id}/snapshot`
- `POST /metrics/ingest`
- `POST /plan/generate`
- `GET /plan/{account_id}/latest`
- Updates:
  - `GET /updates/version`
  - `POST /updates/check`
  - `POST /updates/apply-local`
  - `GET /updates/post-verify`

Workspace endpoints:
- Profiles:
  - `POST /workspace/profiles`
  - `GET /workspace/profiles`
  - `GET /workspace/profiles/{profile_id}`
  - `POST /workspace/profiles/{profile_id}/connect`
  - `POST /workspace/profiles/{profile_id}/disconnect`
  - `POST /workspace/profiles/{profile_id}/management-mode`
  - `GET /workspace/readiness`
- Session:
  - `POST /workspace/sessions/{profile_id}/open`
  - `POST /workspace/sessions/{profile_id}/close`
  - `POST /workspace/sessions/{profile_id}/viewport`
  - `GET /workspace/sessions/{profile_id}`
- Content:
  - `POST /workspace/content`
  - `GET /workspace/content`
  - `POST /workspace/content/{content_id}/validate`
  - `POST /workspace/content/{content_id}/queue`
- Metrics and analytics:
  - `POST /workspace/metrics/ingest`
  - `POST /workspace/metrics/import`
  - `GET /workspace/analytics/profiles/{profile_id}/performance`
  - `GET /workspace/analytics/profiles/{profile_id}/top-content`
  - `GET /workspace/analytics/profiles/{profile_id}/patterns`
  - `POST /workspace/analytics/profiles/{profile_id}/action-plan`
  - `GET /workspace/analytics/profiles/{profile_id}/recommendations/latest`
- AI mode:
  - `POST /workspace/ai/analyze/frame`
  - `POST /workspace/ai/analyze/asset`
  - `POST /workspace/ai/evaluate/content`
  - `POST /workspace/ai/recommendations/generate`
  - `POST /workspace/ai/feedback/ingest`
  - `POST /workspace/ai/feedback/recommendation`
  - `POST /workspace/ai/feedback/outcome`
  - `GET /workspace/profiles/{profile_id}/ai/recommendations`
  - `GET /workspace/profiles/{profile_id}/ai/learnings`
  - `GET /workspace/ai/workflow/{profile_id}/summary`
  - `GET /workspace/ai/workflow/{profile_id}/guidance`
  - `POST /workspace/ai/profiles/{profile_id}/video-brief`
  - `POST /workspace/ai/video-briefs/{brief_id}/submit`
  - `GET /workspace/ai/video-jobs/{external_job_id}/status`
  - `GET /workspace/ai/video-jobs/{external_job_id}/assets`
- Generation prep:
  - `POST /workspace/profiles/{profile_id}/generation/video-brief`
  - `POST /workspace/profiles/{profile_id}/generation/audio-brief`
  - `POST /workspace/profiles/{profile_id}/generation/script-brief`
  - `POST /workspace/profiles/{profile_id}/generation/text-brief`
  - `POST /workspace/profiles/{profile_id}/generation/bundles/build`
  - `GET /workspace/profiles/{profile_id}/generation/bundles`
- Legacy AI compatibility:
  - `POST /workspace/ai/perception/analyze`
  - `POST /workspace/ai/content/{content_id}/evaluate`
  - `POST /workspace/ai/feedback`
  - `GET /workspace/ai/profiles/{profile_id}/recommendations`
  - `GET /workspace/ai/profiles/{profile_id}/learning-summary`
- Audit:
  - `GET /workspace/audit/log`
  - `GET /workspace/audit/errors`

## What Is Stubbed In This Iteration

- `OfficialAuthConnector` is a contract stub (`not_implemented`)
- device providers are mock/provider-based skeletons for `local_android`, `emulator`, `remote_device`
- `MockVideoGeneratorAdapter` is a contract stub (no real generation yet)
- optional AI model adapter is not connected by default (heuristic mode is active)

## Quick Local Smoke Test

```powershell
.\.venv\Scripts\python.exe -c "from fastapi.testclient import TestClient; from app.api import app; c=TestClient(app); print(c.get('/workspace/health').status_code)"
```
