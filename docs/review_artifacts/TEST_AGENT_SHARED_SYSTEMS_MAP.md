# Test Agent Shared Systems Map

## Required Shared Systems in Core Model

| System | Integration Status | Used In Lanes |
| --- | --- | --- |
| `ui_qa_toolkit` | integrated | `ui_audit_lane` |
| `verification_toolkit` | integrated | `project_intake`, `verification_lane`, `readiness_lane`, `final_admission_gate` |
| `reporting_toolkit` | integrated | `reporting_lane`, `localization_audit_lane`, `audit_observability_lane`, `evidence_collection`, `final_admission_gate` |
| `localization_toolkit` | integrated | `localization_audit_lane` |
| `audit_observability_toolkit` | integrated | `audit_observability_lane`, `evidence_collection`, `final_admission_gate` |

## Optional / Future Lanes

| System | Integration Status | Planned Lane |
| --- | --- | --- |
| `update_patch_toolkit` | partial_future_lane | `update_patch_lane` |
| `security_baseline` | partial_future_lane | `security_baseline_lane` |
