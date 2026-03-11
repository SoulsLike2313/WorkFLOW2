# UI Changelog

## 2026-03-11

### Layout / Stability
- `user_window`: добавлен надёжный cleanup fade-переходов, чтобы исключить “пустые” страницы после быстрого переключения.
- `user_window`: добавлены scroll wrappers для страниц и rebalance split-геометрии.
- `pages (Sessions)`: устранён риск clipping в статусных зонах при средних размерах окна.

### Validation / QA
- `ui_doctor`: разделены проверки required buttons и required labels для снижения ложных срабатываний.
- Добавлен `ui_snapshot_runner` для baseline-скриншотов по экранам/масштабам.
- Добавлен `ui_validate` как единый orchestrator (`doctor + snapshots + consolidated artifacts`).

### Review System
- Обновлены артефакты в `docs/ui_review_artifacts/`:
  - problem audit
  - layout bug report
  - fix plan
  - acceptance checklist
  - automation plan
  - direction confirmation

### Build Discipline
- Введены явные UI-правила в `docs/UI_BUILD_RULES.md`.
