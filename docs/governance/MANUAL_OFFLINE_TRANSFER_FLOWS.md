# MANUAL_OFFLINE_TRANSFER_FLOWS

Status:
- flow_pack_version: `v1`
- scope: `owner-manual offline rank transfer procedures`

## FLOW A — ASTARTES Workspace Transfer

1. copy full repo workspace 1:1 to target machine;
2. do not provide genome bundle;
3. do not provide local sovereign substrate;
4. run rank detection;
5. expected result: `ASTARTES`.

## FLOW B — PRIMARCH Grant via Genome Bundle

1. on EMPEROR machine issue genome bundle;
2. transfer repo copy + genome bundle manually offline;
3. set genome bundle env hook on target machine;
4. run rank detection;
5. expected result: `PRIMARCH`;
6. confirm `EMPEROR` is still denied without local substrate.

## FLOW C — EMPEROR Transfer (Owner-only)

1. transfer full repo copy manually;
2. transfer local sovereign substrate manually (owner-controlled offline);
3. configure substrate env hook on target machine;
4. run rank detection;
5. expected result: `EMPEROR`;
6. clear substrate hook and rerun -> downgrade confirms fail-closed behavior.
