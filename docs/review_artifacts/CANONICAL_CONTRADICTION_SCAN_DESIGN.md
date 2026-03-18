# CANONICAL_CONTRADICTION_SCAN_DESIGN

## Scope
Design and current implementation contract for:
- `scripts/validation/scan_canonical_contradictions.py`

## Surfaces Scanned
- `docs/CURRENT_PLATFORM_STATE.md`
- `docs/NEXT_CANONICAL_STEP.md`
- `README.md`
- `REPO_MAP.md`
- `MACHINE_CONTEXT.md`
- `docs/INSTRUCTION_INDEX.md`

## Contradiction Classes
- `phase_conflict` (FAIL): different current-phase claims across canonical surfaces.
- `next_step_conflict` (FAIL): conflicting explicit next-step claims.
- `mission_status_conflict` (FAIL): mission layer marked both accepted and pending.
- `stale_phrase_detected` (FAIL): stale routing phrases contradict constitution-first routing.
- `phase_claim_missing` (WARNING): surface without explicit phase marker.
- `phase_not_constitution_first` (WARNING): phase claim not aligned with constitution-first.

## Warning vs Fail
- FAIL:
  - direct conflict between canonical claims;
  - stale phrase that contradicts current routing;
  - mixed mission status semantics.
- WARNING:
  - missing claim or weak explicitness without direct conflict.

## Current Implementation Depth
- implemented now:
  - phase claim extraction
  - next-step claim extraction
  - mission accepted/pending conflict detection
  - stale phrase detection
  - JSON report + machine exit code
- not yet covered:
  - deep semantic contradiction detection in long-form prose
  - cross-check against runtime state semantics
  - per-section source-precedence weighting in scan output

## Execution Points
- pre-completion / pre-certification check
- before final sync push for canonical narrative changes
- optional in CI-style validation chain once approved

## Output Contract
- default output:
  - `runtime/repo_control_center/validation/canonical_contradiction_scan.json`
- verdict values:
  - `PASS`
  - `WARNING`
  - `FAIL`
