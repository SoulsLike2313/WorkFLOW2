# 09_SEED_REVIEW_REGISTRY

Seed review registry binds current review evidence to onboarding layers.

## Current review roots (latest-first)
1. `docs/review_artifacts/imperium_wave1_native_organs_zero_drift_internal_first_delta_20260328T082128Z`

## Current safe review set
- review root: `docs/review_artifacts/imperium_safe_review_pipeline_set_20260327T200851Z`
- export set: `runtime/chatgpt_bundle_exports/imperium_safe_review_pipeline_set_20260327T200851Z`

## Injection layers

1. GPT layer:
- compact summary + `for_chatgpt/06_CURRENT_REVIEW_POINTERS.md`
- no heavy payload in paste block

2. Codex layer:
- full registry + reconstruction order + full pointer set
- use `for_codex/05_CONTEXT_POINTERS_AND_RECOVERY.md`

## Refresh rule

- `python scripts/refresh_imperium_seed_capsule.py --capsule-root docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1`

Last refreshed (UTC): 2026-03-28T08:21:49Z
