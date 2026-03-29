# AI_DEPENDENCY_POLICY_V1

Статус:
- version: `v1`
- memory_role: `ai_dependency_boundaries`
- labels_used: `ACTIVE | RECOMMENDED | FUTURE | NOT YET IMPLEMENTED`

## 1) Core principle (`ACTIVE`)

AI-зависимость должна быть осознанной и экономически оправданной.
AI не должен автоматически становиться ядром каждого продукта.

## 2) Local-first classes (`RECOMMENDED`)

Классы, где лучше держать основу локально:
1. system tools;
2. network/performance utilities;
3. часть productivity/automation apps.

Причина: ниже операционные риски и выше контролируемость.

## 3) Selective AI/API augmentation (`RECOMMENDED`)

Разрешено, когда:
1. улучшение ценности измеримо;
2. есть fallback path;
3. unit economics не разрушается на ранних продажах.

## 4) Too expensive too early (`ACTIVE`)

Рано для старта:
1. продукты, где постоянный expensive inference является обязательным ядром;
2. продукты без плана ограничения API-cost.

## 5) Как решать: AI core vs enhancement (`RECOMMENDED`)

Вопросы перед решением:
1. может ли продукт работать на минимальном уровне без внешнего AI;
2. дает ли AI критически важную дифференциацию;
3. выдержит ли экономика продукта реальные API-затраты.

Если ответы слабые — AI остается enhancement, не core.

## 6) Dependency risk control (`ACTIVE`)

1. избегать single-provider lock-in как единственной архитектуры;
2. иметь базовый graceful degradation;
3. фиксировать, какие функции критично зависят от внешнего AI.

## 7) `NOT YET IMPLEMENTED`

1. общий фабричный dependency orchestrator;
2. автоматический cost governor для всех продуктов.
