# FEDERATED_PRODUCTION_SYSTEM_V1_SPEC

Status:
- spec_version: `v1`
- scope: `next operational layer on top of completed Brain/Constitution/Governance baseline`
- intent: `turn governed analysis into repeatable product production flow`
- posture: `practical, cheap, repo-first, evidence-gated`

Assertion labels used in this document:
- `PROVEN` = already established in current canonical repo surfaces
- `REUSABLE` = exists and can be reused directly in this phase
- `DESIGNED` = formalized now as target model, not yet fully implemented in runtime automation
- `NOT YET IMPLEMENTED` = intentionally left for later execution hardening

## 1. Что это за система

Federated Production System V1 это производственная надстройка над уже собранным brain/governance ядром.

Простыми словами:
1. Brain уже держит закон и границы.
2. Production layer превращает вход (идея, демка, сырой проект) в управляемый поток работ.
3. Результат должен быть не "красивый текст", а структурный путь к рабочему продукту.

## 2. Зачем это нужно

Ключевая боль без этой системы:
1. каждый новый запуск начинается с хаотичного ручного разбора;
2. нет стабильного department-grade маршрута от intake до release;
3. Astartes может тратить ресурсы на невалидный scope;
4. Primarch может получать неоднородные входы и не видеть реальную доступную силу.

Что это дает owner:
1. входной проект быстро получает техническую карту и roadmap;
2. видно, где реальные дыры, а где ложные тревоги;
3. понятен следующий шаг для каждой машины/роли;
4. меньше лишних правок, меньше ложного "готово".

## 3. Почему это правильная следующая фаза

1. `PROVEN`: brain/governance/constitution слой уже собран и green.
2. `PROVEN`: rank/mode и authority boundaries стабилизированы.
3. `REUSABLE`: analytics/intake doctrine уже есть и работает как первый operational head.
4. `DESIGNED`: теперь нужна производственная orchestration-логика поверх готового закона, без нового brain-overhaul.

## 4. Что значит "production system on a ready brain"

Это означает:
1. закон не переписывается;
2. departments работают под существующими законами;
3. каждый выход требует доказательства;
4. переход между стадиями идет через bundle/queue/gate дисциплину.

## 5. Базовый производственный контур V1

### 5.1 Core building blocks

1. Department charters and map.
2. Primarch/Astartes authority chain.
3. Entry manifest + force map.
4. Bundle protocols + interdepartment queues.
5. Product lifecycle scenarios.
6. Trust and anti-slop gate rules.
7. Pilot configuration (1 Emperor, 1 Primarch, 2 Astartes).

### 5.2 Current activation policy

1. `PROVEN`: active now = `Analytics Department`.
2. `DESIGNED`: other departments are mapped now, activated later by explicit trigger.
3. `NOT YET IMPLEMENTED`: full multi-department runtime orchestration engine.

## 6. Как это помогает превращать сырой проект в продукт

Для owner это выглядит так:
1. Даете проект/демку/идею в intake.
2. Analytics делает техническую карту, risk map и roadmap.
3. Primarch собирает bounded задачи для Astartes.
4. Astartes возвращают доказательные result bundles.
5. Primarch делает synthesis и готовит department pass/fail.
6. Verification + Release gates решают readiness.
7. Emperor получает только финальные и эскалационные решения.

## 7. Снижение prompt burden на будущих нодах

Без production spec:
1. каждую задачу нужно объяснять заново "вручную".

С production spec:
1. у ролей есть фиксированные входы/выходы;
2. у очередей есть обязательные поля;
3. у bundle есть обязательная доказательная структура;
4. меньше свободного трактования и меньше шума.

## 8. Границы автономии (строго bounded)

1. Astartes не расширяет scope сам.
2. Primarch не выдает sovereign acceptance.
3. Department не закрывает продукт без required gates.
4. Нельзя объявить completion без evidence path.
5. Integration posture не является источником authority.

## 9. Дешевый и практичный профиль V1

1. Repo-first orchestration (документы + контракты + простые очереди).
2. Минимальный состав: 1 Primarch + 2 Astartes вокруг одного активного department head.
3. Без преждевременного построения тяжелой enterprise платформы.
4. Вначале важнее дисциплина артефактов, чем дорогая автоматизация.

## 10. Что уже можно считать готовым

1. `PROVEN`: governing core и authority boundaries.
2. `REUSABLE`: Analytics Department doctrine + intake model + escalation baseline.
3. `DESIGNED`: department-scale production flow and bundle discipline.
4. `NOT YET IMPLEMENTED`: full runtime automation of all queue transitions.

## 11. Не overclaim

Эта спецификация:
1. не объявляет, что все departments уже operational;
2. не объявляет, что любой проект автоматически выходит в release;
3. не заменяет verification chain;
4. не дает Astartes права на организационные решения.

## 12. Load-bearing anchors

1. `docs/governance/FEDERATION_OPERATIONAL_MODEL.md`
2. `docs/governance/ANALYTICS_DEPARTMENT_DOCTRINE.md`
3. `docs/governance/TEST_PRODUCT_INTAKE_MODEL.md`
4. `docs/governance/DEPARTMENT_EXCEPTION_ESCALATION_HARDENING_V1.md`
5. `workspace_config/department_guardian_registry.json`
6. `workspace_config/department_exception_escalation_contract.json`
7. `workspace_config/shared_taxonomy_contract.json`

