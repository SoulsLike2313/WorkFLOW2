# CHAT_TRANSFER_CAPSULE_DOCTRINE_V1

Status:
- class: `foundation_transfer_capsule_doctrine`
- mutability: `immutable_by_default`
- change_authority: `EMPEROR_ONLY`

## Purpose

Define cheap transfer capsule for new chat/account/session without full bundle archaeology.

## Capsule minimum fields

1. system identity,
2. foundation/live split pointers,
3. current active mode,
4. current primary artifact path,
5. current companion path (if required),
6. open owner decisions,
7. next canonical step.

## Capsule constraints

1. compact by default,
2. no long retelling,
3. exact paths mandatory,
4. truth-linked and updateable per bounded step.

## Capsule boundary

Capsule is entry aid, not replacement for validation/report bundle internals.

## Integration

1. `docs/governance/SYSTEM_ENTRYPOINT_V1.md`
2. `docs/governance/SYSTEM_CHEAP_ONBOARDING_CONTRACT_V1.md`
3. `docs/governance/SINGLE_ARTIFACT_ENTRYPOINT_RESPONSE_LAW_V1.md`
