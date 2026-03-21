# OWNER_DECISION_SCOPE_CLOSURE_MATRIX

## Current Residual Scope (after targeted status-surface remediation)
- [OBSERVED] Tracked dirty entries: 43
- [OBSERVED] Untracked entries: 140
- [OBSERVED] All tracked status/evidence surfaces in paradox scope are now clean.

## Matrix

| item/group | exact required action | why Codex cannot decide alone | if kept | if removed | blocks all-green |
|---|---|---|---|---|---|
| `docs/governance/*` tracked modifications (22 files in current dirty list) | Owner decide commit set vs rollback set | Mixed doctrinal rewrites from multiple prior phases; potential authoritative intent | preserves ongoing doctrine work but keeps dirty tree until committed | potential loss of intentional canonical changes | yes |
| `docs/review_artifacts/*` tracked modifications (`DEPARTMENT_OWNERSHIP_GAP_REPORT.md`, `PROJECT_PATH_STATUS_MATRIX.md`, `TAXONOMY_ALIGNMENT_REPORT.md`) | Owner decide whether these are active truth updates or stale leftovers | Semantics can be either intended correction or temporary analysis drift | retains evidence but blocks clean state | may drop meaningful updates | yes |
| `README.md`, `MACHINE_CONTEXT.md`, `REPO_MAP.md`, `docs/INSTRUCTION_INDEX.md`, `docs/CURRENT_PLATFORM_STATE.md`, `docs/CHATGPT_BUNDLE_EXPORT.md` (tracked modified) | Owner approve canonical-doc commit bundle or rollback | Canonical surfaces are load-bearing; unsafe to auto-discard | preserves intended canon updates; still dirty until committed | could regress current doctrine alignment | yes |
| `scripts/detect_machine_mode.py`, `scripts/repo_control_center.py`, `scripts/validation/check_sovereign_claim_denial.py`, `scripts/validation/detect_node_rank.py`, `scripts/validation/run_constitution_checks.py` | Owner choose implementation baseline to keep | Code changes may be intentional architecture hardening; unsafe to auto-revert | preserves functional changes but blocks clean until committed | could remove required behavior fixes | yes |
| `workspace_config/*.json` tracked modifications (`claim_taxonomy_contract.json`, `creator_mode_detection_contract.json`, `delegation_registry.json`, `federation_mode_contract.json`, `workspace_manifest.json`) | Owner confirm contract baseline | Contract edits can be canonical and cross-validator dependent | keeps intended contracts; still dirty until commit | may break doctrine-script alignment | yes |
| `integration/review_queue/20260317T094958Z_TASK-PLATFORM_TEST_AGENT-001_helper-node-audit/review_result.{json,md}` | Owner decide archive/commit/revert | Could be historical evidence vs accidental local edits | keeps audit history continuity if intentional | may lose local audit edits | yes |
| `docs/review_artifacts/*` untracked bulk (93 files) | Owner choose: archive externally, commit selected, or remove | Contains mixed value: high-value reports + temporary snapshots | preserves analyses but blocks clean tree | may lose evidence if not archived first | yes |
| `docs/governance/*` untracked bulk (30 files) | Owner approve doctrinal introduction set | New doctrinal surfaces may be intentional canonical additions | preserves hardening work; still dirty until commit | may discard valid doctrine | yes |
| `scripts/*.py` untracked (`build_chatgpt_deep_audit_bundle_set.py`, `export_manual_safe_bundle.py`, `generate_fresh_audit_reports.py`, `search_repo_safe.py`) | Owner decide production adoption vs discard | Tooling may be strategic; cannot infer final adoption | keeps tooling progress; blocks clean until commit | may lose useful automation | yes |
| `workspace_config/*.json` untracked contracts (13 files currently) | Owner approve contract adoption set | New contracts can alter canonical policy surfaces | preserves formalization progress | may drop needed machine-readable contracts | yes |

## Closed vs Open
- [OBSERVED] Closed in this cycle: status-surface paradox scope (tracked evidence files now clean, default no-write loop removed).
- [OBSERVED] Open and still blocking all-green: large owner-owned dirty/untracked package listed above.
