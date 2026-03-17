# OPERATOR_TASK_PROGRAM_SCENARIO_PACK

## Scope
Operator-grade deterministic scenarios for Task/Program Layer final certification.

## Scenarios

### 1) Refresh -> Validate -> Evidence -> Report
- scenario_name: `status_validation_evidence_report_chain`
- sequence:
  - query: status request
  - command: `status_refresh_command`
  - program: `program.wave2a.full_status_reconstruction.v1`
- expected checkpoints:
  - `status_refresh` -> `validation_run` -> `status_refresh`
- expected outputs:
  - `operator_program_status.json`
  - `operator_program_report.md`
- expected blocking behavior: blocked on sync/authority only when policy requires it.
- evidence chain: runtime status + report + consistency output.

### 2) Creator validation pass
- scenario_name: `creator_grade_validation_sequence`
- sequence: `program.wave2a.creator_grade_validation.v1`
- expected checkpoints: `creator_acceptance_precheck` -> `validation_run`
- expected outputs: repo control status/report + program report
- blocking: creator gate denial if authority absent.
- evidence chain: creator detect output + full-check output.

### 3) Governance evidence package
- scenario_name: `governance_evidence_pack`
- sequence: `program.wave2a.governance_evidence_pack.v1`
- checkpoints: validation -> status refresh -> bundle -> report
- outputs: bundle artifact + operator program report
- blocking: exporter failures.
- evidence: bundle output + program report.

### 4) Creator proof package
- scenario_name: `creator_proof_pack`
- sequence: `program.wave2a.creator_proof_pack.v1`
- checkpoints: creator precheck -> validation -> evidence bundle -> report
- outputs: creator-proof bundle + runtime traces
- blocking: creator authority missing.

### 5) Handoff preparation end-to-end
- scenario_name: `handoff_preparation_e2e`
- sequence: `program.wave2b.handoff_preparation_end_to_end.v1`
- checkpoints: validation -> evidence bundle -> handoff prepare -> report
- outputs: handoff metadata + report
- blocking: required input absence (`task_id`,`node_id`).

### 6) Delivery-ready handoff package
- scenario_name: `delivery_ready_handoff`
- sequence: `program.wave2b.delivery_ready_handoff_package.v1`
- checkpoints: validation -> policy reference -> handoff -> report
- outputs: delivery package + policy trace
- blocking: policy reference failure.

### 7) Inbox review cycle
- scenario_name: `inbox_review_cycle`
- sequence: `program.wave2b.inbox_review_cycle.v1`
- checkpoints: inbox review -> policy reference -> report
- outputs: inbox review result + report
- blocking: mode/policy restrictions.

### 8) Evidence delivery chain
- scenario_name: `evidence_delivery_chain`
- sequence: `program.wave2b.evidence_delivery_chain.v1`
- checkpoints: refresh -> validation -> routing -> report
- outputs: routed evidence + report
- blocking: routing target unavailable.

### 9) Certification pass (creator)
- scenario_name: `creator_certification_pass`
- sequence: `program.wave2b.certification_pass.v1`
- checkpoints: creator precheck -> validation -> policy reference -> report
- outputs: certification report + evidence
- blocking: creator gate or sync precondition.

### 10) Review certification sequence
- scenario_name: `review_certification_sequence`
- sequence: `program.wave2b.review_certification_sequence.v1`
- checkpoints: validation -> inbox review -> policy reference -> report
- outputs: review certification report
- blocking: inbox/policy review blockers.

### 11) Guarded governance maintenance (allowed)
- scenario_name: `guarded_maintenance_allowed`
- sequence: `program.wave2c.guarded_governance_maintenance.v1`
- checkpoints: creator precheck -> maintenance -> safe mirror evidence refresh -> report
- outputs: audit trail + refreshed safe mirror evidence
- blocking: sync or creator preconditions.

### 12) Control artifacts rebuild
- scenario_name: `control_artifacts_rebuild`
- sequence: `program.wave2c.control_artifacts_rebuild.v1`
- checkpoints: creator precheck -> evidence refresh -> policy reference -> report
- outputs: manifest/report refresh + audit trail
- blocking: policy basis failure.

### 13) Creator-only sequence blocked in helper mode
- scenario_name: `creator_only_blocked_helper`
- sequence: `program.wave2c.creator_authorized_sequence.v1` with helper intent
- checkpoints: blocked before step execution
- outputs: blocked execution payload
- blocking: creator gate enforcement
- evidence: `wave2c_blocked_program_execute_output.json`.

### 14) Blocked mutation by missing preconditions
- scenario_name: `blocked_missing_preconditions`
- sequence: `program.wave2c.blocked_missing_preconditions.v1`
- checkpoints: blocked at gate
- outputs: blocked precondition report
- blocking: required input contract violation.

### 15) Blocked mutation by policy basis
- scenario_name: `blocked_policy_mutation`
- sequence: `program.wave2c.blocked_policy_mutation.v1`
- checkpoints: blocked at policy check
- outputs: missing policy basis blocker evidence
- blocking: explicit policy gate denial.

### 16) Controlled lifecycle install
- scenario_name: `controlled_lifecycle_install`
- sequence: `program.wave2c.controlled_install_lifecycle.v1`
- checkpoints: creator precheck -> maintenance -> report
- outputs: lifecycle report + audit trail
- blocking: creator/policy/precondition gates.
