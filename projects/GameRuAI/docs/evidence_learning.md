# Evidence & Learning Core

## Modules
- `app/learning/evidence_store.py`
- `app/learning/correction_memory.py`
- `app/learning/adaptation_engine.py`
- `app/learning/confidence_tracking.py`
- `app/learning/regression_memory.py`
- `app/learning/external_reference_log.py`

## Storage
- `evidence_records`
- `external_reference_events`
- existing learning tables:
  - `correction_history`
  - `adaptation_events`
  - `translation_memory`
  - `glossary_terms`

## Working Loop
1. Translation attempt -> translation package stored.
2. Confidence/uncertainty and warnings recorded.
3. User correction stored.
4. TM/glossary/source registry updated.
5. New attempts can reuse previous evidence.

## Honest Status
- Working: evidence trail persistence and UI visibility.
- Partial: quality comparison logic is heuristic-based.
- No claim of live model retraining.

