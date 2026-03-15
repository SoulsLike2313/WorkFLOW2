# MACHINE_CONTEXT

## Goal

Provide a deterministic context snapshot for Codex/ChatGPT/new machine readers.

## Current Canonical State

- Repository visibility model: private workspace.
- Canonical external state: GitHub (`origin/main`).
- Active project: `platform_test_agent`.
- Guarded projects:
  - `tiktok_agent_platform` (`manual_testing_blocked`)
  - `game_ru_ai` (`audit_required`)

## Mandatory Read Gate

Follow `workspace_config/MACHINE_REPO_READING_RULES.md` exactly.

Minimal boot order:

1. `README.md`
2. `workspace_config/workspace_manifest.json`
3. `workspace_config/codex_manifest.json`
4. `workspace_config/TASK_RULES.md`
5. `workspace_config/AGENT_EXECUTION_POLICY.md`
6. `workspace_config/MACHINE_REPO_READING_RULES.md`
7. `docs/INSTRUCTION_INDEX.md`
8. target `PROJECT_MANIFEST.json`

## Execution Rules

- No strict task contract -> `STATUS: REJECTED`.
- No side work, no silent scope expansion.
- Completion requires `git add -> git commit -> git push`.
- Unsynced local/remote state -> `NOT_COMPLETED`.

## Fast Project Resolution

Canonical registry source:

- `workspace_config/workspace_manifest.json` -> `project_registry`.

Do not infer projects from folder names alone.

## Shared Systems Resolution

- Registry: `workspace_config/shared_systems_registry.json`
- Module authority: `shared_systems/<slug>/SYSTEM_MANIFEST.json`
- Install/remove workflows:
  - `scripts/install_system.py`
  - `scripts/remove_system.py`

## Non-Canonical Inputs

Do not treat the following as source of truth:

- transient runtime outputs
- review artifacts as registry authority
- local-only diagnostics
- any non-committed local files
