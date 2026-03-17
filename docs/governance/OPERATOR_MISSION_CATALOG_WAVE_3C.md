# OPERATOR_MISSION_CATALOG_WAVE_3C

## Scope
Guarded creator missions and controlled state-change mission flows under strict authority/policy/audit gates.

## Mission Classes
- `guarded_creator_mission`
  - mission: `mission.wave3c.guarded_creator_maintenance.v1`
  - programs: `program.wave2c.guarded_governance_maintenance.v1`, `program.wave2c.control_artifacts_rebuild.v1`
- `creator_only_mission`
  - mission: `mission.wave3c.creator_only_acceptance_sequence.v1`
  - programs: `program.wave2c.creator_authorized_sequence.v1`, `program.wave2c.authority_required_program.v1`
- `controlled_state_change_mission`
  - mission: `mission.wave3c.controlled_state_change_cycle.v1`
  - programs: `program.wave2c.controlled_install_lifecycle.v1`, `program.wave2c.controlled_remove_lifecycle.v1`
- `blocked_mission_test_mission`
  - mission: `mission.wave3c.blocked_mission_certification.v1`
  - programs: `program.wave2c.blocked_missing_preconditions.v1`, `program.wave2c.blocked_policy_mutation.v1`

## Wave 3C Controls
- creator authority required for guarded/state-changing classes
- blocked mission class certifies denial paths as expected outcomes
- rollback requirement explicit for guarded mutation failures
- no silent downgrade from guarded mission into safe mission
