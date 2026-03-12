# UI Direction Confirmation

## Подтверждённый вектор
- Tactical AAA Command Center + Premium Minimal Metallic.
- Баланс: `80% premium control center + 20% controlled sci-fi glow`.
- База: dark graphite / near-black.
- Акценты: violet / metallic purple.
- Glow: точечный (focus/active/AI/primary), без neon overload.

## Что исключено
- Witcher / Wild Hunt / fantasy / lore-branding.
- Старый debug-shell feel.
- Плавающие CTA и хаотичная геометрия.
- Hover-only critical controls.
- Грубые «пластиковые» кнопки.

## Product-first трактовка
Premium UI = не только визуальный стиль, а связка:
1. читаемая информационная иерархия,
2. предсказуемая сетка и CTA-логика,
3. устойчивость на resize/DPI,
4. machine-проверяемость через screenshot/validation цикл.

## Подтверждение на текущем цикле
- `ui_validate` (`20260312_160707`) -> `PASS`
- `ui_doctor` (`20260312_161111`) -> `PASS`
- `ui_snapshot_runner` (`20260312_160910`) -> `PASS`
