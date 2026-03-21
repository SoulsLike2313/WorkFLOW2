# OPERATOR_TASK_PROGRAM_CATALOG_WAVE_2C

## Scope
Wave 2C introduces guarded creator-grade programs with controlled state change under explicit authority/policy/audit gates.

## Program Classes

### guarded_maintenance_program
- Purpose: execute guarded governance maintenance and control artifact refresh sequences.
- Mutability: `GUARDED_STATE_CHANGE`.
- Authority: creator-required.
- Command classes used:
  - `creator_only_execution_command`
  - `governance_maintenance_command`
  - `report_generation_command`
- Checkpoints: authority precheck -> maintenance/action -> evidence/report finalization.
- Blocking conditions:
  - creator authority missing
  - policy basis missing
  - sync/clean precondition failures

Programs:
- `program.wave2c.guarded_governance_maintenance.v1`
- `program.wave2c.control_artifacts_rebuild.v1`

### creator_only_program
- Purpose: execute creator-authorized governance sequences that are forbidden for helper authority and integration posture.
- Mutability: `CREATOR_ONLY_MUTATION`.
- Authority: creator-required (strict).
- Command classes used:
  - `creator_only_execution_command`
  - `governance_maintenance_command`
  - `report_generation_command`
- Blocking conditions:
  - machine mode not `creator`
  - creator authority not present
  - failed creator precheck

Programs:
- `program.wave2c.creator_authorized_sequence.v1`
- `program.wave2c.authority_required_program.v1`

### controlled_lifecycle_program
- Purpose: run policy-governed controlled install/remove lifecycle flows.
- Mutability: `GUARDED_STATE_CHANGE`.
- Authority: creator-required.
- Command classes used:
  - `creator_only_execution_command`
  - `governance_maintenance_command`
  - `report_generation_command`
- Blocking conditions:
  - creator gate failure
  - policy gate failure
  - lifecycle command failure

Programs:
- `program.wave2c.controlled_install_lifecycle.v1`
- `program.wave2c.controlled_remove_lifecycle.v1`

### blocked_mutation_test_program
- Purpose: deterministic blocked-path verification for creator gate, precondition gate, and policy gate.
- Mutability: `GUARDED_STATE_CHANGE` / `CREATOR_ONLY_MUTATION` (test-only blocked coverage).
- Authority: mixed by case; designed to prove denial behavior.
- Command classes used:
  - `creator_only_execution_command`
  - `report_generation_command`
- Blocking conditions: intentionally triggered and must remain deterministic.

Programs:
- `program.wave2c.blocked_creator_gate_simulation.v1`
- `program.wave2c.blocked_missing_preconditions.v1`
- `program.wave2c.blocked_policy_mutation.v1`

## Wave 2C Safety Notes
- risky request fallback into safe programs is forbidden.
- guarded mutation requires explicit mutability + authority gates.
- stop/rollback/audit trail fields are mandatory in runtime program payloads.
