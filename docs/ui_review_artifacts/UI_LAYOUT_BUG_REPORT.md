# UI Layout Bug Report

## Проверенные прогоны
- baseline snapshots: `20260311_220907`
- post-fix snapshots: `20260311_221740`
- doctor: `20260311_221939`
- validate: `20260311_222150`

## Актуальная таблица layout-рисков

| Screen | Block | Issue | Severity | Likely Cause | Proposed Fix | Status |
|---|---|---|---|---|---|---|
| All | Main split | Конфликт ширин main/context при resize | major (historical) | Недостаточная проверка split ratio | Добавлены ui_doctor split checks | Fixed |
| Dashboard | HUD summary | Недостаточная отражаемость реального состояния ядра | major | Не хватало явных core-state/next-actions | Добавлены summary-блоки | Fixed |
| Sessions | Session status area | Риск clipping на средних окнах | major (historical) | Плотная геометрия + длинные строки | Укороченные статусы + контейнеризация | Fixed |
| All | CTA visibility | Риск hover-only critical controls | critical (historical) | Неполные проверки валидации | Жёсткий ui_doctor check | Fixed |

## Остаток
- По текущим инвариантам doctor/validate критичных и major layout ошибок не выявили.
- Рекомендуется финальный ручной pass на реальном пользовательском DPI/шрифтах.
