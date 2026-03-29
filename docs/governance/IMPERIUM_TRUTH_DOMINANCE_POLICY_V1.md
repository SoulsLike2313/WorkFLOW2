# IMPERIUM_TRUTH_DOMINANCE_POLICY_V1

Status:
- class: `foundation_truth_safety_policy`
- mutability: `immutable_by_default`
- change_authority: `EMPEROR_ONLY`

Purpose:
- prevent stale/superseded surface mixing,
- define winner rules for dashboard truth lanes,
- keep freshness and authority explicit in live/system surfaces.

Core rule:
1. Every critical lane must have explicit dominance candidates.
2. Each candidate has `authority_tier`, `truth_class`, and freshness assessment.
3. Dashboard must show stale/missing state openly.
4. Stale surfaces must never be presented as current truth without warning.

Mandatory lanes:
1. control sync lane (`one_screen` + `repo_control`),
2. command/mission/task lane,
3. contradiction + owner-gate lane,
4. event + diff-preview lane.

Winner logic:
1. prefer primary authority candidates with non-stale freshness,
2. fallback only when primary is missing/stale and fallback exists,
3. mark lane as `STALE` or `MISSING` when no healthy winner exists.

Owner-facing requirement:
1. winner state is visible,
2. stale rule count is visible,
3. missing rule count is visible,
4. no fake green if stale rules remain.
