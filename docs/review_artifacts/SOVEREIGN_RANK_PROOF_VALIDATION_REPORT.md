# SOVEREIGN_RANK_PROOF_VALIDATION_REPORT

- generated_at_utc: `2026-03-18T14:00:00Z`
- validator: `scripts/validation/detect_node_rank.py`
- policy_anchor: `docs/governance/SOVEREIGN_RANK_PROOF_MODEL_V1.md`

## 1) Proof Classes Currently Machine-Checked

### Required (implemented)

1. canonical root validity (`E:\CVVCODEX` match check);
2. Primarch authority contract validity (`CVVCODEX_CREATOR_AUTHORITY_DIR` + valid `creator_authority.json`);
3. Emperor proof marker contract (`CVVCODEX_EMPEROR_PROOF_DIR` + valid `emperor_sovereign_proof.json` fields + root binding).

### Supporting (policy-level only)

1. sovereign continuity evidence chain;
2. cryptographic issuer identity binding for sovereign proof artifacts;
3. signed inter-node authority proof linkage.

## 2) Observed Runtime Scenarios

1. no authority path -> `ASTARTES` (fail-closed fallback)
2. valid creator authority + missing emperor proof -> `PRIMARCH`
3. valid creator authority + invalid emperor root binding -> `PRIMARCH`
4. valid creator authority + valid emperor proof marker -> `EMPEROR`

## 3) Edge Cases And Residual Gaps

1. canonical-root mismatch behavior is implemented fail-closed, but not observed here because runtime root already equals expected root;
2. supporting proof classes are not yet machine-verified;
3. leftover portable files are ignored for elevation, but broader residue hygiene still depends on operational discipline.

## 4) Canonical Root Influence On Rank Confidence

1. root mismatch blocks Emperor elevation by design;
2. root ambiguity narrows confidence and triggers fail-closed reasons;
3. root validity is now explicit output surface for constitutional aggregation.

## 5) Safe Mirror Influence

`WorkFLOW2` safe mirror has no elevation path in validator logic and does not contribute to sovereign proof status.

## 6) Verdict

`MODERATE`

Rationale:
- required baseline proof gates are now machine-checked,
- full sovereign-proof strength remains partial until supporting proof classes gain machine verification.
