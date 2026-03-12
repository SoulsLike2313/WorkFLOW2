# UI Build Rules - GameRuAI

## Product scope
These rules are specific to GameRuAI desktop workflow screens:
- Top Product HUD
- Project, Scan, Asset Explorer, Entries, Language Hub, Translation, Voice,
  Learning, Glossary, QA, Reports, Diagnostics, Export, Jobs / Logs, Live Demo, Companion.

## Validated baseline run
- Validation run: `20260312_155348`
- Doctor run: `20260312_155348`
- Snapshot run: `20260312_155949`
- Status: `PASS_WITH_WARNINGS` (`ui_doctor`) + `PASS` (`ui_snapshot_runner`)
- Snapshot coverage: `16` screens / `24` product states / `210` captures

## Navigation invariants
- All listed screens must exist in the main tab shell.
- Tab order must stay stable to preserve operator muscle memory.
- Core tabs cannot silently disappear under feature flags.

## Product HUD invariants
- HUD must always show current project context and game path when project is loaded.
- HUD must expose active backend and fallback state.
- HUD must expose pipeline stage statuses (`scan/extract/detect/translate/voice/export/reports/diagnostics`).
- HUD must expose companion session status and next action hint.
- HUD metrics must include entries/languages/translated/uncertain/voice/QA/report state.

## CTA placement rules
- Critical CTA controls must remain visible without hover.
- Critical CTA controls must be layout-anchored, not floating.
- Critical CTA controls:
  - Project: `Create/Select Project`, `Run Full Demo Pipeline`
  - Scan: `Run Scan`, `Extract Strings`
  - Entries: `Detect Language`, `Refresh`
  - Language Hub: `Refresh Language Blocks`
  - Translation: `Translate to Russian`, `Apply Correction`
  - Voice: `Generate Demo Voice Attempts`, `Update Speaker Profile`
  - Reports: `Generate Reports`, `Refresh Reports`
  - Companion: `Launch Companion Session`, `Poll Status / Watch`, `Stop Session`

## State handling rules
- Empty state: project startup must show actionable onboarding hint.
- Loaded state: tables/summaries must show real data after pipeline run.
- Long-content state: long text fields must remain readable and editable.
- Selection state: detail panes must update when row/item selection changes.
- Error-precheck state: Companion invalid executable setup must be visible and understandable.

## Language Hub invariants
- Language Overview must contain language distribution and review counts.
- Language Queue must show pending work, priority, status, and last processed info.
- Backend Status block must show active backend, fallback, availability, latency, context usage, and mode.
- Language Review block must contain uncertain/mixed/problematic lines.
- Localization Stress block must surface long/placeholder/tag/overflow risks.
- Language Flow Summary must expose pipeline steps: detected/normalized/translated/reviewed/exported.

## Screen-specific invariants
- Project: info label must show ready/pipeline completion.
- Scan: manifest text + file table must be populated in loaded state.
- Asset Explorer: tree must load; active selection must fill metadata pane.
- Entries: many-items and language-filter states must remain usable.
- Translation: backend status visible; RU content rendered in table.
- Voice: attempt list + preview/duration details must be available.
- Reports/Diagnostics: quality and backend tables must be populated.
- Live Demo: scene selector must contain fixture scenes.

## Overflow / typography / localization rules
- No clipping on primary buttons and key labels.
- No out-of-bounds interactive widgets.
- No sibling overlaps in control rows.
- No replacement glyph artifacts.
- RU text should fit translation-heavy zones.

## Scaling rules
Supported presets:
- Scales: `1.0`, `1.25`, `1.5`
- Sizes: `1600x960`, `1366x768`, `1280x800`

At each preset:
- critical CTA visibility must be preserved,
- no destructive overflow/overlap,
- splitters cannot collapse critical panes.

## Validation status policy
- `PASS`: no critical or major issues.
- `PASS_WITH_WARNINGS`: no critical issues, but major/minor issues exist.
- `FAIL`: any critical issue or broken validation pipeline.

## Current known violations
- `floating_critical_cta` is repeatedly detected in multiple panels.
- Current warning cluster is layout-related (major severity), not pipeline crash.
- Until CTA anchoring fixes are applied, release UI sign-off remains blocked.

## Required artifacts per run
- `ui_validation_summary.json`
- `ui_validation_summary.md`
- `ui_screenshots_manifest.json`
- `runtime/ui_validation/latest_run.txt`
