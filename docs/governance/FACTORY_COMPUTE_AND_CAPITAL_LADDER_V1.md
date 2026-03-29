# FACTORY_COMPUTE_AND_CAPITAL_LADDER_V1

Статус:
- version: `v1`
- memory_role: `compute_and_capital_reality`
- labels_used: `ACTIVE | RECOMMENDED | FUTURE | NOT YET IMPLEMENTED`

## 1) Local-only tier (`ACTIVE`)

Что это:
1. одна Emperor-машина;
2. локальные инструменты и локальные пайплайны;
3. минимальная зависимость от платных внешних API.

Реально позволяет:
1. hardening 1 продукта за раз;
2. анализ/планирование/контроль качества в owner-steered режиме;
3. локальный dashboard и bundle-операции.

Нереалистично на этом уровне:
1. массовый параллельный поток десятков продуктов;
2. тяжелые AI-first продукты с постоянным дорогим inference;
3. enterprise-grade high-availability контур.

Подходящие классы продуктов:
1. local-first utility tools;
2. productivity/automation apps;
3. lightweight media/voice helpers.

## 2) Low-cost multi-PC tier (`RECOMMENDED`)

Что это:
1. 2-5 рабочих машин;
2. Primarch/Astartes распределение bounded задач;
3. repo-first coordination без дорогой инфраструктуры.

Реально позволяет:
1. параллельные product lanes в умеренном объеме;
2. разделение аналитики/исполнения/верификации;
3. быстрый рост output без потери owner-control.

Нереалистично на этом уровне:
1. полностью автономная фабрика без ручных gate-решений;
2. высокий throughput без зрелой playbook-базы.

Подходящие классы продуктов:
1. consumer tools с повторяемыми pipeline;
2. micro-SaaS и desktop/hybrid utilities;
3. growth/distribution helper products.

## 3) Selective API tier (`RECOMMENDED`)

Что это:
1. выборочное подключение внешних API там, где ROI выше стоимости;
2. API как усиление, а не замена core архитектуры.

Реально позволяет:
1. ускорить отдельные функции (summarization, enrichment, moderation);
2. повысить speed-to-market для некоторых продуктовых классов;
3. быстро валидировать гипотезы до крупных вложений.

Нереалистично на этом уровне:
1. строить продукт, который целиком держится на дорогом API, без плана unit economics;
2. игнорировать lock-in и риск роста переменных затрат.

Подходящие классы продуктов:
1. workflow assistants;
2. selective AI-augmented utilities;
3. growth intelligence modules.

## 4) Scaling tier (`FUTURE`)

Что это:
1. расширение парка машин;
2. больше Primarch capacity;
3. формализованные очереди, метрики, release ladders.

Реально позволит:
1. устойчивый multi-product throughput;
2. controlled рост distribution и revenue циклов;
3. более глубокую специализацию departments.

Что должно быть готово до входа в tier:
1. validated pattern library;
2. стабильная gate-дисциплина;
3. повторяемые unit-economics на ранних продажах.

## 5) Capital loop policy (`ACTIVE`)

1. Ранний доход направляется в compute рост по ступеням.
2. Нельзя перескакивать уровни капитальных трат без доказанного спроса.
3. Compute expansion должен следовать за подтвержденной product traction, а не за мечтой о масштабе.

## 6) Триггеры переходов (`RECOMMENDED`)

Переход на следующий tier открывается только при наличии:
1. повторяемого качества выпуска;
2. подтвержденных early sales сигналов;
3. стабильных затрат на поддержку текущих продуктов.
