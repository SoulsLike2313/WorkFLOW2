# PROJECT PATH STATUS MATRIX

| slug | path | physical_exists | registry_class | status | priority | notes |
|---|---|---|---|---|---|---|
| tiktok_agent_platform | projects/wild_hunt_command_citadel/tiktok_agent_platform | yes | registry_project | active | 1 | canonical active workspace project |
| voice_launcher | projects/voice_launcher | yes | registry_project | supporting | 2 | supporting workspace project |
| adaptive_trading | projects/adaptive_trading | yes | registry_project | experimental | 3 | experimental workspace project |
| game_ru_ai | projects/GameRuAI | yes | registry_project | experimental | 5 | experimental workspace project |
| wild_hunt_command_citadel_container | projects/wild_hunt_command_citadel | yes | non_registry_path | n/a | n/a | project group container, excluded from workspace registry |
| shortform_core_legacy_path | projects/wild_hunt_command_citadel/shortform_core | yes | non_registry_path | n/a | n/a | legacy internal layer path, excluded from workspace registry |
| tiktok_agent_core_layer | projects/wild_hunt_command_citadel/tiktok_agent_platform/core/PROJECT_MANIFEST.json | yes | layer_manifest | supporting (layer-local) | 1 (layer-local) | internal layer manifest, not standalone workspace project |
| tiktok_agent_app_layer | projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/PROJECT_MANIFEST.json | yes | layer_manifest | supporting (layer-local) | 2 (layer-local) | internal layer manifest, not standalone workspace project |

## Consistency Checks
- registry project slugs match `workspace_config/workspace_manifest.json` and corresponding `PROJECT_MANIFEST.json`
- registry project paths exist physically under `projects/`
- active project slug is unique: `tiktok_agent_platform`
- non-registry paths are explicitly classified in `workspace_config/workspace_manifest.json`
- layer manifests are explicitly classified in `workspace_config/workspace_manifest.json`
