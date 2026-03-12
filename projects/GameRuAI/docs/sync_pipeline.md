# Sync Pipeline

## Modules
- `app/sync/duration_alignment.py`
- `app/sync/subtitle_sync.py`
- `app/sync/audio_sync.py`
- `app/sync/rebuild_plan.py`
- `app/sync/export_targets.py`

## Working Outputs
- Per-line sync plan with:
  - source duration
  - target duration
  - delta
  - recommended adjustment
  - confidence/status
- Stored in `sync_plans`.

## UI
- `Sync Review` tab shows plan list, high-risk counts, export-risk summary.

## Honest Status
- Working: heuristic sync planning and risk signaling.
- Partial: no forced alignment with phoneme-level timing.

