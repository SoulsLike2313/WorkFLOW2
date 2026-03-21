# WORKFLOW2 GPT Onboarding Master V1

## 1. Purpose

Single high-density onboarding surface for a new GPT/Codex session.
This document summarizes mandatory operating rules, canonical sources, authority boundaries, control gates, and execution entrypoints.

This file is a summary layer, not a replacement for source authority contracts.

## 2. Canonical Identity

- Working source of truth: `E:\CVVCODEX`
- Public mirror: `safe_mirror/main` (`WorkFLOW2`) and safe-only by design
- Current constitutional regime: `constitution-v1-finalized` with lightweight constitutional enforcement
- Mission Layer status: accepted/certified baseline
- Default authority principle: creator-only canonical acceptance

## 3. Non-Negotiable Laws

1. No completion without repo-visible truth.
2. No completion without sync parity to `safe_mirror/main`.
3. No completion without required verification chain.
4. No silent scope expansion.
5. No side work outside explicit task scope.
6. No canonical acceptance in helper mode.
7. No local sovereign substrate path/raw detail disclosure in tracked repo.
8. No publishing full private runtime/content via unsafe export paths.

## 4. Authority and Machine Mode

Rank-derived model (v2):

- `EMPEROR` -> `creator`
- `PRIMARCH` -> `helper(high)`
- `ASTARTES` -> `helper(low)`

Rank source:

- `repo only` -> `ASTARTES`
- `repo + genome` -> `PRIMARCH`
- `repo + local sovereign substrate` -> `EMPEROR`
- `repo + genome + local sovereign substrate` -> `EMPEROR` (substrate decisive).

Mode consequences:

- `creator`: canonical acceptance/certification decisions.
- `helper(high)`: non-sovereign director-grade helper envelope.
- `helper(low)`: execution-grade helper envelope.
- `integration`: work posture/intent overlay only (`authority_effect=none`).

Legacy compatibility note:

- `CVVCODEX_CREATOR_AUTHORITY_DIR` / `creator_authority.json` remains telemetry-only compatibility surface.
- It is non-load-bearing for rank and non-load-bearing for creator mode.

## 5. Canonical Source Precedence

Use this order on contradictions:

1. `docs/governance/FIRST_PRINCIPLES.md`
2. `docs/governance/GOVERNANCE_HIERARCHY.md`
3. `workspace_config/workspace_manifest.json`
4. `workspace_config/codex_manifest.json`
5. Layer registries/contracts (`workspace_config/*.json`, governance contracts)
6. Runtime artifacts as evidence, never primary policy authority

If surfaces conflict, mark stale claim, align to higher-precedence source, and record correction in review artifact when needed.

## 6. Mandatory Bootstrap Path

Read first:

1. `README.md`
2. `workspace_config/workspace_manifest.json`
3. `workspace_config/codex_manifest.json`
4. `REPO_MAP.md`
5. `MACHINE_CONTEXT.md`
6. `docs/INSTRUCTION_INDEX.md`
7. `docs/CURRENT_PLATFORM_STATE.md`
8. `docs/NEXT_CANONICAL_STEP.md`
9. Constitutional core: `docs/governance/WORKFLOW2_CONSTITUTION_V1.md`
10. Vocabulary freeze: `docs/governance/WORKFLOW2_CANONICAL_VOCABULARY_V1.md`

Full strict read order: `MACHINE_CONTEXT.md` and `docs/INSTRUCTION_INDEX.md`.

## 7. Current Layer Baseline

- Governance brain stack: accepted
- Repo Control Center: accepted
- Query layer: accepted
- Operator command execution layer: accepted
- Task/program layer: accepted
- Mission/work package layer: accepted/certified baseline
- Constitution V1: finalized

## 8. Core Verdict Chain

Primary control verdicts:

- Trust: `TRUSTED | WARNING | NOT_TRUSTED`
- Sync: `IN_SYNC | DRIFTED | BLOCKED`
- Governance: `COMPLIANT | PARTIAL | NON_COMPLIANT`
- Admission: `ADMISSIBLE | CONDITIONAL | REJECTED`
- Governance acceptance: `PASS | FAIL`
- Evolution: `HOLD | PREPARE | V2_CANDIDATE | V2_READY | PROMOTE | BLOCKED`

Constitutional aggregate:

- `PASS | PARTIAL | FAIL | UNKNOWN` (from constitutional checks aggregation)

## 9. Required Runtime Truth Surfaces

- `runtime/repo_control_center/repo_control_status.json`
- `runtime/repo_control_center/repo_control_report.md`
- `runtime/repo_control_center/evolution_status.json`
- `runtime/repo_control_center/evolution_report.md`
- `runtime/repo_control_center/machine_mode_status.json`
- `runtime/repo_control_center/machine_mode_report.md`
- `runtime/repo_control_center/one_screen_status.json`
- `runtime/repo_control_center/plain_status.md`
- `runtime/repo_control_center/constitution_status.json`
- `runtime/repo_control_center/constitution_status.md`

Mission/program evidence surfaces:

- `runtime/repo_control_center/operator_program_*.json`
- `runtime/repo_control_center/operator_mission_*.json`
- `runtime/repo_control_center/mission_proof_index.json`

## 10. Mandatory Validation Chain

Base repository checks:

1. `git status --short --branch`
2. `git rev-parse HEAD`
3. `git rev-parse safe_mirror/main`
4. `git rev-list --left-right --count HEAD...safe_mirror/main`
5. `python scripts/check_repo_sync.py --remote safe_mirror --branch main`
6. `python scripts/validate_workspace.py`

Control checks:

1. `python scripts/detect_machine_mode.py --intent creator --strict-intent` (when creator-grade claim is needed)
2. `python scripts/repo_control_center.py bundle`
3. `python scripts/repo_control_center.py full-check`
4. `python scripts/validation/run_constitution_checks.py`

Layer consistency checks when relevant:

- `python scripts/operator_command_surface.py consistency-check`
- `python scripts/operator_task_program_surface.py consistency-check`
- `python scripts/operator_mission_surface.py consistency-check`

## 11. Completion and Publication Discipline

Completion claim is valid only if:

- required checks pass,
- runtime freshness is current enough for claim context,
- worktree is clean,
- branch is pushed,
- divergence is `0/0`.

Publication to ChatGPT:

- Use targeted export only: `scripts/export_chatgpt_bundle.py`
- Standard modes keep runtime restricted
- Audit runtime mode is separate and allowlist-controlled (`audit-runtime --include-rcc-runtime`)
- Export must explicitly say `SAFE TO SHARE WITH CHATGPT: YES`

## 12. Mission/Program/Command Relationship

- Query layer classifies and explains.
- Command layer executes bounded atomic operations.
- Task/program layer composes repeatable multi-step program flows.
- Mission layer composes work packages over programs with checkpointed evidence and completion semantics.
- None of these layers may bypass governance/authority gates.

## 13. Constitution V1 Lightweight Enforcement Set

Operationally present:

- Canonical vocabulary freeze
- Truth state schema/model
- Canonical contradiction scan
- Registry/doc drift guard
- Proof-output naming policy
- Constitution phase hygiene checklist
- Constitutional admission flow
- Gate severity model + operator response guide
- Constitution status surface

Design intent: lightweight but enforceable discipline, not heavy full-automation gate framework.

## 14. Portable Session / Reintegration (If Used)

Portable workflow references:

- `docs/governance/PORTABLE_WORK_SESSION_PROTOCOL_V1.md`
- `docs/governance/RETURN_BUNDLE_POLICY_V1.md`
- `docs/governance/REINTEGRATION_CHECKLIST_V1.md`
- `runtime/portable_session/PORTABLE_SESSION_BOOTSTRAP_NOTE.md`
- `runtime/portable_session/portable_session_manifest.json`
- `runtime/portable_session/RETURN_BUNDLE_INSTRUCTIONS_V1.md`

Portable transfer never overrides canonical source precedence or rank-derived authority discipline.

## 15. Operator Do/Do-Not Quick Matrix

Do:

- Keep claims evidence-backed.
- Keep phase/current-state surfaces coherent.
- Separate role limitations from system-quality failures.
- Mark stale contradictions explicitly before claiming completion.

Do not:

- Claim PASS with stale critical evidence.
- Treat helper outputs as canonical acceptance.
- Bypass review/certification rules by narrative wording.
- Expose forbidden runtime categories via export.
- Treat safe mirror as full working repository.

## 16. Fast Session Startup (Minimal)

For a new GPT session that needs immediate operational alignment:

1. Read this file.
2. Read `README.md`, `MACHINE_CONTEXT.md`, `docs/CURRENT_PLATFORM_STATE.md`, `docs/NEXT_CANONICAL_STEP.md`.
3. Run `python scripts/detect_machine_mode.py --intent auto`.
4. Run `python scripts/repo_control_center.py full-check`.
5. Run `python scripts/validation/run_constitution_checks.py`.
6. Only then accept bounded execution scope.

## 17. Canonical References

- Core law: `docs/governance/WORKFLOW2_CONSTITUTION_V1.md`
- Vocabulary: `docs/governance/WORKFLOW2_CANONICAL_VOCABULARY_V1.md`
- Source precedence: `docs/governance/CANONICAL_SOURCE_PRECEDENCE.md`
- Admission flow: `docs/governance/CONSTITUTIONAL_ADMISSION_FLOW_V1.md`
- Mission baseline: `docs/governance/OPERATOR_MISSION_LAYER_BASELINE.md`
- Mission registry: `workspace_config/operator_mission_registry.json`
- Control engine: `scripts/repo_control_center.py`
