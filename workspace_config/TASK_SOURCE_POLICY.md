# Task Source Policy (Hard Intake Filter)

## Core Rule

Only strict repo-compliant prompts are executable.

If request is non-compliant, status is:

```text
STATUS: REJECTED
REASON: insufficient-contract | non-canonical | out-of-scope
NO EXECUTION
```

## Authoritative Task Sources

Execution task authority is valid only when all of the following are consistent:

1. user request with strict task contract
2. `workspace_config/TASK_RULES.md`
3. `workspace_config/EXECUTION_ADMISSION_POLICY.md`
4. `workspace_config/AGENT_EXECUTION_POLICY.md`
5. `workspace_config/MACHINE_REPO_READING_RULES.md`
6. `docs/CURRENT_PLATFORM_STATE.md`
7. `docs/NEXT_CANONICAL_STEP.md`
8. `workspace_config/COMMUNICATION_STYLE_POLICY.md`

If sources conflict, policy files and canonical state files override free-form request language.

## Executable Request Classes

Request is executable only when it is strict and maps to one `task_mode`:

1. `build`
2. `audit`
3. `validate`
4. `integrate`
5. `remove`
6. `report`

## Non-Executable Request Classes

The following are non-executable as repository tasks unless reformatted into strict contract:

1. broad creative asks without scope (`"build a game"`, `"make it beautiful"`, `"improve everything"`)
2. open-ended brainstorm asks without target paths
3. requests without acceptance criteria
4. requests without validation steps
5. requests with missing forbidden paths
6. requests conflicting with canonical next step

## Canonical Task Format Requirement

Task request is valid only if includes:

- exact goal
- exact target scope
- target project or module
- allowed paths
- forbidden paths
- expected outputs
- acceptance criteria
- validation steps
- explicit do-not-do block
- task mode

Canonical schema:

- `workspace_config/task_manifest.schema.json`
- `workspace_config/TASK_INTAKE_REFERENCE.md`

## Rejection and Partial Acceptance

### Rejection

```text
STATUS: REJECTED
REASON: insufficient-contract | non-canonical | out-of-scope
NO EXECUTION
```

### Partial acceptance

Only bounded confirmed subset is executable.

```text
STATUS: PARTIAL_ACCEPTED
LIMITED_SCOPE:
- <confirmed_scope_item>
AMBIGUITIES:
- <ambiguity_item>
WILL_NOT_DO:
- anything outside confirmed scope
```
