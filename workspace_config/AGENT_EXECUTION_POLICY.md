# Agent Execution Policy (Machine-Enforced)

## Canonical Operating Model

- Working source of truth: `E:\CVVCODEX`
- Public safe mirror only: `WorkFLOW2` (`safe_mirror/main`)
- External reading channel: targeted bundle export
- Governance brain stack is mandatory interpretation layer

## Rule 1: Mandatory Read Gate

Task execution is forbidden until mandatory read order is completed from:

- `workspace_config/MACHINE_REPO_READING_RULES.md`
- `workspace_config/codex_manifest.json` (`bootstrap_read_order`)
- `docs/INSTRUCTION_INDEX.md`

If read gate is incomplete: `STATUS: REJECTED`.

## Rule 2: Strict Contract Gate

Reject tasks missing strict contract fields:

1. exact goal
2. exact scope
3. target project/module
4. allowed paths
5. forbidden paths
6. expected outputs
7. acceptance criteria
8. validation steps
9. do-not-do block

## Rule 3: Governance Brain Stack Requirement

All execution and interpretation must comply with:

- `docs/governance/FIRST_PRINCIPLES.md`
- `docs/governance/GOVERNANCE_HIERARCHY.md`
- `docs/governance/SELF_VERIFICATION_POLICY.md`
- `docs/governance/CONTRADICTION_CONTROL_POLICY.md`
- `docs/governance/ADMISSION_GATE_POLICY.md`
- `docs/governance/ANTI_DRIFT_POLICY.md`
- `docs/governance/DEVIATION_INTELLIGENCE_POLICY.md`
- `docs/governance/GOVERNANCE_EVOLUTION_POLICY.md`
- `docs/governance/CREATIVE_REASONING_POLICY.md`
- `docs/governance/AGENT_CHARACTER_PROFILE.md`
- `docs/governance/EVOLUTION_READINESS_POLICY.md`
- `docs/governance/MODEL_MATURITY_MODEL.md`
- `docs/governance/EVOLUTION_SIGNAL_REGISTRY.md`
- `docs/governance/POLICY_EVOLUTION_LOG.md`
- `docs/governance/NEXT_EVOLUTION_CANDIDATE.md`

## Rule 4: Bounded Execution

Forbidden:

- side work
- silent scope expansion
- unrequested artifacts
- cross-scope edits without explicit permission

## Rule 5: Completion Gate

Completion is forbidden unless all pass:

1. repo-visible truth
2. sync parity with `safe_mirror/main`
3. mandatory self-verification
4. no unresolved critical contradiction

Failure of any gate => `NOT_COMPLETED`.

## Rule 6: Rejection Reasons

Allowed reasons only:

- `insufficient-contract`
- `non-canonical`
- `out-of-scope`

Required format:

```text
STATUS: REJECTED
REASON: <allowed_reason>
NO EXECUTION
```

## Rule 7: Post-Task Git Finalization

Required sequence:

1. `git add <allowed_task_paths>`
2. `git commit -m "<task-scoped message>"`
3. `git push safe_mirror <active_branch>`
4. verify `HEAD == safe_mirror/main`

## Rule 8: ChatGPT Reading Boundary

- Do not use full repository exposure as default reading channel.
- Use `scripts/export_chatgpt_bundle.py` request-scoped bundles.

## Rule 9: Repo Control Center Enforcement

Before completion claim, run:

1. `python scripts/repo_control_center.py status`
2. `python scripts/repo_control_center.py trust`
3. `python scripts/repo_control_center.py evolution`
4. `python scripts/repo_control_center.py full-check`

If trust/sync/admission are blocked, completion is forbidden.

## Rule 10: Federation Mode Enforcement

- Mode detection contract:
  - `workspace_config/creator_mode_detection_contract.json`
  - env var `CVVCODEX_CREATOR_AUTHORITY_DIR`
  - marker `creator_authority.json`
- Full repo copy without valid creator marker is `helper` mode.
- Helper mode cannot:
  - declare canonical completion
  - override governance
  - perform final acceptance of external deliveries
- External helper deliveries must go through:
  - `integration/inbox/`
  - `scripts/review_integration_inbox.py` review flow

## Rule 11: Operator Command Execution Layer

- Command execution must use:
  - `scripts/operator_command_surface.py`
- Command class/action authority comes only from:
  - `workspace_config/operator_command_registry.json`
- Every executed command must emit contract evidence in:
  - `runtime/operator_command_layer/last_execution.json`
  - `runtime/operator_command_layer/command_surface_status.json`
- Mutable actions are forbidden unless guarded:
  - default dry-run
  - explicit `--allow-mutation` for approved guarded actions only

## Rule 12: Operator Task / Program Layer

- Program execution must use:
  - `scripts/operator_program_surface.py`
- Program class/program_id authority comes only from:
  - `workspace_config/operator_program_registry.json`
- Every executed program must emit contract evidence in:
  - `runtime/operator_program_layer/last_execution.json`
  - `runtime/operator_program_layer/program_surface_status.json`
  - `runtime/operator_program_layer/program_surface_report.md`
- Program execution must be checkpointed:
  - explicit step plan
  - current step tracking
  - blocking factor emission
  - deterministic next-step output
- Guarded mutation programs are forbidden unless explicitly approved:
  - `--allow-mutation`
  - `--confirm-mutation` when required by policy
