# CODEX.md

## Project Identity

`shortform_core` is a modular decision-support workspace for short-form content operations.

Primary direction:
- multi-profile workspace
- content intelligence
- analytics-driven planning
- AI assist mode for analysis and creative briefing

Safety and compliance scope:
- not anti-detect software
- no stealth/evasion patterns
- no hidden human-like mass automation
- use provider abstractions for future official integrations

Project root:
- `projects/wild_hunt_command_citadel/shortform_core`

Path policy:
- use paths relative to this root
- avoid absolute machine-specific paths in docs/scripts/code

## Architecture Contract

Keep these layers separated:
- domain models (`app/workspace/models.py`)
- provider contracts (`app/workspace/contracts.py`)
- connectors/providers/adapters (`connectors.py`, `device_providers.py`, `metrics_providers.py`, `video_generator.py`)
- persistence (`app/workspace/persistence.py`)
- repositories/state (`app/workspace/repository.py`)
- policy guard (`app/workspace/policy.py`)
- services (`app/workspace/services/*`)
- transport (`app/workspace/api.py`, `app/api.py`)
- startup/orchestration (`app/startup_manager.py`, `app/launcher.py`)
- update/patch layer (`app/update/*`)

Do not place domain logic in UI/transport code.

## Workspace Design Constraints

- `Profile.connection_type` and `Profile.management_mode` are independent dimensions.
- profile limit is checked in service layer (`ProfileService`) and configured by `SFCO_MAX_PROFILES` (default `10`).
- all state-changing actions pass through `PolicyGuard`.
- analytics formulas must be explainable and testable.
- AI services are assistive, explainable, and policy-bound.

## Current Module Map

```text
app/
  launcher.py
  readiness.py
  startup_manager.py
  verify.py
  version.py
  desktop/
    main.py
    user_window.py
  update/
    models.py
    services.py
  tests_pytest/
    *.py
  tests/
    unit/
    integration/
    smoke/
app/workspace/
  ai_contracts.py
  ai_providers.py
  api.py
  connectors.py
  contracts.py
  demo_seed.py
  device_providers.py
  diagnostics.py
  persistence.py
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
```

## Verification Contract

- Use `python -m app.verify` as the canonical verification entrypoint.
- Verification gate statuses:
  - `PASS`
  - `PASS_WITH_WARNINGS`
  - `FAIL`
- User mode manual testing is allowed only when gate is `PASS`.
- Every significant change must be followed by:
  - real execution,
  - test/flow verification,
  - diagnostic logs,
  - status classification (`verified`, `partially verified`, `stub / not tested`, `failed`).
- Verification artifacts are written under:
  - `runtime/verification/<run_id>/verification_summary.json`
  - `runtime/verification/<run_id>/verification_summary.md`
  - `runtime/verification/<run_id>/readiness_summary.json`
  - `runtime/verification/<run_id>/consolidated_status.json`
  - `runtime/verification/<run_id>/patch_application_summary.json`
  - `runtime/verification/<run_id>/update_audit_summary.json`
  - `runtime/verification/<run_id>/diagnostics_manifest.json`
  - `runtime/verification/<run_id>/diagnostics/*.jsonl`
  - `runtime/verification/<run_id>/test_artifacts/*`

## Launch Modes

- `user mode`:
  - single entrypoint: `python -m app.launcher user`
  - launcher enforces machine gate before opening UI
  - desktop window starts with internal backend lifecycle orchestration
  - user should not manually manage `uvicorn`
- `developer mode`:
  - `python -m app.launcher developer backend`
  - `python -m app.launcher developer ui`
  - `python -m app.launcher developer verify`

## Extension Rules

- When adding a new external integration, first define/extend contract interfaces.
- Keep stubs honest with explicit `not_implemented` states.
- Preserve deterministic fallback behavior for local testing.
- Keep docs and run scripts aligned with current repository path.
