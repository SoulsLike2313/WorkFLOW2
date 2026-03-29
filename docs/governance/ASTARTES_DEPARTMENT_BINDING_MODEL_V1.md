# ASTARTES_DEPARTMENT_BINDING_MODEL_V1

Status:
- model_version: `v1`
- scope: `bounded Astartes execution discipline in production departments`
- authority_type: `execution_low_helper`

Assertion labels:
- `PROVEN`
- `REUSABLE`
- `DESIGNED`
- `NOT YET IMPLEMENTED`

## 1) Astartes role in production

Astartes is not department strategist.
Astartes is bounded executor:
1. берет письменную задачу;
2. исполняет в заданных границах;
3. возвращает доказательный результат;
4. не меняет scope сам.

## 2) What is Astartes Binding Gramota

`Astartes Binding Gramota` is a task-binding document issued under Primarch authority.

It fixes:
1. issuer and authority source;
2. exact task boundary;
3. execution scope and allowed assets;
4. forbidden actions;
5. evidence and return format;
6. revocation and reassignment conditions.

## 3) Why Astartes must obey written bound task

Without hard binding:
1. scope expands silently;
2. evidence quality falls;
3. false completion risk grows.

Therefore:
1. no written binding = no execution start;
2. out-of-scope request = return with blocker flag.

## 4) Astartes forbidden actions

1. redefine task scope autonomously;
2. issue organizational decisions;
3. claim department PASS;
4. claim sovereign authority;
5. hide failed checks or unresolved blockers.

## 5) Astartes expected outputs

Minimum return pack:
1. task execution summary;
2. changed artifact list;
3. evidence set (tests, logs, checks, rationale);
4. unresolved blocker list;
5. explicit confidence level.

## 6) Primarch use of Astartes

Primarch should use Astartes for:
1. repeatable execution tasks;
2. bounded validation and instrumentation tasks;
3. structured evidence packaging;
4. controlled implementation deltas.

Primarch must not offload:
1. synthesis ownership;
2. escalation ownership;
3. pass/fail final recommendation.

## 7) Revocation semantics

Binding may be revoked when:
1. task boundary is invalid;
2. risk is higher than allowed;
3. evidence protocol is violated;
4. upstream directive changes.

Revocation must be logged in blocker/handoff protocol.

## 8) Evidence anchors

1. `docs/governance/HELPER_NODE_POLICY.md` (`PROVEN`)
2. `docs/governance/TASK_ID_EXECUTION_CONTRACT.md` (`PROVEN`)
3. `workspace_config/delegation_registry.json` (`REUSABLE`)
4. `workspace_config/department_exception_escalation_contract.json` (`REUSABLE`)
5. `docs/governance/ASSIGNMENT_BINDING_DOCTRINE_V1.md` (`PROVEN`)

