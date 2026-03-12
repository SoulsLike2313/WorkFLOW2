# Machine Instruction Audit

## Audit Scope

Audited instruction/config/governance layer for machine execution:

- workspace-level contracts (`workspace_config/*`)
- workspace map (`README.md`)
- active project contracts (`projects/wild_hunt_command_citadel/tiktok_agent_platform/*`)
- cross-cutting instruction docs under `docs/`

## Instruction Inventory and Status

| File | Status | Source of Truth Role | Normalization Need |
| --- | --- | --- | --- |
| `README.md` | clear | workspace map | none |
| `workspace_config/workspace_manifest.json` | clear | workspace registry and active project resolution | normalized (task governance section added) |
| `workspace_config/codex_manifest.json` | clear | machine onboarding policy | normalized (task governance files added to required set) |
| `workspace_config/codex_bootstrap.md` | clear | startup reading order and bootstrap sequence | normalized (strict governance files added to mandatory order) |
| `workspace_config/PROJECT_RULES.md` | clear | workspace project policy baseline | normalized (task governance binding section added) |
| `workspace_config/TASK_RULES.md` | clear | strict task acceptance gate | new |
| `workspace_config/task_manifest.schema.json` | clear | machine-readable task contract schema | new |
| `workspace_config/AGENT_EXECUTION_POLICY.md` | clear | execution boundary policy | new |
| `workspace_config/MACHINE_REPO_READING_RULES.md` | clear | deterministic repository reading policy | new |
| `workspace_config/UI_BUILD_RULES.md` | ambiguous/conflicting | intended UI rules | requires UTF-8 normalization and de-dup with docs UI rules |
| `docs/UI_BUILD_RULES.md` | clear | active UI validation artifact contract | none |
| `docs/CHECKPOINT.md` | stale | historical dev log (not active governance) | mark as legacy/non-authoritative for machine routing |
| `docs/DEV_CONTINUITY.md` | stale | historical voice launcher continuity note | mark as legacy/non-authoritative for machine routing |
| `projects/wild_hunt_command_citadel/tiktok_agent_platform/PROJECT_MANIFEST.json` | clear | active project source of truth | none |
| `projects/wild_hunt_command_citadel/tiktok_agent_platform/CODEX.md` | clear | active project execution contract | none |
| `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/PROJECT_MANIFEST.json` | clear | core-layer source of truth | none |
| `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/CODEX.md` | clear | core-layer execution contract | none |

## Conflict and Ambiguity Findings

1. `workspace_config/UI_BUILD_RULES.md` contains encoding-degraded content (mojibake in current read context) and overlaps with `docs/UI_BUILD_RULES.md`.
2. `docs/CHECKPOINT.md` and `docs/DEV_CONTINUITY.md` describe legacy voice-launcher workflows with machine-local absolute paths and are not aligned with current active-project governance.
3. Modular system governance is incomplete:
   - `shared_systems/` directory is absent,
   - `scripts/install_system.py|ps1` is absent,
   - `scripts/remove_system.py|ps1` is absent,
   - project manifests do not declare installed shared systems.

## Normalization Applied in This Change Set

1. Added strict task intake policy: `workspace_config/TASK_RULES.md`.
2. Added strict task manifest standard: `workspace_config/task_manifest.schema.json`.
3. Added strict execution boundaries: `workspace_config/AGENT_EXECUTION_POLICY.md`.
4. Added deterministic machine reading contract: `workspace_config/MACHINE_REPO_READING_RULES.md`.
5. Bound governance layer into workspace source-of-truth files:
   - `workspace_config/workspace_manifest.json`
   - `workspace_config/codex_manifest.json`
   - `workspace_config/PROJECT_RULES.md`
   - `workspace_config/codex_bootstrap.md`
   - `README.md`

## Modular Install/Remove Architecture Check

### Machine discoverability now

- Active project discovery: **clear** (via `workspace_manifest.json`).
- Project status discovery: **clear** (via `project_registry[].status`).
- Verification entrypoint discovery: **clear** (via project/workspace manifests).
- Task acceptance policy discovery: **clear** (new governance files).

### Current gaps

1. Shared systems registry: **missing** (`shared_systems/` absent).
2. Install workflow script: **missing** (`install_system.py|ps1` absent).
3. Remove workflow script: **missing** (`remove_system.py|ps1` absent).
4. Per-project installed system declaration: **missing** (`installed_systems` not present in project manifests).

### Net result

Task governance is now strict and machine-readable, but modular install/remove lifecycle is still not fully machine-operational due missing shared-system layer and workflows.
