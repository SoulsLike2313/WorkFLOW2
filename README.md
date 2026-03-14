# WorkFLOW Multi-Project Repository

## Overview

This repository is a structured multi-project workspace.

Current engineering priority is one active platform module:

- `projects/platform_test_agent`

## Active Module

Primary active module:

- `projects/platform_test_agent`

Primary references:

- `projects/platform_test_agent/README.md`
- `projects/platform_test_agent/PROJECT_MANIFEST.json`

## Platform Direction (Active Module)

The active module is a tester agent workflow (audit-first gate), not an app product layer.

Primary workflow:

1. project intake (`path` + `slug` + manifest resolution)
2. verification/readiness/UI-QA/reporting/localization/audit checks
3. evidence collection (screenshots/logs/traces/summaries)
4. final machine audit report
5. manual testing admission verdict (`PASS` or `PASS_WITH_WARNINGS` required)

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
- `workspace_config/PROMPT_OUTPUT_POLICY.md`
- `workspace_config/PROJECT_AUDIT_POLICY.md`
- `workspace_config/TEST_AGENT_EXECUTION_POLICY.md`
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
7. `workspace_config/PROMPT_OUTPUT_POLICY.md`
8. `workspace_config/PROJECT_AUDIT_POLICY.md`
9. `workspace_config/TEST_AGENT_EXECUTION_POLICY.md`
10. `docs/INSTRUCTION_INDEX.md`
11. relevant `PROJECT_MANIFEST.json`
12. relevant project `README.md`
13. relevant `CODEX.md` if present
14. relevant `SYSTEM_MANIFEST.json` if shared system is involved

Shared system workflows:

- install: `python scripts/install_system.py --project-slug <slug> --system-slug <system_slug>`
- remove: `python scripts/remove_system.py --project-slug <slug> --system-slug <system_slug>`

## Project Priority and Status

Status source of truth:

- `workspace_config/workspace_manifest.json`

Current priority model:

- `active`: `platform_test_agent`
- `supporting`: `voice_launcher`
- `experimental`: `adaptive_trading`
- `manual_testing_blocked`: `tiktok_agent_platform`
- `audit_required`: `game_ru_ai`

## Canonical Project Registry

Workspace-level projects (and only these) are canonical:

- `platform_test_agent` -> `projects/platform_test_agent` (`active`)
- `tiktok_agent_platform` -> `projects/wild_hunt_command_citadel/tiktok_agent_platform` (`manual_testing_blocked`)
- `voice_launcher` -> `projects/voice_launcher` (`supporting`)
- `adaptive_trading` -> `projects/adaptive_trading` (`experimental`)
- `game_ru_ai` -> `projects/GameRuAI` (`audit_required`)

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
powershell -ExecutionPolicy Bypass -File .\projects\platform_test_agent\run_project.ps1 -Mode intake -TargetProjectPath projects\wild_hunt_command_citadel\tiktok_agent_platform
```

Intake mode:

```powershell
powershell -ExecutionPolicy Bypass -File .\projects\platform_test_agent\run_project.ps1 -Mode intake -TargetProjectPath projects\GameRuAI
```

Audit mode:

```powershell
powershell -ExecutionPolicy Bypass -File .\projects\platform_test_agent\run_project.ps1 -Mode audit -TargetProjectPath projects\wild_hunt_command_citadel\tiktok_agent_platform -TargetProjectSlug tiktok_agent_platform
```

Verification:

```powershell
powershell -ExecutionPolicy Bypass -File .\projects\platform_test_agent\run_project.ps1 -Mode verify -TargetProjectSlug game_ru_ai
```

Manual test policy:

- manual testing is blocked for guarded projects until tester-agent final audit status is `PASS` or `PASS_WITH_WARNINGS`.
- repo-visible audit summaries are mandatory for admission.
