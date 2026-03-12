# Codex Bootstrap Guide

## Mandatory startup order
1. Read `workspace_config/workspace_manifest.json`.
2. Read `workspace_config/MACHINE_REPO_READING_RULES.md`.
3. Read `workspace_config/TASK_RULES.md`.
4. Read `workspace_config/AGENT_EXECUTION_POLICY.md`.
5. Run `python scripts/validate_workspace.py`.
6. Resolve `active_project` from workspace manifest.
7. Read active `PROJECT_MANIFEST.json`.
8. Read active project `README.md` and `CODEX.md`.
9. Run active verification entrypoint before manual test claims.
10. Run startup preflight for the project before launch commands.

## Active project policy
- Analyze active project first.
- Legacy/archived projects are touched only on explicit user request.
- Do not infer project scope from folder names; use manifests.
- Do not accept broad tasks without strict scope parameters.

## Bootstrap command
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_workspace.ps1
```

Optional active setup:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_workspace.ps1 -SetupActive
```

## First action plan for human + Codex
1. Validate workspace registry (`python scripts/validate_workspace.py`).
2. Confirm active project and entrypoints from manifests.
3. Execute active verify pipeline.
4. Review latest runtime artifacts before any manual UI testing.
5. Run `python scripts/project_startup.py prepare --project-slug <slug> --port-mode fixed` before user/developer launch.
