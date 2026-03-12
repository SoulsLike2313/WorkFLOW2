# UI Problem Audit - GameRuAI

## Product screens under audit
- Project
- Scan
- Asset Explorer
- Entries
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
   Project -> Scan -> Entries -> Translation -> Voice -> Reports -> Export.
2. Learning visibility flow:
   Translation correction -> Learning history -> Glossary/TM reuse.
3. Companion flow:
   Companion setup -> watch events visibility -> diagnostics impact.
4. Asset research flow:
   Asset tree -> active file metadata/preview fallback.

## Latest automated evidence
- Validation run: `20260312_150606`
- Doctor run: `20260312_150607`
- Snapshot run: `20260312_151135`
- Validation status: `PASS_WITH_WARNINGS`
- Doctor status: `PASS_WITH_WARNINGS`
- Snapshot status: `PASS`
- Captures (snapshot manifest): `192`
- Covered screens: `15`
- Covered screen/state pairs: `22`

## Critical UI zones
- Project onboarding controls and status text.
- Translation backend/context status line and correction form.
- Voice attempt table + preview/duration widgets.
- Reports quality widgets and Diagnostics backend table.
- Companion session controls and events table.

## Current findings (from doctor)
- No `critical` issues detected in this run.
- `major` issues: `243`.
- Dominant issue category: `floating_critical_cta`.
- Dominant issue type: `layout`.
- Most affected screens by count:
  - Companion (`54`)
  - Entries (`54`)
  - Translation (`36`)
  - Voice (`36`)
  - Asset Explorer (`18`)

## Evidence source
- `ui_screenshots_manifest.json`
- `ui_validation_summary.json`
- `runtime/ui_validation/validate_20260312_150606/ui_validation_summary.json`
- `runtime/ui_validation/20260312_150607/ui_doctor_summary.json`
