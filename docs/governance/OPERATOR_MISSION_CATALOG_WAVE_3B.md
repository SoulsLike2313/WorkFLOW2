# OPERATOR_MISSION_CATALOG_WAVE_3B

## Scope
Controlled multi-program operational missions for packaging/review/readiness transitions.

## Mission Classes
- `multi_program_operational_mission`
  - mission: `mission.wave3b.operational_delivery_cycle.v1`
  - programs: `program.wave2b.handoff_preparation_end_to_end.v1`, `program.wave2b.inbox_review_cycle.v1`
- `packaging_review_transition_mission`
  - mission: `mission.wave3b.packaging_review_transition.v1`
  - programs: `program.wave2b.delivery_ready_handoff_package.v1`, `program.wave2b.evidence_delivery_chain.v1`
- `evidence_aggregation_mission`
  - mission: `mission.wave3b.evidence_aggregation_cycle.v1`
  - programs: `program.wave2a.governance_evidence_pack.v1`, `program.wave2b.evidence_delivery_chain.v1`, `program.wave2a.status_evidence_report.v1`
- `readiness_transition_mission`
  - mission: `mission.wave3b.readiness_transition_cycle.v1`
  - programs: `program.wave2b.certification_pass.v1`, `program.wave2b.review_certification_sequence.v1`

## Wave 3B Controls
- required inputs enforced (`task_id`, `node_id`) where declared
- failure/resume model remains deterministic
- no unrestricted mutation paths
