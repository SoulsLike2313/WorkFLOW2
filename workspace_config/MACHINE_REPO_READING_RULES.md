# Machine Repo Reading Rules

## Purpose
Define deterministic reading order and source-of-truth resolution for machine agents reading this repository (including via GitHub URL).

## Deterministic Reading Order

Always read in this order:

1. `README.md` (workspace map)
2. `workspace_config/workspace_manifest.json` (workspace registry)
3. `workspace_config/codex_manifest.json` (machine onboarding policy)
4. `workspace_config/TASK_RULES.md` (task acceptance gate)
5. `workspace_config/AGENT_EXECUTION_POLICY.md` (execution constraints)
6. target `PROJECT_MANIFEST.json` (project source of truth)
7. target project `README.md` + `CODEX.md`
8. `shared_systems/*/SYSTEM_MANIFEST.json` (if directory exists)

## Source of Truth Resolution

1. Root README = workspace map.
2. `workspace_manifest.json` = project registry + active project status.
3. `codex_manifest.json` = machine onboarding and scope controls.
4. `PROJECT_MANIFEST.json` = project truth contract.
5. `SYSTEM_MANIFEST.json` = shared system truth contract.

If documents conflict, higher-priority source above wins.

## Rule Set

### 1. Determine active project
- Read `workspace_config/workspace_manifest.json`.
- Use `active_project` slug.
- Resolve `project_registry[].manifest_path` for that slug.

### 2. Determine shared systems
- If `shared_systems/` exists: enumerate direct child folders.
- For each folder, require `SYSTEM_MANIFEST.json`.
- If `shared_systems/` does not exist: shared systems are `not configured`.

### 3. Determine project status
- Use `project_registry[].status` as primary source.
- `project_status_index` is consistency mirror, not primary source.

### 4. Determine installed systems in each project
- Read project `PROJECT_MANIFEST.json`.
- If field `installed_systems` exists: use it.
- If field missing: status is `unknown/not-declared` (do not guess).

### 5. Determine manifests
- Workspace manifest: `workspace_config/workspace_manifest.json`
- Codex manifest: `workspace_config/codex_manifest.json`
- Project manifest(s): `projects/**/PROJECT_MANIFEST.json`
- System manifest(s): `shared_systems/**/SYSTEM_MANIFEST.json`

### 6. Determine verification entrypoints
- Project-level: `PROJECT_MANIFEST.json -> verification_entrypoints`.
- Workspace-level: `workspace_manifest.json -> verification_entrypoints`.
- If both exist, project-level is execution target for that project.

### 7. Determine install/remove workflows
- Expected install scripts:
  - `scripts/install_system.py` or `scripts/install_system.ps1`
- Expected remove scripts:
  - `scripts/remove_system.py` or `scripts/remove_system.ps1`
- If missing, declare workflow as `not implemented`.

### 8. Determine source-of-truth docs for execution
- Task intake: `workspace_config/TASK_RULES.md` + `workspace_config/task_manifest.schema.json`
- Agent behavior: `workspace_config/AGENT_EXECUTION_POLICY.md`
- Repo reading: this file

## GitHub-Link Readability Constraints

To keep repository machine-readable from remote URL:

1. Paths in manifests must be repo-relative.
2. Avoid machine-local absolute paths in governance files.
3. Keep required contracts in stable locations under `workspace_config/`.
4. Use explicit slugs and explicit status values only.

## Non-Guessing Rule

If a required contract field is missing, agent must return:

- `insufficient_contract_data`

and must not infer missing data from naming conventions alone.
