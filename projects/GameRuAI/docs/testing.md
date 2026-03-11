# Testing

## Run all tests
```powershell
pytest
```

## Coverage groups
- `tests/unit/`
  - extractors and registry
  - language detector
  - placeholder/tag guards
  - glossary/memory
  - feedback service
  - voice linker
  - QA checks
- `tests/integration/`
  - full end-to-end pipeline with export
  - correction reuse through translation memory
- `tests/regression/`
  - scan manifest stability
  - extraction snapshot stability
  - language detection stability
  - TM reuse stability
  - learning loop stability
  - crash-safety (interrupted jobs/resume state)

## Notes
- Tests use temporary SQLite runtime paths.
- Fixture dataset is generated automatically by test session setup.
