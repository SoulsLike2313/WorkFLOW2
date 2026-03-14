# CODEX.md

## Project Identity

`platform_test_agent` is the canonical active project for workspace-level project audit and test admission.

## Execution Contract

1. Intake target project path and slug.
2. Resolve project type and manifests.
3. Run bounded audit flows:
   - verification
   - readiness
   - UI-QA (if UI exists)
   - reporting checks
   - localization checks
   - audit/observability checks
4. Collect machine evidence artifacts.
5. Emit final machine report with admission verdict.

## Manual Testing Gate

1. `manual_testing_blocked` is default for guarded projects.
2. Admission allowed only on tester-agent final status:
   - `PASS`, or
   - `PASS_WITH_WARNINGS`
3. Admission requires repo-visible audit summaries.
