# SHORT_FIRST_REPLY_LAW_V1

## Status

- status: `active`
- scope: `E:\CVVCODEX`
- default_mode: `very_short_first_reply`

## Purpose

Keep first chat reply compact without losing operator control or review traceability.

## Mandatory First Reply Payload

For bounded fix/review/sync/packaging/verification steps, first reply must contain only:

1. `fixed`
2. `touched`
3. `sync`
4. `path`
5. `essence`
6. `next`

Large handoff-receipt fallback may use:

1. `BUNDLE ROOT`
2. `DONE`
3. `NEXT`

This bounded result-block format is the safe lower bound for short external chat handoff.
Further compression is allowed only inside wording, not by removing required blocks.

Default one-path form:
1. primary bundle latest path, or
2. step-folder path (when folder-mode is canonically chosen).

Required details (timestamped zip / companion / internals) stay inside artifact review surfaces unless owner explicitly requests expanded external listing.
Default short response must not include multi-path companion listing.

## Detail Placement Rule

Long details must go to artifacts:

1. review index,
2. integration report,
3. validation report,
4. contradiction delta/remainder report,
5. remaining gaps report,
6. artifact manifest.

## Path Integrity Rule

Short mode is invalid if exact paths are missing.
Compression may reduce words, never path precision.

## Override

Expanded first reply is allowed only with explicit owner request.
Even then, exact paths remain mandatory.

## Linked Law

- `docs/governance/CODEX_OUTPUT_DISCIPLINE_V1.md`
- `docs/governance/CODEX_RESULT_BLOCK_OUTPUT_LAW_V1.md`
- `docs/governance/LIMIT_ECONOMY_MODE_LAW_V1.md`
- `docs/governance/SINGLE_ARTIFACT_ENTRYPOINT_RESPONSE_LAW_V1.md`
- `docs/governance/PRIMARY_TRUTH_NAME_AND_SINGLE_ARTIFACT_PATH_RESPONSE_CONTRACT_V1.md`
- `docs/governance/VNEXT_PROMPT_COMPRESSION_PROFILE_V1.md`
