# Codex Bootstrap Guide

## Mandatory startup order
1. Read `workspace_config/workspace_manifest.json`.
2. Run `python scripts/validate_workspace.py`.
3. Resolve `active_project` from workspace manifest.
4. Read active `PROJECT_MANIFEST.json`.
5. Read active project `README.md` and `CODEX.md`.
6. Run active verification entrypoint before manual test claims.
7. Run startup preflight for the project before launch commands.

## Active project policy
- Analyze active project first.
- Legacy/archived projects are touched only on explicit user request.
- Do not infer project scope from folder names; use manifests.

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
