# CONSTITUTION_GATE_SEVERITY_MODEL_V1

## Scope
Severity calibration model for Constitution V1 checks.  
This model is lightweight and is used by `run_constitution_checks.py` and admission discipline docs.

## Severity Classes
| class | meaning | completion claim | certification claim | mirror refresh | phase transition | required operator response |
|---|---|---|---|---|---|---|
| `INFO` | healthy state, no constitutional risk | allow | allow | allow | allow | no action |
| `WARNING` | non-critical deviation, still understandable and controlled | allow with note | review required | allow with note | review required | record note + schedule fix |
| `SOFT_FAIL` | significant deviation; not catastrophic, but protected claims unsafe | block | block | review required | block | refresh/review/fix, rerun checks |
| `HARD_FAIL` | critical constitutional violation or broken trust/sync discipline | block | block | block | block | stop, resolve root issue, rerun full chain |

## Tolerated Partial
`PARTIAL` is tolerated only when:
- no `HARD_FAIL`;
- no unresolved critical contradiction;
- operator explicitly records debt and next correction action.

`PARTIAL` is not enough for:
- completion claim;
- certification claim;
- canonical phase transition claim.

## Not Allowed At Completion Claim
- any `HARD_FAIL`;
- any `SOFT_FAIL`;
- unresolved contradiction `FAIL`;
- unknown-critical constitutional dependencies.

## Not Allowed At Certification Claim
- all completion blockers above;
- any unresolved drift `FAIL`;
- stale `repo_control_status` that leaves trust/sync/governance acceptance unknown.

## Notes
- `mirror refresh` is less strict than completion/certification under `SOFT_FAIL`, but requires explicit review.
- `UNKNOWN` is not a severity class; it is an aggregation verdict when critical inputs are unavailable.
