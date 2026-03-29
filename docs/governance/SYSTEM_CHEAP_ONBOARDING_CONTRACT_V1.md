# SYSTEM_CHEAP_ONBOARDING_CONTRACT_V1

Status:
- class: `foundation_onboarding_contract`
- mutability: `immutable_by_default`
- change_authority: `EMPEROR_ONLY`
- default_mode: `entrypoint_first_no_bundle_archaeology`

## Purpose

Set a cheap, deterministic system-entry contract for new chat/Codex/owner review.

## Contract levels

### Level U: Ultra-short onboarding

Goal:
1. identify source of truth,
2. split foundation vs mutable,
3. locate current active primary truth line.

Required read path:
1. `docs/governance/SYSTEM_ENTRYPOINT_V1.md`
2. `docs/governance/FOUNDATION_VS_MUTABLE_READING_GUIDE_V1.md`
3. `docs/governance/FOUNDATION_INDEX_V1.md`
4. `docs/governance/LIVE_SYSTEM_INDEX_V1.md`
5. current step primary declaration in `docs/review_artifacts/*PRIMARY_BUNDLE_DECLARATION*`.
6. current transfer capsule in `docs/review_artifacts/*TRANSFER_CAPSULE*` when available.
7. `docs/governance/VNEXT_PROMPT_COMPRESSION_PROFILE_V1.md` (for compact prompt/response floor).

Expected output:
1. one active primary truth channel,
2. explicit companion disclosure,
3. explicit open risks.

### Level N: Normal onboarding

Goal:
1. run bounded execution/review without re-reading whole history.

Required read path:
1. Level U,
2. `docs/INSTRUCTION_INDEX.md`,
3. `REPO_MAP.md`,
4. `MACHINE_CONTEXT.md`,
5. current step review index + validation + remaining gaps.

Expected output:
1. bounded step scope,
2. one-primary-bundle discipline preserved,
3. no stale-bundle ambiguity.

### Level D: Deep onboarding

Goal:
1. audit-level interpretation with full boundary awareness.

Required read path:
1. Level N,
2. constitutional/governance stack via instruction index,
3. active primary bundle (latest + timestamped) + required companion,
4. declared historical anchors only if explicitly needed.

Expected output:
1. evidence-linked verdict,
2. explicit remainder/gap map,
3. no false completeness claim.

## Hard rules

1. no bundle archaeology before Level U completion,
2. no broad history retelling in chat by default,
3. no replacement of foundation law by mutable projection,
4. no completion claims without repo-visible evidence,
5. one primary truth bundle per active step is mandatory.
6. external chat response exposes one artifact entrypoint path by default.
7. short handoff form is fixed:
   `CURRENT PRIMARY TRUTH` (name-only) + `ARTIFACT PATH` (one-path-only).
8. capsule is cheap entry aid and must not be replaced by broad history retelling.

## Known boundaries

1. reference-brain meta-index layer remains `PARTIALLY_CLEAN`,
2. skipped lineage history remains disclosed and must not be hidden.

## Anchors

1. `docs/governance/SYSTEM_ENTRYPOINT_V1.md`
2. `docs/governance/SYSTEM_ONBOARDING_READING_ORDER_V1.md`
3. `docs/governance/CANONICAL_TRUTH_REVIEW_BUNDLE_LAW_V1.md`
4. `docs/governance/LIMIT_ECONOMY_MODE_LAW_V1.md`
5. `docs/governance/SINGLE_ARTIFACT_ENTRYPOINT_RESPONSE_LAW_V1.md`
6. `docs/governance/PRIMARY_TRUTH_NAME_AND_SINGLE_ARTIFACT_PATH_RESPONSE_CONTRACT_V1.md`
