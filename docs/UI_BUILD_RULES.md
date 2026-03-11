# UI Build Rules

Канонические правила для active module:  
`projects/wild_hunt_command_citadel/shortform_core`

## 1. Product Direction
- Tactical AAA Command Center + Premium Minimal Metallic.
- 80% premium control center + 20% controlled sci-fi glow.
- No Witcher/Wild Hunt/fantasy branding.
- No retro cheap sci-fi, no plastic UI, no debug-shell feel.

## 2. HUD Truthfulness Rules
- Dashboard обязан показывать реальные operational states:
  - readiness,
  - verification,
  - active profiles/sessions,
  - content queue,
  - AI/update status,
  - next actions.
- Пустые “красивые” блоки без product-смысла запрещены.

## 3. Grid & Composition Rules
- Стабильная shell-структура: sidebar / top status / workspace / context panel.
- Единые внешние и внутренние отступы.
- CTA должны быть встроены в композицию блока, не “плавать”.
- Split-панели обязаны иметь безопасные min sizes и ratio.

## 4. Spacing & Rhythm Rules
- Использовать scale-токены, а не случайные числа.
- Сохранять вертикальный rhythm между секциями.
- Не жертвовать информативностью ради пустоты.

## 5. Typography Rules
- Ясная иерархия: display/title/body/helper/metric.
- Русские тексты должны быть естественными и читабельными.
- Длинные строки не должны ломать layout.

## 6. Interaction Rules
- No hover-only critical controls.
- Hover/focus/pressed состояния обязательны и предсказуемы.
- Primary/secondary/context action hierarchy обязательна.

## 7. Layout Invariants
- No overlaps.
- No clipping ключевых CTA/статусов.
- No broken containers.
- No detached action groups.
- No out-of-bounds interactive widgets.

## 8. Scaling Rules
- Проверки минимум на 100%, 125%, 150%.
- UI должен оставаться читаемым и стабильным при каждом масштабе.

## 9. Extensibility Rules
- Новые блоки добавляются через переиспользуемые компоненты, не через one-off hacks.
- Новые панели должны иметь:
  - явную цель,
  - явные CTA,
  - ясный статус.
- Изменения должны быть локальными и не ломать весь экран.

## 10. Screenshot-driven Loop (Mandatory)
Перед финальным визуальным ревью обязательно:
1. `ui_snapshot_runner` (baseline/after).
2. `ui_doctor` (layout + interaction checks).
3. `ui_validate` (consolidated gate + artifacts).
4. `ui_compare_runs` (base vs target visual delta).

## 11. Required Artifacts
- `runtime/ui_snapshots/<run_id>/...`
- `runtime/ui_validation/<run_id>/...`
- `ui_validation_summary.json`
- `ui_validation_summary.md`
- `ui_screenshots_manifest.json`
- `runtime/ui_validation/latest_run.txt`

Без этих артефактов UI готовность не подтверждается.
