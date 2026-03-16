# GOVERNANCE STACK PLAN

Plan for building a governance brain stack without rewriting the whole layer in one step.

## 1) Proposed hierarchy

### Layer G0 — Governance Constitution (single authority)

Purpose: define canonical governance hierarchy, conflict resolution, and compliance boundaries.

### Layer G1 — Execution Admission Law

Purpose: strict task contract gate, acceptance/refusal rules, scope and anti-side-work controls.

### Layer G2 — Runtime Operation Laws

Purpose: machine reading order, sync/completion gates, publication boundaries, export safety boundaries.

### Layer G3 — State Contracts

Purpose: machine-readable manifests and required state artifacts with freshness/validity rules.

### Layer G4 — Evidence and Audit Trail

Purpose: review artifacts and generated reports as evidence-only outputs (non-authoritative for routing).

## 2) Proposed document set

## G0 (new/updated)

- `docs/governance/GOVERNANCE_CONSTITUTION.md` (new)
- `docs/governance/GOVERNANCE_STACK_MAP.md` (new)

## G1 (reuse, normalize links)

- `workspace_config/TASK_RULES.md`
- `workspace_config/EXECUTION_ADMISSION_POLICY.md`
- `workspace_config/TASK_SOURCE_POLICY.md`
- `workspace_config/AGENT_EXECUTION_POLICY.md`

## G2 (reuse, normalize links)

- `workspace_config/MACHINE_REPO_READING_RULES.md`
- `workspace_config/GITHUB_SYNC_POLICY.md`
- `workspace_config/COMPLETION_GATE_RULES.md`
- `docs/repo_publication_policy.md`
- `docs/CHATGPT_BUNDLE_EXPORT.md`

## G3 (reuse + fill gaps)

- `workspace_config/workspace_manifest.json`
- `workspace_config/codex_manifest.json`
- `workspace_config/SAFE_MIRROR_MANIFEST.json`
- `docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md`

## G4 (evidence only)

- `docs/review_artifacts/*`

## 3) Order of implementation

1. **Stabilize current truth inputs**
   - refresh stale sanitization report
   - resolve absolute-path policy contradiction

2. **Create G0 authority layer**
   - add governance constitution and stack map
   - define conflict resolution order and legacy-reference policy

3. **Link G1/G2 to G0**
   - make existing policy docs reference G0 as parent authority
   - remove duplicate normative text where possible, keep concise operational rules

4. **Harden G3 state controls**
   - define freshness rule for generated artifacts
   - define generation->commit sequencing rule for safe-state manifests/reports
   - fill `codex_manifest.bootstrap_read_order`

5. **Constrain G4 evidence role**
   - mark review artifacts as non-authoritative in one consistent language pattern

6. **Add governance self-audit loop**
   - define required periodic checks (contradictions, stale reports, legacy noise, false completion risk)

## 4) Short rationale by layer

- **G0**: removes ambiguity; gives machine one source for governance authority.
- **G1**: protects against scope drift and non-contract execution.
- **G2**: enforces deterministic machine operations and completion discipline.
- **G3**: makes machine-readable state trustworthy and fresh.
- **G4**: preserves evidence value without letting artifacts override authority.

## 5) Non-goals for this phase

- no architecture rebuild
- no UI work
- no broad policy rewrite in one step
- no additional governance docs beyond those needed for G0 kickoff

## 6) Immediate next move after this plan

Implement G0 minimal set first:

1. `GOVERNANCE_CONSTITUTION.md`
2. `GOVERNANCE_STACK_MAP.md`
3. cross-links from `README.md`, `INSTRUCTION_INDEX.md`, and `workspace_config` policy files
