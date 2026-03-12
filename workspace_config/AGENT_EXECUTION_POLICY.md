# Agent Execution Policy (Strict Scope)

## Purpose
Define mandatory execution behavior for Codex in this repository.

## Mandatory Execution Sequence

Execution must always follow this order:

1. `scope_analysis`
2. `execution`
3. `validation`
4. `exact_output_delivery`

No step may be skipped.

## Phase 1: scope_analysis (Machine-Readable)

Before code changes:

1. Resolve task mode (`build` | `audit` | `validate` | `integrate` | `remove` | `report`).
2. Resolve exact target (`project/module/path`).
3. Resolve `allowed_paths` and `forbidden_paths`.
4. Resolve exact `expected_outputs`.
5. Resolve exact `acceptance_criteria`.

If any item is missing: do not accept full task execution.

## Phase 2: execution (Bounded)

1. Modify only files inside `allowed_paths`.
2. Do not modify files in `forbidden_paths`.
3. Do not run side workflows not requested in task scope.
4. Do not generate artifacts outside declared `expected_outputs`.

## Phase 3: validation (Required)

1. Execute listed validation commands only.
2. Report pass/fail per acceptance criterion.
3. If validation cannot run, return explicit blocked reason.

No "integration complete" claim is allowed without machine-run evidence.

## Phase 4: exact_output_delivery

1. Return only requested deliverables.
2. Include exact changed files and exact validation outcomes.
3. Mark unresolved criteria explicitly.

## Hard Restrictions

1. No scope drift.
2. No silent refactor outside target scope.
3. No hidden expansion of requirements.
4. No unrelated cleanup without explicit approval.
5. No implicit cross-project edits.

## Project and Module Isolation

1. If task targets one project, other projects are read-only.
2. If task targets one module, sibling modules are read-only.
3. Cross-project or cross-module changes require explicit task parameters.

## External Unrelated Changes

If unrelated local changes are detected:

1. Mark them as `external_unrelated_changes`.
2. Do not revert them.
3. Do not mix them into task claims.

## Decision States

Allowed execution states:

1. `accepted`
2. `partial_accepted`
3. `blocked`
4. `completed`
5. `completed_with_gaps`

These states must map to explicit evidence (changes + validation outputs).
