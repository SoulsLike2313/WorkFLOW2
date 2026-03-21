# PROJECT PATH STATUS MATRIX

Status:
- matrix_version: `v2-current-truth`
- surface_class: `secondary_review_artifact`
- canonical_source: `workspace_config/workspace_manifest.json`
- canonical_operational_model_anchor: `docs/governance/FEDERATION_OPERATIONAL_MODEL.md`

| slug | path | physical_exists | registry_class | status | priority | operational_framing | notes |
|---|---|---|---|---|---|---|---|
| platform_test_agent | projects/platform_test_agent | yes | registry_project | active | 1 | current implementation of `Analytics Department` | canonical active workspace project |
| tiktok_agent_platform | projects/wild_hunt_command_citadel/tiktok_agent_platform | yes | registry_project | manual_testing_blocked | 4 | `test_product` + `intake_subject` + `analysis_candidate` | non-department line in current stage |
| voice_launcher | projects/voice_launcher | yes | registry_project | supporting | 2 | `test_product` + `intake_subject` + `analysis_candidate` | non-department line in current stage |
| adaptive_trading | projects/adaptive_trading | yes | registry_project | experimental | 3 | `test_product` + `intake_subject` + `analysis_candidate` | non-department line in current stage |
| game_ru_ai | projects/GameRuAI | yes | registry_project | audit_required | 5 | `test_product` + `intake_subject` + `analysis_candidate` | non-department line in current stage |
| wild_hunt_command_citadel_container | projects/wild_hunt_command_citadel | yes | non_registry_path | n/a | n/a | historical/container path | project group container, excluded from workspace registry |
| shortform_core_legacy_path | projects/wild_hunt_command_citadel/shortform_core | yes | non_registry_path | n/a | n/a | historical trace | local legacy residue, excluded from workspace registry |
| tiktok_agent_core_layer | projects/wild_hunt_command_citadel/tiktok_agent_platform/core/PROJECT_MANIFEST.json | yes | layer_manifest | supporting (layer-local) | 1 (layer-local) | internal layer | not standalone workspace project |
| tiktok_agent_app_layer | projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/PROJECT_MANIFEST.json | yes | layer_manifest | supporting (layer-local) | 2 (layer-local) | internal layer | not standalone workspace project |

## Consistency Checks
- registry project slugs match `workspace_config/workspace_manifest.json` and corresponding `PROJECT_MANIFEST.json`
- registry project paths exist physically under `projects/`
- active project slug is unique: `platform_test_agent`
- non-registry paths are explicitly classified in `workspace_config/workspace_manifest.json`
- layer manifests are explicitly classified in `workspace_config/workspace_manifest.json`
- this matrix is secondary evidence; canonical truth remains `workspace_config/workspace_manifest.json`
