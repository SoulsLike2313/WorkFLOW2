# UI Fix Plan - GameRuAI

## Baseline findings source
- Validation run: `20260312_163846`
- Doctor run: `20260312_163846`
- Main issue cluster: `floating_critical_cta` (`315` major findings)

## Priority order
1. Eliminate repeated `floating_critical_cta` in core workflow screens.
2. Recheck overflow/overlap/splitter stability after CTA layout normalization.
3. Manual polish pass for dense table screens at `1366x768` and `1280x800`.

## Screen-level actions
- Language Hub
  - Keep action row (`Refresh`, `Focus Uncertain`, `Focus Stress`, `Open Translation`) inside one fixed toolbar container.
- Asset Explorer
  - Rebuild header CTA row (`Refresh Asset Index`) inside a persistent parent layout.
- Companion
  - Place `Launch/Poll/Stop` in one stable horizontal layout with explicit min widths.
- Entries
  - Normalize toolbar container for `Detect Language` and `Refresh`; avoid detached controls.
- Translation
  - Keep `Translate to Russian` and `Apply Correction` in one anchored action row.
- Voice
  - Align voice action controls to one parent pane layout and remove detached widgets.

## Verification loop
1. Apply small layout patch for one panel.
2. Run `python scripts/ui_validate.py`.
3. Confirm `floating_critical_cta` count drops for that panel in doctor summary.
4. Record result in `UI_CHANGELOG.md`.
5. Continue until major layout findings are near zero.

## Exit criteria for this plan
- `ui_doctor` returns `PASS` or low, explained `PASS_WITH_WARNINGS`.
- No repeated `floating_critical_cta` in core tabs and Language Hub.
- Manual acceptance checklist updated with checked layout/scaling blocks.
