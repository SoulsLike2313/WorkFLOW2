# UI ChangeLog - GameRuAI

## Entries

### 2026-03-12
- Run ID: `20260312_155348`
- Validation status: `PASS_WITH_WARNINGS`
- Doctor status: `PASS_WITH_WARNINGS` (`20260312_155348`)
- Snapshot status: `PASS` (`20260312_155949`)
- Change set:
  - Added top Product HUD to `MainWindow` with project/backend/pipeline/QA/voice/companion visibility.
  - Added `Language Hub` screen with overview, queue, backend status, review, stress, and flow blocks.
  - Added real snapshot providers in `AppServices`: `hud_snapshot` and `language_hub_snapshot`.
  - Extended UI-QA scenario catalog and doctor checks for Language Hub states.
  - Re-ran full UI-QA automation and refreshed all review artifacts.
- Resolved findings:
  - Product-specific coverage now includes HUD + Language Hub in real screenshots.
  - Validator/doctor/snapshot artifacts are consistent and point to existing files.
- Remaining findings:
  - `floating_critical_cta` still dominates (major layout warnings).
  - Layout anchoring quality is not yet release-ready on dense toolbar screens.
- Notes:
  - Existing MVP pipeline remains functional (`tests/integration/test_pipeline_e2e.py` passed).
