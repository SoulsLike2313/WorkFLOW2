# Project Audit Policy (Machine-Enforced)

## Platform Reframe

Primary platform project:

- `platform_test_agent`

Platform model:

1. audit-first
2. evidence-first
3. admission-gate-first

## Canonical Audit Workflow

Tester agent workflow for each target project:

1. project intake (`target_project_path`, `target_project_slug`, manifest resolution)
2. verification run
3. readiness run
4. UI-QA run (if UI exists)
5. reporting checks
6. localization audit
7. audit/observability audit
8. evidence collection (screenshots/logs/traces/summaries)
9. final machine report with admission decision

## Status Model for Guarded Projects

Guarded projects must remain in one of these states before tester-agent admission:

1. `audit_required`
2. `manual_testing_blocked`

## Manual Testing Admission Gate

Manual testing is forbidden unless all conditions are true:

1. tester-agent final status is `PASS` or `PASS_WITH_WARNINGS`;
2. repo-visible audit summaries exist;
3. final machine audit report exists and is readable by repo-relative path.

If any condition fails:

- admission status = `manual_testing_blocked`

## Source of Truth

Authoritative files:

1. `workspace_config/workspace_manifest.json`
2. `workspace_config/codex_manifest.json`
3. `workspace_config/PROJECT_AUDIT_POLICY.md`
4. target project `PROJECT_MANIFEST.json`
5. audit report artifacts in `docs/review_artifacts/`
