# Tester Agent Admission Policy

## Admission States

1. `audit_required`
2. `under_audit`
3. `manual_testing_blocked`
4. `manual_testing_allowed`
5. `failed_audit`

## Manual Testing Allowed Only If

1. tester-agent report exists.
2. required checks are completed.
3. repo-visible evidence exists.
4. final status is `PASS` or `PASS_WITH_WARNINGS`.

## Blocking Conditions

Manual testing remains blocked if any required condition is missing.

## Source of Truth

1. `projects/platform_test_agent/PROJECT_MANIFEST.json`
2. `workspace_config/PROJECT_AUDIT_POLICY.md`
3. `runtime/projects/platform_test_agent/audit_reports/<run_id>/admission_decision.json`
