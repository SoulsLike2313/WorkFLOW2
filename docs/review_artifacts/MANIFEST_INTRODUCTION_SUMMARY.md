# MANIFEST_INTRODUCTION_SUMMARY

## Added/normalized manifests
1. Workspace level:
- `workspace_config/workspace_manifest.json`
- `workspace_config/codex_manifest.json`

2. Project level:
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/PROJECT_MANIFEST.json`
- `projects/voice_launcher/PROJECT_MANIFEST.json`
- `projects/adaptive_trading/PROJECT_MANIFEST.json`
- `projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/PROJECT_MANIFEST.json`

## Why manifests are required
- machine-readable project registration,
- strict status tracking (`active/supporting/experimental/archived/legacy`),
- deterministic entrypoint mapping,
- validator-friendly schema checks,
- onboarding without guesswork.

## Coverage status
- all major projects in `projects/` now have `PROJECT_MANIFEST.json`.
