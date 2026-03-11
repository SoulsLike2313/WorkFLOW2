# UI Changelog

## 2026-03-11 — UI Resilience & Validation Phase

### Dashboard / HUD
- Усилен Dashboard блоком состояния ядра:
  - `core_state_summary` (readiness + verification + update status),
  - `next_action_summary` (системные next steps по текущему состоянию).
- Добавлены стили для новых summary-блоков в `theme.py`.

### UI Doctor
- Добавлены проверки:
  - main splitter stability (left/right width + ratio),
  - top status bar completeness,
  - context panel action/info sufficiency,
  - dashboard core-state/next-actions presence.
- Расширены summary-метрики:
  - `screenshots_by_page`,
  - `issue_categories`.

### UI Snapshot Runner
- В manifest добавлены `screens_by_page`.
- Добавлен `runtime/ui_snapshots/latest_run.txt`.

### UI Validate
- Добавлен screen-level audit (`screen_audit`) из doctor issues.
- Добавлен `ui_visual_review.md` в каждый validate run.
- Расширены artifact ссылки:
  - doctor summary/manifest paths,
  - snapshot summary/manifest paths.

### Review docs
- Обновлены:
  - `UI_PROBLEM_AUDIT.md`
  - `UI_FIX_PLAN.md`
  - `UI_AUTOMATION_PLAN.md`
  - `UI_ACCEPTANCE_CHECKLIST.md`
  - `UI_LAYOUT_BUG_REPORT.md`
- Добавлен:
  - `UI_RESILIENCE_REVIEW.md`
