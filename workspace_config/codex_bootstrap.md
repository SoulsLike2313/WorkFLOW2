# Codex Bootstrap Guide

## Mandatory Pre-Task Read Order (Execution Gate)
Codex must complete this order before any task analysis or code change:

1. `README.md`
2. `workspace_config/workspace_manifest.json`
3. `workspace_config/codex_manifest.json`
4. `workspace_config/TASK_RULES.md`
5. `workspace_config/AGENT_EXECUTION_POLICY.md`
6. `workspace_config/MACHINE_REPO_READING_RULES.md`
7. `docs/INSTRUCTION_INDEX.md`
8. relevant `PROJECT_MANIFEST.json`
9. relevant project `README.md`
10. relevant `CODEX.md` if present
11. relevant `SYSTEM_MANIFEST.json` if shared system is involved

If read order is not complete: task status is `REJECTED`.

## Mandatory Task Contract Gate
Task execution is forbidden without strict parameters.

Missing any required item:

- exact goal
- exact target scope
- target project or module
- allowed paths
- forbidden paths
- expected outputs
- acceptance criteria
- validation steps
- explicit do-not-do block

results in:

- `STATUS: REJECTED`
- `REASON: insufficient task contract`

## Active project policy
- Analyze active project first.
- Legacy/archived projects are touched only on explicit user request.
- Do not infer project scope from folder names; use manifests.
- No side work.
- No unrequested artifacts.
- No silent scope expansion.

## Bootstrap command
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_workspace.ps1
```

Optional active setup:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_workspace.ps1 -SetupActive
```

## Verification Gate After Intake
1. Validate workspace registry: `python scripts/validate_workspace.py`.
2. Resolve active project and read relevant manifests.
3. Execute declared project verification entrypoint.
4. Without acceptance criteria and validation evidence, completion claim is forbidden.
