# Public Mirror Performance Diagnosis

- generated_at_utc: 2026-03-15T10:56:53.8462642Z
- status: PASS
- source_path: E:\CVVCODEX
- mirror_path: E:\_public_repo_mirror\WorkFLOW

## Observed Bottlenecks

- monolithic full-pass sync timed out before delivering early usable mirror
- full recursive inventory / full manifest in critical path increased runtime
- heavy trees (`runtime`, `setup_assets`, local `.venv`, legacy `shortform_core`) dominated cost
- long operations lacked practical intermediate readiness checkpoints

## Fast Mode Fix

- staged strategy implemented: Stage A (usable) -> Stage B (incremental) -> Stage C (heavy tail)
- each stage has time budget and log
- PUBLIC_* state files are created in early stage
- heavy tail is deferred by default and does not block engineering-ready state
- progress snapshots are written to setup_reports/public_mirror_progress_status.{json,md}
