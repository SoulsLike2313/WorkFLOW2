# MACHINE BOOTSTRAP CONTRACT

Policy class: control contract for deterministic machine onboarding.

## 1) Canonical bootstrap authority

Primary bootstrap sequence source:

- `workspace_config/codex_manifest.json` -> `bootstrap_read_order`

Supporting interpretation sources:

- `workspace_config/MACHINE_REPO_READING_RULES.md`
- `docs/INSTRUCTION_INDEX.md`
- `MACHINE_CONTEXT.md`

## 2) Contract rule for multiple read-order sources

1. `codex_manifest.bootstrap_read_order` is the canonical base sequence.
2. `MACHINE_REPO_READING_RULES.md` Rule 1 must be set-equivalent to the canonical base sequence.
3. `docs/INSTRUCTION_INDEX.md` may extend the sequence only with additional policy/project context.
4. Any conflict with the canonical base sequence is a contradiction and must block completion.

## 3) Mandatory bootstrap outcome

Before task execution, machine must deterministically resolve:

1. working source of truth path (`E:\CVVCODEX`)
2. canonical remote and branch (`safe_mirror/main`)
3. active project from `workspace_config/workspace_manifest.json`
4. governance stack path set
5. completion gate conditions

If any item is unresolved, task status must be `REJECTED` or `BLOCKED`.

## 4) Verification checks

Minimum verification for bootstrap integrity:

1. `python scripts/validate_workspace.py`
2. `python scripts/repo_control_center.py status`
3. `python scripts/repo_control_center.py trust`

If verification fails, machine cannot claim trusted bootstrap.

## 5) Completion prohibition

Completion is forbidden when:

1. bootstrap sequence is incomplete
2. bootstrap sources conflict
3. canonical root/remote is unresolved
4. governance stack is missing required files

## 6) Traceability requirement

Bootstrap-sensitive changes must update:

1. `workspace_config/codex_manifest.json`
2. `workspace_config/MACHINE_REPO_READING_RULES.md`
3. `docs/INSTRUCTION_INDEX.md`
4. `MACHINE_CONTEXT.md` (if canonical context changes)
