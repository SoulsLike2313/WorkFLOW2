# MACHINE_CAPABILITIES_SUMMARY

## Capability Surface
- Detect machine role and authority state (`creator`/`helper`/`integration`).
- Evaluate control gates: trust, sync, governance, governance acceptance, admission, evolution.
- Validate safe-state evidence chain and bootstrap contract.
- Emit runtime evidence reports for audit and operator review.

## Authority-Bound Actions
Creator-only actions:
- Canonical acceptance decisions.
- Final completion claim for canonical flow.
- Protected governance-layer mutations.
- Final integration admission decisions.

## Helper/Integration Boundaries
- Helper node can execute scoped block tasks only.
- Helper node cannot declare canonical completion.
- Integration flow can review/route handoff packages but does not auto-accept canon.

## Forbidden Actions
- Bypass sync parity requirements.
- Return PASS while critical gate blockers exist.
- Treat role limitations as governance compliance.
- Suppress blocking evidence or contradiction signals.

## Reporting and Verdict Behavior
Mandatory runtime outputs:
- `runtime/repo_control_center/repo_control_status.json`
- `runtime/repo_control_center/repo_control_report.md`
- `runtime/repo_control_center/evolution_status.json`
- `runtime/repo_control_center/evolution_report.md`
- `runtime/repo_control_center/one_screen_status.json`
- `runtime/repo_control_center/plain_status.md`

Verdict model:
- trust: `TRUSTED` | `WARNING` | `NOT_TRUSTED`
- sync: `IN_SYNC` | `DRIFTED` | `BLOCKED`
- governance: `COMPLIANT` | `PARTIAL` | `NON_COMPLIANT`
- admission: `ADMISSIBLE` | `CONDITIONAL` | `REJECTED`
- evolution: `HOLD` | `PREPARE` | `V2_CANDIDATE` | `V2_READY` | `PROMOTE` | `BLOCKED`

## Transfer Surface
- Targeted ChatGPT bundle export for controlled external reading.
- Audit-safe runtime export mode with explicit allowlist only.
