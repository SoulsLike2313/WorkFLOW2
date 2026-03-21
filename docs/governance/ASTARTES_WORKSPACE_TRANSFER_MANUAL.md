# ASTARTES_WORKSPACE_TRANSFER_MANUAL

Status:
- manual_version: `v1`
- scope: `repo-only transfer with no elevation material`

## Procedure

1. copy canonical repo workspace 1:1;
2. keep genome bundle unset;
3. keep local sovereign substrate unset;
4. run rank detection script.

## Expected Result

1. `detected_rank=ASTARTES` when repo-copy anchors are valid.

## Hard Guard Expectations

1. ASTARTES must not pass `primarch_rank_claim`;
2. ASTARTES must not pass `emperor_rank_claim`;
3. ASTARTES must not pass sovereign mutation claims.
