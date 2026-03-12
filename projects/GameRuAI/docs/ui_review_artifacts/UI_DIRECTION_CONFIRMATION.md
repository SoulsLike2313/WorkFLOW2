# UI Direction Confirmation - GameRuAI

## Confirmed UI direction
- Operations-first desktop workflow with transparent pipeline status.
- Product HUD first: users should see project stage and next action immediately.
- Language bottlenecks must be visible as first-class product blocks.
- Reproducible UI-QA loop using machine-readable run artifacts.

## Product-specific UX priorities
- Users must quickly understand pipeline readiness and next action.
- Language Hub must expose uncertain lines, queue, and localization stress.
- Critical translation/voice/companion controls must be discoverable without hover.
- Reports/diagnostics must stay legible under realistic data volume.

## Scenario coverage baseline
Automation validates GameRuAI product states directly, including:
- HUD-visible startup and loaded project contexts.
- `Language Hub::overview_loaded`
- `Language Hub::review_and_stress_loaded`
- Translation, Voice, Reports, Diagnostics, Companion, and pipeline tabs.

## Current confirmation
- Last run: `20260312_155348`
- Validation: `PASS_WITH_WARNINGS`
- Main open risk: layout consistency (`floating_critical_cta`) across action rows.

## Scope boundaries
- This layer validates UI structure/state handling and diagnostic visibility.
- It does not claim production-grade styling or final release readiness yet.
- Manual visual acceptance remains mandatory before release freeze.
