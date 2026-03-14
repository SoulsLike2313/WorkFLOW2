# Test Agent Admission Flow

## Admission Status Model

1. `audit_required`
2. `under_audit`
3. `manual_testing_blocked`
4. `manual_testing_allowed`
5. `failed_audit`

## Gate Rules

Manual testing allowed only if:

1. tester-agent report exists;
2. required checks completed;
3. repo-visible evidence exists;
4. final status is `PASS` or `PASS_WITH_WARNINGS`.

If any condition is unmet:

- final admission decision = `manual_testing_blocked`

## Evidence Paths

- `runtime/projects/platform_test_agent/audit_reports/<run_id>/final_machine_report.json`
- `runtime/projects/platform_test_agent/audit_reports/<run_id>/evidence_manifest.json`
- `runtime/projects/platform_test_agent/audit_reports/<run_id>/admission_decision.json`
