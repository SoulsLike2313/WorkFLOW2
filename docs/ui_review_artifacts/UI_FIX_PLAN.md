# UI Fix Plan

## Цель текущей итерации
Не добавлять новые функции, а закрыть системные UI-риски и нормализовать UI-QA артефакты.

## Приоритеты
### Priority 1 — Artifact portability
- Убрать machine-local absolute paths из summary/manifest/latest pointers.
- Зафиксировать repo-relative path contract.

### Priority 2 — Critical/Major UI geometry
- Устранить splitter-конфликт между main workspace и context panel.
- Убрать clipping в Sessions.
- Убрать clipping CTA в AI Studio.

### Priority 3 — Доказательство через прогоны
- Запустить новый `snapshot -> validate -> doctor` цикл.
- Сохранить новые run_id и статусы в документации.

## Что сделано
- Обновлены `scripts/ui_snapshot_runner.py`, `scripts/ui_validate.py`, `scripts/ui_doctor.py`.
- Добавлены `latest_run.{txt,json}` для `ui_doctor`.
- `manual_testing_allowed` и строгий gate в `ui_validate` (только `PASS`).
- Исправлены UI-проблемы, выявленные в run `20260312_160134`.

## Верификация
- Baseline warning run: `20260312_160134` (`PASS_WITH_WARNINGS`).
- Fixed run (validate): `20260312_160707` (`PASS`).
- Fixed run (doctor): `20260312_161111` (`PASS`).
- Snapshot evidence: `20260312_160910` (`PASS`).
