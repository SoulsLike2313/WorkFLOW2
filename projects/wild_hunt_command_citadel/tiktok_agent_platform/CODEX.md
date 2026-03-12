# CODEX.md

## Project Identity

`tiktok_agent_platform` is a unified product project that combines:

- a core platform/runtime layer (`core/`)
- an agent application layer (`agent/`)

Do not treat these as unrelated projects.

## Layer Contract

- `core/` owns platform runtime, verification, readiness, update/patch, diagnostics, and UI-QA foundations.
- `agent/` owns user-facing automation UX, profile workflows, scheduling, and execution controls.
- Cross-layer integration must remain explicit:
  - agent can call core workflows
  - core must stay runnable independently for verification
  - no silent path guessing across layers

## Startup Contract

Use product root run entrypoint:

- `run_project.ps1`

Supported modes:

- `user`, `developer`, `verify`, `update`
- `core-user`, `core-developer`, `core-verify`
- `agent-user`, `agent-developer`, `agent-verify`

## Verification Contract

Unified verify mode must validate:

1. core verification gate
2. agent verification gate
3. core UI-QA entrypoint availability

Manual testing remains gated by verification PASS status.
