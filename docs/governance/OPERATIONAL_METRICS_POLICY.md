# OPERATIONAL METRICS POLICY

Policy class: Governance v1.1 hardening measurement control.

Authority inputs:

- `docs/governance/DEVIATION_INTELLIGENCE_POLICY.md`
- `docs/governance/EVOLUTION_SIGNAL_REGISTRY.md`
- `docs/governance/PROMOTION_THRESHOLD_POLICY.md`

## 1) Improvement definition

Improvement is valid only if metrics show better control quality, not just more output volume.

## 2) Core mandatory metrics

1. contradiction rate
2. repeated failure rate
3. drift rate
4. sync stability
5. false PASS count
6. evidence completeness
7. trusted entry speed
8. governance compliance

## 3) Metric definitions

- contradiction rate: contradictions per cycle (`critical`, `major`).
- repeated failure rate: repeated incident classes per rolling window.
- drift rate: cycles with drift signals / total cycles.
- sync stability: share of cycles with divergence `0/0` and clean worktree.
- false PASS count: number of confirmed false PASS incidents.
- evidence completeness: required evidence fields present / required fields.
- trusted entry speed: time to reach `TRUSTED` after task start.
- governance compliance: percentage of cycles with `COMPLIANT` governance verdict.

## 4) Interpretation rules

1. single-cycle spikes do not define trend alone.
2. promotion decisions require observation window trends.
3. blocking metrics override positive aggregate score.

## 5) Misuse prevention

Forbidden metric misuse:

1. cherry-picking favorable cycles
2. ignoring blocking signal metrics
3. claiming improvement without baseline comparison
4. replacing evidence with narrative

## 6) Reporting requirement

Each full-check/evolution report must include:

1. current metric snapshot
2. change vs previous baseline
3. blocker metrics highlighted explicitly