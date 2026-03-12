# UI ChangeLog - GameRuAI

## Entries

### 2026-03-12
- Run ID: `20260312_161125`
- Validation status: `PASS_WITH_WARNINGS`
- Doctor status: `PASS_WITH_WARNINGS` (`20260312_161126`)
- Snapshot status: `PASS` (`20260312_161728`)
- Change set:
  - Strengthened top Product HUD with language bottlenecks and quick action row.
  - Strengthened Language Hub with workflow action buttons (`Focus Uncertain`, `Focus Stress`, `Open Translation`).
  - Added corresponding main-window workflow handlers for language triage and fast transitions.
  - Extended doctor checks for HUD visibility and language block state expectations.
  - Re-ran full UI-QA automation and refreshed artifacts.
- Resolved findings:
  - HUD + Language Hub are now product-visible working zones with actionable controls.
  - UI-QA pipeline remains operational with fresh artifacts and valid screenshot paths.
  - Existing MVP pipeline still passes smoke e2e (`tests/integration/test_pipeline_e2e.py`).
- Remaining findings:
  - `floating_critical_cta` still dominates (major layout warnings).
  - Dense toolbar layout anchoring requires manual panel-level fixes.
- Notes:
  - No critical UI-QA blockers in this run.
