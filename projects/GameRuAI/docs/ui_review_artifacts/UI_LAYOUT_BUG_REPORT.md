# UI Layout Bug Report - GameRuAI

## Baseline run
- Validation run: `20260312_161125`
- Doctor run: `20260312_161126`
- Snapshot run: `20260312_161728`
- Status: `PASS_WITH_WARNINGS`

## Observed defect clusters

| Severity | Type | Category | Screen | State | Viewport scope | Expected | Actual | Recommendation |
|---|---|---|---|---|---|---|---|---|
| major | layout | floating_critical_cta | Asset Explorer | tree_loaded_no_selection / active_selection_metadata | all scales and all sizes | `Refresh Asset Index` anchored inside toolbar layout | CTA exists but flagged as floating/not layout-anchored | Bind button to persistent layout container in panel header |
| major | layout | floating_critical_cta | Companion | idle_no_session / configured_invalid_executable | all scales and all sizes | `Launch/Poll/Stop` CTAs remain stable in action row | CTA controls reported as floating in every tested viewport | Rebuild action row with explicit parent layout and min widths |
| major | layout | floating_critical_cta | Entries | many_items_loaded / filtered_language_fr / long_search_query | all scales and all sizes | `Detect Language` and `Refresh` behave as anchored table actions | CTA controls reported as floating in dense table toolbar states | Normalize entries toolbar layout and size policy |
| major | layout | floating_critical_cta | Language Hub | overview_loaded / review_and_stress_loaded | all scales and all sizes | Language Hub action row remains anchored near language blocks | CTA controls reported as floating in both language states | Keep language hub action row in fixed parent layout |
| major | layout | floating_critical_cta | Translation / Voice | loaded/correction + no-selection/active-selection | all scales and all sizes | Translation/voice control rows remain anchored and stable | CTA controls reported as floating across tested states | Normalize action rows and avoid detached containers |

## Reference screenshots
- `runtime/ui_validation/20260312_161126/screenshots/scale_1_0/doctor__language_hub__overview_loaded__1600x960__scale_1_0.png`
- `runtime/ui_validation/20260312_161126/screenshots/scale_1_0/doctor__language_hub__review_and_stress_loaded__1600x960__scale_1_0.png`
- `runtime/ui_validation/20260312_161126/screenshots/scale_1_0/doctor__companion__configured_invalid_executable__1600x960__scale_1_0.png`
- `runtime/ui_validation/20260312_161126/screenshots/scale_1_0/doctor__entries__many_items_loaded__1600x960__scale_1_0.png`
- `runtime/ui_validation/20260312_161126/screenshots/scale_1_0/doctor__translation__loaded_translations__1600x960__scale_1_0.png`

## Notes
- No critical blockers detected in this run.
- Major layout warnings remain systematic and include Language Hub action row.
- HUD and Language Hub are visible and captured in automation, but layout anchoring quality is still unresolved.
