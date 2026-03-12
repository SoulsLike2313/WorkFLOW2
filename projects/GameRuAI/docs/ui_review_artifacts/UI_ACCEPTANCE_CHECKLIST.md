# UI Acceptance Checklist - GameRuAI

## Core screen coverage
- [ ] All main screens are present in tab navigation.
- [ ] Screen order remains stable and recognizable for operators.

## Critical CTA checks
- [ ] Project CTA: `Create/Select Project`, `Run Full Demo Pipeline`.
- [ ] Translation CTA: `Translate to Russian`, `Apply Correction`.
- [ ] Voice CTA: `Generate Demo Voice Attempts`, `Update Speaker Profile`.
- [ ] Companion CTA: `Launch Companion Session`, `Poll Status / Watch`, `Stop Session`.
- [ ] No critical CTA is hover-only.

## Product flow checks
- [ ] Core localization flow is visible end-to-end across screens.
- [ ] Learning loop surfaces correction/adaptation evidence in UI.
- [ ] Reports/Diagnostics show non-empty runtime metrics.
- [ ] Companion state is understandable in idle and invalid-executable precheck states.

## State checks
- [ ] Initial/empty state is clear on Project screen.
- [ ] Loaded states are populated on Scan/Entries/Translation/Voice/Reports/Diagnostics.
- [ ] Many-items and long-content states remain readable.
- [ ] No-selection vs active-selection states are both stable on Voice and Asset Explorer.

## Layout/visual quality checks
- [ ] No clipping/overflow for critical controls.
- [ ] No destructive overlaps.
- [ ] No collapsed critical splitters.
- [ ] RU text fits translation-heavy zones.

## Scaling and consistency
- [ ] Presets `1.0`, `1.25`, `1.5` pass without critical regressions.
- [ ] Presets `1600x960`, `1366x768`, `1280x800` keep key zones usable.

## Product clarity / premium feel
- [ ] Primary actions are obvious on each screen.
- [ ] Summary blocks are informative, not placeholder-like.
- [ ] Dense tables/panels still communicate hierarchy and next action.

## Sign-off
- Reviewer:
- Date:
- Run ID:
- Decision:
