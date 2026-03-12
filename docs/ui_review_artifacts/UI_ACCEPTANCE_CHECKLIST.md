# UI Acceptance Checklist

## Machine gate prerequisites
- [x] `ui_snapshot_runner` completed with `PASS`.
- [x] `ui_validate` completed with `PASS`.
- [x] `ui_doctor` (within validate) completed with `PASS`.
- [x] `manual_testing_allowed=true` in `ui_validation_summary.json`.

## Layout and interaction invariants
- [x] No overlaps reported by latest doctor run.
- [x] No hover-only critical controls reported.
- [x] No critical CTA visibility failures reported.
- [x] No out-of-bounds blockers reported.

## Walkthrough coverage
- [x] Dashboard visited.
- [x] Profiles visited.
- [x] Sessions visited.
- [x] Content visited.
- [x] Analytics visited.
- [x] AI Studio visited.
- [x] Audit visited.
- [x] Updates visited.
- [x] Settings visited.
- [x] Walkthrough trace saved (`ui_walkthrough_trace.json`).

## Required manual-only checks (not fully machine-verifiable)
- [ ] Semantic premium feel verification.
- [ ] Physical monitor contrast verification.
- [ ] Perceived motion smoothness verification.
