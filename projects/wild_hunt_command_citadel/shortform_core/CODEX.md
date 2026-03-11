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
- repositories/state (`app/workspace/repository.py`)
- policy guard (`app/workspace/policy.py`)
- services (`app/workspace/services/*`)
- transport (`app/workspace/api.py`, `app/api.py`)

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
  verify.py
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
- Every significant change must be followed by:
  - real execution,
  - test/flow verification,
  - diagnostic logs,
  - status classification (`verified`, `partially verified`, `stub / not tested`, `failed`).
- Verification artifacts are written under:
  - `runtime/verification/<run_id>/verification_summary.json`
  - `runtime/verification/<run_id>/verification_summary.md`
  - `runtime/verification/<run_id>/diagnostics/*.jsonl`

## Extension Rules

- When adding a new external integration, first define/extend contract interfaces.
- Keep stubs honest with explicit `not_implemented` states.
- Preserve deterministic fallback behavior for local testing.
- Keep docs and run scripts aligned with current repository path.
