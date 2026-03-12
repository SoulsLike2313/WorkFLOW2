# Task Rules (Hard Contract)

## Execution Gate (Mandatory Before Any Task)

Task execution is forbidden until Codex reads instruction/governance files in this exact order:

1. `README.md`
2. `workspace_config/workspace_manifest.json`
3. `workspace_config/codex_manifest.json`
4. `workspace_config/TASK_RULES.md`
5. `workspace_config/AGENT_EXECUTION_POLICY.md`
6. `workspace_config/MACHINE_REPO_READING_RULES.md`
7. `docs/INSTRUCTION_INDEX.md`
8. relevant `PROJECT_MANIFEST.json`
9. relevant project `README.md`
10. relevant `CODEX.md` (if present)
11. relevant `SYSTEM_MANIFEST.json` (if shared system is involved)

If this gate is not completed: task status is `REJECTED`.

## Rule 0

`No strict parameters = no task acceptance.`

## Required Task Contract

A task is accepted only if all fields below are explicit:

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

Canonical machine format:

- `workspace_config/task_manifest.schema.json`
- `workspace_config/TASK_INTAKE_REFERENCE.md`

## Acceptance States

Only these intake states are valid:

1. `REJECTED`
2. `PARTIAL_ACCEPTED`
3. `ACCEPTED`

Decision logic:

1. Missing required fields: `REJECTED`.
2. Conflicting boundaries (`allowed_paths` intersects `forbidden_paths`): `REJECTED`.
3. Undefined acceptance criteria or validation steps: `REJECTED`.
4. Partially strict contract with bounded subset: `PARTIAL_ACCEPTED`.
5. Fully strict and non-conflicting contract: `ACCEPTED`.

## Refusal Protocol (Machine-Enforced)

When rejected, response format is mandatory:

```text
STATUS: REJECTED
REASON: insufficient task contract
MISSING:
- <missing_parameter_1>
- <missing_parameter_2>
ACTION REQUIRED:
- resubmit task with strict parameters
```

## Partial Acceptance Protocol (Machine-Enforced)

When partially accepted, response format is mandatory:

```text
STATUS: PARTIAL_ACCEPTED
LIMITED_SCOPE:
- <only_confirmed_scope_item_1>
- <only_confirmed_scope_item_2>
AMBIGUITIES:
- <ambiguity_1>
- <ambiguity_2>
WILL_NOT_DO:
- anything outside confirmed scope
```

Execution rules for `PARTIAL_ACCEPTED`:

1. Scope expansion is forbidden.
2. Side work is forbidden.
3. Unrequested artifacts are forbidden.
4. Only confirmed scope is executable.

## Hard Prohibitions

1. No silent scope expansion.
2. No side work.
3. No unrequested artifacts.
4. No silent refactor outside scope.
5. No completion claim without acceptance criteria and validation evidence.
