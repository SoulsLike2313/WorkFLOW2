# UI Layout Bug Report

## Таблица дефектов

| Screen | Block | Issue | Likely Cause | Fix Strategy | Status |
|---|---|---|---|---|---|
| All | Page transition | Пустой/битый экран после быстрых переключений | Fade animation stop без cleanup effect | Явный `_clear_page_fade()` + очистка target effect | Fixed |
| Sessions | Session frame / chips | Clipping статуса на средних размерах | Длинный статус и ограниченная ширина чипа | Сократить статус, выровнять text strategy | Fixed |
| Sessions | Session frame | Нижняя часть визуально “срезалась” | Высокая min-height preview + плотный layout | Снизить min-size preview + scroll container на уровне stack | Fixed |
| Content | Action row | Риск визуальной “оторванности” CTA при плотном окне | Слабая связка action bar и контента | Уточнена иерархия CTA + подсказка workflow | Fixed |
| Analytics | Validation expectations | Ложный critical “missing CTA” | Валидатор проверял кнопки вместо labels | Развести required buttons/required labels | Fixed |
| Updates | Action context | Непонятный user flow обновления | Недостаток product copy | Добавлен flow-hint + статусы PASS/PASS+/FAIL | Fixed |

## Остаточные наблюдения
- Критичных layout-багов по текущим инвариантам не обнаружено.
- Рекомендован ручной pass на реальном мониторе с русскими шрифтами (в дополнение к offscreen проверкам).
