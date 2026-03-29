# CODEX_RESULT_BLOCK_OUTPUT_LAW_V1

## Status

- status: `active`
- scope: `E:\CVVCODEX`
- default_domain: `bounded_fix_review_sync_packaging_verification`

## Purpose

Normalize bounded-step Codex result replies into one compact, readable, low-noise shape.

## Canonical Result Block Order

For bounded fix/review/sync/packaging/verification steps, default reply order is mandatory:

1. `fixed`
2. `touched`
3. `sync`
4. `path`
5. `essence`
6. `next`

## Field Law

### `fixed`

- only core fix/result
- 1-2 short lines
- no broad retelling
- no repeated checks dump

### `touched`

- list layers, not long file inventory
- preferred layer forms:
  - `root`
  - `for_chatgpt`
  - `for_codex`
  - `mutable tracker`
  - `foundation tracker`
  - `refresh script`
  - `review registry`
  - `acceptance surfaces`
- one important concrete file may be added only when necessary

### `sync`

- value must be `PASS` or `FAIL`
- local domain status only
- never presented as global IMPERIUM closure

### `path`

- exactly one artifact entrypoint path
- clean, openable, no surrounding prose

### `essence`

- 2-3 words
- human-readable, compact
- no bureaucratic wording

### `next`

- one canonical next step
- no broad roadmap
- one arrow chain allowed if needed (for example `owner checkpoint review -> coverage blockers`)

## General Constraints

1. visual lightness first
2. short lines
3. no repeated wording
4. no broad retelling
5. no fake completion
6. if step is small, result block must be even shorter

## Compatibility Rule

This law governs bounded result replies.
Bundle-first evidence law remains active; detailed payload still belongs in artifact surfaces.

For large handoff-only outputs where owner explicitly requests receipt shape, `BUNDLE ROOT / DONE / NEXT` may be used.
Otherwise bounded domains default to this result block.

## Anchors

1. `docs/governance/CODEX_OUTPUT_DISCIPLINE_V1.md`
2. `workspace_config/codex_output_mode_contract.json`
3. `docs/governance/CODEX_OUTPUT_PRECEDENCE_MODEL.md`
4. `docs/governance/SYSTEM_ENTRYPOINT_V1.md`
5. `docs/governance/CANONICAL_TRUTH_REVIEW_BUNDLE_LAW_V1.md`
6. `docs/governance/SINGLE_ARTIFACT_ENTRYPOINT_RESPONSE_LAW_V1.md`
