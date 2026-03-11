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
  analytics.py
  api.py
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
    api.py
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
      metrics_service.py
      profile_service.py
      session_service.py
      video_generation_service.py
CODEX.md
PROMPT_FOR_CODEX.txt
requirements.txt
run_setup.ps1
```

## Quick Start (Windows)

```powershell
cd projects/wild_hunt_command_citadel/shortform_core
powershell -ExecutionPolicy Bypass -File .\run_setup.ps1
```

Then run API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload
```

## Manual Start

```powershell
cd projects/wild_hunt_command_citadel/shortform_core
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python -m app.main
python -m app.bootstrap_v2
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload
```

## Verification Workflow

Run full verification pipeline:

```powershell
cd projects/wild_hunt_command_citadel/shortform_core
.\.venv\Scripts\python.exe -m app.verify
```

What it does:
- checks environment and installs dependencies (`pip install -r requirements.txt`)
- initializes verification SQLite database
- applies schema/bootstrap and loads demo seed
- runs `unit`, `integration`, and API smoke tests
- validates key workspace/analytics/AI/generation flows
- collects structured diagnostics logs
- writes machine-readable report:
  - `runtime/verification/<run_id>/verification_summary.json`
  - `runtime/verification/<run_id>/verification_summary.md`

Optional direct test runs:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s app/tests/unit -t . -p "test_*.py"
.\.venv\Scripts\python.exe -m unittest discover -s app/tests/integration -t . -p "test_*.py"
.\.venv\Scripts\python.exe -m unittest discover -s app/tests/smoke -t . -p "test_*.py"
```

## Config (Environment Variables)

- `SFCO_MAX_PROFILES` (default: `10`)
- `SFCO_API_HOST` (default: `127.0.0.1`)
- `SFCO_API_PORT` (default: `8000`)
- `SFCO_DATABASE_PATH`
- `SFCO_OUTPUT_DIR`
- `SFCO_LOGS_DIR`
- `SFCO_VERIFICATION_DIR`
- `SFCO_DEBUG_LOGS` (`1/true/on` enables debug diagnostics)
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
- `POST /bootstrap/load-demo`
- `GET /accounts/{account_id}/snapshot`
- `POST /metrics/ingest`
- `POST /plan/generate`
- `GET /plan/{account_id}/latest`

Workspace endpoints:
- Profiles:
  - `POST /workspace/profiles`
  - `GET /workspace/profiles`
  - `GET /workspace/profiles/{profile_id}`
  - `POST /workspace/profiles/{profile_id}/connect`
  - `POST /workspace/profiles/{profile_id}/disconnect`
  - `POST /workspace/profiles/{profile_id}/management-mode`
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
