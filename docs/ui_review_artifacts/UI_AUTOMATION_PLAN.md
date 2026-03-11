# UI Automation Plan

## Цель
Перевести UI-контроль из “визуально кажется норм” в повторяемый machine-run процесс.

## Добавленный инструмент
- `projects/wild_hunt_command_citadel/shortform_core/scripts/ui_doctor.py`

## Что проверяет `ui_doctor`
- Запуск UI в test/offscreen режиме.
- Проход по экранам: Dashboard, Profiles, Sessions, Content, Analytics, AI Studio, Audit, Updates, Settings.
- Скриншоты по DPI/scaling сценариям (`1.0`, `1.25`, `1.5`) и типовым размерам окна.
- Проверка видимости обязательных кнопок.
- Проверка hover-only anti-pattern.
- Проверка clipping для labels/buttons.
- Проверка out-of-bounds/negative positioning.
- Проверка overlap среди sibling controls.
- Проверка stuck opacity эффекта страницы.

## Артефакты `ui_doctor`
- `ui_validation_summary.json`
- `ui_validation_summary.md`
- `ui_screenshots_manifest.json`
- скриншоты в `runtime/ui_validation/<run_id>/screenshots/`

## Gate policy
- `PASS`: можно переходить к ручному acceptance.
- `PASS_WITH_WARNINGS`: ручной pass допустим, но warning-пункты фиксируются в backlog.
- `FAIL`: ручной acceptance блокируется.

## Следующие шаги автоматизации
- Добавить baseline diff по скриншотам (visual regression).
- Добавить проверку контрастности текста/кнопок.
- Добавить “golden interactions” сценарии (click path smoke).
