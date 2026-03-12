# UI Changelog - GameRuAI

## Entries

### 2026-03-12
- Run ID: `20260312_152940`
- Validation status: `PASS_WITH_WARNINGS`
- Doctor status: `PASS_WITH_WARNINGS` (`20260312_152940`)
- Snapshot status: `PASS` (`20260312_153507`)
- Change set:
  - Continued from interrupted patch state without reset.
  - Recovered and finalized product-aware `scripts/ui_doctor.py`.
  - Extended `scripts/ui_validate.py` with product scenario manifest checks.
  - Ensured required snapshot fields and state coverage validation.
  - Updated all review artifacts for real GameRuAI screens/states.
- Resolved findings:
  - Validation pipeline executes end-to-end and emits required artifacts.
  - Product scenario coverage confirmed (`15` screens / `22` states / `192` captures).
- Remaining findings:
  - `floating_critical_cta` repeats across Asset Explorer, Companion, Entries, Translation, Voice.
  - Major layout count remains high (`243`).
- Notes:
  - No critical issues in this run.
  - Manual visual acceptance still required after CTA anchoring fixes.

