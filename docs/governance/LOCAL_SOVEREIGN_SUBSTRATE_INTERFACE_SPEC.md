# LOCAL_SOVEREIGN_SUBSTRATE_INTERFACE_SPEC

Status:
- spec_version: `v1`
- scope: `generic repo-visible interface for local sovereign substrate`

## 1) Purpose

Expose only minimal hooks needed for machine validation without exposing sovereign raw internals.

## 2) Generic Interface Elements

1. `local_sovereign_substrate` path hook via env var;
2. `emperor_local_proof_surface` marker filename/fields;
3. `local_authority_root` marker filename presence;
4. companion files required for continuity/possession checks.

## 3) Contract Anchor

`workspace_config/emperor_local_proof_contract.json`

Defines:
1. env hook names (primary + compatibility);
2. marker fields/literals/booleans;
3. forbidden origins;
4. export and portability booleans;
5. path rule `outside_repo_root`.

## 4) What Repo Must Not Know

1. substrate raw secret structure;
2. owner-specific sovereign internals;
3. private transfer details and secret material.

## 5) Verification Logic

1. find substrate path by env hook;
2. enforce forbidden-origin and path rules;
3. parse marker and validate required contract fields;
4. verify companion files;
5. fail-closed on any mismatch.
