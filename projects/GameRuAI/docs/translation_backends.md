# Translation Backends (Sprint Scope)

## Working Architecture
- Router: `app/translator/router.py`
- Backends:
  - `app/translator/local_mock_backend.py`
  - `app/translator/dummy_backend.py`
  - `app/translator/backends/argos_backend.py`
  - `app/translator/backends/transformers_backend.py`
- Orchestrator: `app/translator/realtime_orchestrator.py`
- Context builder: `app/translator/context_builder.py`
- Context model: `app/core/context_models.py`

## Backend Selection
`TranslatorRouter.resolve(requested_backend)` returns:
- active backend
- fallback info (`fallback_used`, `fallback_backend`, reason)

If requested optional backend is unavailable, router falls back to `local_mock` (or `dummy` if needed).

## Context-Aware Translation
Context fields used:
- `speaker_id`
- `scene_id`
- `neighboring_lines`
- `line_type`
- `file_group`
- `style_preset`

Context is built before translation and passed to backend.
`context_used` is stored in `translations` and `translation_backend_runs`.

## Transparency Data (Implemented)
For each translation run, the app stores and/or displays:
- requested backend
- active backend
- fallback backend
- TM hit / glossary hit
- context used
- latency (ms)
- quality score
- uncertainty warning

UI locations:
- `Translation` tab: backend status + translation table columns
- `Entries` tab: `Context` column
- `Jobs / Logs` tab: backend run records

## Database Tables Used
- `translations` (includes `backend`, `fallback_backend`, `context_used`)
- `translation_backend_runs`

## Working vs Fallback/Demo
Working now:
- full pipeline with `local_mock` and `dummy`
- graceful fallback if `argos`/`transformers` are missing
- context pipeline end-to-end

Fallback/demo behavior:
- `argos` and `transformers` backends are lightweight adapters and require optional dependencies
- when dependencies are not installed, fallback is expected and logged

Not implemented in this sprint:
- heavy production-grade MT model orchestration
- remote provider integrations
- automatic model download/management UI
