# PRODUCT_CLASS_MAP_V1

Статус:
- version: `v1`
- memory_role: `product_family_map`
- labels_used: `PROVEN | ACTIVE | MAPPED | FROZEN | NOT YET IMPLEMENTED`

## Принцип

Фабрика хранит память не как бесконечный список приложений, а как классы продуктов.
Это позволяет переиспользовать patterns, playbooks и gates.

## 1) System tools

- Почему важно: дают инфраструктурную устойчивость и контроль среды.
- Общие patterns: status surfaces, diagnostics, control planes.
- Department involvement: Analytics + Tooling/Infra + Verification.
- Reusable assets: runtime checklists, observability templates.

## 2) Network / performance tools

- Почему важно: влияют на reliability и user-perceived quality.
- Общие patterns: benchmarking, regression profiles, resource guards.
- Department involvement: Analytics + Engineering + Verification.
- Reusable assets: perf baselines, incident playbooks.

## 3) Voice tools

- Почему важно: user-facing interaction quality и latency sensitivity.
- Общие patterns: pipeline quality checks, model/flow fallback safety.
- Department involvement: Analytics + Engineering + Product Intelligence.
- Reusable assets: flow templates, UX risk maps.

## 4) Health / fitness tools

- Почему важно: высокий риск недостоверных выводов и доверия.
- Общие patterns: strict claims discipline, safety messaging gates.
- Department involvement: Analytics + Verification + Release/Integration.
- Reusable assets: risk disclosure templates, trust-check cards.

## 5) Creative tools

- Почему важно: баланс между flexibility и predictability.
- Общие patterns: before/after presentation, iteration loops.
- Department involvement: Analytics + Engineering + Product Intelligence.
- Reusable assets: workflow blueprints, quality ladders.

## 6) Engineering / education tools

- Почему важно: влияют на продуктивность и качество решений.
- Общие patterns: explainability + deterministic checks.
- Department involvement: Analytics + Engineering + Verification.
- Reusable assets: learning playbooks, validation packs.

## 7) Growth / distribution tools

- Почему важно: impact на acquisition/retention/reach.
- Общие patterns: experimentation gates, anti-fake-metric rules.
- Department involvement: Analytics + Product Intelligence + Release.
- Reusable assets: decision matrices, KPI guardrails.

## 8) Other reusable product families (`MAPPED`)

- Допускаются как расширение карты, если:
1. есть повторяемые кейсы;
2. есть уникальные risk patterns;
3. есть смысл в отдельном class-level playbook.

## 9) Текущее состояние

1. `ACTIVE`: class-oriented мышление закрепляется на TikTok Agent кейсе.
2. `MAPPED`: остальные классы готовы как рамка для следующих продуктов.
3. `NOT YET IMPLEMENTED`: полная автоматическая классификация классов в runtime.

