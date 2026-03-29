# SINGLE_ARTIFACT_ENTRYPOINT_RESPONSE_LAW_V1

## Status

- status: `active`
- scope: `E:\CVVCODEX`
- default_mode: `single_external_artifact_path`

## Purpose

Keep external response surface deterministic and cheap:
one chat-facing artifact path per bounded step.

## Core Rule

By default, Codex must return exactly one external artifact entrypoint path.

Allowed:
1. one primary bundle path, or
2. one step-folder path containing internal bundles/reports/companions/indexes.

## Primary Truth Name + Single Path Contract

Bounded result-block domain (fix/review/sync/packaging/verification) must use:

1. `fixed`
2. `touched`
3. `sync`
4. `path` (single artifact entrypoint)
5. `essence`
6. `next`

Large handoff fallback form may use:

1. `BUNDLE ROOT`
2. `DONE`
3. `NEXT`

In step-folder fallback mode:
1. `path` or `BUNDLE ROOT` points to one step-folder path,
2. companion/internal complexity stays inside review surfaces.

## Why

1. removes path-sprawl in chat,
2. keeps bundle-first discipline intact,
3. reduces limit waste on listing internals,
4. preserves one clear handoff point for owner/ChatGPT.

## Internal Complexity Rule

Rich structure is allowed internally:
1. companions,
2. reports,
3. manifests,
4. validation chains,
5. indexes.

But this complexity is disclosed inside artifact surfaces, not as a long chat list.

## Companion Handling

Companion dependencies remain mandatory when required by truth law.
They must be declared inside the artifact review surfaces.
Chat still exposes one external path by default and must not list companion paths in short reply unless explicit sovereign/owner override is issued.

## Exception

Multiple external artifact paths are allowed only by explicit sovereign/owner override.

## Non-Goals

1. does not ban rich internal packaging,
2. does not replace one-primary-bundle law,
3. does not permit hidden dependencies or false completeness claims.

## Anchors

1. `docs/governance/CODEX_OUTPUT_DISCIPLINE_V1.md`
2. `docs/governance/CANONICAL_TRUTH_REVIEW_BUNDLE_LAW_V1.md`
3. `docs/governance/SHORT_FIRST_REPLY_LAW_V1.md`
4. `docs/governance/SYSTEM_ENTRYPOINT_V1.md`
5. `docs/governance/CODEX_RESULT_BLOCK_OUTPUT_LAW_V1.md`
