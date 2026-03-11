# UI Fix Plan

## Priority Model
1. Critical blockers (task flow breakage).
2. Major usability degradations.
3. Minor visual consistency issues.

## Fix Workflow
1. Reproduce via run artifact screenshot.
2. Patch the minimal affected panel/layout.
3. Re-run `ui_validate`.
4. Confirm issue removed from summary.
5. Log change in `UI_CHANGELOG.md`.

## Regression Guard
Do not merge UI fixes without a fresh validation run and updated run pointer.
