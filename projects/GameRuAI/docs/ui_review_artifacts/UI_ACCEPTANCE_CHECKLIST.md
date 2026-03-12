# UI Acceptance Checklist - GameRuAI

## Baseline under review
- Validation run: `20260312_163846`
- Doctor run: `20260312_163846`
- Snapshot run: `20260312_164518`

## Core screen coverage
- [x] All main screens are present in tab navigation.
- [x] `Language Hub` screen is present in tab navigation.
- [x] Top Product HUD is visible in app shell.

## Critical CTA checks
- [x] Project CTA: `Create/Select Project`, `Run Full Demo Pipeline`.
- [x] Translation CTA: `Translate to Russian`, `Apply Correction`.
- [x] Voice CTA: `Generate Demo Voice Attempts`, `Update Speaker Profile`.
- [x] Companion CTA: `Launch Companion Session`, `Poll Status / Watch`, `Stop Session`.
- [x] Language Hub CTA: `Refresh Language Blocks`, `Focus Uncertain`, `Focus Stress`, `Open Translation Workbench`.
- [x] No critical CTA is hover-only.
- [ ] CTA anchoring quality passes (`floating_critical_cta` remains open).

## Product flow checks
- [x] Core localization flow is visible end-to-end across screens.
- [x] HUD shows project stage, language bottlenecks, and next action.
- [x] Language Hub shows overview/queue/backend/review/stress/flow blocks.
- [x] Language Hub actions provide workflow shortcuts.
- [x] Learning loop surfaces correction/adaptation evidence in UI.
- [x] Reports/Diagnostics show non-empty runtime metrics.
- [x] Companion state is understandable in idle and invalid-executable precheck states.

## State checks
- [x] Initial/empty state is clear on Project screen.
- [x] Loaded states are populated on Scan/Entries/Language Hub/Translation/Voice/Reports/Diagnostics.
- [x] Many-items and long-content states remain readable.
- [x] No-selection vs active-selection states are stable on Voice and Asset Explorer.

## Layout/visual quality checks
- [ ] No clipping/overflow for critical controls (major layout warnings remain).
- [ ] No destructive overlaps (needs manual follow-up after CTA anchoring fix).
- [ ] No collapsed critical splitters (needs manual follow-up after CTA anchoring fix).
- [x] RU text is visible and rendered in translation-heavy zones.

## Scaling and consistency
- [x] Presets `1.0`, `1.25`, `1.5` run successfully.
- [ ] Presets `1600x960`, `1366x768`, `1280x800` are clean of major issues (currently false).

## Product clarity
- [x] Primary actions are obvious on each screen.
- [x] HUD quickly communicates project and pipeline state.
- [x] Language blocks expose bottlenecks and uncertain lines.
- [ ] Dense tables still need polish for production visual quality.

## Sign-off
- Reviewer: automation + manual review required
- Date: 2026-03-12
- Run ID: `20260312_163846`
- Decision: `PASS_WITH_WARNINGS` (not release sign-off)
