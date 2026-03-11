# UI Resilience Review

Дата: 2026-03-11  
Модуль: `projects/wild_hunt_command_citadel/shortform_core`

## 1. Насколько UI устойчив к добавлению новых блоков

Текущее состояние: **умеренно устойчивый фундамент**.

Что уже устойчиво:
- Единая shell-композиция: `sidebar -> top status -> main workspace -> context panel`.
- Страницы разнесены по модулям (`pages.py`, `pages_extra.py`) и не собраны в монолит.
- Единые компоненты (`GlowCard`, `MetricCard`, `MotionButton`, `SectionHeader`, `StatusPill`) переиспользуются по экранам.
- Тема и токены вынесены отдельно (`theme.py`, `ui_customization.py`).
- Валидация UI и screenshot loop автоматизированы (`ui_doctor`, `ui_snapshot_runner`, `ui_validate`).

## 2. Где архитектура сильная

- **Component layer**: новые карточки/блоки можно добавлять без дублирования стилей.
- **Validation layer**: есть машинный гейт, который ловит critical layout/visibility проблемы.
- **Artifact discipline**: каждый прогон формирует run_id, manifests и summary.
- **CTA discipline**: введены проверки против hover-only критичных действий.

## 3. Где ещё есть хрупкость

- Часть page-level компоновок всё ещё вручную управляется через локальные layout-блоки (не полностью slot-based).
- При сильном росте числа карточек на отдельных экранах может потребоваться дополнительная адаптивная логика группировки.
- Visual acceptance по-прежнему требует ручного этапа (особенно на реальном железе с пользовательскими шрифтами и DPI).

## 4. Что сделано для future-proofing

- Dashboard усилен блоками `core_state_summary` и `next_action_summary`, чтобы HUD отражал реальные силы ядра.
- `ui_doctor` расширен проверками:
  - splitter-устойчивость (left/right/ratio),
  - top status completeness,
  - context panel action/info presence,
  - dashboard core-state/next-actions presence.
- `ui_validate` расширен:
  - screen-level audit aggregation,
  - `ui_visual_review.md` в каждом validate run,
  - расширенные artifact links до doctor/snapshot summaries.
- `ui_snapshot_runner` теперь хранит `screens_by_page` и `latest_run.txt` для comparison-ready loop.

## 5. Какие компоненты уже можно считать стабильной базой

- `TopStatusBar`
- `ContextPanel`
- `MetricCard`
- `Dashboard` (в части системного summary + next-actions + quick actions)
- Validation scripts (`ui_doctor`, `ui_snapshot_runner`, `ui_validate`)

## 6. Рекомендация по следующему шагу

Текущее состояние подходит для финального human acceptance pass:
- проверить микроритм и copy на реальном пользовательском окружении;
- зафиксировать baseline-скриншоты как эталон текущей итерации;
- только затем переходить к новым крупным UI-модулям.
