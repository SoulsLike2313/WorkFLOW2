# MACHINE_OPERATOR_GUIDE

## Scope
Operator-facing governance/control runbook for WorkFLOW2.
Focus: gate interpretation, role constraints, execution routing.

## System Context
- Working source of truth: `E:\CVVCODEX`
- Public safe mirror: `safe_mirror/main` (`WorkFLOW2`)
- Control runtime entrypoint: `python scripts/repo_control_center.py <mode>`

## Role Model
- `creator`: creator authority present; canonical acceptance operations permitted.
- `helper`: authority absent; scoped execution only; no canonical acceptance.
- `integration`: canonical review lane for external handoff packages.

## Gate Model
Canonical decision chain:
1. `sync_verdict`
2. `trust_verdict`
3. `governance_verdict`
4. `governance_acceptance_verdict`
5. `admission_verdict`
6. `evolution_verdict` (progression signal, not acceptance substitute)

## Health/Status Layering
- `workspace_health`: technical integrity of workspace checks.
- `authority_status`: authority/role state.
- `governance_status`: governance state after compliance/acceptance logic.
- `admission_status`: admission gate state class.

## Execution Procedure
1. `python scripts/repo_control_center.py bundle`
2. `python scripts/repo_control_center.py full-check`
3. Inspect:
   - `runtime/repo_control_center/one_screen_status.json`
   - `runtime/repo_control_center/plain_status.md`

## Operator Command Surface
Execution entrypoint:
- `python scripts/operator_command_surface.py execute --command "<operator command>"`

Routing/contract references:
- `docs/governance/OPERATOR_COMMAND_INTENT_ROUTING.md`
- `docs/governance/OPERATOR_COMMAND_EXECUTION_CONTRACT.md`
- `workspace_config/operator_command_registry.json`

Required execution evidence:
- `runtime/operator_command_layer/last_execution.json`
- `runtime/operator_command_layer/command_surface_status.json`
- `runtime/operator_command_layer/command_surface_report.md`

## Operator Task / Program Surface
Execution entrypoint:
- `python scripts/operator_program_surface.py execute --request "<program request>"`

Routing/contract references:
- `docs/governance/OPERATOR_PROGRAM_INTENT_ROUTING.md`
- `docs/governance/OPERATOR_PROGRAM_EXECUTION_CONTRACT.md`
- `workspace_config/operator_program_registry.json`

Required execution evidence:
- `runtime/operator_program_layer/last_execution.json`
- `runtime/operator_program_layer/program_surface_status.json`
- `runtime/operator_program_layer/program_surface_report.md`

## Block Routing
Route by:
- `blocking_reason_category`
- `blocking_reason_detail`

Categories are gate-oriented (`SYNC`, `ROLE_AUTHORITY`, `GOVERNANCE_POLICY`, `ADMISSION_GATE`, `TRUST`).

## Boundaries
- No canonical completion in non-creator mode.
- No completion when sync/worktree parity is broken.
- No completion with unresolved critical contradictions.
- No override of governance acceptance gate.

## Related Documents
- Capability matrix: `docs/governance/MACHINE_CAPABILITIES_SUMMARY.md`
- Policy map digest: `docs/governance/POLICY_DIGEST.md`
