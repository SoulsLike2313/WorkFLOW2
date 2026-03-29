# DECISION_GATE_REGISTRY_V1

Статус:
- version: `v1`
- memory_role: `owner_controlled_fork_registry`
- labels_used: `PROVEN | ACTIVE | MAPPED | FROZEN | NOT YET IMPLEMENTED`

## Правило реестра

Если gate обязателен, следующий шаг не может идти без его approval.

## GATE_A_PRODUCT_INTERPRETATION (`ACTIVE`)

- What decided: правильность трактовки продукта и его проблем.
- When opens: после intake + forensic + technical map.
- Who may propose: Analytics/Primarch.
- Who must approve: Owner.
- What blocked without it: option selection и execution waves.

## GATE_B_OPTION_SELECTION (`ACTIVE`)

- What decided: выбор пути A/B/C.
- When opens: после готового option space и comparison matrix.
- Who may propose: Analytics/Primarch.
- Who must approve: Owner.
- What blocked without it: любой wave execution.

## GATE_C_UI_VISUAL_DIRECTION (`ACTIVE`)

- What decided: границы UI/visual rewrite.
- When opens: после option choice и UI impact breakdown.
- Who may propose: Primarch/Engineering lead.
- Who must approve: Owner.
- What blocked without it: крупные UI/flow изменения.

## GATE_D_WAVE_TRANSITION (`ACTIVE`)

- What decided: переход между wave 1/2/3/4.
- When opens: после wave evidence pack.
- Who may propose: Primarch.
- Who must approve: Owner.
- What blocked without it: запуск следующей волны.

## GATE_E_RELEASE_SHAPE (`MAPPED`)

- What decided: целевая форма релиза.
- When opens: после wave 3 readiness evidence.
- Who may propose: Release/Integration.
- Who must approve: Owner.
- What blocked without it: release candidate finalization.

## GATE_F_FINAL_PRODUCT_VERDICT (`MAPPED`)

- What decided: final ready/partial/blocked verdict.
- When opens: после full evidence chain.
- Who may propose: Primarch + Verification.
- Who must approve: Owner (Emperor authority context).
- What blocked without it: завершение продукта как release-grade.

## GATE_HARDEN_VS_REBUILD (`ACTIVE`)

- What decided: продолжать hardening или переходить в rebuild.
- When opens: при накоплении критических structural blockers.
- Who may propose: Primarch + Analytics.
- Who must approve: Owner.
- What blocked without it: deep strategy pivot.

## GATE_PUBLIC_RELEASE_DISTRIBUTION (`MAPPED`)

- What decided: можно ли выходить в публичное распространение.
- When opens: после release-grade внутренней стадии.
- Who may propose: Release/Integration.
- Who must approve: Owner.
- What blocked without it: public release actions.

## GATE_STRATEGIC_ACTIVATION (`MAPPED`)

- What decided: открытие новых стратегических программ/департаментов.
- When opens: при закрытии текущего frontier и выполнении unlock criteria.
- Who may propose: Primarch/Strategic layer.
- Who must approve: Owner.
- What blocked without it: переход в следующий стратегический контур.

