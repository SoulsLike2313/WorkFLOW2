# UI Fix Plan

## Стратегия этой фазы

Не “косметика”, а системная коррекция:
1. Screenshot baseline.
2. Visual audit + инженерный аудит на устойчивость.
3. Правки HUD и validation tooling.
4. Повторный screenshot + doctor + validate.
5. Фиксация артефактов и статусов.

## Приоритеты

### Priority 1 — Critical stability
- Исключить broken page states.
- Исключить hover-only критичные действия.
- Стабилизировать layout при resize/scaling.

### Priority 2 — Product-grade HUD clarity
- Dashboard должен показывать реальную силу ядра:
  - readiness,
  - verification,
  - update state,
  - next actions.

### Priority 3 — Resilience automation
- Усилить автоматические проверки так, чтобы ловить regressions до ручного ревью.

## Выполнено

- Dashboard: добавлены `core_state_summary` и `next_action_summary`.
- `ui_doctor`: добавлены проверки split/top-status/context/dashboard-summary.
- `ui_validate`: добавлены screen-audit и `ui_visual_review.md`.
- `ui_snapshot_runner`: добавлены `screens_by_page` и `latest_run.txt`.
- Финальный автоматический гейт: `PASS`.

## Остаток

- Ручной visual acceptance (на реальном пользовательском окружении) перед финальным freeze.
