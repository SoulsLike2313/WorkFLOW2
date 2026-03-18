# NODE_RANK_SAFETY_TEST_MATRIX

- generated_at_utc: `2026-03-18T14:10:00Z`
- scope: `adversarial rank-safety cases after hardening`
- method: `observed_runtime + code_inference`

| # | case | expected rank | expected mode | expected denial/degradation | observed or inferred current behavior | result |
|---|---|---|---|---|---|---|
| 1 | Missing Emperor-only local proof | `PRIMARCH` | creator-grade | deny Emperor elevation | observed: `detect_node_rank` -> `PRIMARCH`, fail-closed reason includes missing emperor proof | `PASS` |
| 2 | Portable Primarch bundle copied to another machine | `ASTARTES` or `PRIMARCH` (never `EMPEROR`) | helper or creator (contract-dependent) | deny sovereign transfer by bundle copy | inferred: bundle/safe-mirror presence is non-elevating in validators and policy | `PARTIAL` |
| 3 | Missing external authority env var | `ASTARTES` | helper | deny creator/sovereign scope | observed: helper fallback with missing authority path | `PASS` |
| 4 | Invalid `creator_authority.json` | `ASTARTES` | helper | deny creator/sovereign scope | observed earlier in mode tests: marker invalid -> helper fallback | `PASS` |
| 5 | Unknown/stale constitution status | unchanged rank, narrowed claims | constrained | block protected claims | observed: stale/missing repo-control -> `PARTIAL/UNKNOWN`, completion blocked | `PASS` |
| 6 | Broken rank validator invocation | `UNKNOWN` or narrowed fallback | constrained | fail closed | inferred in chain integration: missing script maps to unknown + blocking signals | `PARTIAL` |
| 7 | Leftover files from another machine | no elevation by residue | constrained | deny rank expansion by residue | inferred: validator ignores portable residue for elevation | `PARTIAL` |
| 8 | Unsigned warrant/charter | no sovereign elevation | constrained | deny sovereign-sensitive claims | observed: sovereign claim denied when `signature_status != valid` | `PASS` |
| 9 | Astartes without warrant/charter attempting work | `ASTARTES` | helper | deny unchartered execution authority | policy now requires warrant/charter, but full runtime task-level enforcement is partial | `PARTIAL` |
| 10 | Primarch attempting sovereign claim | `PRIMARCH` | creator-grade non-sovereign | deny sovereign claim | observed: `check_sovereign_claim_denial` -> `DENY` | `PASS` |
| 11 | Helper node attempting creator-grade claim | `ASTARTES`/helper | helper | deny creator-grade claim | observed in mode contract and detection fallback behavior | `PASS` |
| 12 | Partial reintegration bundle attempting elevated authority | no elevation | review-only | reject/quarantine elevated attempt | observed earlier: partial handoff payload quarantined by review logic | `PASS` |
| 13 | Invalid issuer identity in inter-node document | no elevation | constrained | deny sovereign claims | observed: sovereign claim denied with `issuer_identity_status=invalid` | `PASS` |
| 14 | Unknown recipient/rank binding | no elevation | constrained | deny/hold until clarified | schema and policy define fields, but strict machine validation for this field is still partial | `PARTIAL` |
| 15 | Rank-check unavailable during admission | `UNKNOWN`/narrowed | constrained | fail closed | inferred: constitutional integration marks rank unknown as degraded/blocked input | `PARTIAL` |
| 16 | Workspace root not `E:\CVVCODEX` | not `EMPEROR` | narrowed | block sovereign elevation | implemented in rank validator, but not observed on this host due fixed root | `PARTIAL` |
| 17 | Safe mirror only present, no canonical local root | no elevation | constrained | deny sovereign authority | policy + validator logic treat safe mirror as non-elevating | `PASS` |
| 18 | Portable node with mirror docs but no sovereign proof | `PRIMARCH` or `ASTARTES` | constrained | deny Emperor | inferred/implemented: no sovereign proof => no Emperor | `PASS` |
| 19 | Canonical root present but proof missing | `PRIMARCH` | creator-grade non-sovereign | deny Emperor | observed: root valid + missing proof -> `PRIMARCH` | `PASS` |
| 20 | Wrong-root portable unpack with leftover authority artifacts | narrowed fallback | constrained | deny Emperor, narrow rank | implemented by root-validity gate; not directly observed | `PARTIAL` |

## Summary

- pass_count: `12`
- partial_count: `8`
- fail_count: `0`

Overall rank safety status: `PARTIAL` (strong fail-closed direction, but several cases are inferred rather than fully observed).
