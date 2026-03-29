# DEPARTMENT_COMPLETION_GATE_RULES_V1

Status:
- gate_rules_version: `v1`
- scope: `minimum completion gates for department and product-level progression`

Assertion labels:
- `PROVEN`
- `REUSABLE`
- `DESIGNED`
- `NOT YET IMPLEMENTED`

## 1) Gate stack

### G0 - Intake Integrity Gate

Pass requires:
1. source + goal + constraints present;
2. artifact list present.

### G1 - Technical Map Integrity Gate

Pass requires:
1. architecture map;
2. done/not-done map;
3. risk map.

### G2 - Task Boundedness Gate

Pass requires:
1. each execution task has explicit scope;
2. forbidden actions explicitly set;
3. evidence checklist attached.

### G3 - Execution Evidence Gate

Pass requires:
1. Astartes result bundles include evidence refs;
2. unresolved blockers explicitly listed.

### G4 - Department Synthesis Gate

Pass requires:
1. Primarch synthesis bundle present;
2. contradiction check included;
3. recommendation bounded and evidence-backed.

### G5 - Verification Gate

Pass requires:
1. required checks/tests passed;
2. failures addressed or escalated;
3. no hidden critical defects.

### G6 - Release Readiness Gate

Pass requires:
1. release package integrity evidence;
2. known limits documented;
3. rollback/fallback note present where needed.

### G7 - Final Acceptance Gate

Pass requires:
1. full evidence chain;
2. no red critical blockers;
3. sovereign boundary respected.

## 2) Minimum evidence by department role

### Analytics minimum

1. Intake Bundle
2. Technical Map Bundle
3. Routing proposal

### Execution lanes minimum

1. Task Bundle
2. Astartes Result Bundle
3. Blocker/Incident Bundle when needed

### Primarch minimum

1. Department Synthesis Bundle
2. gate-by-gate pass/fail statement
3. escalation note (if any)

## 3) Failure semantics

1. Any failed mandatory gate blocks completion.
2. Department may continue only through explicit remediation loop.
3. No PASS-WORDING override without gate evidence.

## 4) Current status

1. `REUSABLE`: existing constitutional/gate philosophy.
2. `DESIGNED`: department completion gate stack for production.
3. `NOT YET IMPLEMENTED`: one script that calculates all G0-G7 from bundles automatically.

