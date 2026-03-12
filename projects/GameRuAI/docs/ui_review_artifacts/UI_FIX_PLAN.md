# UI Fix Plan - GameRuAI

## Priority order
1. Critical flow blockers (`critical`): missing CTA/navigation/state break.
2. Major usability defects (`major`): overflow/clipping/empty loaded states.
3. Minor polish defects (`minor`): spacing/readability hierarchy issues.

## Fix strategy by problem type
- `navigation`: restore tab registration/order in `MainWindow`.
- `cta`: keep CTA visible and anchored in layout containers.
- `layout` / `overflow`: tune splitter sizes, size policies, and parent layout constraints.
- `state_handling`: ensure state transitions call the required refresh/update paths.
- `localization` / `typography`: update text fit rules and font coverage.

## Loop
1. Reproduce from screenshot + scenario key (`screen::state`).
2. Apply minimal patch to relevant panel.
3. Re-run `python scripts/ui_validate.py`.
4. Verify issue removal in doctor/validation summaries.
5. Log result in `UI_CHANGELOG.md`.
