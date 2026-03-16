# Machine Repo Reading Rules (Execution Gate)

## Rule 1: Task Start Forbidden Without Read Gate

Machine must complete this canonical order before execution:

1. `README.md`
2. `workspace_config/workspace_manifest.json`
3. `workspace_config/codex_manifest.json`
4. `REPO_MAP.md`
5. `MACHINE_CONTEXT.md`
6. `docs/INSTRUCTION_INDEX.md`
7. `docs/CURRENT_PLATFORM_STATE.md`
8. `docs/NEXT_CANONICAL_STEP.md`
9. `docs/governance/FIRST_PRINCIPLES.md`
10. `docs/governance/GOVERNANCE_HIERARCHY.md`
11. `docs/governance/SELF_VERIFICATION_POLICY.md`
12. `docs/governance/CONTRADICTION_CONTROL_POLICY.md`
13. `docs/governance/ADMISSION_GATE_POLICY.md`
14. `docs/governance/ANTI_DRIFT_POLICY.md`
15. `docs/governance/DEVIATION_INTELLIGENCE_POLICY.md`
16. `docs/governance/GOVERNANCE_EVOLUTION_POLICY.md`
17. `docs/governance/CREATIVE_REASONING_POLICY.md`
18. `docs/governance/AGENT_CHARACTER_PROFILE.md`
19. `workspace_config/TASK_RULES.md`
20. `workspace_config/EXECUTION_ADMISSION_POLICY.md`
21. `workspace_config/TASK_SOURCE_POLICY.md`
22. `workspace_config/COMMUNICATION_STYLE_POLICY.md`
23. `workspace_config/AGENT_EXECUTION_POLICY.md`
24. `workspace_config/MACHINE_REPO_READING_RULES.md`
25. `workspace_config/PROMPT_OUTPUT_POLICY.md`
26. `workspace_config/PROJECT_AUDIT_POLICY.md`
27. `workspace_config/TEST_AGENT_EXECUTION_POLICY.md`
28. `workspace_config/GITHUB_SYNC_POLICY.md`
29. `workspace_config/COMPLETION_GATE_RULES.md`
30. relevant `PROJECT_MANIFEST.json`
31. relevant project `README.md`
32. relevant `CODEX.md` if present
33. relevant `SYSTEM_MANIFEST.json` if shared system is involved

If any mandatory step is skipped: `STATUS: REJECTED`.

## Rule 2: Canonical Identity

- Working source of truth: `E:\CVVCODEX`
- Public safe mirror only: `WorkFLOW2` on `safe_mirror/main`
- Targeted bundle export is canonical external reading channel

## Rule 3: Source-of-Truth Resolution

1. `docs/governance/FIRST_PRINCIPLES.md`
2. `docs/governance/GOVERNANCE_HIERARCHY.md`
3. `workspace_config/workspace_manifest.json`
4. `workspace_config/codex_manifest.json`
5. target `PROJECT_MANIFEST.json`
6. `README.md`
7. review artifacts as non-authoritative evidence

## Rule 4: Active Project Detection

Resolve active project only via:

- `workspace_config/workspace_manifest.json` -> `active_project` + `project_registry`

No folder-name guessing.

## Rule 5: Completion Preconditions

Completion is forbidden without:

1. repo-visible truth
2. sync parity (`HEAD == safe_mirror/main`, divergence `0/0`)
3. self-verification pass
4. contradiction control pass

## Rule 6: ChatGPT Reading Contract

For external machine reading use only:

- `scripts/export_chatgpt_bundle.py`
- `docs/CHATGPT_BUNDLE_EXPORT.md`

Do not treat full repository publication as required path for task-scoped ChatGPT analysis.

## Rule 7: Legacy Handling

- `origin` (`WorkFLOW`) is legacy/non-canonical for completion decisions.
- `docs/review_artifacts/PUBLIC_REPO_SANITIZATION_REPORT.md` is legacy evidence and excluded from active bootstrap read order.
