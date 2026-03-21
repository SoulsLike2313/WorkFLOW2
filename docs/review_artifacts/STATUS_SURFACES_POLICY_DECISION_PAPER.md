# STATUS_SURFACES_POLICY_DECISION_PAPER

## Decision Scope
- [OBSERVED] Problem class: tracked status/evidence files can re-dirty worktree and block `worktree_clean=true`.
- [OBSERVED] Target groups:
  - `runtime/repo_control_center/constitution_status.json`
  - `runtime/repo_control_center/constitution_status.md`
  - `workspace_config/SAFE_MIRROR_MANIFEST.json`
  - `docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md`

## Option Set

### Group A: `constitution_status.*`

#### Option A1: keep tracked and commit after each run
- Pros: latest snapshot always in Git history.
- Cons: verification loop re-dirties tree each run; heavy operational friction.
- Audit evidence impact: high freshness, low workflow stability.
- Green workflow impact: negative (self-dirty loop).
- Repo size/noise: high churn.

#### Option A2: keep tracked but stop default rewriting
- Pros: preserves canonical tracked surfaces; avoids loop dirtiness.
- Cons: requires explicit refresh intent when persisted snapshots are needed.
- Audit evidence impact: controlled, intentional snapshots.
- Green workflow impact: positive.
- Repo size/noise: moderate and intentional.

#### Option A3: convert to runtime-only untracked
- Pros: no tracked churn.
- Cons: weakens canonical persisted evidence chain expected by existing docs/scripts.
- Audit evidence impact: weaker external reproducibility.
- Green workflow impact: positive.
- Repo size/noise: low.

#### Option A4: move location / ignore policy workaround
- Pros: can reduce noise.
- Cons: contract/doc/script drift risk; requires broader refactor.
- Audit evidence impact: uncertain during migration.
- Green workflow impact: uncertain.
- Repo size/noise: uncertain.

#### Recommended for Group A
- [OBSERVED] Recommendation: **A2**.
- [OBSERVED] Implemented in this cycle: default no-write with explicit `--write-surfaces`.

---

### Group B: `SAFE_MIRROR_MANIFEST.json` + `SAFE_MIRROR_BUILD_REPORT.md`

#### Option B1: keep tracked and commit after each refresh
- Pros: keeps mirror evidence chain explicit and auditable.
- Cons: refresh must be intentional; otherwise unnecessary churn.
- Audit evidence impact: strong.
- Green workflow impact: neutral if refresh discipline is respected.
- Repo size/noise: moderate.

#### Option B2: keep tracked but stop rewriting
- Pros: stable tree.
- Cons: stale mirror evidence risk; can reduce trust quality.
- Audit evidence impact: degrades over time.
- Green workflow impact: can become negative (stale warning paths).
- Repo size/noise: low.

#### Option B3: convert to runtime-only untracked
- Pros: no tracked churn.
- Cons: breaks current tracked evidence contract and export assumptions.
- Audit evidence impact: weaker.
- Green workflow impact: uncertain, likely policy conflict.
- Repo size/noise: low.

#### Option B4: deprecate and replace
- Pros: can be cleaner long-term.
- Cons: out of scope for targeted closure; broad migration risk.
- Audit evidence impact: temporary ambiguity.
- Green workflow impact: risky short-term.
- Repo size/noise: unknown.

#### Recommended for Group B
- [OBSERVED] Recommendation: **B1** with strict trigger discipline: refresh only when intentionally closing mirror evidence cycle.

## Decision Summary
- [OBSERVED] Constitution surfaces policy: tracked + explicit-write only.
- [OBSERVED] Mirror evidence policy: tracked + intentional refresh/commit cycles only.
- [INFERRED] This combination preserves evidence strength while removing the verification-loop paradox.
