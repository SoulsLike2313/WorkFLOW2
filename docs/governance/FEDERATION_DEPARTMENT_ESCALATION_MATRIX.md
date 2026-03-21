# FEDERATION_DEPARTMENT_ESCALATION_MATRIX

Status:
- matrix_version: `v2-single-department`
- scope: `federation department escalation discipline (current stage)`
- non_goal: `no speculative multi-department ownership map`

## Global Rules

1. Federation is an assembly/development block only and is not sovereign authority.
2. Sovereign signoff is required for canonical acceptance and sovereign claim classes.
3. Primarch layer may direct bounded operational execution but cannot issue sovereign claims.
4. Astartes layer is execution-constrained and cannot self-elevate command authority.
5. Current department model is single-department (`Analytics Department`).

## Current Department Escalation Matrix

| department | implementation | current_status | oversight_layer | execution_layer | escalation_path | sovereign_signoff_boundary | primarch_handling_boundary | astartes_handling_boundary | confidence |
|---|---|---|---|---|---|---|---|---|---|
| `Analytics Department` | `platform_test_agent` | `active` | `PRIMARCH (operational oversight)` | `ASTARTES/helper execution + creator-grade maintainers` | `ASTARTES -> PRIMARCH -> EMPEROR (if sovereign claim needed)` | `canonical acceptance, sovereign policy change, unrestricted structural mutation` | `audit orchestration, bounded intake triage, non-sovereign corrective direction` | `task-scoped audit execution and evidence reporting` | `OBSERVED` |

## Non-Department Operational Lines (Escalation Routing)

These lines are intake/analysis subjects in current stage, not departments:

| line | status | operational_classification | routing model |
|---|---|---|
| `tiktok_agent_platform` | `manual_testing_blocked` | `test_product + intake_subject + analysis_candidate` | `route through Analytics Department intake/audit path` |
| `game_ru_ai` | `audit_required` | `test_product + intake_subject + analysis_candidate` | `route through Analytics Department intake/audit path` |
| `voice_launcher` | `supporting` | `test_product + intake_subject + analysis_candidate` | `route through Analytics Department intake/audit path when required` |
| `adaptive_trading` | `experimental` | `test_product + intake_subject + analysis_candidate` | `route through Analytics Department intake/audit path when required` |

## Not Current Operational Entities

1. `shortform_core` - historical residue only.
2. `tiktok_automation_app` - migration trace only.
3. `wild_hunt_command_citadel` - container path, not a department.

## Not Yet Formalized

1. Permanent owner/guardian identity by individual operator.
2. Machine-readable mandate linkage between named operators and the department.
3. Department-specific sovereign signoff exception list.

These remain intentionally open until explicit canonical doctrine is provided.

## Hardening Anchors

1. Guardian/ownership registry: `workspace_config/department_guardian_registry.json`.
2. Exception/escalation policy: `docs/governance/DEPARTMENT_EXCEPTION_ESCALATION_HARDENING_V1.md`.
3. Exception/escalation contract: `workspace_config/department_exception_escalation_contract.json`.
