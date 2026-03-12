# REPO TRUTH RECONCILIATION REPORT

## Scope
- README.md
- workspace_config/workspace_manifest.json
- workspace_config/codex_manifest.json
- All PROJECT_MANIFEST.json files under projects/
- Visible repository tree at root and projects/

## Reconciliation Run
- run_id: reconcile-20260312T200944Z
- branch: main

## Discrepancies Found
1. Priority mismatch between workspace registry and project manifests.
- voice_launcher priority in workspace registry: 3
- voice_launcher priority in project manifest: 2
- adaptive_trading priority in workspace registry: 4
- adaptive_trading priority in project manifest: 3
- game_ru_ai priority in workspace registry: 6
- game_ru_ai priority in project manifest: 5

2. Tree visibility ambiguity for non-registry path.
- Path exists: projects/wild_hunt_command_citadel/shortform_core
- Path was not explicitly classified in root-level truth map.
- Risk: machine can interpret it as independent project scope.

3. Layer manifest ambiguity inside active project.
- Files exist:
  - projects/wild_hunt_command_citadel/tiktok_agent_platform/core/PROJECT_MANIFEST.json
  - projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/PROJECT_MANIFEST.json
- These manifests are layer-level manifests and not workspace project registry entries.
- This rule was implicit, not explicit in root README.

## Corrections Applied
1. workspace_config/workspace_manifest.json updated.
- project_registry.voice_launcher.priority: 3 -> 2
- project_registry.adaptive_trading.priority: 4 -> 3
- project_registry.game_ru_ai.priority: 6 -> 5
- Added non_registry_paths classification for:
  - projects/wild_hunt_command_citadel/shortform_core

2. README.md updated.
- Added canonical project registry mapping slug -> path -> status.
- Added explicit non-registry clarifications for:
  - projects/wild_hunt_command_citadel/shortform_core
  - core/agent layer PROJECT_MANIFEST files inside tiktok_agent_platform

## Source of Truth After Reconciliation
- Workspace map: README.md
- Workspace registry and statuses: workspace_config/workspace_manifest.json
- Machine onboarding policy: workspace_config/codex_manifest.json
- Project-level truth: each projects/**/PROJECT_MANIFEST.json

## Validation Result
- README active project: tiktok_agent_platform
- workspace_manifest active_project: tiktok_agent_platform
- Registry slugs and paths exist in repository tree.
- Registry status index aligns with project manifest statuses for canonical workspace projects.
- Canonical/non-canonical path interpretation is explicitly documented.
- workspace validation run: runtime/workspace_validation/workspace-validate-20260312T200944Z
