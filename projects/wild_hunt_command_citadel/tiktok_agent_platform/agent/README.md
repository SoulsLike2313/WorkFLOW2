# TikTok Agent App Layer

This folder contains the product-facing desktop TikTok agent layer.

It is part of the unified project:

- `projects/wild_hunt_command_citadel/tiktok_agent_platform`

Core integration path:

- `../core`

## Responsibilities

- profile/session UX
- scheduler and queue execution
- automation engine orchestration
- operator-facing dashboards and logs
- invoking core workflows when requested

## Run

```powershell
cd projects/wild_hunt_command_citadel/tiktok_agent_platform/agent
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode developer -PortMode fixed
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode user -PortMode fixed
```

## Verify

```powershell
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode verify -PortMode fixed
```
