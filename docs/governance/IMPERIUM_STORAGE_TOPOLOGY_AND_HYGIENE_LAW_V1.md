# IMPERIUM_STORAGE_TOPOLOGY_AND_HYGIENE_LAW_V1

Status:
- class: `foundation_storage_law`
- mutability: `immutable_by_default`
- change_authority: `EMPEROR_ONLY`

Purpose:
- keep IMPERIUM storage topology controlled, reviewable, and continuity-safe before large execution waves.

Core law:
1. machine-local canonical root is `E:\CVVCODEX`,
2. bundle-first + repo-law-first + delta-only remain mandatory,
3. no direct destructive deletion in hygiene steps,
4. any confident trash goes to quarantine outside canonical root with manifest,
5. any ambiguous surface goes to explicit owner-review queue, not hidden.

Topology split:
1. immutable canon: `docs/governance/*`,
2. mutable active: `docs/review_artifacts/*`, `runtime/*`, execution surfaces,
3. dashboard-bound semantic/state surfaces: adapter/state JSON layers,
4. continuity/capsule: `docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/*`,
5. exports: `runtime/chatgpt_bundle_exports/*`,
6. quarantine: external non-canonical storage only,
7. owner review queue: explicit manifest surface.

Integrity law:
1. every storage-hygiene step must emit inventory/classification/integrity manifests,
2. moves/mirrors require source-to-target mapping,
3. no silent loss and no silent mismatch.

Optimization law:
1. optimize for read/search/index/write clarity, not cosmetic appearance,
2. separate hot-path and cold-path surfaces with explicit indexes,
3. allow two-disk migration preparation as placeholder only until validated.

Honesty boundary:
1. no fake completeness,
2. no fake migration validation,
3. no hardcoded/live confusion,
4. exact/derived/gap boundaries stay explicit.
