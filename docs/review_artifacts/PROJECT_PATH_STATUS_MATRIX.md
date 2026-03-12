# PROJECT PATH STATUS MATRIX

## Canonical Workspace Projects

| slug | name | status | registry_root_path | manifest_path | readme_path | runtime_namespace | registry_vs_manifest_status | registry_vs_tree_path |
|---|---|---|---|---|---|---|---|---|
| tiktok_agent_platform | TikTok Agent Platform | active | projects/wild_hunt_command_citadel/tiktok_agent_platform | projects/wild_hunt_command_citadel/tiktok_agent_platform/PROJECT_MANIFEST.json | projects/wild_hunt_command_citadel/tiktok_agent_platform/README.md | tiktok_agent_platform | MATCH | EXISTS |
| voice_launcher | Voice Launcher | supporting | projects/voice_launcher | projects/voice_launcher/PROJECT_MANIFEST.json | projects/voice_launcher/README.md | voice_launcher | MATCH | EXISTS |
| adaptive_trading | Adaptive Trading | experimental | projects/adaptive_trading | projects/adaptive_trading/PROJECT_MANIFEST.json | projects/adaptive_trading/README.md | adaptive_trading | MATCH | EXISTS |
| game_ru_ai | GameRuAI | experimental | projects/GameRuAI | projects/GameRuAI/PROJECT_MANIFEST.json | projects/GameRuAI/README.md | game_ru_ai | MATCH | EXISTS |

## Non-Registry Paths (Explicitly Classified)

| path | classification | registry_visibility | owner | status_mapping |
|---|---|---|---|---|
| projects/wild_hunt_command_citadel/shortform_core | legacy_internal_layer | excluded_from_project_registry | tiktok_agent_platform | NOT_A_WORKSPACE_PROJECT |

## Layer Manifests Inside Active Project

| manifest_path | slug | role | workspace_registry_membership |
|---|---|---|---|
| projects/wild_hunt_command_citadel/tiktok_agent_platform/core/PROJECT_MANIFEST.json | tiktok_agent_core_layer | active project core layer manifest | EXCLUDED_BY_DESIGN |
| projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/PROJECT_MANIFEST.json | tiktok_agent_app_layer | active project app layer manifest | EXCLUDED_BY_DESIGN |

## Effective Canonical Status Mapping

- active: tiktok_agent_platform
- supporting: voice_launcher
- experimental: adaptive_trading, game_ru_ai
- archived: none
- legacy: none
