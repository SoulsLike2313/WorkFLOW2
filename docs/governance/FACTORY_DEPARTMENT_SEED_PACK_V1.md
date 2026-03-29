# FACTORY_DEPARTMENT_SEED_PACK_V1

Статус:
- version: `v1`
- role: `master seed package for factory department entities`
- labels_used: `PROVEN | ACTIVE | MAPPED | FROZEN | NOT YET IMPLEMENTED`

## 1) Назначение пакета

Дать фабрике “цеха как сущности” уже сейчас, даже если не все цеха operationalized.

Смысл:
1. owner видит структуру фабрики заранее;
2. департаменты не появляются “из воздуха” в момент кризиса;
3. есть каноничная база для dashboard и будущей активации.

## 2) Что входит в seed pack

1. `docs/governance/DEPARTMENT_STATUS_CLASSIFICATION_V1.md`
2. `docs/governance/DEPARTMENT_MINIMUM_BUNDLE_SET_V1.md`
3. `docs/governance/ANALYTICS_DEPARTMENT_SEED_V1.md`
4. `docs/governance/ENGINEERING_DEPARTMENT_SEED_V1.md`
5. `docs/governance/VERIFICATION_DEPARTMENT_SEED_V1.md`
6. `docs/governance/RELEASE_AND_INTEGRATION_DEPARTMENT_SEED_V1.md`
7. `docs/governance/TOOLING_AND_INFRASTRUCTURE_DEPARTMENT_SEED_V1.md`
8. `docs/governance/PRODUCT_INTELLIGENCE_RESEARCH_DEPARTMENT_SEED_V1.md`
9. `docs/governance/DEPARTMENT_SEED_REGISTRY_V1.json`

## 3) Текущая честная классификация

1. `ACTIVE`: Analytics Department.
2. `SEED`: Engineering, Verification, Release&Integration, Tooling&Infrastructure, Product Intelligence/Research.
3. `MAPPED`: будущая активация и расширение ролей.
4. `NOT YET IMPLEMENTED`: full interdepartment runtime orchestration.

## 4) Dashboard visibility rule

Даже неактивные цеха должны быть видны owner в “окне в цех”:
1. зачем существуют;
2. что умеют уже сейчас;
3. что блокирует переход к `ACTIVE`;
4. когда и через какой gate открываются.

## 5) Анти-ложная operationalization

Seed-пакет не дает права объявлять департаменты operational-ready без activation gates.

Правило:
1. seed полезен как каркас;
2. seed не равен полной рабочей линии.

