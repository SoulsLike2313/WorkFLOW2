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

## Critical UI zones
- Project onboarding controls and status text.
- Translation backend/context status line and correction form.
- Voice attempt table + preview/duration widgets.
- Reports quality widgets and Diagnostics backend table.
- Companion session controls and events table.

## Recurrent risk categories
- CTA visibility loss on resize.
- Dense tables causing clipping/overflow.
- Empty summary zones after state transitions.
- Selection-dependent detail panes not updating.
- Localization fit issues in long-text states.

## Evidence source
- `ui_screenshots_manifest.json`
- `ui_validation_summary.json`
- `runtime/ui_validation/<run_id>/ui_doctor_summary.json`
