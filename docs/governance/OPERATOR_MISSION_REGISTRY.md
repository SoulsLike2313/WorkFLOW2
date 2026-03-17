# OPERATOR_MISSION_REGISTRY

Operator-facing registry snapshot synchronized with `workspace_config/operator_mission_registry.json`.

## Registry Meta
- schema_version: `operator_mission_registry.wave3c.v1.0.0`
- wave: `3C`
- class_count: `12`
- mission_count: `15`
- canonical_registry: `workspace_config/operator_mission_registry.json`

## Classes and Missions

### `certification_mission`
- missions:
  - `mission.wave3a.certification.baseline.v1`
- mutability_level: `CREATOR_ONLY_TRANSITION`
- authority_requirement: `creator_required`

### `readiness_mission`
- missions:
  - `mission.wave3a.readiness.next_stage.v1`
- mutability_level: `CREATOR_ONLY_TRANSITION`
- authority_requirement: `creator_required`

### `review_prep_mission`
- missions:
  - `mission.wave3a.review_prep.package.v1`
- mutability_level: `PACKAGE_ONLY`
- authority_requirement: `none`

### `status_consolidation_mission`
- missions:
  - `mission.wave3a.status_consolidation.complete.v1`
- mutability_level: `REFRESH_ONLY`
- authority_requirement: `none`

### `external_review_mission`
- missions:
  - `mission.wave3b.external_review.prep.v1`
- mutability_level: `REVIEW_DELIVERY`
- authority_requirement: `none`

### `readiness_transition_mission`
- missions:
  - `mission.wave3b.readiness_transition.next_stage.v1`
- mutability_level: `CREATOR_ONLY_TRANSITION`
- authority_requirement: `creator_required`

### `handoff_delivery_mission`
- missions:
  - `mission.wave3b.handoff_delivery.sequence.v1`
- mutability_level: `REVIEW_DELIVERY`
- authority_requirement: `none`

### `evidence_consolidation_mission`
- missions:
  - `mission.wave3b.evidence_consolidation.chain.v1`
- mutability_level: `PACKAGE_ONLY`
- authority_requirement: `none`

### `guarded_baseline_transition_mission`
- missions:
  - `mission.wave3c.guarded_baseline_transition.v1`
- mutability_level: `GUARDED_STATE_CHANGE`
- authority_requirement: `creator_required`

### `creator_only_certification_mission`
- missions:
  - `mission.wave3c.creator_only_certification.v1`
- mutability_level: `CREATOR_ONLY_TRANSITION`
- authority_requirement: `creator_required`

### `controlled_upgrade_mission`
- missions:
  - `mission.wave3c.controlled_upgrade.allowed.v1`
  - `mission.wave3c.controlled_upgrade.policy_blocked.v1`
- mutability_level: `GUARDED_STATE_CHANGE`
- authority_requirement: `creator_required`

### `blocked_mutation_mission`
- missions:
  - `mission.wave3c.blocked_mutation.creator_gate.v1`
  - `mission.wave3c.blocked_mutation.missing_preconditions.v1`
  - `mission.wave3c.blocked_mutation.policy.v1`
- mutability_level: `READ_ONLY`
- authority_requirement: `none`
