# BUNDLE_RETENTION_AND_CLEANUP_MODEL_V1

Status:
- status: `active`
- model_version: `v1`

## Model Layers

1. Canonical retained artifacts:
   - governance docs/contracts
   - tracked review artifacts in active canon
   - policy-linked reports
2. Ephemeral operational artifacts:
   - staging folders
   - request include lists
   - generated export zips used as transfer carriers
3. Protected current set:
   - latest bundle run per ephemeral root
   - pinned items

## Why This Model Exists

1. prevent workspace bloat from temporary exports;
2. preserve reproducibility and safety;
3. avoid accidental deletion of canonical evidence;
4. keep cleanup deterministic and machine-runnable.

## Retention Behavior

1. ephemeral items live in explicit runtime roots;
2. after 24h they become cleanup-eligible;
3. janitor deletes only eligible + non-protected entries.

## Cleanup Behavior

1. default mode = dry-run with full target listing;
2. apply mode = explicit deletion with per-item action logs;
3. report output includes deleted/skipped/protected breakdown.

## Non-Goals

1. deleting canonical tracked docs;
2. rewriting governance history;
3. replacing evidence retention policy for non-ephemeral classes.

## Anchors

- `docs/governance/EPHEMERAL_BUNDLE_TTL_POLICY_V1.md`
- `workspace_config/EPHEMERAL_BUNDLE_TTL_CONTRACT.json`
- `scripts/ttl_bundle_janitor.py`
- `docs/governance/EVIDENCE_RETENTION_POLICY.md`

