# OPERATOR_QUERY_CONSISTENCY_REPORT

## Scope
Consistency/predictability audit for Operator Query Layer request classification and response contract stability.

## Covered Request Classes
- `mode_query`
- `authority_query`
- `workspace_health_query`
- `governance_query`
- `admission_query`
- `capability_query`
- `blocker_query`
- `next_step_query`
- `policy_reference_query`

## Checks Performed
1. Similar wording -> same request class routing.
2. Same request class -> same response contract shape.
3. Response contract vs governance baseline consistency.
4. Capability answers constrained by authority boundaries.
5. Blocker explanation category isolation:
   - authority limitation
   - governance non-compliance
   - sync failure
   - admission closure
   - evolution progression
6. Golden-pack routing replay:
   - source: `docs/review_artifacts/operator_golden_response_pack.json`
   - output: `runtime/repo_control_center/operator_query_consistency_check.json`

## Findings
- Golden routing replay result: `24/24` class matches, `0` mismatches.
- No response-shape contradictions detected.
- No authority-boundary violations in capability/authority classes.
- Blocker category and detail are consistently sourced from one-screen runtime status.

## Ambiguities Identified
- Multi-intent wording remains possible by design.
- Current precedence resolves overlaps deterministically with no golden-pack misroutes.

## Resolutions Applied
- Explicit precedence order defined in `OPERATOR_INTENT_ROUTING.md`.
- Fallback class fixed to `workspace_health_query`.
- Contract field naming fixed (`*_verdict`, `*_status`, `workspace_health`).

## Remaining Edge Cases
- Highly ambiguous multilingual mixed queries may require operator clarification.
- Current routing is pattern-based; semantic parser is intentionally out of scope for this stage.

## Verdict
Operator query layer is consistent for current baseline and golden test set.
