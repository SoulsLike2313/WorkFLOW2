# UI Fix Plan

## Приоритеты
### 1) Critical (сразу)
- Убрать broken page states при быстром переключении.
- Убрать hover-only риски для критичных CTA.
- Закрыть любые битые/пустые зоны.

### 2) Major
- Починить clipping и out-of-bounds на `Sessions` и плотных размерах окна.
- Укрепить split-геометрию между main area и context panel.
- Устранить ложные ошибки в автоматической UI-валидации.

### 3) Minor
- Дошлифовать копирайтинг и micro-spacing.
- Обновить review artifacts после каждого крупного прогона.

## Порядок выполнения
1. Исправления в UI/runtime (`user_window`, `pages`).
2. Усиление автоматической проверки (`ui_doctor`, затем `ui_validate`).
3. Снимки baseline (`ui_snapshot_runner`).
4. Пересборка артефактов (`json` + `md` + run pointers).
5. Финальный ручной acceptance pass по чек-листу.
