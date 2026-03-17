# NARRATIVE_COMPRESSION_REVIEW

## Scope
Constitution-first narrative compression review for:
- `README.md`
- `REPO_MAP.md`
- `MACHINE_CONTEXT.md`
- `docs/INSTRUCTION_INDEX.md`
- `docs/CURRENT_PLATFORM_STATE.md`

## Findings

### 1) Bootstrap list duplication across 3 surfaces
- surfaces: `REPO_MAP.md`, `MACHINE_CONTEXT.md`, `docs/INSTRUCTION_INDEX.md`
- issue: long near-duplicate read-order blocks increase drift risk.
- risk of change: medium (order changes can break gate assumptions).
- recommendation: keep one canonical machine-readable order (`workspace_config/codex_manifest.json.bootstrap_read_order`) and keep docs as pointer + minimal excerpt.
- action: later (after constitution stabilization).

### 2) Governance stack listing duplication
- surfaces: `README.md`, `docs/INSTRUCTION_INDEX.md`, manifests.
- issue: same policy inventory repeated in full multiple times.
- risk of change: low.
- recommendation: keep complete list in one anchor section and point to it elsewhere.
- action: later (low-risk, doc-only).

### 3) Current-phase statements now aligned (fixed)
- surfaces: all five reviewed surfaces.
- issue: previously mission was still presented as next active layer.
- status: resolved in current pass.
- action: do now complete (already done).

### 4) Mission examples drift risk
- surfaces: `README.md` examples vs registry ids.
- issue: examples can stale when mission ids change.
- risk of change: low.
- recommendation: add lightweight doc-registry drift check proposal (not implementation here).
- action: later.

### 5) State snapshot duplication
- surfaces: `docs/CURRENT_PLATFORM_STATE.md` and runtime reports.
- issue: narrative snapshot can lag runtime truth.
- risk of change: low.
- recommendation: keep snapshot concise and reference runtime truth files for volatile fields.
- action: later.

## Low-Risk Compression Opportunities
1. Replace repeated full bootstrap blocks in docs with canonical pointer to:
   - `workspace_config/codex_manifest.json.bootstrap_read_order`
2. Replace repeated full governance inventory in `README`/`INSTRUCTION_INDEX` with one canonical pointer section.
3. Add a fixed “phase signal” mini-block template reused across canonical surfaces.

## Lingering Phrasing Drift Check
- no critical lingering phrase found that still claims Mission Layer as pending next step.
- no direct contradiction found across reviewed canonical surfaces for current phase routing.

## Compression Verdict
`LOW-RISK COMPRESSION POSSIBLE`

Narrative is currently coherent enough for Constitution-first execution. Further compression should be incremental to avoid destabilizing bootstrap semantics.
