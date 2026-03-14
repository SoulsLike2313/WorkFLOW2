# Tester Agent Shared Systems Integration Map

## Required Foundation Systems

| Shared System | Lane Usage | Integration Role | Inputs | Outputs |
| --- | --- | --- | --- | --- |
| `verification_toolkit` | `project_intake`, `verification_lane`, `readiness_lane`, `final_admission_gate` | verification/readiness contracts and gate status model | target manifest, verification entrypoints | verification lane status, readiness lane status, gate decision inputs |
| `ui_qa_toolkit` | `ui_audit_lane` | UI snapshot and UI validation flow | UI entrypoints, UI rules | ui validation summary, screenshot manifests |
| `reporting_toolkit` | `reporting_lane`, `localization_audit_lane`, `audit_observability_lane`, `evidence_collection`, `final_admission_gate` | consolidated dry machine reporting | lane outputs and diagnostics | consolidated status, final machine report |
| `localization_toolkit` | `localization_audit_lane` | localization checks and contracts | locale config, localization rules | localization audit summary |
| `audit_observability_toolkit` | `audit_observability_lane`, `evidence_collection`, `final_admission_gate` | structured logs and diagnostics manifests | diagnostics paths, logs, timeline | diagnostics manifest, evidence manifest |

## Future Lanes (Partial Integration)

1. `update_patch_toolkit` -> `update_patch_lane` (future)
2. `security_baseline` -> `security_baseline_lane` (future)

No forced integration is applied in this bootstrap phase.
