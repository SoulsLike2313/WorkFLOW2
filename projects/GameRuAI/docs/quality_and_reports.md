# Quality And Reports

## Scope
Reports layer provides compact project diagnostics for long-running iteration.
It is designed for transparency, not marketing claims.

## Generated Reports
- Translation report:
  - backend usage statistics
  - latency statistics (avg/min/max/p95)
  - glossary hit rate
  - TM hit rate
  - uncertain language detection rate
  - low-quality translation counts
- Language report:
  - language distribution
  - uncertain/mixed-language lines
  - lines by context type and translation status
- Voice report:
  - attempt totals and status counts
  - alignment and quality averages
  - per-speaker summary
  - synthesis mode usage (`mock_demo_tts_stub` vs others if present)
- QA dashboard:
  - broken placeholders
  - broken tags
  - untranslated lines
  - export integrity summary
  - problematic files/lines
- Companion diagnostics:
  - session count/statuses
  - watched file event totals and event types

## UI
- `Reports` tab:
  - quality dashboard widgets
  - translation metrics table
  - language distribution table
  - QA summary table
  - compact summary JSON block
- `Diagnostics` tab:
  - backend diagnostics table
  - project report history
  - quality snapshot history

## Persistence Tables
- `language_reports`
- `project_reports`
- `backend_diagnostics`
- `quality_snapshots`

## Notes
- Reports are generated from real pipeline data only.
- Demo/mock fallback behavior is shown explicitly; it is not hidden.
- Metrics are diagnostic indicators for iteration, not final production guarantees.
