# CODEX_OUTPUT_PRECEDENCE_MODEL

Status:
- status: `active`
- scope: `E:\CVVCODEX`
- model_version: `v1`

## Purpose

Define deterministic precedence for Codex response mode and reporting format.

## Canonical Precedence Order

From highest to lowest:

1. Repo reality and hard execution gates.
2. Repo-native output law surfaces:
   - `docs/governance/CODEX_OUTPUT_DISCIPLINE_V1.md`
   - `docs/governance/CODEX_RESULT_BLOCK_OUTPUT_LAW_V1.md`
   - `workspace_config/codex_output_mode_contract.json`
3. Canonical bootstrap/index anchors:
   - `README.md`
   - `MACHINE_CONTEXT.md`
   - `REPO_MAP.md`
   - `docs/INSTRUCTION_INDEX.md`
4. Task-specific canonical policy docs/contracts in scope.
5. Prompt-level formatting request in current task.

## Prompt-Level Override Rule

Prompt-level response formatting is not authoritative by default.

Allowed only when all are true:

1. override is explicit and unambiguous;
2. override is owner-level instruction for current task;
3. override does not violate repo hard law (safe mode, proof discipline, completion gates);
4. override is not conflicting with output safety requirements.

If conditions are not met, Codex must keep repo-native output mode.

## Default Output Behavior

1. chat stays ultra-short and navigation-only;
2. bounded fix/review/sync/packaging/verification replies use `fixed/touched/sync/path/essence/next`;
3. heavy detail stays in bundle/report artifacts;
4. exact artifact/bundle paths are shown from first reply;
5. large-task completion cannot be claimed without required bundle.

## Conflict Handling

If prompt format conflicts with repo-native output law:

1. keep repo-native mode;
2. state short limit note in chat;
3. place full evidence in bundle/report artifacts.
