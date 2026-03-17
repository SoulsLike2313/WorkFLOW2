# CONSTITUTION_PHASE_MACHINE_ACCESS_REVIEW

## Scope
Low-risk machine-access and hygiene review for Constitution-first phase. No large refactor, no new implementation layer rollout.

## Improvement Candidates

### 1) Canonical Phase Header Consistency
- problem: phase signal previously diverged between narrative files.
- expected effect: faster machine/operator orientation (`mission accepted`, `constitution next`) in first read.
- risk: low.
- action window: do now.

### 2) Mission Registry Snapshot Drift Guard
- problem: `docs/governance/OPERATOR_MISSION_REGISTRY.md` can drift from JSON registry if regenerated manually.
- expected effect: reduces narrative-registry mismatch risk.
- risk: low.
- action window: after constitution stabilization (add lightweight regeneration/check script only if needed).

### 3) Runtime Truth Access Shortcut
- problem: key runtime truth files are spread across multiple docs.
- expected effect: one explicit pointer block in `MACHINE_CONTEXT.md` for mission/runtime truth surface reduces lookup latency.
- risk: low.
- action window: after constitution stabilization (small doc-only tweak).

### 4) Canonical Surface Contradiction Scan
- problem: stale phrases can survive phase transitions.
- expected effect: periodic grep-based contradiction scan before completion claims.
- risk: low.
- action window: after constitution stabilization (add to self-verification checklist, not new layer).

### 5) Proof Output Naming Discipline
- problem: runtime proof outputs can vary by ad-hoc names.
- expected effect: predictable bundle composition and lower export mistakes.
- risk: low.
- action window: after constitution stabilization (document naming convention, no refactor).

### 6) Bootstrap Compression Pointers
- problem: bootstrap lists are long and cognitively heavy.
- expected effect: better machine-access speed via compact pointer sections while preserving full read order.
- risk: medium (can introduce precedence ambiguity if over-compressed).
- action window: after constitution stabilization only.

## Immediate Recommendation Set
- apply now:
  - keep canonical phase header consistency in root narrative surfaces.
- defer until constitution stabilization:
  - registry snapshot drift guard
  - contradiction scan integration
  - proof output naming discipline
  - runtime truth shortcut block
  - bootstrap compression pointers (with precedence safeguards)

## Risk Notes
- no immediate high-risk machine-access blockers found.
- avoid introducing parallel “shortcut docs” that compete with canonical precedence.
- constitutional closure should be completed before automation of new hygiene gates.
