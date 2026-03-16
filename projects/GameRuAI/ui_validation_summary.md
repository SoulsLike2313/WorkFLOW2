# UI Validation Summary

- Run ID: `20260313_045243`
- Started: `2026-03-13T01:52:43.534556+00:00`
- Finished: `2026-03-13T01:54:12.662405+00:00`
- Duration: `89.13s`
- Overall status: `PASS_WITH_WARNINGS`
- Manual acceptance recommended: `True`

## Sub-runs

- ui_doctor: run=`20260313_045243` status=`PASS_WITH_WARNINGS`
- ui_snapshot_runner: run=`20260313_045340` status=`PASS`

## Screen Audit

- Asset Explorer: critical=0, major=2, minor=0
- Companion: critical=0, major=6, minor=0
- Entries: critical=0, major=6, minor=0
- Export: critical=0, major=1, minor=0
- Glossary: critical=0, major=1, minor=0
- Language Hub: critical=0, major=8, minor=0
- Live Demo: critical=0, major=1, minor=0
- Reports: critical=0, major=2, minor=0
- Translation: critical=0, major=4, minor=0
- Voice: critical=0, major=4, minor=0

## Issues By Type

- layout: 35

## Top Issues

- [major] Asset Explorer::active_selection_metadata / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_active_selection]
- [major] Asset Explorer::tree_loaded_no_selection / floating_critical_cta: CTA not anchored to layout: Refresh Asset Index [scenario=asset_tree_loaded]
- [major] Companion::configured_invalid_executable / floating_critical_cta: CTA not anchored to layout: Launch Companion Session [scenario=companion_invalid_exec]
- [major] Companion::configured_invalid_executable / floating_critical_cta: CTA not anchored to layout: Poll Status / Watch [scenario=companion_invalid_exec]
- [major] Companion::configured_invalid_executable / floating_critical_cta: CTA not anchored to layout: Stop Session [scenario=companion_invalid_exec]
- [major] Companion::idle_no_session / floating_critical_cta: CTA not anchored to layout: Launch Companion Session [scenario=companion_idle]
- [major] Companion::idle_no_session / floating_critical_cta: CTA not anchored to layout: Poll Status / Watch [scenario=companion_idle]
- [major] Companion::idle_no_session / floating_critical_cta: CTA not anchored to layout: Stop Session [scenario=companion_idle]
- [major] Entries::filtered_language_fr / floating_critical_cta: CTA not anchored to layout: Detect Language [scenario=entries_filtered_fr]
- [major] Entries::filtered_language_fr / floating_critical_cta: CTA not anchored to layout: Refresh [scenario=entries_filtered_fr]
- [major] Entries::long_search_query / floating_critical_cta: CTA not anchored to layout: Detect Language [scenario=entries_long_search]
- [major] Entries::long_search_query / floating_critical_cta: CTA not anchored to layout: Refresh [scenario=entries_long_search]
- [major] Entries::many_items_loaded / floating_critical_cta: CTA not anchored to layout: Detect Language [scenario=entries_many_items]
- [major] Entries::many_items_loaded / floating_critical_cta: CTA not anchored to layout: Refresh [scenario=entries_many_items]
- [major] Export::export_log_loaded / floating_critical_cta: CTA not anchored to layout: Export Patch Output [scenario=export_log_loaded]
- [major] Glossary::loaded_terms / floating_critical_cta: CTA not anchored to layout: Add Term [scenario=glossary_loaded]
- [major] Language Hub::overview_loaded / floating_critical_cta: CTA not anchored to layout: Refresh Language Blocks [scenario=language_hub_overview]
- [major] Language Hub::overview_loaded / floating_critical_cta: CTA not anchored to layout: Focus Uncertain In Entries [scenario=language_hub_overview]
- [major] Language Hub::overview_loaded / floating_critical_cta: CTA not anchored to layout: Focus Stress In Entries [scenario=language_hub_overview]
- [major] Language Hub::overview_loaded / floating_critical_cta: CTA not anchored to layout: Open Translation Workbench [scenario=language_hub_overview]

## Artifacts

- root_summary_json: `<REPO_ROOT>\projects\GameRuAI\ui_validation_summary.json`
- root_summary_md: `<REPO_ROOT>\projects\GameRuAI\ui_validation_summary.md`
- root_screenshots_manifest: `<REPO_ROOT>\projects\GameRuAI\ui_screenshots_manifest.json`
- validate_run_dir: `<REPO_ROOT>\projects\GameRuAI\runtime\ui_validation\validate_20260313_045243`
- latest_run_txt: `<REPO_ROOT>\projects\GameRuAI\runtime\ui_validation\latest_run.txt`
- doctor_summary_json: `<REPO_ROOT>\projects\GameRuAI\runtime\ui_validation\20260313_045243\ui_doctor_summary.json`
- doctor_manifest_json: `<REPO_ROOT>\projects\GameRuAI\runtime\ui_validation\20260313_045243\ui_screenshots_manifest.json`
- snapshot_summary_json: `<REPO_ROOT>\projects\GameRuAI\runtime\ui_snapshots\20260313_045340\ui_snapshot_summary.json`
- snapshot_manifest_json: `<REPO_ROOT>\projects\GameRuAI\runtime\ui_snapshots\20260313_045340\ui_screenshots_manifest.json`

## Warnings

- none

## Failures

- none
