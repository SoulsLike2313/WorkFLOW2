# Prompt Output Policy (Machine-Enforced)

## Scope

This policy is mandatory when a user requests prompt writing, including intents such as:

- "write prompt"
- "give prompt"
- "build prompt"
- "make a prompt"
- equivalent prompt-writing intent in any language

## Hard Output Contract

When scope is prompt writing, Codex must output:

1. Exactly one copyable prompt block.
2. No fragmented prompt parts.
3. No alternative prompt versions unless explicitly requested.
4. No analysis inside the prompt block.
5. No mixed prompt + reasoning format inside the prompt block.

Outside the prompt block, only short context is allowed.

## Prompt Block Requirements

The single prompt block must be self-contained and include:

1. Clear goal.
2. Explicit scope boundaries.
3. Explicit do-not-do constraints.
4. Explicit expected output format.
5. No filler text.

## Short Prompt Mode

If user explicitly asks for a short prompt:

1. Output only one short prompt block.
2. Do not append expanded or alternate versions.

## Persistent Formatting Preference

If user explicitly says "always only this format" (or equivalent), Codex must treat single-block prompt output as persistent repository preference for prompt-writing requests.

## Source of Truth

Prompt-writing format enforcement is authoritative in:

- `workspace_config/PROMPT_OUTPUT_POLICY.md`
- `workspace_config/TASK_RULES.md`
- `workspace_config/AGENT_EXECUTION_POLICY.md`
- `workspace_config/MACHINE_REPO_READING_RULES.md`
