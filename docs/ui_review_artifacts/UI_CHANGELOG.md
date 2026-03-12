# UI Changelog

## 2026-03-12 — UI QA hardening pass

### Scripts updated
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/scripts/ui_snapshot_runner.py`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/scripts/ui_validate.py`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/scripts/ui_doctor.py`

### Automation changes
- Walkthrough trace now produced and persisted.
- Screenshot manifest now includes scenario metadata.
- Validation now checks state coverage and walkthrough actions.
- Doctor now reports acceptance blockers and grouped issue views.

### Run evidence
- snapshot run: `20260312_170735` (`PASS`)
- validate run: `20260312_170515` (`PASS`)
- doctor run inside validate: `20260312_170515` (`PASS`)

### Artifact updates
- Root artifacts updated:
  - `ui_validation_summary.json`
  - `ui_validation_summary.md`
  - `ui_screenshots_manifest.json`
  - `ui_walkthrough_trace.json`
- Runtime latest pointers updated:
  - `runtime/ui_snapshots/latest_run.{txt,json}`
  - `runtime/ui_validation/latest_run.{txt,json}`
