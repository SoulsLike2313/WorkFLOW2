# UI Problem Audit

## Objective
Track recurrent UI defects to prevent regressions across GameRuAI tabs.

## Current Focus Areas
- Clipping and overflow under resize.
- Missing/hidden critical controls.
- Splitter instability and panel collapse.
- Weak action hierarchy in dense screens.

## Severity Rules
- Critical: blocks core flow or hides mandatory action.
- Major: degrades usability and likely causes operator error.
- Minor: polish/readability issue without direct task blockage.

## Evidence Source
- `ui_screenshots_manifest.json`
- `ui_validation_summary.json`
- Per-run folder under `runtime/ui_validation/`
