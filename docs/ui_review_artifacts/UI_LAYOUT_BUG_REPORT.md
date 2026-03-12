# UI Layout Bug Report

## Run references
- Baseline with blind spots: `runtime/ui_validation/20260312_165931/ui_validation_summary.json`
- Corrected run: `runtime/ui_validation/20260312_170515/ui_validation_summary.json`

## Layout issue register
| screen | issue_type | severity | status | evidence |
|---|---|---|---|---|
| analytics | missing_critical_cta (false positive) | critical | resolved in detector logic | 165931 -> 170515 |
| sessions/updates/settings | floating_cta_risk over-detection | major | reduced by rule hardening | 165931 -> 170515 |

## Current layout status (latest)
- `critical=0`, `major=0`, `minor=0` in run `20260312_170515`.
- No acceptance blockers in latest validate run.

## Artifact links
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/ui_validation/20260312_170515/ui_screenshots_manifest.json`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/ui_validation/20260312_170515/ui_walkthrough_trace.json`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/runtime/ui_validation/validate_20260312_170515/ui_validation_summary.json`
