# Translation Backends

## Working Architecture
- Router: `app/translator/router.py`
- Backends:
  - `app/translator/local_mock_backend.py`
  - `app/translator/dummy_backend.py`
  - `app/translator/backends/argos_backend.py`
  - `app/translator/backends/transformers_backend.py`
- Orchestrator: `app/translator/realtime_orchestrator.py`
- Context builder/model:
  - `app/translator/context_builder.py`
  - `app/core/context_models.py`

## Backend Selection
`TranslatorRouter.resolve(requested_backend)` returns active backend plus fallback metadata.
If optional backend is unavailable, fallback is explicit and logged.

## Persisted Transparency Data
Per translation/backend run:
- requested backend
- active backend
- fallback flag and fallback backend
- latency
- context-used flag
- TM/glossary usage
- quality/uncertainty

Tables:
- `translations`
- `translation_backend_runs`
- `backend_diagnostics` (aggregated report view)

## Diagnostics and Metrics
Reports layer calculates:
- backend usage distribution
- avg/min/max/p95 latency
- fallback rate
- context usage rate
- glossary hit rate
- TM hit rate
- uncertain language rate
- low-quality translation counts

UI:
- `Translation` tab (line-level transparency)
- `Reports` tab (project translation metrics)
- `Diagnostics` tab (backend aggregated diagnostics)

## Honest Status
- `local_mock`/`dummy` are primary local demo backends.
- `argos`/`transformers` are optional adapters and may fallback if dependencies are missing.
- No production-grade MT claims in this MVP.
