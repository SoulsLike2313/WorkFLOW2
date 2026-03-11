# UI Build Rules (GameRuAI)

## Purpose
This file defines non-negotiable UI build/QA rules for GameRuAI desktop screens.

## Hard Gates
- No critical CTA may be hover-only.
- No critical CTA may disappear under supported resize presets.
- No clipping for primary action buttons.
- No out-of-bounds interactive controls in target viewport presets.
- No broken tab shell (missing root layout, collapsed splitters, empty interactive area).

## Supported Validation Presets
- Scales: `1.0`, `1.25`, `1.5`
- Sizes: `1600x960`, `1366x768`, `1280x800`

## Validation Status Policy
- `PASS`: no critical/major findings.
- `PASS_WITH_WARNINGS`: no critical, but major/minor findings exist.
- `FAIL`: one or more critical findings, or infrastructure failure.

## Artifact Contract
Each validation run must produce:
- `ui_validation_summary.json`
- `ui_validation_summary.md`
- `ui_screenshots_manifest.json`
- `runtime/ui_validation/latest_run.txt`

## Required Run Loop
1. Run `scripts/ui_validate.py`.
2. Review JSON + markdown summary.
3. Fix highest-severity findings first.
4. Re-run validation and compare run IDs.
5. Update `docs/ui_review_artifacts/UI_CHANGELOG.md` after each accepted fix batch.

## Scope Boundaries
- UI-QA layer checks layout and interaction signals, not product/business correctness.
- Visual checks are screenshot-driven and heuristic-based; final acceptance still includes manual review.
