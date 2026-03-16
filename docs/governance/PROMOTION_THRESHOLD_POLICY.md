# PROMOTION THRESHOLD POLICY

Policy class: Governance v1.1 hardening promotion control.

Authority inputs:

- `docs/governance/MODEL_MATURITY_MODEL.md`
- `docs/governance/EVOLUTION_SIGNAL_REGISTRY.md`
- `docs/governance/EVOLUTION_READINESS_POLICY.md`

## 1) Formal promotion criteria

Promotion (`V1 -> V2` and beyond) is allowed only when:

1. all blocking signals are zero
2. required observation window is complete
3. evidence thresholds are met
4. admission and sync discipline remain stable

## 2) Minimum evidence thresholds

Required minimum for promotion decision:

1. contradiction rate: no unresolved critical contradictions in observation window
2. false PASS count: zero
3. sync stability: parity maintained on all required completion cycles
4. evidence completeness: 100% mandatory evidence fields present
5. governance compliance: `COMPLIANT` on control checks

## 3) Observation window

Default minimum window:

- 5 consecutive clean cycles with `full-check` evidence.

A cycle is valid only if:

1. worktree clean at decision point
2. divergence `0/0`
3. no hidden blocker

## 4) Required successful cycles

- `candidate` declaration: at least 3 consecutive clean cycles.
- `ready` declaration: at least 5 consecutive clean cycles.
- `promote` declaration: at least 5 clean cycles + no blocking signal + explicit recommendation.

## 5) Required governance hardening evidence

At least one of the following within window:

1. policy gap closure with validation evidence
2. incident hardening update with verified effect
3. measurable drift/failure reduction confirmed by metrics

## 6) Declaration authority

- Candidate/ready status can be proposed by Repo Control Center evidence run.
- Final `PROMOTE` requires explicit approval in task contract.

## 7) Promotion forbidden conditions

Promotion forbidden if any is true:

1. unresolved critical contradiction
2. false PASS incident unresolved
3. broken sync discipline
4. hidden blocker
5. incomplete evidence package