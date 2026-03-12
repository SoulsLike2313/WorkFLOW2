# UI Build Rules

Канонический документ для active module:  
`projects/wild_hunt_command_citadel/shortform_core`

## 1. Product Direction
- Tactical AAA Command Center + Premium Minimal Metallic.
- 80% premium control center + 20% controlled sci-fi glow.
- Запрещено: Witcher/Wild Hunt/lore-branding, cheap retro sci-fi, debug-shell aesthetics.

## 2. Artifact Portability Rules
- В machine artifacts запрещены machine-local absolute paths (`E:\...`).
- Разрешены только repo-relative пути (`runtime/...`, `ui_validation_summary.json`, и т.д.).
- Обязательно поддерживать:
  - `runtime/ui_snapshots/latest_run.{txt,json}`
  - `runtime/ui_validation/latest_run.{txt,json}`

## 3. Screenshot Manifest Contract
Каждый screenshot entry обязан содержать:
- `screen_name`
- `state_name`
- `screenshot_path` (repo-relative)
- `timestamp`
- `notes`
- `tags`
- `severity_reference`
- `issue_reference`

## 4. Grid & Composition
- Shell-структура неизменна: sidebar / top-status / workspace / context panel.
- CTA должны быть встроены в panel-grid, без floating placement.
- Splitter должен сохранять безопасные min widths для обеих колонок.

## 5. CTA Rules
- Критичные CTA не могут быть hover-only.
- Primary/secondary/context hierarchy обязательна.
- Длинные CTA обязаны иметь anti-clipping стратегию (grid/stack/label policy).

## 6. Typography Rules
- Чёткая иерархия: section title / hint / metric value / helper text.
- Русские тексты должны быть естественными и не ломать layout.
- Типографика не должна быть «дубовой» или визуально агрессивной.

## 7. Layout Invariants
- No overlaps.
- No clipping ключевых CTA и state-labels.
- No out-of-bounds interactive widgets.
- No detached action groups.

## 8. DPI / Scaling Matrix
Обязательные проверки:
- `100%`
- `125%`
- `150%`

Для каждого масштаба проверяются:
- русские тексты,
- кнопки и pills,
- cards/panels,
- sidebar/context panel,
- long strings,
- overflow/clipping риски.

## 9. Machine Gate
Канонический gate: `scripts/ui_validate.py`
- `PASS` -> ручной тест разрешён.
- `PASS_WITH_WARNINGS` или `FAIL` -> ручной тест запрещён.

## 10. Mandatory Pipeline
1. `scripts/ui_snapshot_runner.py`
2. `scripts/ui_validate.py`
3. `scripts/ui_doctor.py`
4. (опционально) `scripts/ui_compare_runs.py`

## 11. Required Artifacts
- `ui_validation_summary.json`
- `ui_validation_summary.md`
- `ui_screenshots_manifest.json`
- `runtime/ui_snapshots/<run_id>/...`
- `runtime/ui_validation/<run_id>/...`
- `runtime/ui_validation/validate_<run_id>/...`
- `runtime/ui_validation/latest_run.txt`
