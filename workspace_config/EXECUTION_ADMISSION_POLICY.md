# Execution Admission Policy (Hard Gate)

## Gate Statement

Codex is forbidden to start repository execution without a strict task contract.

If contract is incomplete or non-canonical, execution result must be:

```text
STATUS: REJECTED
REASON: insufficient-contract | non-canonical | out-of-scope
NO EXECUTION
```

## Required Contract Fields (All Mandatory)

A task is executable only if all fields are explicit:

1. `exact_goal`
2. `exact_target_scope`
3. `target_project_or_module`
4. `allowed_paths`
5. `forbidden_paths`
6. `expected_outputs`
7. `acceptance_criteria`
8. `validation_steps`
9. `do_not_do`
10. `task_mode` (`build` | `audit` | `validate` | `integrate` | `remove` | `report`)

No strict parameters equals no task acceptance.

## Admission States

Only three states are valid:

1. `REJECTED`
2. `PARTIAL_ACCEPTED`
3. `ACCEPTED`

State rules:

1. Missing required field: `REJECTED`.
2. Scope/path conflict: `REJECTED`.
3. Non-canonical workflow request: `REJECTED`.
4. Out-of-scope request: `REJECTED`.
5. Strict bounded subset only: `PARTIAL_ACCEPTED`.
6. Full strict contract and canonical alignment: `ACCEPTED`.

## Canonical Alignment Rules

Task execution is allowed only if request aligns with:

- `workspace_config/TASK_RULES.md`
- `workspace_config/TASK_SOURCE_POLICY.md`
- `docs/CURRENT_PLATFORM_STATE.md`
- `docs/NEXT_CANONICAL_STEP.md`

If request conflicts with any listed source, status is `REJECTED` with reason `non-canonical`.

## Forbidden Execution Behaviors

1. No side work.
2. No scope expansion.
3. No silent interpretation drift.
4. No unrequested artifacts.
5. No cross-project edits outside allowed paths.
6. No completion claim without acceptance criteria.
7. No confirmation claim without validation steps.
8. No broad creative execution asks without strict contract.

## Mandatory Refusal Format

```text
STATUS: REJECTED
REASON: insufficient-contract | non-canonical | out-of-scope
MISSING:
- <missing_parameter>
ACTION REQUIRED:
- resubmit task with strict parameters
NO EXECUTION
```

## Mandatory Partial Acceptance Format

```text
STATUS: PARTIAL_ACCEPTED
LIMITED_SCOPE:
- <confirmed_scope_item>
AMBIGUITIES:
- <ambiguity_item>
WILL_NOT_DO:
- anything outside confirmed scope
```

## Read Order Dependency

Admission gate is valid only after mandatory pre-task read order from `workspace_config/TASK_RULES.md` is completed.