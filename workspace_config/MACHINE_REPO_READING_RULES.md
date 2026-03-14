# Machine Repo Reading Rules (Execution Gate)

## Rule 1: Task Start Is Forbidden Without Read Gate

Codex must complete this exact order before any task analysis or code change:

1. `README.md`
2. `workspace_config/workspace_manifest.json`
3. `workspace_config/codex_manifest.json`
4. `workspace_config/TASK_RULES.md`
5. `workspace_config/EXECUTION_ADMISSION_POLICY.md`
6. `workspace_config/TASK_SOURCE_POLICY.md`
7. `workspace_config/AGENT_EXECUTION_POLICY.md`
8. `workspace_config/MACHINE_REPO_READING_RULES.md`
9. `workspace_config/PROMPT_OUTPUT_POLICY.md`
10. `workspace_config/PROJECT_AUDIT_POLICY.md`
11. `workspace_config/TEST_AGENT_EXECUTION_POLICY.md`
12. `workspace_config/GITHUB_SYNC_POLICY.md`
13. `workspace_config/COMPLETION_GATE_RULES.md`
14. `docs/INSTRUCTION_INDEX.md`
15. `docs/CURRENT_PLATFORM_STATE.md`
16. `docs/NEXT_CANONICAL_STEP.md`
17. relevant `PROJECT_MANIFEST.json`
18. relevant project `README.md`
19. relevant `CODEX.md` if present
20. relevant `SYSTEM_MANIFEST.json` if shared system is involved

If any mandatory step is skipped, task status is `REJECTED`.

## Rule 2: Source of Truth Resolution

1. root `README.md` = workspace map
2. `workspace_config/workspace_manifest.json` = workspace registry
3. `workspace_config/codex_manifest.json` = machine onboarding policy
4. `PROJECT_MANIFEST.json` = project source of truth
5. `SYSTEM_MANIFEST.json` = shared system source of truth

Conflict rule: higher item in this list wins.

State/priority continuity rules:

6. `docs/CURRENT_PLATFORM_STATE.md` = canonical current state snapshot
7. `docs/NEXT_CANONICAL_STEP.md` = canonical immediate execution direction
8. `docs/MACHINE_CHANGELOG.md` = canonical machine continuity log

## Rule 3: Active Project Detection

1. Read `workspace_config/workspace_manifest.json`.
2. Resolve `active_project`.
3. Resolve matching `project_registry[].manifest_path`.
4. Canonical tester-agent active project is `platform_test_agent`.

No directory-name guessing is allowed.

## Rule 4: Shared Systems Detection

1. Check `shared_systems/`.
2. For each child folder, require `SYSTEM_MANIFEST.json`.
3. If folder or manifest is missing, report `not_configured` or `incomplete_registry`.

## Rule 5: Project Status Detection

Primary source:

- `project_registry[].status`

Secondary mirror:

- `project_status_index`

If mismatch exists, treat registry as authoritative and report mismatch.

## Rule 6: Installed Systems Detection

Per project:

1. Read project `PROJECT_MANIFEST.json`.
2. Use `installed_systems` if present.
3. If missing, report `unknown_not_declared`.

Do not infer installed systems from folder names only.

## Rule 7: Manifest Detection

1. Workspace manifest: `workspace_config/workspace_manifest.json`
2. Codex manifest: `workspace_config/codex_manifest.json`
3. Project manifests: `projects/**/PROJECT_MANIFEST.json`
4. System manifests: `shared_systems/**/SYSTEM_MANIFEST.json`
5. Shared systems registry: `workspace_config/shared_systems_registry.json`

## Rule 8: Verification Entrypoint Detection

1. Project-level source: `PROJECT_MANIFEST.json -> verification_entrypoints`
2. Workspace-level source: `workspace_manifest.json -> verification_entrypoints`
3. For project execution, project-level entrypoint is mandatory.

## Rule 9: Install/Remove Workflow Detection

Install workflow source:

- `scripts/install_system.py` or `scripts/install_system.ps1`

Remove workflow source:

- `scripts/remove_system.py` or `scripts/remove_system.ps1`

If scripts are absent, workflow status is `not_implemented`.

## Rule 10: Non-Guessing Failure Contract

If required contract data is missing, Codex must emit:

- `STATUS: REJECTED`
- `REASON: insufficient_contract_data`

and must not execute speculative edits.

## Rule 11: Task Contract Enforcement Outcomes

1. Without strict task contract: task is `REJECTED`.
2. Without scope boundaries: code changes are forbidden.
3. Without acceptance criteria: completion claim is forbidden.
4. Without validation steps: confirmation claim is forbidden.
5. Without canonical workflow match to `docs/NEXT_CANONICAL_STEP.md`: task is `REJECTED`.
6. Broad creative asks without strict contract are `REJECTED`.

## Rule 12: Prompt Output Policy Detection

For prompt-writing tasks, machine must read and enforce:

- `workspace_config/PROMPT_OUTPUT_POLICY.md`

Prompt-writing output is valid only if:

1. exactly one copyable prompt block is returned;
2. prompt block is self-contained (goal, scope, do-not-do, expected output format);
3. no analysis is inside prompt block;
4. no alternate prompt variants are returned unless explicitly requested;
5. short prompt requests return only short prompt block.

## Rule 13: Tester-Agent Admission Gate

For guarded projects:

1. detect project status (`audit_required` or `manual_testing_blocked`);
2. enforce tester-agent audit admission from `workspace_config/PROJECT_AUDIT_POLICY.md`;
3. if repo-visible audit evidence is missing, keep project in `manual_testing_blocked`.

## Rule 14: Rejection Reason Contract

Allowed rejection reasons:

1. `insufficient-contract`
2. `non-canonical`
3. `out-of-scope`

Mandatory response fragment:

- `STATUS: REJECTED`
- `REASON: <allowed_reason>`
- `NO EXECUTION`

## Rule 15: Post-Task Git Finalization Detection

Completion is valid only when machine can confirm:

1. task outputs are staged and committed
2. commit is pushed to remote branch
3. remote branch head matches local head
4. worktree is clean after push

If any item fails, completion status is `NOT_COMPLETED`.
