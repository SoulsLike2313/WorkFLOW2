# UI Automation Plan - GameRuAI

## Automation components
- `scripts/ui_snapshot_runner.py`
  - captures product scenarios by `screen_name` + `state_name`.
- `scripts/ui_doctor.py`
  - runs product-specific diagnostics with severity/type/recommendation.
- `scripts/ui_validate.py`
  - orchestrates doctor+snapshot and validates scenario coverage/artifact schema.

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

## Execution order
1. Run product snapshot scenarios.
2. Run doctor diagnostics on same scenario set.
3. Validate artifact schema + required scenario coverage.
4. Publish canonical root artifacts and latest run pointer.
