# PORTABLE_WORK_SESSION_PROTOCOL_V1

Status:
- protocol_version: `v1`
- scope: `portable creator/helper operation without sovereign transfer`

## 1) Purpose

Define portable work session rules for cross-machine operation under WorkFLOW2 without transferring Emperor sovereignty.

## 2) Portable Session Nature

Portable session bundle is:
1. operational working-state transfer artifact;
2. bounded by constitutional and reintegration discipline.

Portable session bundle is not:
1. sovereign canonical-node transfer;
2. automatic Emperor-rank grant.
3. replacement for canonical root validation.

## 3) Rank Outcome On Target Machine

Target node rank is resolved by policy:

1. valid creator authority contract + valid Emperor local proofs -> `Emperor`
2. valid creator authority contract (without Emperor local proofs) -> `Primarch`
3. no valid creator authority contract -> `Astartes`

Default portable outcome:
- no Emperor sovereignty by bundle alone.

## 4) Authority Contract Requirement

Primarch-grade operation requires valid external creator authority contract:

1. `CVVCODEX_CREATOR_AUTHORITY_DIR` set;
2. pointed directory exists;
3. valid `creator_authority.json` in that external path.

If this contract fails, node operates as `Astartes` helper/integration mode.

## 4.1) Canonical Root Requirement

Expected root context:
1. `E:\CVVCODEX` across nodes, unless explicit documented exception.

If root context is invalid or ambiguous:
1. no Emperor elevation;
2. rank confidence narrows fail-closed;
3. sovereign claims are denied.

## 5) Portable Content Rules

Portable bundle should include:
1. repo working state and required runtime truth surfaces;
2. policy references and reintegration instructions;
3. evidence artifacts required for return review.

Portable bundle must exclude:
1. Emperor-only local proofs;
2. canonical local secret paths;
3. sovereign-transfer claims.

## 6) Bootstrap And Validation On Target Machine

Required order:

1. read bootstrap docs listed in `runtime/portable_session/PORTABLE_SESSION_BOOTSTRAP_NOTE.md`;
2. resolve node rank and authority placement;
3. run canonical checks;
4. proceed only within admitted mode boundaries.

## 7) Claim Discipline

Portable node may claim:
1. creator-grade readiness when authority contract is valid;
2. helper/integration readiness when authority contract is absent.

Portable node may not claim:
1. Emperor sovereignty by bundle possession;
2. sovereign/canonical-node identity transfer.
3. sovereign acceptance in safe mirror or portable-only context.

## 8) Reintegration Discipline

Portable sessions return through:
1. `RETURN_BUNDLE_POLICY_V1.md`
2. `REINTEGRATION_CHECKLIST_V1.md`
3. source precedence and manual sync doctrine.

Canonical machine remains final sovereign acceptance authority.

## 9) Astartes Constraint

If node resolves to `Astartes`, execution authority must be treated as warrant/charter-bound and report-only for non-sovereign claims.
