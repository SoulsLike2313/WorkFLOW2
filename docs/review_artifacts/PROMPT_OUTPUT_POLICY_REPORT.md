# Prompt Output Policy Report

## Scope

Policy enforcement for prompt-writing responses only.

## Files Updated

1. `workspace_config/PROMPT_OUTPUT_POLICY.md` (new)
2. `workspace_config/TASK_RULES.md`
3. `workspace_config/AGENT_EXECUTION_POLICY.md`
4. `workspace_config/MACHINE_REPO_READING_RULES.md`
5. `workspace_config/codex_bootstrap.md`
6. `docs/INSTRUCTION_INDEX.md`

## Rules Added

1. Prompt-writing requests must return exactly one copyable prompt block.
2. No fragmented prompt parts.
3. No alternate prompt versions unless explicitly requested.
4. Prompt block must contain goal, scope, do-not-do constraints, expected output format.
5. No analysis text inside prompt block.
6. Only short context is allowed outside prompt block.
7. Explicit short-prompt requests return only short prompt block.
8. Explicit "always only this format" is treated as persistent formatting preference for prompt-writing in repository context.

## Machine Output Contract

For prompt-writing intents, machine output is valid only when all conditions are met:

1. single prompt block;
2. self-contained prompt content;
3. no mixed analysis inside block;
4. no unrequested alternatives.

## Source of Truth

Primary:

- `workspace_config/PROMPT_OUTPUT_POLICY.md`

Enforcement mirrors:

- `workspace_config/TASK_RULES.md`
- `workspace_config/AGENT_EXECUTION_POLICY.md`
- `workspace_config/MACHINE_REPO_READING_RULES.md`
- `workspace_config/codex_bootstrap.md`
- `docs/INSTRUCTION_INDEX.md`
