# Agent Execution Policy (Machine-Enforced)

## Rule 1: Pre-Task Read Gate

Codex must not execute any task until the read order defined in:

- `workspace_config/TASK_RULES.md`
- `workspace_config/MACHINE_REPO_READING_RULES.md`

is completed.

If read gate is not completed: status is `REJECTED`.

## Rule 2: Strict Contract Gate

Codex must reject tasks without strict parameters.

Missing any of the following is a hard rejection:

1. exact goal
2. exact target scope
3. target project or module
4. allowed paths
5. forbidden paths
6. expected outputs
7. acceptance criteria
8. validation steps
9. explicit do-not-do block

Without exact target scope, code changes are forbidden.

## Rule 3: Mandatory Execution Sequence

Execution order is fixed:

1. `scope_analysis`
2. `contract_verdict` (`REJECTED` | `PARTIAL_ACCEPTED` | `ACCEPTED`)
3. `bounded_execution`
4. `validation_execution`
5. `exact_output_delivery`

Skipping or reordering is forbidden.

## Rule 4: Refusal Behavior

On rejection, Codex must emit exact refusal format:

```text
STATUS: REJECTED
REASON: insufficient task contract
MISSING:
- <missing_parameter_1>
- <missing_parameter_2>
ACTION REQUIRED:
- resubmit task with strict parameters
```

## Rule 5: Partial Acceptance Behavior

If and only if a bounded subset is strict, Codex may use `PARTIAL_ACCEPTED`.

Mandatory output format:

```text
STATUS: PARTIAL_ACCEPTED
LIMITED_SCOPE:
- <confirmed_scope_item_1>
- <confirmed_scope_item_2>
AMBIGUITIES:
- <ambiguity_1>
- <ambiguity_2>
WILL_NOT_DO:
- anything outside confirmed scope
```

## Rule 6: Bounded Execution Controls

1. No side work.
2. No silent scope expansion.
3. No unrequested artifacts.
4. No silent refactor outside allowed paths.
5. No cross-project edits unless explicitly in scope.
6. No cross-module edits unless explicitly in scope.

## Rule 7: Validation and Completion Controls

1. Without acceptance criteria, completion claim is forbidden.
2. Without validation steps, confirmation claim is forbidden.
3. Validation must run against declared validation steps.
4. Any unmet criterion must be reported as failed, not omitted.

## Rule 8: External Unrelated Changes

If external unrelated changes are detected:

1. Mark as `external_unrelated_changes`.
2. Keep excluded from task scope and task claims.
3. Do not revert unless explicitly requested.
