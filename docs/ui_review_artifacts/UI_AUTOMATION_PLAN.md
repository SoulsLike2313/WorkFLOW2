# UI Automation Plan

## Цель
Сделать UI-поддержку повторяемой: каждый прогон должен оставлять machine-readable следы и быстро показывать regressions.

## Инструменты

### 1) `scripts/ui_snapshot_runner.py`
- Проходит все ключевые экраны.
- Делает скриншоты по scale/size.
- Сохраняет hashes и `screens_by_page`.
- Артефакты:
  - `runtime/ui_snapshots/<run_id>/ui_screenshots_manifest.json`
  - `runtime/ui_snapshots/<run_id>/ui_snapshot_summary.json`
  - `runtime/ui_snapshots/latest_run.json`
  - `runtime/ui_snapshots/latest_run.txt`

### 2) `scripts/ui_doctor.py`
- Проверяет layout/visibility инварианты:
  - критичные CTA;
  - hover-only anti-pattern;
  - clipping/out-of-bounds/overlap;
  - splitter/top-status/context/dashboard resiliency checks.
- Артефакты:
  - `runtime/ui_validation/<run_id>/ui_validation_summary.json`
  - `runtime/ui_validation/<run_id>/ui_validation_summary.md`
  - `runtime/ui_validation/<run_id>/ui_screenshots_manifest.json`

### 3) `scripts/ui_validate.py`
- Единый orchestrator:
  - запускает `ui_doctor`,
  - запускает `ui_snapshot_runner`,
  - формирует consolidated summary.
- Артефакты:
  - `ui_validation_summary.json`
  - `ui_validation_summary.md`
  - `ui_screenshots_manifest.json`
  - `runtime/ui_validation/latest_run.txt`
  - `runtime/ui_validation/latest_run.json`
  - `runtime/ui_validation/validate_<run_id>/ui_visual_review.md`

### 4) `scripts/ui_compare_runs.py`
- Берёт два `run_id` (или пути к run-папкам).
- Сравнивает manifests и фактические screenshot hashes.
- Показывает, какие экраны реально изменились.
- Артефакты:
  - `runtime/ui_compare/<compare_run_id>_<base>_vs_<target>/ui_compare_summary.json`
  - `runtime/ui_compare/<compare_run_id>_<base>_vs_<target>/ui_compare_summary.md`
  - `runtime/ui_compare/latest_run.json`
  - `runtime/ui_compare/latest_run.txt`

## Принцип запуска
1. До правок: baseline snapshots.
2. После правок: doctor + validate.
3. Для диффа итераций: compare (base run vs target run).
4. Только после PASS — ручной visual acceptance.
