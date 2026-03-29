# IMPERIUM_SAFE_REVIEW_PIPELINE_CANON_V1

Status:
- class: `mutable_operational_pipeline_canon`
- mutability: `operational_delta_allowed`
- change_authority: `EMPEROR_OR_OWNER_APPROVED_DELTA`

Purpose:
- give owner a canonical manual-safe pipeline for routine deep review bundle gathering,
- reduce repeated Codex execution budget on evidence collection,
- preserve safe policy and zero-mutation behavior.

Entrypoint:
- `scripts/imperium_safe_review_pipeline.py`

Default lane set:
1. repo cleanliness and git truth,
2. code-bank inventory/anomaly/growth,
3. dashboard source-truth and brain-surface map,
4. full IMPERIUM coverage matrix,
5. freshness/authority/dominance reconciliation,
6. safe review pipeline contract and operator flow.

Safety law:
1. manual-safe export only by default,
2. no hidden repository mutation,
3. explicit disclosure of skipped/blocked/pointer-only/missing paths,
4. no secret/credential export,
5. safe-relaxed fallback requires explicit narrow policy and disclosure.

Output law:
1. one set folder in `docs/review_artifacts/<set_id>`,
2. one export folder in `runtime/chatgpt_bundle_exports/<set_id>`,
3. set-level files:
- entrypoint,
- master index,
- reading order,
- bundle map,
- validation report,
- remaining gaps.

Boundary:
1. pipeline collects evidence; it does not auto-remediate code,
2. PASS in collection does not equal product completion,
3. unresolved contradictions and open doctrine gaps remain explicit.
