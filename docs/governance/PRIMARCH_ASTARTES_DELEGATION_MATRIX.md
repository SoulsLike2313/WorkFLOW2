# PRIMARCH_ASTARTES_DELEGATION_MATRIX

Status:
- matrix_version: `v1-draft-safe`
- intent: `targeted doctrine intake for future Federation department command architecture`
- scope: `oversight, delegation, execution boundaries, rank-to-department relation`
- non_goal: `no speculative leadership hierarchy beyond repo-visible doctrine`

## 1) Doctrine Strength Scale

- `LOAD_BEARING`: canonical policy/contract directly used for authority or execution gating.
- `SECONDARY`: strong contextual support, but not primary gate source.
- `REVIEW_ONLY`: evidence/review memo; useful but non-authoritative.
- `HISTORICAL_ONLY`: legacy/history context, not active authority source.
- `TOO_WEAK`: absent/insufficient for safe architectural decision.

## 2) Doctrinal Fragments

| path | fragment role | doctrine_strength | intake note |
|---|---|---|---|
| `docs/governance/NODE_AUTHORITY_RANK_POLICY_V1.md` | rank classes, capabilities/limits, sovereign claim boundaries | `LOAD_BEARING` | defines Emperor/Primarch/Astartes authority split |
| `docs/governance/SOVEREIGN_RANK_PROOF_MODEL_V1.md` | rank resolution order + fail-closed narrowing | `LOAD_BEARING` | binds rank to proof model; blocks mirror/bundle elevation |
| `docs/governance/SOVEREIGN_CLAIM_DENIAL_POLICY_V1.md` | allow/deny per rank and claim class | `LOAD_BEARING` | formal boundary for what ranks may claim |
| `docs/governance/WARRANT_CHARTER_LIFECYCLE_V1.md` | delegated authority issuance/acceptance and lifecycle gates | `LOAD_BEARING` | critical for execution delegation semantics |
| `docs/governance/INTER_NODE_DOCUMENT_ARCHITECTURE_V1.md` | issuer classes and document authority matrix | `LOAD_BEARING` | strongest explicit command-document relation by rank |
| `docs/governance/INTER_NODE_DOCUMENT_SCHEMA_V1.md` | machine-readable required fields and validation rules | `LOAD_BEARING` | execution/reintegration validation substrate |
| `docs/governance/CREATOR_AUTHORITY_POLICY.md` | creator-only canonical acceptance operations | `LOAD_BEARING` | command cutoff for final acceptance |
| `docs/governance/HELPER_NODE_POLICY.md` | helper execution boundaries and forbidden actions | `LOAD_BEARING` | implementation lane guardrail |
| `docs/governance/TASK_ID_EXECUTION_CONTRACT.md` | bounded task execution contract | `LOAD_BEARING` | implementation boundary at path/scope level |
| `docs/governance/INTEGRATION_INBOX_POLICY.md` | review routing and decision classes | `LOAD_BEARING` | command/review boundary before canonical acceptance |
| `docs/governance/CANONICAL_MACHINE_PROTECTION_POLICY.md` | protected zones and anti-bypass rules | `LOAD_BEARING` | prevents delegation overreach into protected zones |
| `workspace_config/federation_mode_contract.json` | mode-level allowed/forbidden operations | `LOAD_BEARING` | machine-enforced operational surface by mode |
| `workspace_config/delegation_registry.json` | machine-readable rank/authority/delegation baseline | `LOAD_BEARING` | bounded formalization for federation command architecture |
| `docs/governance/FEDERATION_DEPARTMENT_ESCALATION_MATRIX.md` | department-level escalation path baseline | `LOAD_BEARING` | explicit sovereign vs operational escalation boundaries |
| `scripts/validation/detect_node_rank.py` | runtime rank detection (fail-closed fallback) | `LOAD_BEARING` | executable rank signal in current pipeline |
| `scripts/validation/check_sovereign_claim_denial.py` | runtime claim denial evaluator | `LOAD_BEARING` | executable claim gate aligned with canonical claim classes (legacy aliases tolerated) |
| `docs/governance/FEDERATION_ARCHITECTURE.md` | Federation role model (creator/helper/integration) | `SECONDARY` | strong context for command flow, not full department doctrine |
| `docs/CURRENT_PLATFORM_STATE.md` | active project status reality | `SECONDARY` | current department candidates by project lines |
| `docs/review_artifacts/PROJECT_PATH_STATUS_MATRIX.md` | project/path classification map | `SECONDARY` | distinguishes registry project vs container/layer traces |
| `docs/governance/EMPEROR_MACHINE_GPT_BRIEFING_V1.md` | operational orientation for rank semantics | `SECONDARY` | useful interpretation guide |
| `docs/governance/EMPEROR_MACHINE_CODEX_BRIEFING_V1.md` | operational orientation for acceptance flow | `SECONDARY` | useful interpretation guide |
| `docs/review_artifacts/EMPEROR_ACCEPTANCE_DOSSIER_V1.md` | pre-sovereign recommendation packet | `REVIEW_ONLY` | explicitly non-final acceptance source |
| `workspace_config/emperor_local_proof_contract.json` | expected explicit Emperor proof contract file | `TOO_WEAK` | file not present in tree; cannot be used as doctrine anchor |
| `workspace_config/node_rank_claim_denial_contract.json` | expected explicit claim-denial contract file | `TOO_WEAK` | file not present in tree; cannot be used as doctrine anchor |

## 3) Rank-to-Department Delegation Matrix (Draft-Safe)

This matrix defines what can be safely stated now for Federation department command architecture.

| rank | relation to departments | may direct | may execute | may not claim | command stops | implementation begins |
|---|---|---|---|---|---|---|
| `EMPEROR` | sovereign oversight over federation/departments; final canonical authority | sovereign directives (`edict`), warrants/charters, canonical acceptance decisions | creator-grade operations including protected decisions | cannot transfer sovereignty by bundle/mirror/import; cannot bypass fail-closed gates | at sovereign acceptance and policy boundary | delegated execution under issued warrant/charter scope |
| `PRIMARCH` | creator-grade non-sovereign department command/execution actor | reintegration/engineering proposals; delegated bounded warrants only when Emperor charter explicitly allows | creator-grade non-sovereign work; bounded delegated execution | cannot assert Emperor rank; cannot assert sovereign final acceptance; cannot issue sovereign policy change | at proposal/delegated-scope boundary; no sovereign finalization | project/department execution inside bounded non-sovereign scope |
| `ASTARTES` | bounded execution lane for departments; no sovereign command role | bounded execution reporting; task return dossiers; only within warrant/charter and task scope | helper/integration bounded tasks and evidence delivery | cannot claim creator-grade sovereignty; cannot claim sovereign acceptance; cannot self-grant authority | at bounded execution/report boundary; no canonical acceptance | task/block implementation in allowed paths with required checks |

## 4) Command/Execution Boundary Cut

1. Sovereign command origin:
   - `EMPEROR` (sovereign directive/policy acceptance layer).
2. Non-sovereign directive/proposal layer:
   - `PRIMARCH` proposals and bounded delegated directives (charter-constrained).
3. Bounded implementation layer:
   - `ASTARTES`/helper task execution under contract/warrant-charter constraints.
4. Reintegration and review gate:
   - integration inbox decision flow (`ACCEPT_CANDIDATE | REJECT | QUARANTINE`).
5. Final canonical acceptance:
   - creator-authority operation only.

## 5) Explicit Limits (No Guesswork Zone)

Known strong truth:
1. Rank-based claim and execution boundaries are well defined and mostly machine-checked.
2. Warrant/charter lifecycle provides delegated execution semantics.
3. Creator-only final acceptance boundary is explicit.

Not yet proven for deep department command architecture:
1. no canonical per-department guardianship/ownership registry by rank;
2. no machine-readable delegation registry mapping rank -> department -> mandate owner;
3. no explicit escalation matrix tied to each department line;
4. no machine-readable escalation override map for department-specific exceptions.

Safety implication:
- This matrix is safe for draft-level architecture boundaries.
- Final deep leadership/delegation architecture is still blocked until missing department-level doctrine artifacts are defined.
