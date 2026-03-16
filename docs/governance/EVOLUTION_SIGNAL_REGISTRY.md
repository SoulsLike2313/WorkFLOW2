# EVOLUTION SIGNAL REGISTRY

Signal taxonomy for evidence-based maturity progression.

## Signal severity and weight model

- `POSITIVE`: contributes to readiness score.
- `BLOCKING`: prevents promotion regardless of score.
- Weight scale: `1..20` (higher = stronger impact).

## Positive signals

| signal_id | description | weight | maturity_mapping | evidence |
| --- | --- | --- | --- | --- |
| sync_in_sync | `HEAD == safe_mirror/main`, divergence `0/0` | 15 | V1_STABLE+ | git parity checks |
| worktree_clean | no uncommitted tracked changes at verdict time | 10 | V1_STABLE+ | `git status --short --branch` |
| governance_compliant | governance verdict `COMPLIANT` | 15 | V1_PLUS+ | repo control governance verdict |
| brain_stack_complete | all mandatory stack docs exist | 10 | V1_PLUS+ | file existence checks |
| evolution_layer_present | all evolution layer docs exist | 10 | V1_EVOLVING+ | file existence checks |
| contradictions_zero_critical | critical contradiction count = 0 | 10 | V1_PLUS+ | contradiction scan |
| admission_gate_green | admission verdict `ADMISSIBLE` | 10 | V1_EVOLVING+ | admission verdict |
| bundle_ready | exporter modes and docs available | 10 | V1_PLUS+ | bundle readiness check |
| mirror_artifacts_ready | safe mirror artifacts present and not blocked | 5 | V1_PLUS+ | mirror check |
| trust_not_failed | trust verdict not `NOT_TRUSTED` | 5 | V1_PLUS+ | trust verdict |

## Blocking signals

| signal_id | description | severity | blocking_scope | evidence |
| --- | --- | --- | --- | --- |
| false_pass_incident | proven false PASS claim unresolved | CRITICAL | blocks all promotion | self-audit incident evidence |
| unresolved_critical_contradiction | critical contradiction count > 0 | CRITICAL | blocks all promotion | contradiction report |
| hidden_blocker | blocker exists but omitted from report | CRITICAL | blocks all promotion | report vs check mismatch |
| repeated_drift_without_hardening | recurring drift with no corrective control update | HIGH | blocks V2 promotion | drift trend + policy log |
| broken_sync_discipline | sync verdict not `IN_SYNC` | CRITICAL | blocks all promotion | sync verdict |
| cosmetic_churn | repeated non-operational edits used as progress claims | HIGH | blocks V2 promotion | change review evidence |
| uncontrolled_experiment | experimental changes bypass contract gates | CRITICAL | blocks all promotion | gate failure evidence |

## Maturity mapping guidance

- `score < 55` -> hold in V1 range
- `55..74` -> `V1_EVOLVING` with `PREPARE`
- `75..89` -> `V2_CANDIDATE`
- `>=90` with zero blockers -> `V2_READY` / `PROMOTE`

## Evidence linkage rule

Every signal used in readiness computation must include:

1. command or artifact path
2. timestamp/run_id
3. pass/fail value
4. optional note for interpretation

No evidence linkage => signal cannot be counted.