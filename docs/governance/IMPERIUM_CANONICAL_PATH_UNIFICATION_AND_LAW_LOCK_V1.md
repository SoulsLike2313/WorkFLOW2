# IMPERIUM_CANONICAL_PATH_UNIFICATION_AND_LAW_LOCK_V1

Status:
- class: `foundation_law_lock`
- mutability: `owner_ratified_delta`
- change_authority: `OWNER_ONLY`
- effective_date_utc: `2026-03-30`
- canonical_enforcement_path: `scripts/repo_control_center.py`

Purpose:
- enforce one tracked enforcement truth center;
- lock owner-ratified foundation laws into canonical governance;
- prevent law duplication, ambiguous command execution, and unported integration.

## Canonical Law Set

1. `LAW-FOUNDATION-NO-DUPLICATE-LAWS`
Purpose:
- unresolved duplicate laws are forbidden.
Required resolution:
- `destroy duplicate`, `controlled merge`, or `strict scope split`.

2. `LAW-FOUNDATION-IMPERIUM-COMMIT-PHRASE`
Formal owner commit phrase:
- `Закрепи в Империуме`
Rule:
- law surfaced by this phrase must enter the next working cycle and pass duplicate/conflict lock.

3. `LAW-FOUNDATION-SINGLE-THREAD-COMPLETION`
Rule:
- started work must be carried to working integration unless owner changes priority.

4. `LAW-FOUNDATION-FULL-EXECUTION-DUTY`
Rule:
- mechanical incompleteness is fixed inside the same run, not escalated to owner.

5. `LAW-FOUNDATION-SERVITOR-FIDELITY`
Rule:
- cosmetic, partial, or false-done execution is forbidden.

6. `LAW-FOUNDATION-PORT-GATED-INTEGRATION`
Rule:
- no entity/module/law is considered introduced without lawful integration port evidence.
Required integration fields:
- address, owner, class, basis, links, system place, acceptance criteria, value proof, operability proof, soft integration proof.

7. `LAW-FOUNDATION-ONE-TRUTH-CENTER`
Rule:
- two competing enforcement paths are forbidden.
- if tracked canonical path exists, missing logic must be merged into it.

8. `LAW-FOUNDATION-AMBIGUOUS-OWNER-COMMAND-HARD-GATE`
Rule:
- ambiguous owner command must be blocked before execution.

9. `LAW-FOUNDATION-CODEX-RESPONSE-FORMAT`
Default Codex output law:
- chat output is short artifact handoff only;
- maximum `3-4` critical lines plus path.
Override:
- only explicit owner "Emperor signature" command with reason.

## Canonical Hierarchy Placement

1. `docs/governance/WORKFLOW2_CONSTITUTION_V1.md`
2. `docs/governance/GOVERNANCE_HIERARCHY.md`
3. `docs/governance/IMPERIUM_CANONICAL_PATH_UNIFICATION_AND_LAW_LOCK_V1.md`
4. execution contracts and runtime gate surfaces.

## Enforcement Bindings

Tracked canonical enforcement path:
- `scripts/repo_control_center.py`

Runtime gate outputs:
- `runtime/administratum/IMPERIUM_GATE_EXECUTION_SUMMARY_V1.json`
- `runtime/administratum/IMPERIUM_FOUNDATION_LAW_LOCK_STATUS_V1.json`
- `runtime/administratum/IMPERIUM_DUPLICATE_LAW_SCAN_V1.json`
- `runtime/administratum/IMPERIUM_AMBIGUOUS_COMMAND_HARD_GATE_STATUS_V1.json`
- `runtime/administratum/IMPERIUM_OWNER_COMMAND_GATE_RUNTIME_STATE_V1.json`
- `runtime/administratum/IMPERIUM_PORT_INTEGRATION_GATE_STATUS_V1.json`

## Duplicate-Law Canonical Resolution Protocol

Detection classes:
- exact duplicate (`law_id`)
- semantic duplicate (`title semantic token`)
- cross-file active duplicate (`same law id outside canonical law lock surface`)

Allowed decisions:
1. `DESTROY_DUPLICATE`
2. `MERGE_INTO_CANONICAL`
3. `SPLIT_SCOPE_AND_READDRESS`

Forbidden:
- silent coexistence of conflicting duplicate law centers.

## One-Truth-Center Constraint

Canonical enforcement path:
- `scripts/repo_control_center.py`

Forbidden competing path:
- `scripts/imperium_gate_implementation.py`

Any missing gate logic must be merged into the canonical tracked path.
