# OUTPUT_MODE_HARDENING_V1

Status:
- status: `active`
- scope: `E:\CVVCODEX`
- hardening_version: `v1`

## Hardening Goal

Make output mode deterministic and repo-derived:

1. no ad-hoc format drift;
2. no silent prompt-level override of repository output law;
3. short chat + bundle-first detail delivery as workspace default;
4. exact artifact paths from first reply.

## Mandatory Rules

1. Codex must derive output mode from repo-native law surfaces before replying.
2. Chat response must remain short when output contract says ultra-short.
3. Detailed evidence must go to bundles/reports for large tasks.
4. First chat reply after execution must include exact artifact/bundle paths.
5. ChatGPT-authored task prompts cannot silently replace repo output law.
6. Completion status for large tasks is invalid without required bundle.

## Owner Override Window

Owner-level override is allowed only when explicit and task-bounded.

Even with owner override, forbidden:

1. disabling safe-mode boundaries;
2. suppressing critical blocker reporting;
3. claiming completion without required evidence chain.

## Machine-Readable Anchor

- `workspace_config/codex_output_mode_contract.json`

## Linked Governance Anchors

- `docs/governance/CODEX_OUTPUT_DISCIPLINE_V1.md`
- `docs/governance/CODEX_OUTPUT_PRECEDENCE_MODEL.md`
- `docs/governance/MANUAL_SAFE_BUNDLE_STANDARD.md`
- `workspace_config/bundle_fallback_contract.json`

