# Tester Agent Execution Flow

## Goal

Provide machine-first audit flow for target projects before manual testing admission.

## Input Contract

Required:

1. `target_project_path`
2. `target_project_slug`
3. target `PROJECT_MANIFEST.json`
4. workspace governance manifests

## Lane Sequence

1. `project_intake`
2. `verification_lane`
3. `readiness_lane`
4. `ui_audit_lane` (if UI applicable)
5. `reporting_lane`
6. `localization_audit_lane`
7. `audit_observability_lane`
8. `evidence_collection`
9. `final_admission_gate`

## Core Runner

- `python projects/platform_test_agent/scripts/test_agent_core.py --mode intake --target-project-path <path> --target-project-slug <slug>`
- `python projects/platform_test_agent/scripts/test_agent_core.py --mode audit --target-project-path <path> --target-project-slug <slug>`
- `python projects/platform_test_agent/scripts/test_agent_core.py --mode verify --target-project-slug <slug> --execute-verification`

## Outputs

- `runtime/projects/platform_test_agent/audit_reports/<run_id>/final_machine_report.json`
- `runtime/projects/platform_test_agent/audit_reports/<run_id>/final_machine_report.md`
- `runtime/projects/platform_test_agent/audit_reports/<run_id>/evidence_manifest.json`
- `runtime/projects/platform_test_agent/audit_reports/<run_id>/admission_decision.json`
