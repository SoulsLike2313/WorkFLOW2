# Platform Test Agent

`platform_test_agent` is the primary platform project for audit-first test admission.

Role:

1. Accept target project path/slug.
2. Run verification/readiness/UI-QA/reporting/localization/audit checks.
3. Collect screenshots/logs/traces/summaries.
4. Produce machine-readable final audit report.
5. Decide manual testing admission (`PASS` / `PASS_WITH_WARNINGS` required).

## Core Modes

Run from repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\projects\platform_test_agent\run_project.ps1 -Mode intake -TargetProjectPath <repo_relative_project_path>
```

```powershell
powershell -ExecutionPolicy Bypass -File .\projects\platform_test_agent\run_project.ps1 -Mode audit -TargetProjectPath <repo_relative_project_path> -TargetProjectSlug <project_slug>
```

```powershell
powershell -ExecutionPolicy Bypass -File .\projects\platform_test_agent\run_project.ps1 -Mode verify -TargetProjectSlug <project_slug>
```

## Admission Rule

Manual testing is blocked unless the final tester-agent audit status is:

- `PASS`, or
- `PASS_WITH_WARNINGS`

and required summaries are repo-visible.

## Repo Trust Desktop UI

One-screen desktop control center for repository trust diagnostics:

```powershell
python .\projects\platform_test_agent\scripts\repo_control_center.py
```

The UI gives a fast verdict (`TRUSTED` / `NOT TRUSTED`) and shows:

- Repo integrity
- GitHub sync
- Safe reading files presence
- Safe reading hash match against `workspace_config/safe_reading_manifest.json`
