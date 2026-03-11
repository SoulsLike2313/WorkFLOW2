# Testing

## Run all tests
```powershell
pytest -q
```

## Coverage groups
- `tests/unit/`
  - extractors and registry
  - language detector
  - placeholder/tag guards
  - glossary/memory
  - feedback service
  - voice linking/grouping/duration/history
  - report builders and diagnostics calculations
  - QA checks
- `tests/integration/`
  - full end-to-end pipeline with export
  - translation context/fallback
  - companion quick rescan
  - asset research indexing/preview fallback
  - voice preparation pipeline
  - report generation after pipeline
- `tests/regression/`
  - scan manifest stability
  - extraction snapshot stability
  - language detection stability
  - TM reuse stability
  - learning loop stability
  - crash-safety (interrupted jobs/resume state)
  - previous sprint flow stability (translation/companion)

## Useful focused runs
```powershell
pytest -q tests/integration/test_reports_generation.py
pytest -q tests/unit/test_report_builders.py tests/unit/test_metrics_aggregation.py tests/unit/test_backend_diagnostics_calculations.py
```

## Notes
- Tests use temporary SQLite runtime paths.
- Fixture dataset is generated automatically by test session setup.
- Metrics/diagnostics tests validate real stored pipeline data (no fake metrics).
