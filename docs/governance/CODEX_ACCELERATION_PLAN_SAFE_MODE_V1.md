# CODEX_ACCELERATION_PLAN_SAFE_MODE_V1

Status:
- plan_version: `v1`
- scope: `repo-safe acceleration for Codex workflows`
- non_goal: `no security weakening, no broad redesign`
- mode_anchor: `ultra-short chat + bundle-first detail delivery`
- p1_bundle_acceleration_standard: `implemented`
- p1_anchors:
  - `docs/governance/MANUAL_SAFE_BUNDLE_STANDARD.md`
  - `workspace_config/bundle_fallback_contract.json`
  - `scripts/export_manual_safe_bundle.py`
- p2_search_acceleration_fallback: `implemented`
- p2_anchors:
  - `docs/governance/REPO_SEARCH_ENTRYPOINTS.md`
  - `workspace_config/search_zone_manifest.json`
  - `scripts/search_repo_safe.py`

## 1) CURRENT FRICTION MAP

### F1. Shell command shape rejection
- observed:
  1. [OBSERVED] complex one-liner PowerShell calls are occasionally rejected by policy engine.
  2. [OBSERVED] long chained commands trigger fallback to smaller sequential invocations.
- impact:
  1. [OBSERVED] additional retries and manual decomposition time.
  2. [OBSERVED] higher risk of partial execution drift.

### F2. `rg` / recursive search friction
- observed:
  1. [OBSERVED] `rg.exe` is discoverable but runtime calls can fail with `Access is denied`.
- impact:
  1. [OBSERVED] fallback to slower search paths and higher command count.

### F3. Exporter limitations with untracked files
- observed:
  1. [OBSERVED] `scripts/export_chatgpt_bundle.py` skips untracked files as `exists_but_not_tracked`.
  2. [OBSERVED] large bounded steps can produce valid new artifacts that exporter excludes.
- impact:
  1. [OBSERVED] bundle incompleteness despite relevant repo-visible outputs.
  2. [OBSERVED] extra manual packaging pass required.

### F4. Safe-share verdict coupling to repo sync/worktree state
- observed:
  1. [OBSERVED] exporter marks `NOT SAFE TO SHARE` when worktree is dirty or tracking state is not clean.
- impact:
  1. [OBSERVED] packaging path blocks even when selected payload is safe.

### F5. Big report handling friction
- observed:
  1. [OBSERVED] single heavy write/command operations are more failure-prone.
  2. [OBSERVED] high context cost when repeatedly opening large surfaces.
- impact:
  1. [OBSERVED] slower iteration and more fallback edits.

### F6. Repeated heavy rereads
- observed:
  1. [OBSERVED] repeated opening of broad canonical sets across adjacent tasks.
- impact:
  1. [INFERRED] avoidable time loss and context churn.

## 2) ROOT CAUSES

1. [OBSERVED] policy friction: heavy command shape and shell invocation constraints.
2. [OBSERVED] tooling design issue: exporter tracked-only inclusion policy for requested files.
3. [OBSERVED] pipeline coupling issue: safe-share verdict tied to global git state.
4. [INFERRED] reading/indexing issue: no dedicated acceleration index optimized for repeated large-task cycles.
5. [INFERRED] workflow issue: manual fallback patterns are not yet standardized as first-class safe workflow.

## 3) SAFE ACCELERATION PRINCIPLES

1. Keep fail-closed behavior and safe-mode boundaries unchanged.
2. Prefer deterministic, small-step command sequences over brittle mega one-liners.
3. Standardize fallback as policy-compliant primary path, not ad-hoc emergency behavior.
4. Preserve bundle information density; speed gains must not reduce evidence quality.
5. Separate “safe payload quality” from “global repo sync verdict” in reporting (without weakening safety claims).

## 4) READING ACCELERATION

Actions:
1. Maintain a compact recurring “quick-entry set” for large-task starts:
   - `MACHINE_CONTEXT.md`
   - `REPO_MAP.md`
   - `docs/INSTRUCTION_INDEX.md`
   - active step anchor docs.
2. Add task-specific “read-set manifest” per major phase to avoid broad re-scan.
3. Use bounded summary surfaces as first-pass, then drill into load-bearing docs only.

Expected gain:
1. [INFERRED] less re-reading overhead.
2. [INFERRED] faster context bootstrap without loss of canonical traceability.

Evidence of completion:
1. repeatable read-set manifests used in large tasks.
2. lower command count for context bootstrap.

## 5) SEARCH ACCELERATION

Actions:
1. Prefer `Select-String` + targeted path sets as canonical fallback for Windows policy-safe search.
2. Introduce a small helper script for scoped search zones (allowlisted directories only).
3. Avoid repo-wide blind recursion by default; search by known canonical zones first.

Expected gain:
1. [OBSERVED] reduced failure rate from `rg` access issues.
2. [INFERRED] predictable search latency and fewer blocked commands.

Evidence of completion:
1. search helper usage documented and repeatable.
2. fewer rejected search invocations per large task.

## 6) BUNDLE ACCELERATION

Actions:
1. Add “staged safe bundle assembly” convention:
   - explicit include list,
   - bundle-local manifest,
   - bundle-local summary,
   - exclusions note.
2. Keep exporter as default; define manual-safe packaging as standard fallback when untracked artifacts are in-scope.
3. Add bundle index + reading order by default for large analytical packages.
4. Add explicit field: “exporter limitations encountered” in bundle export report.

Expected gain:
1. [OBSERVED] fewer incomplete bundles caused by tracked-only limitations.
2. [INFERRED] faster handoff to ChatGPT/GPT-machines.

Evidence of completion:
1. bundle contains all intended scoped artifacts.
2. index + reading order + exclusions note present.
3. safe-mode verdict and limitations explicitly documented.

## 7) LARGE-OUTPUT HANDLING

Actions:
1. Write/report in bounded sections (chunk-wise) instead of one huge generation step.
2. Keep one primary report + optional compact machine-readable companion.
3. Use “ultra-short chat + bundle-first detail” as mandatory delivery split.
4. Prefer additive updates to existing bounded surfaces over creating many parallel docs.

Expected gain:
1. [INFERRED] fewer command failures and lower rework.
2. [OBSERVED] preserved informational depth through bundle surfaces.

Evidence of completion:
1. large tasks consistently produce a primary bundle-backed report.
2. chat remains compressed while bundle remains evidence-rich.

## 8) QUICK WINS

1. Standardize manual-safe bundle fallback template (manifest + summary + exclusions).
2. Add canonical “search fallback pattern” snippet for Windows policy-safe execution.
3. Add “read-set manifest” mini-template for major tasks.
4. Keep exporter limitation note mandatory when tracked-only skip occurs.

## 9) DO NOT CHANGE YET

1. Do not weaken safe-mode file blocking.
2. Do not force broad runtime allowlist expansion.
3. Do not remove sync/trust-based safety semantics from completion logic.
4. Do not replace canonical precedence model with speed-only shortcuts.
5. Do not launch heavy orchestration framework for acceleration.

## 10) WHAT IMPROVES SPEED WITHOUT LOSING INFORMATION DENSITY

1. Staged bundle assembly with index/reading order/exclusions.
2. Scoped search strategy (zone-first, fallback-safe commands).
3. Chunk-wise large report generation into one primary bounded surface.
4. Read-set manifests to reduce redundant scanning.

## 11) WHAT MUST BE PRESERVED TO KEEP BUNDLES STRONG

1. Evidence chain completeness (checks, reports, rationale).
2. Gap/contradiction visibility (no silent omissions).
3. Safe-mode exclusions transparency.
4. Canonical source precedence references.
5. Clear distinction between observed/inferred/not-proven claims.

## 12) PRIORITIZED IMPLEMENTATION ORDER

1. P1: Bundle acceleration standard (staged fallback + index + exclusions).
2. P2: Search acceleration standard (scoped fallback helper/patterns).
3. P3: Read acceleration standard (phase read-set manifests).
4. P4: Large-output handling standard (chunk-wise + one primary surface rule).
5. P5: Metrics pass (track rejection/fallback frequency and bundle completeness ratio).

Final statement:
1. [OBSERVED] this plan accelerates workflow while preserving safe-mode.
2. [INFERRED] speed gains are compatible with evidence-rich bundle quality.
