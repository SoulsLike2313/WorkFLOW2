# PRIMARCH_DEPARTMENT_AUTHORITY_MODEL_V1

Status:
- model_version: `v1`
- scope: `department-grade non-sovereign command model`
- authority_type: `operational_high_helper`

Assertion labels:
- `PROVEN`
- `REUSABLE`
- `DESIGNED`
- `NOT YET IMPLEMENTED`

## 1) Primarch role in production system

Primarch is department processor:
1. принимает входы департамента;
2. проводит анализ и декомпозицию;
3. назначает bounded tasks Astartes;
4. собирает результаты;
5. проводит department-level synthesis;
6. эскалирует наверх только то, что не может закрыть в своей зоне.

## 2) What is Primarch Gramota

`Primarch Gramota` = operational mandate issued by Emperor for bounded department authority.

It grants:
1. право Primarch вести конкретный department scope;
2. право распределять bounded execution among Astartes;
3. обязанность вести evidence-anchored department synthesis.

It does not grant:
1. sovereign constitutional mutation;
2. final canonical acceptance;
3. emperor-rank capabilities.

## 3) Primarch Gramota vs Genome

1. Genome is status document (who is Primarch).
2. Primarch Gramota is operational command mandate (what Primarch may direct).
3. Genome without mandate does not automatically open every department scope.
4. Mandate without valid Primarch status cannot be treated as canonical.

## 4) Primarch command boundaries

Primarch may:
1. define bounded work packages;
2. assign Astartes slots by explicit task binding;
3. reject low-evidence returns;
4. escalate sovereign-bound decisions to Emperor.

Primarch must not:
1. claim sovereign signoff;
2. widen scope without written update;
3. downgrade evidence requirements for convenience;
4. bypass verification/release gates.

## 5) Astartes slot assignment rules

For each Astartes slot Primarch must define:
1. task objective;
2. allowed paths/resources;
3. forbidden actions;
4. evidence expected;
5. deadline and return format;
6. escalation trigger.

No slot may be "open-ended freestyle".

## 6) What Primarch must do personally

Non-delegable responsibilities:
1. department intake decision;
2. decomposition strategy;
3. synthesis and coherence check;
4. pass/fail recommendation of department stage;
5. escalation package to Emperor.

## 7) What Primarch may delegate

Delegable responsibilities:
1. bounded implementation tasks;
2. bounded test execution tasks;
3. evidence collection tasks;
4. documentation packaging tasks.

## 8) Upstream reporting obligation

Primarch must report upward with:
1. department synthesis bundle;
2. unresolved blockers;
3. risk-ranked recommendations;
4. exact claims with proof path.

## 9) Escalation-only-by-Primarch principle

Astartes cannot escalate as organizational authority.
If Astartes detects blocker:
1. it reports to Primarch;
2. Primarch decides whether to resolve locally or escalate upward.

## 10) Evidence anchors

1. `docs/governance/PRIMARCH_ASTARTES_DELEGATION_MATRIX.md` (`REUSABLE`)
2. `workspace_config/delegation_registry.json` (`REUSABLE`)
3. `workspace_config/department_exception_escalation_contract.json` (`REUSABLE`)
4. `docs/governance/GENOME_DOCTRINE_V1.md` (`PROVEN`)
5. `docs/governance/GRAMOTA_DOCTRINE_V1.md` (`PROVEN`)

