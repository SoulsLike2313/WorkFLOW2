# WorkFLOW Multi-Project Repository

## Overview

This repository is a structured multi-project workspace.

Current engineering priority is one active product module:

- `projects/wild_hunt_command_citadel/tiktok_agent_platform`

## Active Module

Primary active module:

- `projects/wild_hunt_command_citadel/tiktok_agent_platform`

Primary references:

- `projects/wild_hunt_command_citadel/tiktok_agent_platform/README.md`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/PROJECT_MANIFEST.json`

## Product Architecture (Active Module)

The active module is one product with explicit layers:

- `core/` - platform/runtime core and verification/update/UI-QA foundations.
- `agent/` - TikTok agent application layer.

## Root-Level Structure

Top-level purpose:

- `docs/`: repository-level documentation and review artifacts.
- `projects/`: project source roots.
- `shared_systems/`: portable reusable system modules.
- `scripts/`: workspace bootstrap, validation, startup, and utility scripts.
- `workspace_config/`: machine-readable workspace governance and templates.
- `runtime/`: generated runtime and diagnostics artifacts.

## Task Governance Layer

Strict machine task governance is defined in:

- `workspace_config/TASK_RULES.md`
- `workspace_config/task_manifest.schema.json`
- `workspace_config/TASK_INTAKE_REFERENCE.md`
- `workspace_config/AGENT_EXECUTION_POLICY.md`
- `workspace_config/MACHINE_REPO_READING_RULES.md`
- `workspace_config/shared_systems_registry.json`

Acceptance gate:

- no strict parameters -> no task acceptance.
- missing strict task contract -> `STATUS: REJECTED`, `REASON: insufficient task contract`.

Mandatory pre-task read gate:

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

Shared system workflows:

- install: `python scripts/install_system.py --project-slug <slug> --system-slug <system_slug>`
- remove: `python scripts/remove_system.py --project-slug <slug> --system-slug <system_slug>`

## Project Priority and Status

Status source of truth:

- `workspace_config/workspace_manifest.json`

Current priority model:

- `active`: `tiktok_agent_platform`
- `supporting`: `voice_launcher`
- `experimental`: `adaptive_trading`, `game_ru_ai`

## Canonical Project Registry

Workspace-level projects (and only these) are canonical:

- `tiktok_agent_platform` -> `projects/wild_hunt_command_citadel/tiktok_agent_platform` (`active`)
- `voice_launcher` -> `projects/voice_launcher` (`supporting`)
- `adaptive_trading` -> `projects/adaptive_trading` (`experimental`)
- `game_ru_ai` -> `projects/GameRuAI` (`experimental`)

Tree paths that exist but are non-registry:

- `projects/wild_hunt_command_citadel` is a project-group container path and is not a standalone workspace project.
- `projects/wild_hunt_command_citadel/shortform_core` is a local legacy residue path (if present on workstation), ignored by git and not GitHub-visible; it is not part of workspace project inventory.
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/PROJECT_MANIFEST.json` and `projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/PROJECT_MANIFEST.json` are product layer manifests, not workspace project registry entries.

## Source of Truth Order

If any document conflicts, interpret repository truth in this order:

1. `workspace_config/workspace_manifest.json` (active project, statuses, registry, non-registry paths, layer manifest registry)
2. canonical `PROJECT_MANIFEST.json` for each registry project
3. this `README.md` as root navigation map
4. review artifacts in `docs/review_artifacts/` as evidence logs, not registry authority

## Root Entrypoints for the Active Module

Run from repository root (`.`):

Canonical user-mode root entrypoint:

```powershell
python scripts/project_startup.py run --project-slug tiktok_agent_platform --entrypoint user --startup-kind user --port-mode fixed
```

User mode:

```powershell
python scripts/project_startup.py run --project-slug tiktok_agent_platform --entrypoint user --startup-kind user --port-mode fixed
```

Developer mode:

```powershell
python scripts/project_startup.py run --project-slug tiktok_agent_platform --entrypoint developer --startup-kind developer --port-mode fixed
```

Verification:

```powershell
python scripts/project_startup.py run --project-slug tiktok_agent_platform --entrypoint verify --startup-kind verify --port-mode fixed
```

Update flow:

```powershell
python scripts/project_startup.py run --project-slug tiktok_agent_platform --entrypoint update --startup-kind update --port-mode fixed
```

Manual test policy:

- manual testing is allowed only after verification gate `PASS`.
