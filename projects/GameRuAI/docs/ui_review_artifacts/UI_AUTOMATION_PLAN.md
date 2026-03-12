# UI Automation Plan - GameRuAI

## Automation components
- `scripts/ui_snapshot_runner.py`
  - Captures product scenarios by `screen_name` + `state_name`.
  - Produces screenshot manifest entries with: `run_id`, `screen_name`, `state_name`, `screenshot_path`, `timestamp`, `notes`.
- `scripts/ui_doctor.py`
  - Runs product-specific diagnostics and classifies findings as `critical` / `major` / `minor`.
  - Adds `issue_type` and `recommendation` fields.
- `scripts/ui_validate.py`
  - Orchestrates doctor + snapshot.
  - Validates manifest schema and required scenario coverage.
  - Publishes canonical root artifacts.

## Product scenario set (current)
- Project: `initial_empty`, `pipeline_loaded_ready`
- Scan: `manifest_loaded`
- Asset Explorer: `tree_loaded_no_selection`, `active_selection_metadata`
- Entries: `many_items_loaded`, `filtered_language_fr`, `long_search_query`
- Language Hub: `overview_loaded`, `review_and_stress_loaded`
- Translation: `loaded_translations`, `correction_form_long_content`
- Voice: `no_selection`, `active_selection_details`
- Learning, Glossary, QA, Reports, Diagnostics, Export, Jobs / Logs, Live Demo, Companion

## Run pipeline
1. `python scripts/ui_validate.py`
2. Validator runs:
   - `python scripts/ui_doctor.py --scales 1.0,1.25,1.5 --sizes 1600x960,1366x768,1280x800`
   - `python scripts/ui_snapshot_runner.py --scales 1.0,1.25,1.5 --sizes 1600x960,1366x768,1280x800`
3. Validator merges outputs and writes root artifacts.

## Last completed run
- Validation run: `20260312_162437`
- Result: `PASS_WITH_WARNINGS`
- Doctor run: `20260312_162437`
- Snapshot run: `20260312_163109`
- Snapshot coverage: `16` screens / `24` states / `210` captures
- Combined manifest captures (doctor + snapshot): `420`

## Artifact contract
- Root outputs:
  - `ui_validation_summary.json`
  - `ui_validation_summary.md`
  - `ui_screenshots_manifest.json`
- Runtime outputs:
  - `runtime/ui_validation/latest_run.txt`
  - `runtime/ui_validation/<validate_run_id>/...`
  - `runtime/ui_snapshots/<snapshot_run_id>/...`
