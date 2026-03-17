# OPERATOR_PROGRAM_INTENT_ROUTING

## Purpose
Define deterministic mapping from operator task/program requests to program class and program id.

## Routing Precedence
1. `creator_guarded_program`
2. `operational_handoff_review_program`
3. `operational_task_routing_program`
4. `safe_read_validate_report_program`

## Request Class Mapping

| program_class | program_id(s) | example request patterns | authority boundary |
| --- | --- | --- | --- |
| `safe_read_validate_report_program` | `program.safe_status_validation_report.v1`, `program.safe_evidence_bundle.v1`, `program.safe_policy_reference.v1` | status validation report, evidence bundle program, policy reference program | all modes |
| `operational_handoff_review_program` | `program.task_handoff_review_packaging.v1`, `program.integration_inbox_triage.v1` | task handoff review packaging, integration inbox triage | creator/helper/integration (program-specific constraints apply) |
| `operational_task_routing_program` | `program.deterministic_task_route.v1` | deterministic task route, resolve task program | all modes |
| `creator_guarded_program` | `program.creator_guarded_refresh_precheck.v1`, `program.creator_install_remove_cycle.v1` | creator guarded refresh precheck, creator install remove cycle | creator only |

## Determinism Constraints
- Explicit `--program-id` override has highest priority.
- Explicit `--program-class` resolves first matching program for class.
- Exact `program_id` token overrides pattern routing.
- Fallback program is `program.safe_status_validation_report.v1`.

## Routing Output Contract
Every classification result must include:
- `request_text`
- `program_class`
- `program_id`
- `route_basis`
- `resolved_goal`
- `wave`
