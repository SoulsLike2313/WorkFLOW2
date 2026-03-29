# 03_CAPSULE_UPDATE_PROTOCOL

Seed refresh must be predictable, repeatable, and low-noise.

## Standard refresh command

- `python scripts/refresh_imperium_seed_capsule.py --capsule-root docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1`

## Update order

1. refresh `MUTABLE_TRACKER.json`
2. refresh `06_CURRENT_WORK_LADDER_AND_RECENT_CHAIN.md`
3. refresh `08_CURRENT_POINT_VERIFICATION.md`
4. refresh `09_SEED_REVIEW_REGISTRY.md`
5. refresh `for_chatgpt/05_CURRENT_BUNDLE_POINTERS.md`
6. refresh `for_chatgpt/06_CURRENT_REVIEW_POINTERS.md`
7. refresh `for_chatgpt/07_IMPERIUM_SEED_SUPERCOMPACT_STATE.md`
8. refresh `for_codex/05_CONTEXT_POINTERS_AND_RECOVERY.md`

## Invariants

1. do not collapse continuity/handoff/live lines
2. do not mix foundation and mutable
3. do not allow stale active-live wording
4. keep open gaps explicit
5. keep one external artifact entrypoint in chat handoff
