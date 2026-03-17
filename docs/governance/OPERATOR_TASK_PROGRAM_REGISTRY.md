# OPERATOR_TASK_PROGRAM_REGISTRY

Operator-facing registry snapshot synchronized with `workspace_config/operator_task_program_registry.json`.

## Registry Meta
- schema_version: `operator_task_program_registry.wave2c.v1.0.0`
- wave: `2C`
- class_count: `12`
- program_count: `23`

## Classes and Programs

### `status_refresh_program`
- authority_requirement: `none`
- mutability_level: `REFRESH_ONLY`
- routing_basis: `class_precedence + keyword matching + deterministic registry lookup`
- checkpoint_model: `runtime/repo_control_center/operator_program_checkpoint.json`
- evidence_outputs: `runtime/repo_control_center/plain_status.md, runtime/repo_control_center/one_screen_status.json, runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md`
- blocking_logic: `authority_mode_not_allowed, policy_basis_missing, invalid_resume_pointer, step_execution_failed`
- program: `program.wave2a.status_refresh_surface.v1`
  - authority_requirement: `none`
  - mutability_level: `REFRESH_ONLY`
  - command_dependencies: `status_refresh, report_generation, validation_run`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/plain_status.md, runtime/repo_control_center/one_screen_status.json, runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md`
  - blocking_logic: `step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`
- program: `program.wave2a.full_status_reconstruction.v1`
  - authority_requirement: `none`
  - mutability_level: `REFRESH_ONLY`
  - command_dependencies: `status_refresh, report_generation, validation_run`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/plain_status.md, runtime/repo_control_center/one_screen_status.json, runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md`
  - blocking_logic: `step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`

### `validation_program`
- authority_requirement: `program_specific`
- mutability_level: `READ_ONLY`
- routing_basis: `class_precedence + keyword matching + deterministic registry lookup`
- checkpoint_model: `runtime/repo_control_center/operator_program_checkpoint.json`
- evidence_outputs: `runtime/repo_control_center/repo_control_status.json, runtime/repo_control_center/repo_control_report.md, runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md`
- blocking_logic: `creator_authority_required, authority_mode_not_allowed, policy_basis_missing, step_execution_failed`
- program: `program.wave2a.creator_grade_validation.v1`
  - authority_requirement: `creator_required`
  - mutability_level: `READ_ONLY`
  - command_dependencies: `validation_run, creator_acceptance_precheck, policy_reference_execute`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/repo_control_status.json, runtime/repo_control_center/repo_control_report.md, runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md`
  - blocking_logic: `creator_authority_required, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`
- program: `program.wave2a.governance_chain_validation.v1`
  - authority_requirement: `none`
  - mutability_level: `READ_ONLY`
  - command_dependencies: `validation_run, creator_acceptance_precheck, policy_reference_execute`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/operator_command_layer/policy_reference_output.md, runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md`
  - blocking_logic: `step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`

### `evidence_pack_program`
- authority_requirement: `program_specific`
- mutability_level: `PACKAGE_ONLY`
- routing_basis: `class_precedence + keyword matching + deterministic registry lookup`
- checkpoint_model: `runtime/repo_control_center/operator_program_checkpoint.json`
- evidence_outputs: `runtime/chatgpt_bundle_exports, runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md`
- blocking_logic: `creator_authority_required, policy_basis_missing, step_execution_failed`
- program: `program.wave2a.governance_evidence_pack.v1`
  - authority_requirement: `none`
  - mutability_level: `PACKAGE_ONLY`
  - command_dependencies: `evidence_bundle_context, status_refresh, creator_acceptance_precheck, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/chatgpt_bundle_exports, runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md`
  - blocking_logic: `step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`
- program: `program.wave2a.creator_proof_pack.v1`
  - authority_requirement: `creator_required`
  - mutability_level: `PACKAGE_ONLY`
  - command_dependencies: `evidence_bundle_context, status_refresh, creator_acceptance_precheck, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/chatgpt_bundle_exports, runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md`
  - blocking_logic: `creator_authority_required, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`

### `report_program`
- authority_requirement: `none`
- mutability_level: `READ_ONLY`
- routing_basis: `class_precedence + keyword matching + deterministic registry lookup`
- checkpoint_model: `runtime/repo_control_center/operator_program_checkpoint.json`
- evidence_outputs: `runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_status.json`
- blocking_logic: `policy_basis_missing, step_execution_failed`
- program: `program.wave2a.operator_engineering_report.v1`
  - authority_requirement: `none`
  - mutability_level: `READ_ONLY`
  - command_dependencies: `status_refresh, report_generation, policy_reference_execute, validation_run`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_status.json`
  - blocking_logic: `step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`
- program: `program.wave2a.status_evidence_report.v1`
  - authority_requirement: `none`
  - mutability_level: `READ_ONLY`
  - command_dependencies: `status_refresh, report_generation, policy_reference_execute, validation_run`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_status.json, runtime/operator_command_layer/policy_reference_output.md`
  - blocking_logic: `step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`

### `handoff_preparation_program`
- authority_requirement: `none`
- mutability_level: `PACKAGE_ONLY`
- routing_basis: `class_precedence + keyword matching + deterministic registry lookup`
- checkpoint_model: `runtime/repo_control_center/operator_program_checkpoint.json`
- evidence_outputs: `runtime/operator_command_layer/handoff_prepare_output.json, runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json`
- blocking_logic: `required_input_missing, step_execution_failed, delivery_target_unavailable`
- program: `program.wave2b.handoff_preparation_end_to_end.v1`
  - authority_requirement: `none`
  - mutability_level: `PACKAGE_ONLY`
  - command_dependencies: `validation_run, evidence_bundle_context, handoff_prepare, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/operator_command_layer/handoff_prepare_output.json, runtime/repo_control_center/operator_program_report.md`
  - blocking_logic: `required_input_missing, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`
- program: `program.wave2b.delivery_ready_handoff_package.v1`
  - authority_requirement: `none`
  - mutability_level: `PACKAGE_ONLY`
  - command_dependencies: `validation_run, evidence_bundle_context, handoff_prepare, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/operator_command_layer/handoff_prepare_output.json, runtime/repo_control_center/operator_program_report.md`
  - blocking_logic: `required_input_missing, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`

### `inbox_review_program`
- authority_requirement: `none`
- mutability_level: `READ_ONLY`
- routing_basis: `class_precedence + keyword matching + deterministic registry lookup`
- checkpoint_model: `runtime/repo_control_center/operator_program_checkpoint.json`
- evidence_outputs: `runtime/operator_command_layer/inbox_review_output.json, runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json`
- blocking_logic: `authority_mode_not_allowed, step_execution_failed, review_dependency_missing`
- program: `program.wave2b.inbox_review_cycle.v1`
  - authority_requirement: `none`
  - mutability_level: `READ_ONLY`
  - command_dependencies: `inbox_review, report_generation, policy_reference_execute`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/operator_command_layer/inbox_review_output.json, runtime/repo_control_center/operator_program_report.md`
  - blocking_logic: `authority_mode_not_allowed, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`

### `evidence_delivery_program`
- authority_requirement: `none`
- mutability_level: `PACKAGE_ONLY`
- routing_basis: `class_precedence + keyword matching + deterministic registry lookup`
- checkpoint_model: `runtime/repo_control_center/operator_program_checkpoint.json`
- evidence_outputs: `runtime/operator_command_layer/evidence_routing_output.json, runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json`
- blocking_logic: `step_execution_failed, delivery_target_unavailable`
- program: `program.wave2b.evidence_delivery_chain.v1`
  - authority_requirement: `none`
  - mutability_level: `PACKAGE_ONLY`
  - command_dependencies: `status_refresh, validation_run, evidence_routing, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/operator_command_layer/evidence_routing_output.json, runtime/repo_control_center/operator_program_report.md`
  - blocking_logic: `step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`

### `certification_program`
- authority_requirement: `program_specific`
- mutability_level: `READ_ONLY`
- routing_basis: `class_precedence + keyword matching + deterministic registry lookup`
- checkpoint_model: `runtime/repo_control_center/operator_program_checkpoint.json`
- evidence_outputs: `runtime/repo_control_center/repo_control_status.json, runtime/repo_control_center/repo_control_report.md, runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json`
- blocking_logic: `creator_authority_required, policy_basis_missing, step_execution_failed`
- program: `program.wave2b.certification_pass.v1`
  - authority_requirement: `creator_required`
  - mutability_level: `READ_ONLY`
  - command_dependencies: `creator_acceptance_precheck, validation_run, inbox_review, policy_reference_execute, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/repo_control_status.json, runtime/repo_control_center/operator_program_report.md`
  - blocking_logic: `creator_authority_required, step_execution_failed, sync_not_in_sync`
  - final_outputs: `execution_result + artifacts_produced + next_step`
- program: `program.wave2b.review_certification_sequence.v1`
  - authority_requirement: `none`
  - mutability_level: `READ_ONLY`
  - command_dependencies: `creator_acceptance_precheck, validation_run, inbox_review, policy_reference_execute, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/operator_command_layer/inbox_review_output.json, runtime/repo_control_center/operator_program_report.md`
  - blocking_logic: `authority_mode_not_allowed, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`

### `guarded_maintenance_program`
- authority_requirement: `creator_required`
- mutability_level: `GUARDED_STATE_CHANGE`
- routing_basis: `class_precedence + keyword matching + deterministic registry lookup`
- checkpoint_model: `runtime/repo_control_center/operator_program_checkpoint.json`
- evidence_outputs: `runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json, runtime/repo_control_center/operator_program_audit_trail.json`
- blocking_logic: `creator_authority_required, policy_basis_missing, step_execution_failed`
- program: `program.wave2c.guarded_governance_maintenance.v1`
  - authority_requirement: `creator_required`
  - mutability_level: `GUARDED_STATE_CHANGE`
  - command_dependencies: `creator_acceptance_precheck, governance_maintenance_check, refresh_safe_mirror_evidence, report_generation, policy_reference_execute`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json, runtime/repo_control_center/operator_program_audit_trail.json`
  - blocking_logic: `creator_authority_required, policy_basis_missing, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`
- program: `program.wave2c.control_artifacts_rebuild.v1`
  - authority_requirement: `creator_required`
  - mutability_level: `GUARDED_STATE_CHANGE`
  - command_dependencies: `creator_acceptance_precheck, governance_maintenance_check, refresh_safe_mirror_evidence, report_generation, policy_reference_execute`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json, runtime/repo_control_center/operator_program_audit_trail.json`
  - blocking_logic: `creator_authority_required, policy_basis_missing, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`

### `creator_only_program`
- authority_requirement: `creator_required`
- mutability_level: `CREATOR_ONLY_MUTATION`
- routing_basis: `class_precedence + keyword matching + deterministic registry lookup`
- checkpoint_model: `runtime/repo_control_center/operator_program_checkpoint.json`
- evidence_outputs: `runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json, runtime/repo_control_center/operator_program_audit_trail.json`
- blocking_logic: `creator_authority_required, authority_mode_not_allowed, step_execution_failed`
- program: `program.wave2c.creator_authorized_sequence.v1`
  - authority_requirement: `creator_required`
  - mutability_level: `CREATOR_ONLY_MUTATION`
  - command_dependencies: `creator_acceptance_precheck, governance_maintenance_check, refresh_safe_mirror_evidence, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json, runtime/repo_control_center/operator_program_audit_trail.json`
  - blocking_logic: `creator_authority_required, authority_mode_not_allowed, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`
- program: `program.wave2c.authority_required_program.v1`
  - authority_requirement: `creator_required`
  - mutability_level: `CREATOR_ONLY_MUTATION`
  - command_dependencies: `creator_acceptance_precheck, governance_maintenance_check, refresh_safe_mirror_evidence, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json, runtime/repo_control_center/operator_program_audit_trail.json`
  - blocking_logic: `creator_authority_required, authority_mode_not_allowed, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`

### `controlled_lifecycle_program`
- authority_requirement: `creator_required`
- mutability_level: `GUARDED_STATE_CHANGE`
- routing_basis: `class_precedence + keyword matching + deterministic registry lookup`
- checkpoint_model: `runtime/repo_control_center/operator_program_checkpoint.json`
- evidence_outputs: `runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json, runtime/repo_control_center/operator_program_audit_trail.json`
- blocking_logic: `creator_authority_required, required_input_missing, step_execution_failed`
- program: `program.wave2c.controlled_install_lifecycle.v1`
  - authority_requirement: `creator_required`
  - mutability_level: `GUARDED_STATE_CHANGE`
  - command_dependencies: `creator_acceptance_precheck, install_system, remove_system, governance_maintenance_check, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json, runtime/repo_control_center/operator_program_audit_trail.json`
  - blocking_logic: `creator_authority_required, required_input_missing, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`
- program: `program.wave2c.controlled_remove_lifecycle.v1`
  - authority_requirement: `creator_required`
  - mutability_level: `GUARDED_STATE_CHANGE`
  - command_dependencies: `creator_acceptance_precheck, install_system, remove_system, governance_maintenance_check, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json, runtime/repo_control_center/operator_program_audit_trail.json`
  - blocking_logic: `creator_authority_required, required_input_missing, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`

### `blocked_mutation_test_program`
- authority_requirement: `program_specific`
- mutability_level: `CREATOR_ONLY_MUTATION`
- routing_basis: `class_precedence + keyword matching + deterministic registry lookup`
- checkpoint_model: `runtime/repo_control_center/operator_program_checkpoint.json`
- evidence_outputs: `runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json, runtime/repo_control_center/operator_program_audit_trail.json`
- blocking_logic: `creator_authority_required, required_input_missing, policy_basis_missing, step_execution_failed`
- program: `program.wave2c.blocked_creator_gate_simulation.v1`
  - authority_requirement: `creator_required`
  - mutability_level: `CREATOR_ONLY_MUTATION`
  - command_dependencies: `refresh_safe_mirror_evidence, handoff_prepare, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json, runtime/repo_control_center/operator_program_audit_trail.json`
  - blocking_logic: `creator_authority_required, required_input_missing, policy_basis_missing, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`
- program: `program.wave2c.blocked_missing_preconditions.v1`
  - authority_requirement: `program_specific`
  - mutability_level: `OPERATIONAL_ROUTING`
  - command_dependencies: `refresh_safe_mirror_evidence, handoff_prepare, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json, runtime/repo_control_center/operator_program_audit_trail.json`
  - blocking_logic: `creator_authority_required, required_input_missing, policy_basis_missing, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`
- program: `program.wave2c.blocked_policy_mutation.v1`
  - authority_requirement: `creator_required`
  - mutability_level: `CREATOR_ONLY_MUTATION`
  - command_dependencies: `refresh_safe_mirror_evidence, handoff_prepare, report_generation`
  - checkpoint_model: `step_plan + resume_pointer + can_resume`
  - evidence_outputs: `runtime/repo_control_center/operator_program_status.json, runtime/repo_control_center/operator_program_report.md, runtime/repo_control_center/operator_program_checkpoint.json, runtime/repo_control_center/operator_program_history.json, runtime/repo_control_center/operator_program_audit_trail.json`
  - blocking_logic: `creator_authority_required, required_input_missing, policy_basis_missing, step_execution_failed`
  - final_outputs: `execution_result + artifacts_produced + next_step`
