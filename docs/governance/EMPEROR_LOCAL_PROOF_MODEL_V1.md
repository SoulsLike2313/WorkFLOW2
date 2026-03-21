# EMPEROR_LOCAL_PROOF_MODEL_V1

Status:
- policy_version: `v1.rewritten_for_status_model_v2`
- scope: `local sovereign substrate interface for Emperor rank`
- security_posture: `strict local-only, non-exportable`

## 1) Purpose

Define Emperor-only proof as:
1. full repo copy validation pass;
2. valid external local sovereign substrate.

This model explicitly excludes creator marker dependency.

## 2) Canonical Generic Names

Repo-visible surfaces use only:
1. `local_sovereign_substrate`
2. `sovereign_local_contract`
3. `local_authority_root`
4. `emperor_local_proof_surface`

## 3) Contract Anchor

Machine-readable anchor:
1. `workspace_config/emperor_local_proof_contract.json`

It defines:
1. env hook for substrate location;
2. proof surface marker requirements;
3. local authority root marker naming;
4. companion-file requirements;
5. forbidden origins and export boundaries.

Canonical env hook:
1. `CVVCODEX_LOCAL_SOVEREIGN_SUBSTRATE_DIR` only.

Legacy env/marker names:
1. may exist in machine environment as historical residue;
2. are deprecated and ignored for authority determination.

## 4) Verification Conditions

Emperor validity requires all pass:
1. repo-copy anchors valid;
2. substrate path exists and is external to repo root;
3. substrate path not in forbidden origin zones;
4. proof surface marker fields/literals/booleans match contract;
5. local root binding matches expected workspace slug;
6. required companion files are present.

## 5) Fail-Closed Behavior

1. missing substrate env/path/marker -> not Emperor;
2. invalid marker or binding mismatch -> not Emperor;
3. forbidden origin token/path -> not Emperor;
4. repo-only copy -> at most `ASTARTES`.

## 6) Export and Visibility Discipline

1. raw substrate internals are not tracked and not exported;
2. only contract-level and validator-level safe equivalents are shareable;
3. mirror/portable/import artifacts cannot transport Emperor status.

## 7) Compatibility Notice

Legacy creator-marker surfaces may still exist for compatibility telemetry, but they are never load-bearing for Emperor determination and never authoritative for creator mode in v2. Legacy emperor env/marker fallback is removed from authority path.
