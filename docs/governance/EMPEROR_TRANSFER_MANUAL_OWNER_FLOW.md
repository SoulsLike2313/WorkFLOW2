# EMPEROR_TRANSFER_MANUAL_OWNER_FLOW

Status:
- manual_version: `v1`
- scope: `owner-only offline Emperor transfer`

## Preconditions

1. target machine has full repo copy anchors;
2. owner controls local sovereign substrate package outside repo;
3. no network-dependent transfer step is required.

## Procedure

1. place local sovereign substrate directory outside repo on target machine;
2. ensure `emperor_local_proof_surface` marker + companion files exist;
3. set `CVVCODEX_LOCAL_SOVEREIGN_SUBSTRATE_DIR` to that directory;
4. run `python scripts/validation/detect_node_rank.py --json-only --no-write`;
5. verify:
   - `detected_rank=EMPEROR`
   - substrate proof status `VALID`.

## Negative Control

1. clear substrate env var;
2. rerun rank detection;
3. confirm downgrade (`PRIMARCH` if genome exists, else `ASTARTES`).

## Safety Notes

1. never place substrate inside repo root;
2. never include substrate in public mirror or ChatGPT safe bundles;
3. never treat genome bundle as sovereign substrate replacement.
