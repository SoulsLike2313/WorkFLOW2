# CODEX_OUTPUT_DISCIPLINE_V1

## Status

- status: `active`
- scope: `E:\CVVCODEX`
- default regime: `ultra_short_chat + bundle_first_detail_delivery`

## Purpose

Set a stable output discipline so operator chat remains short while full technical context is delivered through bundle/report artifacts.

## Output Law Precedence

Output mode must be derived from repository law, not ad-hoc prompt formatting.

Precedence:

1. repo reality + hard execution gates,
2. `docs/governance/CODEX_OUTPUT_DISCIPLINE_V1.md`,
3. `workspace_config/codex_output_mode_contract.json`,
4. task-specific canonical contracts,
5. prompt-level formatting request.

Prompt-level format override is allowed only as explicit owner override and only when it does not violate repository hard law.

## Default Output Contract

Codex default behavior in this workspace:

1. Chat output is ultra-short by default.
2. Detailed explanation goes to bundle/report surfaces.
3. For large tasks, bundle is the primary answer surface.
4. Chat stays navigation-only.
5. This default persists until user explicitly overrides it.
6. Large-task result is not considered closed if required bundle is not produced.
7. First chat response after execution must include exact bundle/artifact paths.
8. For bounded fix/review/sync/packaging/verification domains, hard result block shape is:
   - `fixed`
   - `touched`
   - `sync`
   - `path`
   - `essence`
   - `next`
9. For explicit large handoff-receipt mode, compact shape may be:
   - `BUNDLE ROOT`
   - `DONE`
   - `NEXT`
10. Any longer A/B/C/... dump in chat is a contract violation unless explicit owner override exists.

## Single Artifact Entrypoint Doctrine

Default external response form must expose exactly one artifact entrypoint path.

Allowed forms:
1. one primary bundle path, or
2. one step-folder path (when folder is the best carrier for multiple internal artifacts).

Not allowed by default:
1. scattering many bundle paths in chat,
2. long companion file lists in chat,
3. long artifact inventory dumps in chat.

Complex structure stays inside bundle/folder artifacts, not in chat surface.
Different behavior is allowed only by explicit sovereign/owner override.

## Permanent Limit Economy Link

Output discipline is executed under permanent limit economy mode:

1. repetition is compressed by default,
2. truth/evidence is never compressed away,
3. CORE stays in repo law surfaces, prompts carry DELTA.

Anchor:
- `docs/governance/LIMIT_ECONOMY_MODE_LAW_V1.md`
- `workspace_config/limit_economy_mode_contract.json`

## Chat Surface Rules

Chat response must stay receipt-only by default:

1. bounded domains default:
   - `fixed` (1-2 short lines)
   - `touched` (layers only)
   - `sync` (`PASS` or `FAIL`)
   - `path` (single entrypoint path)
   - `essence` (2-3 words)
   - `next` (one canonical next step)
2. large handoff receipt fallback:
   - `BUNDLE ROOT`
   - `DONE`
   - `NEXT`

Hard constraints:

1. no long execution summary in chat;
2. no long artifact list in chat;
3. no zip inventory in chat;
4. no mirrored integration report in chat.
5. no long touched file lists; prefer touched layers.

All detailed truth/evidence/validation content must live inside bundle root surfaces.

Allowed deviation:

1. explicit sovereign/owner override only.

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
2. for canonical review steps, `chatgpt_transfer/` package must be generated under step root as operator upload surface.
3. `chatgpt_transfer/` packaging mode:
   - segmented `core/visual/optional`,
   - split target `32 MB` (allowed range `20-40 MB`),
   - wave target `<= 9` parts for operator upload.

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

## Prompt-Level Conflict Rule

If prompt formatting conflicts with this policy:

1. keep repository output mode;
2. state short limitation note in chat;
3. place complete evidence in bundle/report artifacts.

## Non-Goals

This policy does not replace TTL retention mechanics; lifecycle cleanup is defined separately.

## Anchors

- `workspace_config/codex_output_mode_contract.json`
- `workspace_config/review_bundle_output_contract.json`
- `docs/governance/MANUAL_SAFE_BUNDLE_STANDARD.md`
- `workspace_config/bundle_fallback_contract.json`
- `docs/governance/CODEX_OUTPUT_PRECEDENCE_MODEL.md`
- `docs/governance/OUTPUT_MODE_HARDENING_V1.md`
- `docs/governance/LIMIT_ECONOMY_MODE_LAW_V1.md`
- `docs/governance/CORE_DELTA_PROMPT_DISCIPLINE_V1.md`
- `docs/governance/SHORT_FIRST_REPLY_LAW_V1.md`
- `docs/governance/VNEXT_PROMPT_COMPRESSION_PROFILE_V1.md`
- `docs/governance/SINGLE_ARTIFACT_ENTRYPOINT_RESPONSE_LAW_V1.md`
- `docs/governance/CHECKPOINT_CAPSULE_CONTEXT_COMPRESSION_LAW_V1.md`
- `docs/governance/OWNER_CHATGPT_CODEX_ECONOMY_WORKFLOW_V1.md`
- `docs/governance/EPHEMERAL_BUNDLE_TTL_POLICY_V1.md`
- `docs/governance/CODEX_RESULT_BLOCK_OUTPUT_LAW_V1.md`
- `workspace_config/limit_economy_mode_contract.json`
- `MACHINE_CONTEXT.md`
- `REPO_MAP.md`
- `docs/INSTRUCTION_INDEX.md`
