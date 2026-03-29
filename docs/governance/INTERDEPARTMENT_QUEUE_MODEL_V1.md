# INTERDEPARTMENT_QUEUE_MODEL_V1

Status:
- queue_model_version: `v1`
- scope: `production queue routing between departments and roles`

Assertion labels:
- `PROVEN`
- `REUSABLE`
- `DESIGNED`
- `NOT YET IMPLEMENTED`

## 1) Queue types

1. `intake_queue`
2. `assignment_queue`
3. `execution_queue`
4. `review_queue`
5. `blocker_queue`
6. `release_queue`

## 2) Queue ownership matrix

| Queue | Primary writer | Primary reader | Typical payload | Escalation trigger | Close condition |
| --- | --- | --- | --- | --- | --- |
| intake_queue | owner/Primarch/Analytics intake | Analytics | Intake Bundle | missing baseline data or policy mismatch | intake classified and routed |
| assignment_queue | Primarch | Astartes | Task Bundle | no eligible slot in force map | task bound to executor |
| execution_queue | Astartes | Primarch | in-flight task state + partial evidence | scope conflict or hard blocker | task result submitted |
| review_queue | Primarch/Verification | Primarch + Emperor path as needed | Department Synthesis / Completion candidate | claim not evidence-backed | review decision emitted |
| blocker_queue | Astartes/Primarch | Primarch (+ Emperor if sovereign boundary) | Blocker/Incident Bundle | critical severity or sovereign boundary | blocker resolved or accepted workaround |
| release_queue | Release role/Primarch | Emperor signoff path + integration recipients | Release Bundle | verification regression or integration mismatch | release accepted/rejected |

## 3) Queue item mandatory fields

1. `queue_item_id`
2. `queue_type`
3. `producer`
4. `consumer`
5. `priority`
6. `deadline_utc`
7. `bundle_ref`
8. `state` (`OPEN/IN_PROGRESS/BLOCKED/CLOSED`)
9. `evidence_ref`

## 4) Queue state transitions

1. `OPEN` -> `IN_PROGRESS` when consumer accepts item.
2. `IN_PROGRESS` -> `BLOCKED` when blocker bundle is attached.
3. `BLOCKED` -> `IN_PROGRESS` when blocker resolved and reaccepted.
4. `IN_PROGRESS` -> `CLOSED` only with required bundle and evidence.

## 5) Anti-chaos rules

1. Queue item without linked bundle is invalid.
2. Queue item without explicit consumer is invalid.
3. Queue closure without evidence ref is forbidden.
4. Silent timeout is forbidden; must produce blocker or closure action.

## 6) Current status

1. `REUSABLE`: integration/review queue patterns already exist.
2. `DESIGNED`: normalized interdepartment queue taxonomy for production layer.
3. `NOT YET IMPLEMENTED`: single queue orchestrator enforcing this model end-to-end.

