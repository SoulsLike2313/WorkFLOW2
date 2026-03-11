# UI Automation Plan

## Automation Components
- `scripts/ui_snapshot_runner.py`: screenshot harvesting by tab/size/scale.
- `scripts/ui_doctor.py`: structural and visibility diagnostics.
- `scripts/ui_validate.py`: orchestrator and artifact publisher.

## Run Sequence
1. Bootstrap demo project state.
2. Capture screenshot baseline.
3. Run diagnostics.
4. Consolidate summaries and machine-readable outputs.
5. Publish latest run pointer.

## Cadence
- Mandatory before release tagging.
- Mandatory after UI-affecting PR batches.
- Recommended after any layout refactor.
