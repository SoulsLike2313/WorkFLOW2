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
- `scripts/`: workspace bootstrap, validation, startup, and utility scripts.
- `workspace_config/`: machine-readable workspace governance and templates.
- `runtime/`: generated runtime and diagnostics artifacts.

## Project Priority and Status

Status source of truth:

- `workspace_config/workspace_manifest.json`

Current priority model:

- `active`: `tiktok_agent_platform`
- `supporting`: `voice_launcher`
- `experimental`: `adaptive_trading`, `game_ru_ai`

## Root Entrypoints for the Active Module

Run from repository root (`.`):

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
