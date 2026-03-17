# OPERATOR_MISSION_CATALOG_WAVE_3A

## Scope
Safe mission foundation: certification/readiness/review/report missions with no uncontrolled mutation surface.

## Mission Classes
- `status_refresh_mission`
  - mission: `mission.wave3a.status_refresh_certification.v1`
  - programs: `program.wave2a.status_refresh_surface.v1`, `program.wave2a.full_status_reconstruction.v1`
- `validation_mission`
  - mission: `mission.wave3a.creator_readiness_validation.v1`
  - programs: `program.wave2a.creator_grade_validation.v1`, `program.wave2a.governance_chain_validation.v1`
- `evidence_pack_mission`
  - mission: `mission.wave3a.evidence_review_pack.v1`
  - programs: `program.wave2a.governance_evidence_pack.v1`, `program.wave2a.creator_proof_pack.v1`
- `report_mission`
  - mission: `mission.wave3a.operator_report_compilation.v1`
  - programs: `program.wave2a.operator_engineering_report.v1`, `program.wave2a.status_evidence_report.v1`

## Wave 3A Controls
- read/package-safe scope only
- no guarded mutation mission classes
- deterministic mission checkpoint/resume by program index
