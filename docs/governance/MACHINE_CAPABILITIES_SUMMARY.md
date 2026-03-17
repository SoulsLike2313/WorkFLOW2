# MACHINE_CAPABILITIES_SUMMARY

## Capability Matrix

| Domain | Capability | Constraint |
| --- | --- | --- |
| Mode detection | Detect `creator` / `helper` / `integration` from authority contract | Contract must resolve; otherwise mode is constrained |
| Gate evaluation | Compute trust/sync/governance/governance-acceptance/admission/evolution verdict chain | Hard blockers prevent PASS-class gates |
| Evidence validation | Validate safe-state evidence contract (`basis_head_sha`, evidence mode, evidence freshness) | Non-compliant evidence degrades mirror/trust chain |
| Runtime reporting | Emit machine-readable and operator-readable status artifacts | Output reflects current run only |
| Integration readiness | Validate integration inbox structure and task/handoff tooling presence | Missing structure/contracts block integration verdict |

## Authority-Bound Actions
Creator-only:
- Canonical acceptance decisions.
- Final completion claims for canonical flow.
- Protected governance-layer changes.
- Final integration admission decisions.

## Forbidden Actions
- Bypass sync parity discipline.
- Report PASS while hard blockers are unresolved.
- Treat role limitation as governance compliance.
- Suppress blocking evidence in runtime outputs.

## Runtime Output Surface
- `runtime/repo_control_center/repo_control_status.json`
- `runtime/repo_control_center/repo_control_report.md`
- `runtime/repo_control_center/evolution_status.json`
- `runtime/repo_control_center/evolution_report.md`
- `runtime/repo_control_center/one_screen_status.json`
- `runtime/repo_control_center/plain_status.md`

## Verdict Naming Discipline
- Verdict fields: `*_verdict`
- Status layer fields: `*_status`
- Health field: `workspace_health`

## External Transfer Surface
- Targeted ChatGPT bundle export is canonical external read path.
- Runtime exports are restricted to explicit audit-runtime allowlist.
