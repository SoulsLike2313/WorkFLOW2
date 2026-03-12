# Translation Backends

## Working Core
- Router: `app/translator/router.py`
- Orchestrator: `app/translator/realtime_orchestrator.py`
- Context: `app/translator/context_builder.py`, `app/core/context_models.py`
- Policy + evidence:
  - `app/translator/translation_policies.py`
  - `app/translator/evidence_router.py`
  - `app/translator/reference_compare.py`

## Available Adapters
- `local_mock` - working default backend
- `dummy` - safe fallback backend
- `argos` - optional adapter (fallback if dependency missing)
- `transformers` - optional adapter (fallback if dependency missing)
- `local_nllb` - foundation adapter (dependency-gated)
- `cloud_adapter` - foundation adapter (env-gated, disabled by default)
- `policy_auto` (UI mode) - chooses backend by policy, still fallback-safe

## Translation Package Architecture
Each line can be stored as `translation_packages` with:
- source text/language
- context summary
- chosen backend + fallback flag
- glossary/TM hits
- alternatives (policy candidates)
- quality/confidence
- warnings
- final translation
- reference compare payload (when available)

## Transparency
Persisted tables:
- `translations`
- `translation_backend_runs`
- `translation_packages`
- `external_reference_events`
- `evidence_records`

## Honest Status
- Working: local mock pipeline with full transparency and package persistence.
- Partial: optional advanced adapters depending on local environment.
- Foundation only: cloud/local-nllb adapters as extensible interfaces.
- No production MT claim.

