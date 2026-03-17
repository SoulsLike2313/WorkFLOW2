# OPERATOR_TASK_PROGRAM_CATALOG_WAVE_2A

## Scope
Wave 2A introduces only safe task/program flows on top of command layer v1.

## Program Classes

### 1) status_refresh_program
- Purpose: rebuild runtime truth/status surface.
- Entry conditions: command layer available.
- Command classes used: `status_refresh_command`, `validation_command`, `report_generation_command`.
- Runtime artifacts updated:
  - `runtime/repo_control_center/plain_status.md`
  - `runtime/repo_control_center/one_screen_status.json`
  - `runtime/repo_control_center/operator_program_status.json`
  - `runtime/repo_control_center/operator_program_report.md`
- Expected result: refreshed status evidence and deterministic report output.
- Possible blocked conditions:
  - missing policy basis
  - invalid resume pointer
  - step failure

Programs:
- `program.wave2a.status_refresh_surface.v1`
- `program.wave2a.full_status_reconstruction.v1`

### 2) validation_program
- Purpose: run creator-grade/governance validation chains in safe mode.
- Entry conditions:
  - creator authority for creator-only validation program.
  - otherwise none for governance validation.
- Command classes used: `creator_only_execution_command`, `validation_command`, `policy_reference_command`.
- Runtime artifacts updated:
  - `runtime/repo_control_center/repo_control_status.json`
  - `runtime/repo_control_center/repo_control_report.md`
  - `runtime/repo_control_center/operator_program_status.json`
  - `runtime/repo_control_center/operator_program_report.md`
- Expected result: validation verdict + policy evidence.
- Possible blocked conditions:
  - creator authority required
  - mode not allowed
  - step failure

Programs:
- `program.wave2a.creator_grade_validation.v1`
- `program.wave2a.governance_chain_validation.v1`

### 3) evidence_pack_program
- Purpose: build safe evidence package programs.
- Entry conditions:
  - creator authority for creator-proof program.
  - exporter available.
- Command classes used: `evidence_bundle_command`, `status_refresh_command`, `creator_only_execution_command`, `report_generation_command`.
- Runtime artifacts updated:
  - `runtime/repo_control_center/operator_program_status.json`
  - `runtime/repo_control_center/operator_program_report.md`
  - `runtime/chatgpt_bundle_exports/*`
- Expected result: evidence bundle created with program-run metadata.
- Possible blocked conditions:
  - creator authority required
  - policy basis missing
  - step failure

Programs:
- `program.wave2a.governance_evidence_pack.v1`
- `program.wave2a.creator_proof_pack.v1`

### 4) report_program
- Purpose: generate engineering reports from current truth/evidence state.
- Entry conditions: command layer and policy digest available.
- Command classes used: `status_refresh_command`, `validation_command`, `policy_reference_command`, `report_generation_command`.
- Runtime artifacts updated:
  - `runtime/repo_control_center/operator_program_report.md`
  - `runtime/repo_control_center/operator_program_status.json`
- Expected result: compact operator/governance status report.
- Possible blocked conditions:
  - policy basis missing
  - step failure

Programs:
- `program.wave2a.operator_engineering_report.v1`
- `program.wave2a.status_evidence_report.v1`

## Wave 2A Mutability Discipline
- Allowed only:
  - `READ_ONLY`
  - `REFRESH_ONLY`
  - `PACKAGE_ONLY`
- Forbidden in Wave 2A:
  - guarded mutation programs
  - creator mutation programs
  - integration/handoff heavy orchestration

## Checkpoint Model
- Every run records:
  - `current_step`
  - `completed_steps`
  - `failed_step`
  - `resume_pointer`
  - `can_resume`
- Resume is deterministic via `--resume-from-step`.
