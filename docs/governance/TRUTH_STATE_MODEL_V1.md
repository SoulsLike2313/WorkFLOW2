# TRUTH_STATE_MODEL_V1

## Canonical Enum
- `fact`
- `hypothesis`
- `proposal`
- `decision`
- `certified_result`
- `stale`
- `rejected`
- `superseded`
- `unknown`

Schema source:
- `workspace_config/schemas/truth_state_schema.json`

## Meaning
- `fact`: repo-visible and verifiable current claim.
- `hypothesis`: unverified claim pending evidence.
- `proposal`: intended action/change pending decision.
- `decision`: explicit accepted/rejected determination with basis.
- `certified_result`: decision that passed required review/certification gates.
- `stale`: outdated relative to newer canonical evidence.
- `rejected`: denied by authority/policy/preconditions/validation.
- `superseded`: replaced by newer accepted canonical item.
- `unknown`: insufficient evidence to classify.

## Forbidden Conflations
- `fact` is not `certified_result`.
- `proposal` is not `decision`.
- `stale` is not `superseded`.
- `unknown` is not `rejected`.

## Allowed Transitions (Compact)
- `hypothesis -> proposal|fact|rejected|unknown`
- `proposal -> decision|rejected|stale`
- `fact -> decision|stale|superseded`
- `decision -> certified_result|rejected|superseded`
- `certified_result -> superseded|stale`
- `unknown -> hypothesis|proposal|fact|rejected`
- `rejected -> proposal|superseded`
- `stale -> superseded`

## Non-Transitions (Blocked)
- `unknown -> certified_result`
- `proposal -> certified_result`
- `rejected -> certified_result`
- `stale -> certified_result`

## Relation To Evidence / Review / Certification
- evidence is required for `fact`, `decision`, and `certified_result`.
- review/certification gates are required for `certified_result`.
- completion claims must reference `certified_result`-grade evidence chains when certification is required.
