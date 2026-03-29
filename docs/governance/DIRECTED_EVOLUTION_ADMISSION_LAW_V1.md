# DIRECTED_EVOLUTION_ADMISSION_LAW_V1

Status:
- law_state: `ACTIVE`
- scope: `all_new_evolution_branches`
- binding: `MANDATORY`

## Purpose

Prevent side/noise growth by enforcing owner-visible admission for every new evolution branch.

## Mandatory Admission Questions

A branch cannot start unless it answers all:
1. Which primary cluster does it belong to?
2. What exact system strength does it improve?
3. Why is it not side noise?
4. How is value measured (observable metric/evidence)?
5. Which owner gate is required before promotion?

## Required Admission Payload

1. `candidate_id`
2. `primary_cluster_id`
3. `problem_statement`
4. `intended_gain`
5. `non_noise_rationale`
6. `measurement_method`
7. `required_owner_gate`
8. `promotion_target_state`
9. `rollback_trigger`
10. `evidence_plan_paths`

Missing required fields => automatic rejection.

## Admission Verdicts

1. `ACCEPTED` - admitted to bounded execution.
2. `DEFERRED` - valid but not now.
3. `REJECTED` - side/noise/drift or insufficient rationale.
4. `BLOCKED` - violates boundary/governance law.

## Promotion Rule

Promotion is forbidden unless:
1. admission verdict is `ACCEPTED`,
2. owner gate for this branch is resolved,
3. claimed gain is supported by repo-visible evidence.

## Anti-Noise Filters

Immediate `REJECTED` if any:
1. no primary cluster declared,
2. "improve everything" scope with no bounded objective,
3. no measurable utility definition,
4. branch conflicts with cluster forbidden drift directions.

## Governance Boundary

1. This law does not override canonical repo law.
2. This law does not bypass evidence/admission/sync gates.
3. This law does not authorize hidden learning.

