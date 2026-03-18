# CONSTITUTION_CHECK_CALIBRATION_REPORT

## Scope
Calibration of existing constitutional checks into explicit severity behavior for admission/completion discipline.

## Check Calibration Matrix
| check | current role | proposed severity mapping | block or warn | freshness/runtime dependency |
|---|---|---|---|---|
| `truth_state_schema_status` | validates canonical truth grammar | `PASS->INFO`, `WARNING->WARNING`, `FAIL/MISSING->HARD_FAIL` | block on `HARD_FAIL` | static file presence + schema parse |
| `contradiction_scan_status` | detects canonical narrative conflicts | `PASS->INFO`, `WARNING->SOFT_FAIL`, `FAIL->HARD_FAIL`, `UNKNOWN->SOFT_FAIL` | warn/review on `SOFT_FAIL`, block on `HARD_FAIL` | depends on generated scan output freshness |
| `registry_doc_drift_status` | detects registry/doc drift | `PASS->INFO`, `WARNING->WARNING`, `FAIL->SOFT_FAIL`, `UNKNOWN->SOFT_FAIL` | warn on `WARNING`, block protected claims on `SOFT_FAIL` | depends on generated drift output freshness |
| `proof_output_naming_policy_status` | naming discipline presence guard | `PASS->INFO`, else `WARNING` | warn | static policy file presence |
| `hygiene_checklist_status` | completion preflight control surface | `PASS->INFO`, else `SOFT_FAIL` | block protected claims on `SOFT_FAIL` | static checklist presence |
| `constitution_status` freshness | detects stale constitutional snapshot risk | `fresh->INFO`, stale/missing inputs contribute to `SOFT_FAIL` or `UNKNOWN` | review/block depending on aggregate | runtime generation time + source freshness |
| `repo_control_status` freshness | ensures trust/sync/governance values are current | `FRESH->INFO`, `STALE->SOFT_FAIL`, `MISSING/PARSE_ERROR->SOFT_FAIL + unknown-critical` | block completion/certification until refresh | hard dependency on `HEAD` parity with snapshot |
| `sync_status` | sync discipline | `IN_SYNC->INFO`, `DRIFTED/BLOCKED->HARD_FAIL`, `UNKNOWN->SOFT_FAIL` | block on drift/block | runtime from repo control |
| `trust_status` | trust chain integrity | `TRUSTED->INFO`, `WARNING/UNKNOWN->SOFT_FAIL`, `NOT_TRUSTED->HARD_FAIL` | block on not-trusted | runtime from repo control |
| `governance_acceptance` | governance readiness gate | `PASS->INFO`, `PARTIAL/UNKNOWN->SOFT_FAIL`, `FAIL->HARD_FAIL` | block on fail/soft-fail for protected claims | runtime from repo control |

## Calibration Notes
- Calibration intentionally avoids new checks; it only hardens semantics of existing checks.
- `SOFT_FAIL` is used as the primary "refresh/review required" state.
- `UNKNOWN` remains an aggregation outcome, not a severity class.
