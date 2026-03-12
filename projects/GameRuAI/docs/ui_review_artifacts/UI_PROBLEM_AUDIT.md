# UI Problem Audit - GameRuAI

## Product screens under audit
- Top Product HUD
- Project
- Scan
- Asset Explorer
- Entries
- Language Hub
- Translation
- Voice
- Learning
- Glossary
- QA
- Reports
- Diagnostics
- Export
- Jobs / Logs
- Live Demo
- Companion

## Critical user flows
1. Core localization flow:
   Project -> Scan -> Entries -> Language Hub -> Translation -> Voice -> Reports -> Export.
2. Learning visibility flow:
   Translation correction -> Learning history -> Glossary/TM reuse.
3. Companion flow:
   Companion setup -> watch events visibility -> diagnostics impact.
4. Asset research flow:
   Asset tree -> active file metadata/preview fallback.
5. UI-QA loop:
   Snapshot/Doctor/Validate -> review artifacts -> fix plan -> rerun.

## Latest automated evidence
- Validation run: `20260312_161125`
- Doctor run: `20260312_161126`
- Snapshot run: `20260312_161728`
- Validation status: `PASS_WITH_WARNINGS`
- Doctor status: `PASS_WITH_WARNINGS`
- Snapshot status: `PASS`
- Snapshot captures: `210`
- Combined captures (doctor + snapshot manifest): `420`
- Covered screens: `16`
- Covered screen/state pairs: `24`

## Critical UI zones
- HUD project/backend/language/pipeline summary zone + quick actions.
- Language Hub overview/queue/backend status blocks.
- Language Hub review/stress/flow blocks + triage action buttons.
- Translation backend/context status line and correction form.
- Voice attempt table + preview/duration widgets.
- Reports quality widgets and Diagnostics backend table.
- Companion session controls and events table.

## Current findings (from doctor)
- `critical`: `0`
- `major`: `261`
- `minor`: `0`
- Dominant issue category: `floating_critical_cta`
- Dominant issue type: `layout`
- Most affected screens:
  - Companion (`54`)
  - Entries (`54`)
  - Translation (`36`)
  - Voice (`36`)
  - Asset Explorer (`18`)
  - Language Hub (`18`)

## Evidence source
- `ui_screenshots_manifest.json`
- `ui_validation_summary.json`
- `runtime/ui_validation/validate_20260312_161125/ui_validation_summary.json`
- `runtime/ui_validation/20260312_161126/ui_doctor_summary.json`
