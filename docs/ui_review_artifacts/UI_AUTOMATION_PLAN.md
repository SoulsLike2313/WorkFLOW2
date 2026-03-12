# UI Automation Plan

## Цель
Сделать UI-ревью воспроизводимым, переносимым и удобным для итераций без привязки к конкретной машине.

## Канонический pipeline
1. `scripts/ui_snapshot_runner.py`
2. `scripts/ui_validate.py`
3. `scripts/ui_doctor.py`
4. (опционально) `scripts/ui_compare_runs.py`

## Что проверяет каждый инструмент
### `ui_snapshot_runner`
- Проходит все ключевые экраны (`dashboard ... settings`) по матрице размеров/масштабов.
- Сохраняет скриншоты + hash + manifest.
- Обновляет `runtime/ui_snapshots/latest_run.{txt,json}`.

### `ui_doctor`
- Проверяет layout/interaction-инварианты:
  - splitter balance,
  - visibility критичных CTA,
  - hover-only anti-pattern,
  - clipping/out-of-bounds/overlap.
- Отдаёт severity counters и список issues.
- Обновляет `runtime/ui_validation/latest_run.{txt,json}`.

### `ui_validate`
- Оркестрирует `ui_doctor` + `ui_snapshot_runner`.
- Собирает consolidated status и общий screenshot manifest.
- Пишет root-level summary (`ui_validation_summary.*`, `ui_screenshots_manifest.json`).
- Выставляет `manual_testing_allowed` только при `PASS`.

## Нормализация артефактов
- Только repo-relative пути в summary/manifest/latest pointers.
- run-структура:
  - `runtime/ui_snapshots/<run_id>/...`
  - `runtime/ui_validation/<run_id>/...`
  - `runtime/ui_validation/validate_<run_id>/...` (consolidated validate run)

## Contract для screenshot manifest
Каждый screenshot entry содержит:
- `run_id` (в верхнем уровне manifest)
- `screen_name`
- `state_name`
- `screenshot_path` (repo-relative)
- `timestamp`
- `notes`
- `tags`
- `severity_reference`
- `issue_reference`

## Текущий machine baseline
- snapshot: `20260312_160910` (`PASS`)
- validate: `20260312_160707` (`PASS`)
- doctor: `20260312_161111` (`PASS`)
