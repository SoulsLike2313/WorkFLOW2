# UI Problem Audit

## Контекст
- Активный модуль: `projects/wild_hunt_command_citadel/shortform_core`
- Режим: screenshot-driven + machine validation
- Источники: `ui_snapshot_runner`, `ui_validate`, `ui_doctor`

## Актуальные прогоны
- `ui_snapshot_runner`: `20260312_160910` (`PASS`)
- `ui_validate`: `20260312_160707` (`PASS`)
- `ui_doctor`: `20260312_161111` (`PASS`)
- Матрица: `scales=1.0,1.25,1.5`; `sizes=1540x920,1366x768,1280x800`

## Что было найдено до corrective pass (run `20260312_160134`)
### Critical
- нет

### Major
- `all`: `splitter_right_too_small` (контекстная панель слишком узкая на `1366x768` и `1280x800`)
- `sessions`: `text_clipping` (обрезка подписи источника)
- `ai_studio`: `button_clipping` (обрезка CTA "Сгенерировать рекомендации")

### Minor
- нет

## Что подтверждено после corrective pass
- В run `20260312_161111` (`ui_doctor`) severity-counters: `critical=0`, `major=0`, `minor=0`.
- В run `20260312_160707` (`ui_validate`) warnings/failures: пусто.
- `manual_testing_allowed=true` в `ui_validation_summary.json`.

## Проверяемые артефакты (repo-relative)
- `projects/wild_hunt_command_citadel/shortform_core/ui_validation_summary.json`
- `projects/wild_hunt_command_citadel/shortform_core/ui_validation_summary.md`
- `projects/wild_hunt_command_citadel/shortform_core/ui_screenshots_manifest.json`
- `projects/wild_hunt_command_citadel/shortform_core/runtime/ui_validation/validate_20260312_160707/`
- `projects/wild_hunt_command_citadel/shortform_core/runtime/ui_validation/20260312_161111/`
- `projects/wild_hunt_command_citadel/shortform_core/runtime/ui_snapshots/20260312_160910/`

## Итог
- Machine status: `PASS`.
- Системные major-проблемы из предыдущего цикла закрыты в новых прогонах.
