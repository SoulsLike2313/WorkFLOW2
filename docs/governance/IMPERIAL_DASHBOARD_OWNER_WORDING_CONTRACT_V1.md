# IMPERIAL_DASHBOARD_OWNER_WORDING_CONTRACT_V1

Status:
- class: `owner_readable_wording_contract`
- scope: `imperial_dashboard_full_vision`
- mutability: `bounded_operational`
- authority: `bounded_operational_with_owner_gates`

## Purpose

Сделать первый слой owner-экрана человеком читаемым и русским, без потери truth parity.

## Wording law (first layer)

1. first layer answers in short human Russian:
- что происходит,
- почему так,
- можно ли этому верить,
- что ограничивает,
- что под вопросом.
2. avoid mixed RU/EN noise in primary cards and titles.
3. avoid raw key-value technical dumps in primary zone.

## Technical truth law (second layer)

1. technical labels/codes are preserved in secondary layer only:
- hover/title,
- details/disclosure,
- debug/command surfaces.
2. technical truth must stay source-linked.
3. technical detail cannot be hidden when owner opens disclosure.

## Truth parity law

For each owner-facing zone (overview/brain/product line/history/prompt):
1. statement must be tied to repo-visible surfaces,
2. exact vs derived vs gap vs stale must remain explicit,
3. no fake realtime,
4. no fake completeness,
5. stale and unknown reasons must stay visible.

## Boundary

1. this contract does not remove Command Mode raw surfaces,
2. this contract does not authorize decorative replacements for truth,
3. this contract does not override governance/bundle/validation law.
