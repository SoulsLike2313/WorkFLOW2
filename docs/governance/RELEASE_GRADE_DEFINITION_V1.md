# RELEASE_GRADE_DEFINITION_V1

Статус:
- version: `v1`
- memory_role: `release_standard_contract`
- labels_used: `PROVEN | ACTIVE | MAPPED | NOT YET IMPLEMENTED`

## 1) Жесткое правило release-grade

Продукт считается `release-grade` только если:
1. 100% обязательных declared gates текущей стадии пройдены;
2. нет открытых критических блокеров;
3. owner утвердил финальный gate verdict.

## 2) Что это значит practically

1. Нельзя объявить “готово”, если хотя бы один обязательный gate в состоянии fail/partial/open.
2. Нельзя компенсировать красный gate красивым narrative.
3. Любой release-grade claim должен иметь evidence path.

## 3) Классы gates

1. Product interpretation gates.
2. Option/strategy selection gates.
3. UI/visual direction gates.
4. Wave transition gates.
5. Verification/trust gates.
6. Release shape gates.
7. Final owner verdict gates.

## 4) Уровни готовности

## Internal-use

1. Базовая рабочая функциональность есть.
2. Разрешены известные ограничения.
3. Release-grade claim запрещен.

## Pilot-ready

1. Основные риски контролируемы.
2. Gate-цепочка частично закрыта.
3. Допускается ограниченный controlled pilot.
4. Полный публичный release запрещен.

## Release-grade

1. Все обязательные gates текущей стадии пройдены.
2. Есть полный доказательный пакет.
3. Owner approved final verdict.

## 5) Анти-ложная готовность

1. Отсутствие доказательства = отсутствие готовности.
2. Открытая критическая противоречивость = блок release-grade.
3. Неполный owner gate chain = блок release-grade.

