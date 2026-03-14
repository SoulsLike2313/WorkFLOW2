# Test Agent Execution Policy (Machine-Enforced)

## Scope

Policy for `platform_test_agent` only.

## Required Execution Sequence

1. `project_intake`
2. `lane_selection`
3. `verification_lane`
4. `readiness_lane`
5. `ui_audit_lane` (if UI exists)
6. `reporting_lane`
7. `localization_audit_lane`
8. `audit_observability_lane`
9. `evidence_collection`
10. `final_admission_gate`

## Shared Systems Dependency Contract

Required:

1. `verification_toolkit`
2. `ui_qa_toolkit`
3. `reporting_toolkit`
4. `localization_toolkit`
5. `audit_observability_toolkit`

Optional future:

1. `update_patch_toolkit`
2. `security_baseline`

## Output Contract

Required outputs per run:

1. `final_machine_report.json`
2. `evidence_manifest.json`
3. `admission_decision.json`

## Admission Decision Rule

`manual_testing_allowed` is valid only when:

1. required checks are completed;
2. evidence outputs are repo-visible;
3. final status is `PASS` or `PASS_WITH_WARNINGS`.

Else:

- `manual_testing_blocked`
