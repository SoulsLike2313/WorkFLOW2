# OWNER_DECISION_MATRIX_FOR_ALL_GREEN

- generated_at_utc: `2026-03-21T11:36:37.088147+00:00`

| item/group | recommended action | risk if kept | risk if deleted | can Codex do it safely now | owner-only decision | blocks worktree_clean | blocks trust/governance |
|---|---|---|---|---|---|---|---|
| tracked_dirty_files (44 paths) | KEEP_FOR_CURRENT_PHASE | worktree remains dirty until commit/discard | loss of hardening/reform work | no | yes | yes | yes |
| untracked_governance_doctrine (30 files) | KEEP_FOR_CURRENT_PHASE | blocks clean tree until committed | loss of new canonical surfaces/tooling | no | yes | yes | yes |
| untracked_review_markdown_reports (77 files) | ARCHIVE_AS_EVIDENCE | continues dirty tree/noise | loss of trace if not archived | yes | yes | yes | yes |
| untracked_review_json_reports (7 files) | ARCHIVE_AS_EVIDENCE | continues dirty tree/noise | loss of trace if not archived | yes | yes | yes | yes |
| untracked_scripts (4 files) | KEEP_FOR_CURRENT_PHASE | blocks clean tree until committed | loss of new canonical surfaces/tooling | no | yes | yes | yes |
| untracked_workspace_contracts (13 files) | KEEP_FOR_CURRENT_PHASE | blocks clean tree until committed | loss of new canonical surfaces/tooling | no | yes | yes | yes |
| runtime/repo_control_center/constitution_status.* | DISCARD_AFTER_CHECK | regenerated churn can re-dirty tracked files | none (files are regenerated) | yes | no | yes when modified | indirect via sync chain |