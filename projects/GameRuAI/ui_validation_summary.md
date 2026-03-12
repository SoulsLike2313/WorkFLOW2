# UI Validation Summary

- Run ID: `20260313_010351`
- Started: `2026-03-12T22:03:51.144098+00:00`
- Finished: `2026-03-12T22:10:49.292720+00:00`
- Duration: `418.15s`
- Overall status: `FAIL`
- Manual acceptance recommended: `False`

## Sub-runs

- ui_doctor: run=`20260313_010351` status=`PASS_WITH_WARNINGS`
- ui_snapshot_runner: run=`None` status=`SKIPPED`

## Screen Audit

- Asset Explorer: critical=0, major=18, minor=0
- Companion: critical=0, major=54, minor=0
- Entries: critical=0, major=54, minor=0
- Export: critical=0, major=9, minor=0
- Glossary: critical=0, major=9, minor=0
- Language Hub: critical=0, major=72, minor=0
- Live Demo: critical=0, major=9, minor=0
- Reports: critical=0, major=18, minor=0
- Translation: critical=0, major=36, minor=0
- Voice: critical=0, major=36, minor=0

## Issues By Type

- layout: 315

## Top Issues

- [major] Asset Explorer::active_selection_metadata / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_active_selection]
- [major] Asset Explorer::active_selection_metadata / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_active_selection]
- [major] Asset Explorer::active_selection_metadata / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_active_selection]
- [major] Asset Explorer::active_selection_metadata / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_active_selection]
- [major] Asset Explorer::active_selection_metadata / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_active_selection]
- [major] Asset Explorer::active_selection_metadata / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_active_selection]
- [major] Asset Explorer::active_selection_metadata / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_active_selection]
- [major] Asset Explorer::active_selection_metadata / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_active_selection]
- [major] Asset Explorer::active_selection_metadata / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_active_selection]
- [major] Asset Explorer::tree_loaded_no_selection / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_tree_loaded]
- [major] Asset Explorer::tree_loaded_no_selection / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_tree_loaded]
- [major] Asset Explorer::tree_loaded_no_selection / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_tree_loaded]
- [major] Asset Explorer::tree_loaded_no_selection / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_tree_loaded]
- [major] Asset Explorer::tree_loaded_no_selection / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_tree_loaded]
- [major] Asset Explorer::tree_loaded_no_selection / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_tree_loaded]
- [major] Asset Explorer::tree_loaded_no_selection / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_tree_loaded]
- [major] Asset Explorer::tree_loaded_no_selection / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_tree_loaded]
- [major] Asset Explorer::tree_loaded_no_selection / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_tree_loaded]
- [major] Companion::configured_invalid_executable / floating_critical_cta: CTA not anchored to layout: Launch Companion Session [scenario=companion_invalid_exec]
- [major] Companion::configured_invalid_executable / floating_critical_cta: CTA not anchored to layout: Poll Status / Watch [scenario=companion_invalid_exec]

## Artifacts

- root_summary_json: `E:\CVVCODEX\projects\GameRuAI\ui_validation_summary.json`
- root_summary_md: `E:\CVVCODEX\projects\GameRuAI\ui_validation_summary.md`
- root_screenshots_manifest: `E:\CVVCODEX\projects\GameRuAI\ui_screenshots_manifest.json`
- validate_run_dir: `E:\CVVCODEX\projects\GameRuAI\runtime\ui_validation\validate_20260313_010351`
- latest_run_txt: `E:\CVVCODEX\projects\GameRuAI\runtime\ui_validation\latest_run.txt`
- doctor_summary_json: `E:\CVVCODEX\projects\GameRuAI\runtime\ui_validation\20260313_010351\ui_doctor_summary.json`
- doctor_manifest_json: `E:\CVVCODEX\projects\GameRuAI\runtime\ui_validation\20260313_010351\ui_screenshots_manifest.json`
- snapshot_summary_json: ``
- snapshot_manifest_json: ``

## Warnings

- snapshot manifest has low capture count (0), expected at least 24

## Failures

- snapshot manifest missing required product states: ['Project|initial_empty', 'Project|pipeline_loaded_ready', 'Scan|manifest_loaded', 'Asset Explorer|tree_loaded_no_selection', 'Asset Explorer|active_selection_metadata', 'Entries|many_items_loaded', 'Entries|filtered_language_fr', 'Entries|long_search_query', 'Language Hub|overview_loaded', 'Language Hub|review_and_stress_loaded', 'Translation|loaded_translations', 'Translation|correction_form_long_content', 'Voice|no_selection', 'Voice|active_selection_details', 'Learning|loaded_history', 'Glossary|loaded_terms', 'QA|findings_loaded', 'Reports|dashboard_loaded', 'Diagnostics|backend_metrics_loaded', 'Export|export_log_loaded', 'Jobs / Logs|jobs_payload_loaded', 'Live Demo|scene_selected_ready', 'Companion|idle_no_session', 'Companion|configured_invalid_executable']
