# HANDOFF_AND_BLOCKER_PROTOCOL_V1

Status:
- protocol_version: `v1`
- scope: `safe handoff and explicit blocker handling between departments`

Assertion labels:
- `PROVEN`
- `REUSABLE`
- `DESIGNED`
- `NOT YET IMPLEMENTED`

## 1) Handoff protocol

Handoff is valid only with:
1. clear ownership transfer (`from_role`, `to_role`);
2. explicit scope and boundaries;
3. dependency list;
4. acceptance criteria;
5. evidence references.

If any of these is missing, receiver must reject handoff.

## 2) Handoff bundle minimum

1. `handoff_id`
2. `source_bundle_ids`
3. `target_department`
4. `target_role`
5. `scope_statement`
6. `assumptions`
7. `known_risks`
8. `required_next_gate`
9. `acceptance_checklist`

## 3) Blocker protocol

Blocker is not "noise note"; it is formal incident artifact.

Mandatory blocker fields:
1. `blocker_id`
2. `severity` (`LOW/MEDIUM/HIGH/CRITICAL`)
3. `impact`
4. `scope_affected`
5. `evidence`
6. `attempted_mitigations`
7. `required_decision_owner`

## 4) Escalation rules

1. Astartes reports blocker to Primarch.
2. Primarch resolves if within bounded operational scope.
3. Primarch escalates to Emperor when blocker touches sovereign boundary, final acceptance boundary, or unresolved critical risk.

## 5) Closure rules

Handoff closes when:
1. receiver explicitly accepts ownership;
2. first queue item under new ownership is created.

Blocker closes when:
1. mitigation verified; or
2. accepted workaround approved by correct authority.

## 6) Anti-haltura rules

1. No "done despite blocker" if blocker severity is `HIGH` or `CRITICAL`.
2. No handoff without dependency disclosure.
3. No silent downgrade of blocker severity.

## 7) Why owner can trust this

1. Любая проблема становится формальным объектом, а не теряется в чате.
2. Любая передача ответственности фиксируется и проверяется.
3. Снижается риск ложного "все ок" при скрытых сбоях.

## 8) Current status

1. `REUSABLE`: existing blocker/escalation principles in governance stack.
2. `DESIGNED`: production-grade handoff+blocker contract for department chain.
3. `NOT YET IMPLEMENTED`: unified automated checker for every handoff/blocker bundle.

