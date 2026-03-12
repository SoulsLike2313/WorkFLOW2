# UI Layout Bug Report - GameRuAI

## Baseline run
- Validation run: `20260312_150606`
- Doctor run: `20260312_150607`
- Status: `PASS_WITH_WARNINGS`

## Observed defect clusters

| Severity | Type | Category | Screen | State | Viewport scope | Expected | Actual | Recommendation |
|---|---|---|---|---|---|---|---|---|
| major | layout | floating_critical_cta | Asset Explorer | tree_loaded_no_selection / active_selection_metadata | all scales and all sizes | `Refresh Asset Index` anchored inside toolbar layout | CTA exists but flagged as floating/not layout-anchored | Bind button to persistent layout container in panel header |
| major | layout | floating_critical_cta | Companion | idle_no_session / configured_invalid_executable | all scales and all sizes | `Launch/Poll/Stop` CTAs remain stable in action row | CTA controls reported as floating in every tested viewport | Rebuild action row with explicit parent layout and min widths |
| major | layout | floating_critical_cta | Entries | many_items_loaded / filtered_language_fr / long_search_query | all scales and all sizes | `Detect Language` and `Refresh` behave as anchored table actions | CTA controls reported as floating in dense table toolbar states | Normalize entries toolbar layout and size policy |
| major | layout | floating_critical_cta | Translation | loaded_translations / correction_form_long_content | all scales and all sizes | `Translate to Russian` and `Apply Correction` stay anchored | CTA controls reported as floating in both table and correction states | Place CTA row in one parent layout shared by translation widgets |
| major | layout | floating_critical_cta | Voice | no_selection / active_selection_details | all scales and all sizes | Voice action buttons remain anchored in control pane | CTA controls reported as floating while switching selection state | Stabilize voice control row and avoid detached containers |

## Reference screenshots
- `runtime/ui_validation/20260312_150607/screenshots/scale_1_0/doctor__asset_explorer__tree_loaded_no_selection__1600x960__scale_1_0.png`
- `runtime/ui_validation/20260312_150607/screenshots/scale_1_0/doctor__companion__configured_invalid_executable__1600x960__scale_1_0.png`
- `runtime/ui_validation/20260312_150607/screenshots/scale_1_0/doctor__entries__many_items_loaded__1600x960__scale_1_0.png`
- `runtime/ui_validation/20260312_150607/screenshots/scale_1_0/doctor__translation__loaded_translations__1600x960__scale_1_0.png`
- `runtime/ui_validation/20260312_150607/screenshots/scale_1_0/doctor__voice__active_selection_details__1600x960__scale_1_0.png`

## Notes
- This run did not detect critical blockers, but major layout warnings remain systematic.
- Failures are product-specific and tied to main working screens, not cosmetic side screens.
