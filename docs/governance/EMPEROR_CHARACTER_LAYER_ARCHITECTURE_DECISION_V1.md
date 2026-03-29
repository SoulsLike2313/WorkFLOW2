# EMPEROR_CHARACTER_LAYER_ARCHITECTURE_DECISION_V1

Status:
- decision_state: `ACTIVE`
- decision_id: `ECL-ADR-001`
- scope: `controlled_owner_character_layer`

## Decision

Chosen architecture:
1. one canonical kernel (`EMPEROR_CHARACTER_KERNEL_V1`),
2. two role-specific projections:
   - `CHATGPT_OWNER_MIRROR_PROFILE_V1`,
   - `CODEX_OWNER_GUARD_PROFILE_V1`.

This layer is advisory and guard-rail based only.
It never overrides canonical repo law, governance gates, or evidence discipline.

## Why This Option

1. Preserves one source of owner-character truth.
2. Avoids role confusion between interpretation work (ChatGPT) and execution control (Codex).
3. Gives stable continuity across sessions without hidden learning.
4. Keeps owner control explicit: evolution enters kernel only through repo-visible acceptance.

## Rejected Alternatives

### A) Only-ChatGPT personality layer

Rejected because:
1. Codex execution guard would remain under-specified.
2. Drift detection would not be enforced inside implementation loops.
3. High risk of narrative quality without execution discipline.

### B) Only-Codex personality layer

Rejected because:
1. Owner-level interpretive continuity would be weakened.
2. Explanation quality and reflective mirror support would degrade.
3. Complex strategic discussions would lose structured owner-context handling.

### C) Same behavior profile for both agents

Rejected because:
1. Roles are different by design.
2. A single behavior profile causes either over-soft Codex or over-rigid ChatGPT.
3. Increased risk of contradiction or overreach in one of the agents.

## Hard Boundaries

1. No claim of "living consciousness".
2. No pseudo-psychological diagnosis.
3. No private/intimate details.
4. No hidden mutation from ad-hoc episodes.
5. No authority to rewrite source-of-truth surfaces.

## Canonical Links

1. `docs/governance/EMPEROR_CHARACTER_KERNEL_V1.md`
2. `docs/governance/CHATGPT_OWNER_MIRROR_PROFILE_V1.md`
3. `docs/governance/CODEX_OWNER_GUARD_PROFILE_V1.md`
4. `docs/governance/OWNER_DRIFT_DETECTION_AND_RECOVERY_PROTOCOL_V1.md`
5. `docs/governance/EMPEROR_CHARACTER_EVOLUTION_LEDGER_V1.md`
6. `docs/governance/EMPEROR_CHARACTER_LAYER_USAGE_LAW_V1.md`

