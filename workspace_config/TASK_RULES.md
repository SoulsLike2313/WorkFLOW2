# Task Rules (Machine-Gated)

## Rule 0: Hard Gate
`No strict parameters = no task acceptance.`

Any serious task is blocked until all required parameters are present and unambiguous.

## Required Task Parameters

A task is accepted only if it explicitly defines:

1. `target_scope`
2. `exact_goal`
3. `exact_project_or_module`
4. `allowed_files_or_folders`
5. `forbidden_areas`
6. `expected_outputs_or_artifacts`
7. `acceptance_criteria`
8. `mode` (`build` | `audit` | `validate` | `integrate` | `remove` | `report`)
9. `do_not_do`

For machine tasks, the canonical structure is:

- `workspace_config/task_manifest.schema.json`

## Acceptance Decision States

Only these states are valid:

1. `ACCEPTED`
2. `PARTIAL_ACCEPTED`
3. `REJECTED`

Decision logic:

1. If any required parameter is missing: `REJECTED`.
2. If parameters conflict (`allowed_paths` intersect `forbidden_paths`): `REJECTED`.
3. If goal is broad but one safe subset is explicitly bounded: `PARTIAL_ACCEPTED` (execute only the bounded subset).
4. If all required parameters are strict and non-conflicting: `ACCEPTED`.

## Ambiguity Handling

If the request is ambiguous:

1. Do not expand scope by assumption.
2. Do not perform side work.
3. Execute only the confirmed narrow scope.
4. Mark unresolved items as `ambiguities`.

## Scope Isolation Rules

1. If task targets one project, do not modify other projects.
2. If task targets one module, do not modify sibling modules.
3. Paths outside `allowed_paths` are out of scope.
4. Any external change detected during execution must be recorded as `external_unrelated_changes`.

## Output Contract Rules

1. Generate only outputs listed in `expected_outputs`.
2. Do not create extra reports/files outside declared outputs.
3. Acceptance is valid only when every `acceptance_criteria` item is satisfied or explicitly marked failed with reason.

## Forbidden Behaviors

1. Silent refactor outside declared scope.
2. Hidden task expansion.
3. Placeholder completion claims without machine-run checks.
4. Reinterpretation of undefined requirements as implicit permission.
