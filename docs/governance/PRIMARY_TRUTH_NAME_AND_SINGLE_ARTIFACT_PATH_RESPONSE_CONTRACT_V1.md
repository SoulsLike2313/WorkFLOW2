# PRIMARY_TRUTH_NAME_AND_SINGLE_ARTIFACT_PATH_RESPONSE_CONTRACT_V1

## Status

- status: `active`
- scope: `E:\CVVCODEX`
- default_mode: `name_only_primary_truth_plus_single_path`

## Purpose

Lock exact short external handoff form for Codex responses in vNext.

## Canonical Short Form

Bounded step default output form (fix/review/sync/packaging/verification):

1. `fixed`
2. `touched`
3. `sync`
4. `path` -> exactly one entrypoint path
5. `essence`
6. `next`

Large handoff receipt fallback:

1. `BUNDLE ROOT`
2. `DONE`
3. `NEXT`

This one path may be:
1. one primary bundle path, or
2. one step-folder path in folder fallback mode.

## Folder Fallback Boundary

When folder-mode is used:

1. `path`/`BUNDLE ROOT` points to one step-folder path only,
2. companion/internal detail stays inside bundle surfaces.

## Companion Boundary

Required companions do not disappear.
They remain explicit in bundle declaration/review surfaces.
Default short chat response must not list companion paths as a scattered external list.

## Override Boundary

Different external format is allowed only by explicit sovereign/owner override.

## Anchors

1. `docs/governance/SINGLE_ARTIFACT_ENTRYPOINT_RESPONSE_LAW_V1.md`
2. `docs/governance/SHORT_FIRST_REPLY_LAW_V1.md`
3. `docs/governance/CANONICAL_TRUTH_REVIEW_BUNDLE_LAW_V1.md`
4. `docs/governance/SYSTEM_ENTRYPOINT_V1.md`
5. `docs/governance/CODEX_RESULT_BLOCK_OUTPUT_LAW_V1.md`
