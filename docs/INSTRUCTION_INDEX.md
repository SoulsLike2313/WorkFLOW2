# Instruction Index

## Priority Model

- `P0`: hard machine source of truth (must read first).
- `P1`: execution policy and operational contracts.
- `P2`: domain/layer-specific contracts.
- `P3`: historical/supporting notes (non-authoritative for routing).

## Mandatory Pre-Task Read Order

Before any task execution, Codex must read in this exact order:

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

If this order is not completed, task status is `REJECTED`.

## Index

| File | Role | Priority | Target Audience |
| --- | --- | --- | --- |
| `README.md` | Workspace map and top-level orientation | P0 | machine, codex, developer, product reviewer |
| `workspace_config/workspace_manifest.json` | Project registry, active project, status model | P0 | machine, codex, developer |
| `workspace_config/codex_manifest.json` | Machine onboarding order and scope controls | P0 | machine, codex |
| `workspace_config/TASK_RULES.md` | Strict task acceptance gate | P0 | machine, codex, product reviewer |
| `workspace_config/task_manifest.schema.json` | Machine-readable task manifest contract | P0 | machine, codex, developer |
| `workspace_config/TASK_INTAKE_REFERENCE.md` | Intake validity criteria and refusal templates | P0 | machine, codex, developer, product reviewer |
| `workspace_config/shared_systems_registry.json` | Shared module registry and project installation map | P0 | machine, codex, developer |
| `workspace_config/AGENT_EXECUTION_POLICY.md` | Strict execution boundaries and anti-side-work rules | P0 | machine, codex, product reviewer |
| `workspace_config/MACHINE_REPO_READING_RULES.md` | Deterministic repository reading policy | P0 | machine, codex |
| `workspace_config/PROJECT_RULES.md` | Workspace project lifecycle and isolation standards | P1 | machine, codex, developer |
| `workspace_config/codex_bootstrap.md` | Bootstrap sequence for execution startup | P1 | codex, developer |
| `workspace_config/UI_BUILD_RULES.md` | Workspace-level UI constraints (requires normalization) | P1 | codex, developer |
| `docs/UI_BUILD_RULES.md` | Active UI artifact and validation contract | P1 | codex, developer, product reviewer |
| `projects/*/PROJECT_MANIFEST.json` | Per-project machine source of truth | P2 | machine, codex, developer |
| `projects/wild_hunt_command_citadel/tiktok_agent_platform/CODEX.md` | Active project execution contract | P2 | codex, developer |
| `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/CODEX.md` | Core-layer execution and verification contract | P2 | codex, developer |
| `workspace_config/templates/project_template/*.json` | New-project scaffold contracts | P2 | machine, developer |
| `scripts/install_system.py` | Machine install workflow for shared systems | P2 | machine, codex, developer |
| `scripts/remove_system.py` | Machine remove workflow for shared systems | P2 | machine, codex, developer |
| `shared_systems/*/SYSTEM_MANIFEST.json` | Shared system source of truth per module | P2 | machine, codex, developer |
| `docs/CHECKPOINT.md` | Historical checkpoint log | P3 | developer |
| `docs/DEV_CONTINUITY.md` | Historical continuity note | P3 | developer |
| `docs/review_artifacts/*.md` | Evidence and review outputs; not policy authority | P3 | product reviewer, developer |

## Authority Rules

1. If `P0` and `P1/P2/P3` conflict, `P0` wins.
2. `P3` files are non-authoritative for task routing and scope control.
3. Project-level changes must resolve project truth from `projects/*/PROJECT_MANIFEST.json`, not from historical notes.
