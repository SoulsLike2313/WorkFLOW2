# IMPERIUM_DIFF_PREVIEW_PIPELINE_CANON_V1

Status:
- class: `foundation_diff_preview_pipeline`
- mutability: `immutable_by_default`
- change_authority: `EMPEROR_ONLY`
- implementation_state: `bounded_repeatable_pipeline_active_not_full_auto_preview`

Purpose:
- provide repeatable before/after preview and diff evidence for dashboard/factory changes,
- reduce manual review friction while preserving truth parity.

Pipeline stages:
1. capture stage (`Playwright visual audit loop`),
2. pairing stage (before/after run selection),
3. diff manifest stage (file/hash/change map),
4. contact-sheet stage (review-friendly visual pack),
5. dashboard-binding stage (preview meta and changed-sector signal).

Required outputs:
1. full-page screenshots (command/fullvision),
2. major-zone screenshots,
3. paired html/json dumps,
4. diff manifest with changed/unchanged/missing sectors,
5. contact-sheet or equivalent review surface,
6. explicit blocked/not-yet-implemented disclosure.

Resource law:
1. bounded generation by explicit run (not heavy background watcher),
2. changed-sector focus over full historical recomputation,
3. no fake claim of fully automatic preview pipeline.

Boundary:
1. diff/preview surfaces are review aids, not completion proofs,
2. missing auto pipeline parts must remain explicit,
3. technical disclosure must remain accessible from source paths and manifests.

