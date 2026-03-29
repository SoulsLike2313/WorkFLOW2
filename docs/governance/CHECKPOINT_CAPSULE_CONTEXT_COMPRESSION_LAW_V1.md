# CHECKPOINT_CAPSULE_CONTEXT_COMPRESSION_LAW_V1

## Status

- status: `active`
- scope: `E:\CVVCODEX`

## Goal

Compress long chat history into compact repo-visible checkpoint capsules for reliable context transfer.

## Capsule Rule

After each major step, create one compact checkpoint capsule artifact.

Mandatory capsule fields:

1. what changed,
2. what was proven,
3. what remains open,
4. current primary bundle (latest + immutable),
5. current next step.

## Prompting Rule

Future steps should reference:

1. latest capsule,
2. declared primary bundle,
3. exact new delta.

Avoid re-narrating full historical chat unless owner explicitly requests expansion.

## Compression Boundary

Capsule is a compression tool, not truth replacement.
Exact evidence remains in bundle/report surfaces.

## Minimal Capsule Template

```md
# STEP_CAPSULE_<STEP_ID>_V1
- changed:
- proven:
- open:
- primary_bundle_latest:
- primary_bundle_immutable:
- companion_if_any:
- next_step:
```

## Linked Law

- `docs/governance/LIMIT_ECONOMY_MODE_LAW_V1.md`
- `docs/governance/CANONICAL_TRUTH_REVIEW_BUNDLE_LAW_V1.md`
