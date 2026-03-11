# UI Automation Plan

## Цель
Сделать UI-проверку воспроизводимой и машиночитаемой, чтобы не возвращаться к тем же layout/CTA проблемам.

## Компоненты
1. `scripts/ui_doctor.py`
- Прогоняет экраны на нескольких scale/sizes.
- Проверяет critical CTA visibility.
- Проверяет anti-pattern `hover-only critical controls`.
- Проверяет clipping/overflow/out-of-bounds/sibling-overlap.
- Выдаёт итог: `PASS`, `PASS_WITH_WARNINGS`, `FAIL`.

2. `scripts/ui_snapshot_runner.py`
- Открывает основные экраны.
- Делает baseline скриншоты.
- Формирует manifest для сравнения между итерациями.

3. `scripts/ui_validate.py`
- Единый orchestrator.
- Запускает `ui_doctor` + `ui_snapshot_runner`.
- Собирает сводные артефакты в корне active module:
  - `ui_validation_summary.json`
  - `ui_validation_summary.md`
  - `ui_screenshots_manifest.json`
  - `runtime/ui_validation/latest_run.txt`

## Что автоматизация должна ловить
- Налезания и clipping.
- Floating/выпадающие из сетки CTA.
- Hover-only критичные кнопки.
- Проблемы при масштабах `100%`, `125%`, `150%`.
- Сломанные/пустые зоны после переключений экранов.

## Результат
UI quality становится повторяемой инженерной процедурой, а не только ручной оценкой “на глаз”.
