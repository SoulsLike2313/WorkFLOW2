# PRODUCT_PORTFOLIO_POLICY_V1

Статус:
- version: `v1`
- memory_role: `portfolio_selection_and_anti_chaos_policy`
- labels_used: `ACTIVE | RECOMMENDED | FUTURE | NOT YET IMPLEMENTED`

## 1) Как фабрика выбирает продукты (`ACTIVE`)

Продукт-кандидат активируется, если одновременно:
1. решает понятную проблему;
2. укладывается в текущую compute-реальность;
3. имеет реалистичный путь к early sales;
4. не ломает текущий quality/governance контур.

## 2) Product classes (`ACTIVE`)

Используется класс-ориентированный выбор, а не хаотичный список идей.
База: `docs/governance/PRODUCT_CLASS_MAP_V1.md`.

## 3) Anti-chaos limits (`ACTIVE`)

1. ограничение числа одновременно активных продуктовых линий;
2. обязательные owner gates на крупных развилках;
3. запрет на скрытое расширение scope.

## 4) Что получает `REJECTED` (`RECOMMENDED`)

1. продукт без ясной ценности;
2. продукт с неподъемной стоимостью поддержки на текущем этапе;
3. идея, требующая инфраструктуры, которой фабрика не обладает.

## 5) Что становится `ACTIVE` (`ACTIVE`)

1. продукт с подтвержденным hardening path;
2. продукт с ясным distribution/monetization маршрутом;
3. продукт с понятным планом качества и поддержки.

## 6) Что уходит в `FROZEN FUTURE` (`RECOMMENDED`)

1. перспективные, но преждевременные инициативы;
2. идеи с высоким потенциалом, но без текущих ресурсов;
3. направления, где риск/стоимость сейчас выше ожидаемой пользы.

## 7) Portfolio rebalance policy (`RECOMMENDED`)

1. каждая новая активная линия требует проверки, что она не разрушает текущий throughput;
2. weak-performing продукты могут быть:
   - downgraded,
   - frozen,
   - closed.

## 8) `NOT YET IMPLEMENTED`

1. fully automated portfolio scoring engine;
2. полностью автономная приоритизация без owner участия.
