# UI Fix Plan

## Приоритеты (порядок исправления)
1. Critical layout/render bugs.
2. CTA visibility and interaction stability.
3. Clipping/overflow при resize и DPI.
4. Screen-level composition polish.
5. Автоматизация проверки и повторный прогон.

## Реально выполненный план
1. Исправлен системный баг opacity-transition.
   - Добавлен безопасный cleanup при остановке анимации.
2. Добавлена стабильность layout на плотных размерах окна.
   - Страницы в `workspace_stack` обёрнуты в `QScrollArea`.
3. Исправлен `Sessions` clipping.
   - Уменьшен min-size preview, сокращён статусный текст в чипе, улучшены переносы источника.
4. Добавлен customization layer без ломки геометрии.
   - `ui_customization.py` + optional override-профиль.
5. Добавлен и стабилизирован `ui_doctor`.
   - Исправлены worker/import ошибки.
   - Исправлены ложные срабатывания по analytics CTA.
6. Повторные прогоны до `PASS`.

## Проверка выполнения
- Последний успешный прогон: `runtime/ui_validation/20260311_212039`.
- Итог: `PASS`.
