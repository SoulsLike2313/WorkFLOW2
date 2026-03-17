# OPERATOR_COMMAND_INTENT_ROUTING

## Purpose
Define deterministic mapping from operator command text to execution class and action.

## Routing Precedence
1. `install_remove_controlled_command`
2. `creator_only_execution_command`
3. `guarded_state_change_command`
4. `governance_maintenance_command`
5. `handoff_command`
6. `inbox_review_command`
7. `evidence_routing_command`
8. `policy_reference_command`
9. `validation_command`
10. `evidence_bundle_command`
11. `report_generation_command`
12. `status_refresh_command` (fallback)

## Class Mapping

| command_class | resolved_action(s) | Example command patterns | authority boundary |
| --- | --- | --- | --- |
| `status_refresh_command` | `status_refresh` | status refresh, refresh status | all modes |
| `validation_command` | `validation_run` | run validation, validation sweep | all modes |
| `evidence_bundle_command` | `evidence_bundle_context` | build evidence bundle, export context bundle | all modes |
| `report_generation_command` | `report_generation` | generate execution report | all modes |
| `handoff_command` | `handoff_prepare` | prepare handoff, handoff package | all modes |
| `inbox_review_command` | `inbox_review` | inbox review, review integration inbox | creator/integration |
| `evidence_routing_command` | `evidence_routing` | route evidence | creator/integration |
| `policy_reference_command` | `policy_reference_execute` | policy lookup, policy reference | all modes |
| `guarded_state_change_command` | `refresh_safe_mirror_evidence` | refresh safe mirror evidence | creator only |
| `creator_only_execution_command` | `creator_acceptance_precheck` | creator precheck | creator only |
| `governance_maintenance_command` | `governance_maintenance_check` | governance maintenance check | creator/integration |
| `install_remove_controlled_command` | `install_system`, `remove_system` | install system, remove system | creator only |

## Determinism Constraints
- One command resolves to one dominant action.
- Explicit `--action` override has highest priority.
- Explicit `--command-class` override resolves first matching action for class.
- Direct action token (exact action string) overrides pattern routing.
- No semantic free-form fallback beyond defined precedence.

## Fallback
If no tokens match, route to:
- `status_refresh_command`
- `resolved_action = status_refresh`
