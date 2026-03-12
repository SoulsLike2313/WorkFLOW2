# UI Validation Summary

- Run ID: `20260313_010351`
- Started at: `2026-03-12T22:03:51.125108+00:00`
- Finished at: `2026-03-12T22:03:52.114043+00:00`
- Duration: `0.99s`
- Overall status: `FAIL`
- Manual testing allowed: `False`

## Sub-runs

- ui_doctor: `20260313_010351` (`FAIL`)
- ui_snapshot_runner: `` (`SKIPPED`)

## Checks

- WARN: state_not_observed:ai_studio:loaded_state
- WARN: state_not_observed:analytics:loaded_state
- WARN: state_not_observed:audit:loaded_state
- WARN: state_not_observed:content:loaded_state
- WARN: state_not_observed:content:no_selection_state
- WARN: state_not_observed:dashboard:initial_state
- WARN: state_not_observed:dashboard:loaded_state
- WARN: state_not_observed:profiles:loaded_state
- WARN: state_not_observed:profiles:no_selection_state
- WARN: state_not_observed:sessions:loaded_state
- WARN: state_not_observed:sessions:no_selection_state
- WARN: state_not_observed:settings:loaded_state
- WARN: state_not_observed:updates:loaded_state
- WARN: ui_snapshot_status=SKIPPED
- FAIL: doctor_acceptance_blockers=3
- FAIL: doctor_critical_issues=3
- FAIL: missing_loaded_state:ai_studio
- FAIL: missing_loaded_state:analytics
- FAIL: missing_loaded_state:audit
- FAIL: missing_loaded_state:content
- FAIL: missing_loaded_state:dashboard
- FAIL: missing_loaded_state:profiles
- FAIL: missing_loaded_state:sessions
- FAIL: missing_loaded_state:settings
- FAIL: missing_loaded_state:updates
- FAIL: ui_doctor_status=FAIL
- FAIL: walkthrough_action_missing:boot_window
- FAIL: walkthrough_action_missing:capture_anomaly_state
- FAIL: walkthrough_action_missing:capture_dense_state
- FAIL: walkthrough_action_missing:capture_empty_state
- FAIL: walkthrough_action_missing:capture_loaded_state
- FAIL: walkthrough_action_missing:switch_page
- FAIL: walkthrough_action_missing:verify_no_selection_state
- FAIL: walkthrough_screen_missing:ai_studio
- FAIL: walkthrough_screen_missing:analytics
- FAIL: walkthrough_screen_missing:audit
- FAIL: walkthrough_screen_missing:content
- FAIL: walkthrough_screen_missing:dashboard
- FAIL: walkthrough_screen_missing:profiles
- FAIL: walkthrough_screen_missing:sessions
- FAIL: walkthrough_screen_missing:settings
- FAIL: walkthrough_screen_missing:updates
- FAIL: walkthrough_trace_missing

## Artifacts

- root_summary_json: `ui_validation_summary.json`
- root_summary_md: `ui_validation_summary.md`
- root_screenshots_manifest: `ui_screenshots_manifest.json`
- root_walkthrough_trace: `ui_walkthrough_trace.json`
- validate_run_dir: `runtime/ui_validation/validate_20260313_010351`
- latest_run_txt: `runtime/ui_validation/latest_run.txt`
- latest_run_json: `runtime/ui_validation/latest_run.json`
- validate_visual_review_md: `runtime/ui_validation/validate_20260313_010351/ui_visual_review.md`
- validate_walkthrough_trace_json: `runtime/ui_validation/validate_20260313_010351/ui_walkthrough_trace.json`
- doctor_summary_json: `runtime/ui_validation/20260313_010351/ui_validation_summary.json`
- doctor_manifest_json: `runtime/ui_validation/20260313_010351/ui_screenshots_manifest.json`
- doctor_walkthrough_trace_json: `runtime/ui_validation/20260313_010351/ui_walkthrough_trace.json`
- snapshot_summary_json: ``
- snapshot_manifest_json: ``
- snapshot_walkthrough_trace_json: ``
