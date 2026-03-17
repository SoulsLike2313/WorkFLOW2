# OPERATOR_MISSION_REGISTRY

Operator-facing registry snapshot synchronized with `workspace_config/operator_mission_registry.json`.

## Registry Meta
- schema_version: `operator_mission_registry.final.v1.0.0`
- class_count: `12`
- mission_count: `12`

## Classes and Missions

### `status_refresh_mission`
- mission: `mission.wave3a.status_refresh_certification.v1`
- mutability_level: `READ_ONLY`
- authority_requirement: `none`

### `validation_mission`
- mission: `mission.wave3a.creator_readiness_validation.v1`
- mutability_level: `READ_ONLY`
- authority_requirement: `creator_required`

### `evidence_pack_mission`
- mission: `mission.wave3a.evidence_review_pack.v1`
- mutability_level: `PACKAGE_ONLY`
- authority_requirement: `creator_required`

### `report_mission`
- mission: `mission.wave3a.operator_report_compilation.v1`
- mutability_level: `READ_ONLY`
- authority_requirement: `none`

### `multi_program_operational_mission`
- mission: `mission.wave3b.operational_delivery_cycle.v1`
- mutability_level: `OPERATIONAL_ROUTING`
- authority_requirement: `none`

### `packaging_review_transition_mission`
- mission: `mission.wave3b.packaging_review_transition.v1`
- mutability_level: `OPERATIONAL_ROUTING`
- authority_requirement: `none`

### `evidence_aggregation_mission`
- mission: `mission.wave3b.evidence_aggregation_cycle.v1`
- mutability_level: `OPERATIONAL_ROUTING`
- authority_requirement: `none`

### `readiness_transition_mission`
- mission: `mission.wave3b.readiness_transition_cycle.v1`
- mutability_level: `OPERATIONAL_ROUTING`
- authority_requirement: `creator_required`

### `guarded_creator_mission`
- mission: `mission.wave3c.guarded_creator_maintenance.v1`
- mutability_level: `GUARDED_STATE_CHANGE`
- authority_requirement: `creator_required`

### `creator_only_mission`
- mission: `mission.wave3c.creator_only_acceptance_sequence.v1`
- mutability_level: `CREATOR_ONLY_MUTATION`
- authority_requirement: `creator_required`

### `controlled_state_change_mission`
- mission: `mission.wave3c.controlled_state_change_cycle.v1`
- mutability_level: `GUARDED_STATE_CHANGE`
- authority_requirement: `creator_required`

### `blocked_mission_test_mission`
- mission: `mission.wave3c.blocked_mission_certification.v1`
- mutability_level: `READ_ONLY`
- authority_requirement: `none`
