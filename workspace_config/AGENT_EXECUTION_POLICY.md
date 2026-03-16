# Agent Execution Policy (Machine-Enforced)

## Rule 1: Pre-Task Read Gate

Codex must not execute any task until the read order defined in:

- `workspace_config/TASK_RULES.md`
- `workspace_config/EXECUTION_ADMISSION_POLICY.md`
- `workspace_config/TASK_SOURCE_POLICY.md`
- `workspace_config/COMMUNICATION_STYLE_POLICY.md`
- `workspace_config/MACHINE_REPO_READING_RULES.md`
- `docs/CURRENT_PLATFORM_STATE.md`
- `docs/NEXT_CANONICAL_STEP.md`

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

Without canonical workflow alignment, execution is forbidden.

## Rule 3: Mandatory Execution Sequence

Execution order is fixed:

1. `scope_analysis`
2. `contract_verdict` (`REJECTED` | `PARTIAL_ACCEPTED` | `ACCEPTED`)
3. `canonical_workflow_alignment_check`
4. `bounded_execution`
5. `validation_execution`
6. `exact_output_delivery`

Skipping or reordering is forbidden.

## Rule 4: Refusal Behavior

On rejection, Codex must emit exact refusal format:

```text
STATUS: REJECTED
REASON: insufficient-contract | non-canonical | out-of-scope
MISSING:
- <missing_parameter_1>
- <missing_parameter_2>
ACTION REQUIRED:
- resubmit task with strict parameters
NO EXECUTION
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
7. No broad creative execution asks without strict repo contract.

## Rule 7: Validation and Completion Controls

1. Without acceptance criteria, completion claim is forbidden.
2. Without validation steps, confirmation claim is forbidden.
3. Validation must run against declared validation steps.
4. Any unmet criterion must be reported as failed, not omitted.
5. No completion claim when task is non-canonical to `docs/NEXT_CANONICAL_STEP.md` unless task explicitly updates canonical step documents.
6. No completion claim without post-task `git add` -> `git commit` -> `git push`.

## Rule 8: External Unrelated Changes

If external unrelated changes are detected:

1. Mark as `external_unrelated_changes`.
2. Keep excluded from task scope and task claims.
3. Do not revert unless explicitly requested.

## Rule 9: Prompt Output Format Enforcement

When task intent is prompt writing, output format is mandatory:

1. Exactly one copyable prompt block.
2. No fragmented prompt sections.
3. No alternative prompt versions unless explicitly requested.
4. No analysis inside prompt block.
5. Only short context is allowed outside prompt block.
6. If user requests short prompt, output only one short prompt block.
7. If user states persistent preference ("always only this format"), treat it as mandatory for future prompt-writing responses in this repository context.

Source:

- `workspace_config/PROMPT_OUTPUT_POLICY.md`

## Rule 10: Tester-Agent Admission Enforcement

For guarded projects (`audit_required` / `manual_testing_blocked`):

1. tester-agent audit evidence is mandatory before manual testing admission;
2. admission allowed only on final tester-agent status `PASS` or `PASS_WITH_WARNINGS`;
3. without repo-visible summaries, admission remains blocked.

Source:

- `workspace_config/PROJECT_AUDIT_POLICY.md`

## Rule 11: Tester-Agent Lane Contract

When operating as `platform_test_agent`, execution must follow lane order and output contract from:

- `workspace_config/TEST_AGENT_EXECUTION_POLICY.md`

## Rule 12: Canonical Workflow Boundary

If request conflicts with:

- `docs/CURRENT_PLATFORM_STATE.md`, or
- `docs/NEXT_CANONICAL_STEP.md`

Codex must return:

```text
STATUS: REJECTED
REASON: non-canonical
NO EXECUTION
```

## Rule 13: Mandatory Post-Task Git Finalization

For every completed task, Codex must perform and verify:

1. `git add <allowed_task_paths>`
2. `git commit -m "<task-scoped message>"`
3. `git push safe_mirror <active_branch>`
4. sync check (`HEAD == safe_mirror/<active_branch>`)

If any item is missing, status is `NOT_COMPLETED`.

## Rule 14: Communication Style Enforcement

Codex must follow:

- `workspace_config/COMMUNICATION_STYLE_POLICY.md`

Mandatory behavior:

1. respectful, calm, human communication
2. concise engineering clarity without empty verbosity
3. honest reporting of checks, failures, and uncertainty
4. no dismissive/arrogant wording

## Rule 15: Public Audit Repository Boundary

1. Repository visibility is public for audit readability.
2. Public mirror/tunnel/public endpoint flows are forbidden in canonical execution.
3. Router/WAN/LAN publication diagnostics are non-canonical artifacts and must not be added to tracked state.
4. If sensitive publication artifacts are detected, cleanup and ignore hardening are required before completion.
5. ChatGPT-reading workflow is CLI-first targeted bundle export (`scripts/export_chatgpt_bundle.py`), not full-repository exposure by default.
