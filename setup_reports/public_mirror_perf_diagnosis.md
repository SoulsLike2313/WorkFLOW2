# Public Mirror Performance Diagnosis

- generated_at_utc: 2026-03-15T11:39:25.4678878Z
- source_path: E:/CVVCODEX
- mirror_path: E:\_public_repo_mirror\WorkFLOW
- strategy: FAST_RESUME_STAGED
- status: PASS

## Bottlenecks
- High file count with many small files across projects/docs/runtime artifacts
- Heavy tail directories runtime and setup_assets increase full-pass duration
- Single-pass full-tree sync causes delayed usable result

## Staged Strategy
- STAGE_A_USABLE
- STAGE_B_INCREMENTAL
- STAGE_C_HEAVY_TAIL_OPTIONAL

## Stage A Focus
- README*
- docs
- workspace_config
- scripts
- projects
- setup_reports
- shared_systems

## Heavy Tail Paths
- runtime
- setup_assets

## Acceleration Measures
- robocopy /MT:32 with low retry/wait (/R:1 /W:1)
- stage time budgets with checkpoint snapshots
- PUBLIC_* state files emitted in STAGE_A
- incremental sync from existing mirror baseline
