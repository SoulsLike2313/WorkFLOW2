# PRODUCT_LIFECYCLE_V1

Status:
- lifecycle_version: `v1`
- scope: `end-to-end product movement under federated production system`
- activation_profile: `analytics-first`

Assertion labels:
- `PROVEN`
- `REUSABLE`
- `DESIGNED`
- `NOT YET IMPLEMENTED`

## 1) Common lifecycle gates

1. Intake accepted.
2. Technical map completed.
3. Department routing accepted.
4. Execution bundles completed.
5. Verification gate passed.
6. Release gate passed.
7. Final acceptance boundary respected.

## 2) Scenario A: idea -> product

### Entry point

`idea_seed` enters `Analytics Department`.

### Flow

1. Analytics creates Intake + Technical Map Bundle.
2. Primarch produces roadmap and assigns first bounded tasks.
3. Engineering/Verification mapped-later lanes activate when needed.
4. Completion candidate enters verification and release gates.

### Approval to move stage

Primarch may move from analysis to implementation only with evidence-backed roadmap.

### Product readiness meaning

Idea becomes product only if implementation + verification + release gates pass.

## 3) Scenario B: demo -> product

### Entry point

`demo_seed` enters Analytics for reuse-vs-rebuild assessment.

### Flow

1. Analytics separates reusable and unstable parts.
2. Primarch emits bounded modernization plan.
3. Astartes executes targeted hardening tasks.
4. Verification validates reliability and regressions.

### Approval to move stage

Move to release only with validated technical debt closure on critical areas.

### Product readiness meaning

Demo stops being "showcase only" and becomes stable deliverable.

## 4) Scenario C: broken/raw app -> stable product

### Entry point

`raw_app_seed` with known instability.

### Flow

1. Analytics builds defect and risk map.
2. Primarch prioritizes stabilization before feature expansion.
3. Astartes executes repair bundles.
4. Verification enforces no-fake-pass rule.

### Approval to move stage

Only after critical blockers are closed and evidence is attached.

### Product readiness meaning

App is operable, test-backed, and no longer brittle in core paths.

## 5) Scenario D: existing app -> scaling/refactor/hardening

### Entry point

`legacy_app_seed` with growth or debt pressure.

### Flow

1. Analytics identifies scaling bottlenecks and architecture drift.
2. Primarch splits into safe bounded refactor tracks.
3. Tooling/Infrastructure lane may be activated for delivery speed.
4. Verification checks performance/reliability claims.

### Approval to move stage

Only if each refactor batch passes its own gate chain.

### Product readiness meaning

App can scale without breaking operational guarantees.

## 6) Validation points by stage

1. Intake validation: completeness and traceability.
2. Analysis validation: evidence-backed mapping.
3. Execution validation: bounded scope compliance.
4. Verification validation: test-backed claims.
5. Release validation: package integrity and rollback readiness.

## 7) Who can approve movement

1. Astartes: cannot approve stage movement.
2. Primarch: may approve within non-sovereign operational stage transitions.
3. Emperor: final escalation and sovereign boundary decisions.

## 8) Current status

1. `REUSABLE`: analytics-first intake and bounded execution doctrine.
2. `DESIGNED`: unified lifecycle map for production conversion scenarios.
3. `NOT YET IMPLEMENTED`: full automated lifecycle controller.

