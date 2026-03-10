# WorkFLOW Repository

Current active structure (cleaned):

- `projects/adaptive_trading/`
- `projects/voice_launcher/`
- `projects/wild_hunt_command_citadel/`
  - `tiktok_automation_app/`
  - `shortform_core/`

## Wild Hunt Command Citadel

Main app:

- `E:\CVVCODEX\projects\wild_hunt_command_citadel\tiktok_automation_app`

Analytics core:

- `E:\CVVCODEX\projects\wild_hunt_command_citadel\shortform_core`

EXE output:

- `E:\CVVCODEX\projects\wild_hunt_command_citadel\tiktok_automation_app\dist\WitcherCommandDeck.exe`

## Auto Sync To GitHub

Scripts:

- `scripts/auto_sync.ps1` - one run: fetch/pull/rebase, commit local changes, push.
- `scripts/register_auto_sync_task.ps1` - create Windows Task Scheduler job.
- `scripts/unregister_auto_sync_task.ps1` - remove the task.

Quick setup (every 15 minutes):

```powershell
cd E:\CVVCODEX
powershell -ExecutionPolicy Bypass -File .\scripts\register_auto_sync_task.ps1 -Minutes 15
```
