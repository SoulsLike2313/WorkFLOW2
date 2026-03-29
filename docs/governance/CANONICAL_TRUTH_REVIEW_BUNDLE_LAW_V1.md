# CANONICAL TRUTH REVIEW BUNDLE LAW V1

## Status

- status: `active`
- scope: `E:\CVVCODEX`
- enforcement_mode: `binding_for_active_execution_steps`

## Purpose

Enforce one declared primary review/truth bundle for every active execution step so ChatGPT review and owner truth-tracking never depend on guesswork across many bundles.

## Core Law

For each active step, there must be exactly one declared primary review/truth bundle.

Additional auxiliary bundles are allowed, but they do not replace the required primary declaration.

## External Response Entrypoint Rule

For each active step, external chat response must expose exactly one entrypoint path:
1. primary bundle path, or
2. one step-folder path that contains internal bundles/reports/companions.

Auxiliary bundles/companions may exist internally, but chat surface must keep one external entrypoint path by default.
Multiple external artifact paths are allowed only with explicit sovereign/owner override.

## Short Handoff Contract

Bounded result replies (fix/review/sync/packaging/verification) default shape:

1. `fixed`
2. `touched`
3. `sync`
4. `path`
5. `essence`
6. `next`

Large handoff receipt fallback:

1. `BUNDLE ROOT`
2. `DONE`
3. `NEXT`

Companion dependencies remain mandatory in bundle surfaces but are not listed as path-sprawl in default short chat response.

## Standard Review Root Set (12)

Every canonical step-folder under `docs/review_artifacts/<step_folder>` must contain this standard file set:

1. `00_REVIEW_ENTRYPOINT.md`
2. `01_INTEGRATION_REPORT.md`
3. `02_VALIDATION_REPORT.md`
4. `03_TRUTH_CHECK_AND_GAPS.md`
5. `04_CHANGED_SURFACES.md`
6. `05_API_SMOKE.json`
7. `06_BUNDLE_INCLUDE_PATHS.txt`
8. `07_MACHINE_CAPABILITY_MANIFEST_SNAPSHOT.json`
9. `08_ORGAN_STRENGTH_SNAPSHOT.json`
10. `09_NODE_RANK_DETECTION_SNAPSHOT.json`
11. `10_MACHINE_MODE_SNAPSHOT.json`
12. `11_CONSTITUTION_STATUS_SNAPSHOT.json`

Missing files mean review root is incomplete for canonical handoff.

## Archive Split Rule

Archive outputs must be split into `10 MB` parts.

Execution form:

1. base archive may remain for local handling,
2. split parts must exist as `<archive>.partNNN`,
3. split manifest/report must be present in review root surfaces.

## ChatGPT Transfer Package Rule

Each canonical step-folder must also publish operator-facing ChatGPT upload package under:

`docs/review_artifacts/<step_folder>/chatgpt_transfer/`

Execution form:

1. transfer root default layout is:
   - `chatgpt_transfer/core_chatgpt_transfer.partXXofNN` (required core package in transfer root),
   - `chatgpt_transfer/00_CHATGPT_TRANSFER_README.md`,
   - `chatgpt_transfer/chatgpt_transfer_manifest.json`,
   - `chatgpt_transfer/chatgpt_transfer_manifest.md`,
   - `chatgpt_transfer/visual/` (only if visual payload exists),
   - `chatgpt_transfer/optional/` (only if optional payload exists),
2. split transfer archives into parts with target size `32 MB` and allowed range `20-40 MB`,
3. if core payload is small/medium, keep it as one compact `part01of01` package and avoid unnecessary multi-file scattering,
4. default upload wave target is no more than `9` parts + README/manifest,
5. core package must include:
   - 12 standard review files,
   - review/validation/truth-check/changed-surfaces summaries,
   - seed capsule root (`ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1`) including `for_chatgpt`, `for_codex`, and trackers,
   - other small text surfaces required for reconstruction,
6. core package must not include:
   - visual payload,
   - optional heavy payload,
   - unnecessary binary duplicates,
7. visual layer must carry screenshot/diff evidence only,
8. optional layer must carry heavy non-essential extras only,
9. manifest must explicitly disclose:
   - `core_required`,
   - `parts_total`,
   - `package_completeness`,
   - `review_root`,
   - `included_file_families`,
   - `visual_included`,
   - `optional_included`,
   - split sizing and file paths.

This rule applies to ChatGPT handoff package only and does not remove local canonical review root as the source surface.

## Retention Rule (24h)

Ephemeral bundles/requests/staging older than `24h` must pass retention check.

Enforcement:

1. dry-run report is mandatory before deletion claims,
2. apply mode is allowed only through explicit janitor tooling,
3. tracked canonical files are never deletion targets.

## Mandatory Primary Bundle Requirements

Every active-step primary bundle must declare:

1. latest alias path,
2. timestamped immutable version path,
3. exact absolute/relative bundle path disclosure,
4. current active source disclosure,
5. companion dependency disclosure (if any),
6. review index,
7. artifact manifest,
8. validation report,
9. remaining gaps report,
10. sufficient truth-tracking surfaces for current step verification.

## Companion Dependency Rule

If primary bundle requires a companion:
1. dependency must be explicit and named exactly,
2. dependency purpose must be stated,
3. step is not "fully standalone reviewable" without companion unless explicitly proven.

Hidden or implied dependency is forbidden.

## Manual-Safe Exclusion Rule

If manual-safe exclusions apply:
1. exclusions must be explicitly disclosed,
2. blocked paths must be named or structurally described,
3. disclosure must be present in review surfaces.

## Truth-Tracking Rule For ChatGPT/Owner

ChatGPT and owner truth-tracking for an active step must not require bundle guessing or cross-bundle ambiguity.
Primary bundle identity must be explicit from first operational response/report for that step.
When folder-mode is used, folder path becomes the single external entrypoint and primary bundle identity remains explicit inside the folder review surfaces.

## Limit Economy Coupling

One-primary-bundle rule is also a token/limit economy mechanism:

1. reduces repetitive cross-zip retelling,
2. gives one stable review channel for each active step,
3. keeps chat short while preserving full bundle truth.

## False Completion Guard

It is forbidden to claim a step is fully reviewable when:
1. primary bundle has undisclosed missing surfaces,
2. companion dependency exists but is not disclosed,
3. required review index/manifest/validation/gaps are absent.

## Integration Anchors

This law is interpreted together with:
1. `docs/governance/CODEX_OUTPUT_DISCIPLINE_V1.md`
2. `docs/governance/CODEX_OUTPUT_PRECEDENCE_MODEL.md`
3. `docs/governance/MANUAL_SAFE_BUNDLE_STANDARD.md`
4. `workspace_config/codex_output_mode_contract.json`
5. `workspace_config/bundle_fallback_contract.json`
6. `docs/governance/LIMIT_ECONOMY_MODE_LAW_V1.md`
7. `docs/governance/SINGLE_ARTIFACT_ENTRYPOINT_RESPONSE_LAW_V1.md`
8. `docs/governance/PRIMARY_TRUTH_NAME_AND_SINGLE_ARTIFACT_PATH_RESPONSE_CONTRACT_V1.md`
9. `workspace_config/review_bundle_output_contract.json`
10. `scripts/imperium_bundle_output_enforcer.py`
11. `scripts/ttl_bundle_janitor.py`

## Adoption Boundary

This law is active for bundle discipline and does not rewrite constitutional source-of-truth precedence.
It standardizes review truth-channel clarity for active execution steps.
