# UI Build Rules

Active module: `projects/wild_hunt_command_citadel/shortform_core`

## 1. Artifact portability
- Machine artifacts must use repo-relative paths only.
- Absolute machine-local paths are not allowed.

## 2. Required run outputs
Each validation cycle must produce:
- `ui_validation_summary.json`
- `ui_validation_summary.md`
- `ui_screenshots_manifest.json`
- `ui_walkthrough_trace.json`
- `runtime/ui_snapshots/latest_run.{txt,json}`
- `runtime/ui_validation/latest_run.{txt,json}`

## 3. Screenshot manifest contract
Each screenshot record must contain:
- `screen_name`
- `state_name`
- `screenshot_path`
- `timestamp`
- `notes`
- `tags`
- `importance`
- `scenario_reference`
- `severity_reference`
- `issue_reference`

## 4. Walkthrough contract
Walkthrough trace must include:
- `run_id`
- `step_index`
- `screen`
- `action`
- `result`
- `screenshot_ref`
- `notes`

## 5. Required screen coverage
Screens must be traversed in each cycle:
- dashboard
- profiles
- sessions
- content
- analytics
- ai_studio
- audit
- updates
- settings

## 6. Gate policy
- `PASS`: no failed checks, no acceptance blockers, no critical issues.
- `PASS_WITH_WARNINGS`: no blockers/critical failures, but warnings remain.
- `FAIL`: blockers or critical failures exist.

Manual testing is allowed only when gate status is `PASS`.

## 7. UI doctor required categories
Doctor issues must map to categories:
- layout
- cta
- visibility
- spacing
- typography
- localization
- resize
- session_realism
- analytics_readability
- product_clarity

## 8. Known machine blind spots
These remain manual-only checks:
- semantic visual quality,
- physical monitor contrast perception,
- perceived motion smoothness.
