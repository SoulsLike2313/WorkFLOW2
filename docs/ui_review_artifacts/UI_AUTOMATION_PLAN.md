# UI Automation Plan

## Current executable pipeline
1. `scripts/ui_snapshot_runner.py`
2. `scripts/ui_validate.py`
3. `scripts/ui_doctor.py`

## What is now machine-validated
- Navigation walkthrough across all core screens.
- Screenshot capture for state classes:
  - `initial_state`
  - `loaded_state`
  - `no_selection_state`
  - `dense_state` (when available)
  - `empty_state` (when available)
  - `anomaly_state` (when detected)
- CTA visibility and hover-only anti-pattern checks.
- Layout bounds and overlap checks.
- Splitter ratio/readability checks.
- Per-run walkthrough trace generation.

## Artifact contract in repo
- `runtime/ui_snapshots/<run_id>/`
- `runtime/ui_validation/<run_id>/`
- `runtime/ui_validation/validate_<run_id>/`
- `ui_screenshots_manifest.json`
- `ui_validation_summary.json`
- `ui_validation_summary.md`
- `ui_walkthrough_trace.json`
- `runtime/ui_snapshots/latest_run.{txt,json}`
- `runtime/ui_validation/latest_run.{txt,json}`

## Latest machine evidence
- snapshot: `20260312_170735` -> `PASS`
- validate: `20260312_170515` -> `PASS`
- doctor (inside validate): `20260312_170515` -> `PASS`
