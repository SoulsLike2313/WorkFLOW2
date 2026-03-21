# LOCAL_SOVEREIGN_SUBSTRATE_BOUNDARY_REPORT

Status:
- report_version: `v1`
- scope: `boundary and leakage discipline for sovereign local substrate`

## Boundary Rules

1. substrate must live outside tracked repo;
2. substrate must never be required to pass through network channel;
3. substrate must never be included in safe mirror;
4. substrate must never be included in normal ChatGPT export bundles.

## Detection vs Exposure

Allowed:
1. detect presence/validity through generic contract hooks.

Forbidden:
1. exposing raw substrate internals in repo-visible surfaces.

## Fail-Closed Downgrade

1. substrate absent/invalid -> no EMPEROR;
2. node falls back to PRIMARCH (if genome valid) or ASTARTES.

## Export Leakage Guards

1. marker booleans require `non_exportable=true`, `portable_transferable=false`, `mirror_transferable=false`;
2. forbidden origin tokens block import/export staging paths from acting as sovereign proof.
