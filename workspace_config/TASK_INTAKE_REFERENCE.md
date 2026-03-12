# Task Intake Reference (Machine Contract)

## Mandatory Intake Rule

Task without strict contract is invalid.

Hard gate:

- `No strict parameters = no task acceptance`

## Minimum Required Task Contract

All fields below are mandatory:

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

Canonical JSON structure:

- `workspace_config/task_manifest.schema.json`

## Invalid Task Conditions (Hard Reject)

Task is invalid if any condition is true:

1. Missing any required field.
2. Scope is open-ended ("anywhere", "whole repo") without explicit path boundaries.
3. `allowed_paths` intersects `forbidden_paths`.
4. `expected_outputs` is absent or non-specific.
5. `acceptance_criteria` is absent.
6. `validation_steps` is absent.
7. `do_not_do` block is absent.

## Refusal Output Format (Mandatory)

```text
STATUS: REJECTED
REASON: insufficient task contract
MISSING:
- exact scope
- expected outputs
- acceptance criteria
- validation steps
ACTION REQUIRED:
- resubmit task with strict parameters
```

## Partial Acceptance Conditions

Use `PARTIAL_ACCEPTED` only when:

1. One bounded subset is strict and executable.
2. Remaining requirements are ambiguous or missing.

## Partial Acceptance Output Format (Mandatory)

```text
STATUS: PARTIAL_ACCEPTED
LIMITED_SCOPE:
- <confirmed_scope_only>
AMBIGUITIES:
- <undefined_or_conflicting_items>
WILL_NOT_DO:
- anything outside confirmed scope
```

## Example: Valid Contract (Minimal)

```json
{
  "task_id": "task-2026-03-12-governance-tighten",
  "task_type": "audit",
  "target_scope": {
    "level": "project",
    "selector": "tiktok_agent_platform",
    "exact_goal": "Normalize governance docs without touching source code."
  },
  "target_projects": ["tiktok_agent_platform"],
  "target_modules": ["workspace_config"],
  "allowed_paths": [
    "workspace_config/",
    "docs/INSTRUCTION_INDEX.md",
    "docs/review_artifacts/"
  ],
  "forbidden_paths": [
    "projects/",
    "scripts/"
  ],
  "expected_outputs": [
    {
      "path": "docs/review_artifacts/MACHINE_INSTRUCTION_AUDIT.md",
      "kind": "report",
      "format": "md",
      "required": true
    }
  ],
  "acceptance_criteria": [
    "Instruction audit report exists at exact path.",
    "No file outside allowed paths is modified."
  ],
  "validation_steps": [
    {
      "name": "workspace-validate",
      "command": "python scripts/validate_workspace.py",
      "success_condition": "status: PASS"
    }
  ],
  "post_conditions": [
    "Repository remains machine-readable.",
    "Task scope boundaries preserved."
  ],
  "notes": "Strict audit-only task."
}
```

## Example: Invalid Contract

```text
Goal: improve repository quality
Scope: whatever needed
Output: make it better
```

Reason:

- missing strict scope, paths, outputs, acceptance criteria, validation steps, do-not-do.

## Example: Partial Contract

```text
Goal: update task governance docs
Allowed paths: workspace_config/
Missing: forbidden paths, acceptance criteria, validation steps
```

Result:

- `PARTIAL_ACCEPTED` only for explicitly listed files in `workspace_config/`.
