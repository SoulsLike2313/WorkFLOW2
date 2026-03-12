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

## Product scenario set
- `Project::initial_empty`
- `Project::pipeline_loaded_ready`
- `Scan::manifest_loaded`
- `Asset Explorer::tree_loaded_no_selection`
- `Asset Explorer::active_selection_metadata`
- `Entries::many_items_loaded`
- `Entries::filtered_language_fr`
- `Entries::long_search_query`
- `Translation::loaded_translations`
- `Translation::correction_form_long_content`
- `Voice::no_selection`
- `Voice::active_selection_details`
- `Learning::loaded_history`
- `Glossary::loaded_terms`
- `QA::findings_loaded`
- `Reports::dashboard_loaded`
- `Diagnostics::backend_metrics_loaded`
- `Export::export_log_loaded`
- `Jobs / Logs::jobs_payload_loaded`
- `Live Demo::scene_selected_ready`
- `Companion::idle_no_session`
- `Companion::configured_invalid_executable`

## Run pipeline
1. `python scripts/ui_validate.py`
2. Validator runs:
   - `python scripts/ui_doctor.py --scales 1.0,1.25,1.5 --sizes 1600x960,1366x768,1280x800`
   - `python scripts/ui_snapshot_runner.py --scales 1.0,1.25,1.5 --sizes 1600x960,1366x768,1280x800`
3. Validator merges outputs and writes root artifacts.

## Last completed run
- Validation run: `20260312_150606`
- Result: `PASS_WITH_WARNINGS`
- Doctor run: `20260312_150607`
- Snapshot run: `20260312_151135`
- Snapshot coverage: `15` screens / `22` states / `192` captures

## Artifact contract
- Root outputs:
  - `ui_validation_summary.json`
  - `ui_validation_summary.md`
  - `ui_screenshots_manifest.json`
- Runtime outputs:
  - `runtime/ui_validation/latest_run.txt`
  - `runtime/ui_validation/<validate_run_id>/...`
  - `runtime/ui_snapshots/<snapshot_run_id>/...`
