# UI Direction Confirmation - GameRuAI

## Confirmed UI direction
- Operations-first desktop workflow with transparent pipeline status.
- Screen stability over decorative density.
- Decision visibility over hidden automation.
- Reproducible UI-QA loop using machine-readable run artifacts.

## Product-specific UX priorities
- Users must quickly understand pipeline readiness and next action.
- Critical translation/voice controls must be discoverable without hover.
- Reports/diagnostics must be legible under realistic data volume.
- Companion and asset flows must remain understandable even in fallback states.

## Scenario coverage baseline
The automation now validates GameRuAI product states directly:
- Project (`initial_empty`, `pipeline_loaded_ready`)
- Scan (`manifest_loaded`)
- Asset Explorer (`tree_loaded_no_selection`, `active_selection_metadata`)
- Entries (`many_items_loaded`, `filtered_language_fr`, `long_search_query`)
- Translation (`loaded_translations`, `correction_form_long_content`)
- Voice (`no_selection`, `active_selection_details`)
- Learning / Glossary / QA / Reports / Diagnostics / Export / Jobs / Live Demo / Companion

## Current confirmation
- Last run: `20260312_150606`
- Validation: `PASS_WITH_WARNINGS`
- Main open risk: major layout consistency (`floating_critical_cta`).

## Scope boundaries
- This layer validates UI structure/state handling; it does not guarantee business semantics.
- Manual visual acceptance is still mandatory before release freeze.
