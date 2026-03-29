# 07_OWNER_USE_FLOW

## Fast seed flow

1. open capsule root:
- `docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/`
2. paste to GPT:
- `for_chatgpt/01_PASTE_THIS_FULL.md`
3. if context tight:
- `for_chatgpt/02_PASTE_THIS_IF_CONTEXT_IS_TIGHT.md`
4. ask:
- `for_chatgpt/03_AFTER_PASTE_ASK_THIS.md`
5. validate shape:
- `for_chatgpt/04_EXPECTED_GPT_CONFIRMATION_SHAPE.md`
6. verify pointers:
- `for_chatgpt/05_CURRENT_BUNDLE_POINTERS.md`
- `for_chatgpt/06_CURRENT_REVIEW_POINTERS.md`
- `08_CURRENT_POINT_VERIFICATION.md`

## GPT/Codex cross-check

1. get GPT reconstruction
2. run Codex reconstruction checklist (`for_codex/07_CODEX_RECONSTRUCTION_CHECKLIST.md`)
3. compare key fields: line split, active vertex, open risks, next step
4. if match -> continue work
5. if mismatch -> refresh seed via `03_CAPSULE_UPDATE_PROTOCOL.md`

## Refresh commands

- refresh seed pointers/registry:
`python scripts/refresh_imperium_seed_capsule.py --capsule-root docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1`
