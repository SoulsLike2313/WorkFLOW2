# DEPARTMENT_AUTHORITY_CHAIN_V1

Status:
- chain_version: `v1`
- scope: `department-level authority and escalation chain`
- model: `Emperor -> Primarch -> Astartes`

Assertion labels:
- `PROVEN`
- `REUSABLE`
- `DESIGNED`
- `NOT YET IMPLEMENTED`

## 1) Chain overview

1. Emperor holds canonical law and sovereign signoff boundary.
2. Primarch runs department operations within bounded mandate.
3. Astartes executes bounded tasks only.

## 2) Authority segmentation

### Emperor layer

May:
1. activate department-level operations;
2. issue Primarch Gramota;
3. accept final escalations and final product signoff.

May not delegate:
1. constitutional mutation authority to non-sovereign layers.

### Primarch layer

May:
1. direct department flow;
2. assign Astartes bounded tasks;
3. synthesize department outputs;
4. escalate unresolved or sovereign-bound issues.

May not:
1. claim sovereign final acceptance;
2. bypass constitutional boundaries.

### Astartes layer

May:
1. execute bounded tasks;
2. return evidence and blockers.

May not:
1. perform organizational command;
2. self-escalate as authority source;
3. widen scope.

## 3) Escalation boundaries

1. Astartes -> Primarch (always for blocker beyond task boundary).
2. Primarch -> Emperor (for sovereign boundary, canonical acceptance, unresolved critical risk).
3. Direct Astartes -> Emperor is not canonical in this model.

## 4) Conflict resolution priority

1. Constitution boundary.
2. Direct Emperor Gramota.
3. Primarch mandate within granted scope.
4. Astartes binding task.

If conflict appears:
1. lower level must stop and escalate upward.

## 5) Reporting ladder

1. Astartes emits `Astartes Result Bundle`.
2. Primarch emits `Department Synthesis Bundle`.
3. Emperor receives final synthesis + escalations + completion recommendation.

## 6) Why this chain is practical

1. Owner sees one accountable processor (Primarch) instead of chaotic multi-agent noise.
2. Executors stay fast because scope is bounded.
3. Sovereign layer is not overloaded by low-level task traffic.

## 7) Current-stage truth

1. `PROVEN`: chain applies immediately to active `Analytics Department`.
2. `DESIGNED`: same chain template prepared for mapped-later departments.
3. `NOT YET IMPLEMENTED`: centralized runtime engine auto-enforcing every chain transition.

## 8) Evidence anchors

1. `docs/governance/FEDERATION_OPERATIONAL_MODEL.md`
2. `docs/governance/PRIMARCH_DEPARTMENT_AUTHORITY_MODEL_V1.md`
3. `docs/governance/ASTARTES_DEPARTMENT_BINDING_MODEL_V1.md`
4. `workspace_config/department_guardian_registry.json`
5. `workspace_config/department_exception_escalation_contract.json`

