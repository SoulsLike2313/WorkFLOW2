# DEPARTMENT_MINIMUM_BUNDLE_SET_V1

Статус:
- version: `v1`
- role: `minimum artifact baseline for all department entities`
- labels_used: `PROVEN | ACTIVE | MAPPED | FROZEN | NOT YET IMPLEMENTED`

## 1) Минимальный пакет для каждого департамента

Каждый департамент (даже `SEED`) должен иметь минимум:

1. `charter`
2. `intake_contract`
3. `output_contract`
4. `blocker_contract`
5. `completion_note`
6. `status_card`
7. `future_evolution_note`

## 2) Назначение каждого артефакта

## `charter`

Определяет миссию, границы, ответственность.

## `intake_contract`

Фиксирует, какие входы департамент имеет право принимать и в каком формате.

## `output_contract`

Фиксирует обязательные типы выходов и их минимальное качество/структуру.

## `blocker_contract`

Фиксирует, как департамент сообщает блокеры и куда эскалирует.

## `completion_note`

Фиксирует, при каких условиях департамент может заявить “этап завершен”.

## `status_card`

Короткая owner-facing карточка текущего статуса (`ACTIVE/SEED/...`) и причины.

## `future_evolution_note`

Фиксирует planned шаги роста и условия открытия следующей стадии.

## 3) Статусная дисциплина

1. `ACTIVE` департамент обязан иметь полный пакет в рабочем состоянии.
2. `SEED` департамент обязан иметь пакет хотя бы в seed-версии.
3. `MAPPED/PLANNED` могут иметь частичный пакет, но это должно быть явно отмечено.
4. `NOT_YET_IMPLEMENTED` не должен маскироваться под operational-ready.

## 4) Owner visibility rule

В dashboard owner должен видеть:
1. наличие/отсутствие каждого элемента минимального пакета;
2. статус completeness пакета;
3. что именно блокирует переход в `ACTIVE`.

