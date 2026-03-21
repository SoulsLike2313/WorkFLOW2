# CODEX_OUTPUT_DISCIPLINE_V1

## Status

- status: `active`
- scope: `E:\CVVCODEX`
- default regime: `ultra_short_chat + bundle_first_detail_delivery`

## Purpose

Set a stable output discipline so operator chat remains short while full technical context is delivered through bundle/report artifacts.

## Default Output Contract

Codex default behavior in this workspace:

1. Chat output is ultra-short by default.
2. Detailed explanation goes to bundle/report surfaces.
3. For large tasks, bundle is the primary answer surface.
4. Chat stays navigation-only.
5. This default persists until user explicitly overrides it.
6. Large-task result is not considered closed if required bundle is not produced.

## Chat Surface Rules

Chat response should stay compressed and operator-friendly, preferably in this order:

1. `STATUS`
2. `WHAT WAS CHANGED`
3. `BUNDLES / FILES`
4. `IMPORTANT LIMIT`
5. `NEXT STEP`

Chat should not carry long doctrine analysis, matrices, deep diff walkthroughs, or broad evidence dumps when bundle is present.

## Bundle-First Rules

Use bundle/report artifacts as primary detail carrier for:

1. full reviews and audits
2. architecture analysis
3. inventory/history recovery
4. contradiction/gap maps
5. large verification chains
6. multi-file implementation rationale
7. doctrine/policy comparison
8. evidence-heavy status proofs

Closure rule:
1. if task class is large and bundle is required, completion claim is invalid until bundle exists and is referenced.

## What Must Go To Bundle

When bundle-first mode is active, place these in bundle/report surfaces:

1. detailed technical reasoning
2. proof chains and check outputs
3. diff summaries and file-by-file rationale
4. matrices, maps, inventories, and registries
5. risk and gap tables
6. safe-redacted summaries and exclusions maps

## When Bundle Is Not Required

Bundle may be skipped for small bounded tasks when all of the following are true:

1. change scope is tiny and self-evident
2. no large review/explainability payload is needed
3. no sensitive exclusion mapping is needed

If skipped, Codex must state this briefly in chat.

## Safe-Mode / Protected Content Handling

If bundle is needed but policy blocks direct export of some content:

1. chat: short notice that safe-mode limits apply
2. bundle: include safe summary, redacted summary, and exclusions map
3. no protected artifact leakage

Missing-bundle rule:
1. if bundle is required but not produced, status must be `PARTIAL` or `BLOCKED` (never `DONE`).

## Non-Goals

This policy does not define bundle lifecycle cleanup (for example, deleting bundles older than 24h).

## Anchors

- `workspace_config/codex_output_mode_contract.json`
- `docs/governance/MANUAL_SAFE_BUNDLE_STANDARD.md`
- `workspace_config/bundle_fallback_contract.json`
- `MACHINE_CONTEXT.md`
- `REPO_MAP.md`
- `docs/INSTRUCTION_INDEX.md`
