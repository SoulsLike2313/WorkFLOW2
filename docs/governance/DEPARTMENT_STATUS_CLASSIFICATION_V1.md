# DEPARTMENT_STATUS_CLASSIFICATION_V1

Статус:
- version: `v1`
- role: `department status law for seed-era factory`
- labels_used: `PROVEN | ACTIVE | MAPPED | FROZEN | NOT YET IMPLEMENTED`

## 1) Обязательные статусы

1. `ACTIVE`
2. `SEED`
3. `MAPPED`
4. `DORMANT`
5. `PLANNED`
6. `NOT_YET_IMPLEMENTED`

## 2) Смысл статусов и правила

## `ACTIVE`

Что owner видит в dashboard:
1. департамент реально работает;
2. видны входящие задачи, выходные bundle, блокеры и текущий прогресс.

Что разрешено:
1. выполнять свой operational scope;
2. выпускать обязательные bundle типа для своей роли.

Что запрещено:
1. выдавать sovereign final decisions;
2. выходить за утвержденный scope без gate.

## `SEED`

Что owner видит в dashboard:
1. департамент существует как сущность;
2. есть charter, минимальные контракты и готовность к активации;
3. активной очереди исполнения обычно нет.

Что разрешено:
1. готовить/обновлять seed-charter;
2. принимать подготовительные артефакты для будущей активации.

Что запрещено:
1. имитировать полноценную operational работу;
2. выдавать completion как у ACTIVE-департамента.

## `MAPPED`

Что owner видит в dashboard:
1. департамент зафиксирован в архитектурной карте;
2. есть причина существования и условия активации;
3. контракты могут быть частичными.

Что разрешено:
1. хранить roadmap и activation-условия.

Что запрещено:
1. принимать production workload как действующий цех.

## `DORMANT`

Что owner видит в dashboard:
1. департамент был активен/seed, но временно отключен;
2. причина dormancy и условия возврата.

Что разрешено:
1. хранить историческую память и open context.

Что запрещено:
1. запускать новые цепочки без re-activation gate.

## `PLANNED`

Что owner видит в dashboard:
1. департамент запланирован, но еще не оформлен до seed-уровня.

Что разрешено:
1. формировать черновую концепцию и границы.

Что запрещено:
1. любые claims о runtime readiness.

## `NOT_YET_IMPLEMENTED`

Что owner видит в dashboard:
1. функциональность/роль официально признана отсутствующей.

Что разрешено:
1. только design-level обсуждение и backlog фиксация.

Что запрещено:
1. выдавать сущность как работающую.

## 3) Dashboard rule

Любой департамент в статусе != `ACTIVE` должен визуально иметь badge и пояснение:
1. why exists;
2. what is missing;
3. when/how activates.

