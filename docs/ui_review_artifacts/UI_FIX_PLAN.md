# UI Fix Plan

## Scope of this corrective cycle
- Fix automation blind spots and false PASS risks.
- Keep focus on UI-QA system behavior and machine evidence.

## Executed corrections
1. `ui_snapshot_runner`
- Added state coverage capture (`initial/loaded/no_selection/dense/empty/anomaly`).
- Added walkthrough trace output (`ui_walkthrough_trace.json`).
- Added richer screenshot metadata (`importance`, `scenario_reference`).

2. `ui_validate`
- Added walkthrough/state coverage validation logic.
- Added strict check lists (`passed_checks`, `warned_checks`, `failed_checks`).
- Added root walkthrough artifact publication.
- Added explicit PASS/PASS_WITH_WARNINGS/FAIL gate behavior.

3. `ui_doctor`
- Added acceptance-blocker classification and issue taxonomy.
- Added grouped screen/category summaries.
- Added walkthrough trace output.
- Reduced false positives in CTA checks.

## Outcome
- Latest validate run (`20260312_170515`) is `PASS` with no warnings/failures.
- Machine evidence available in run directories and root summary artifacts.
