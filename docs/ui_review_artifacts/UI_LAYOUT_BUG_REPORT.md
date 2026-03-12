# UI Layout Bug Report

## Источник данных
- Baseline с проблемами: `runtime/ui_validation/20260312_160134/ui_validation_summary.json`
- Подтверждение исправлений: `runtime/ui_validation/20260312_161111/ui_validation_summary.json`

## Layout Issues (история)
| screen | block | issue | severity | likely cause | fix status | evidence |
|---|---|---|---|---|---|---|
| all | main splitter | `splitter_right_too_small` | major | жёстко заниженный minimum для context panel | fixed | 160134 -> 161111 |
| sessions | session chips | `text_clipping` | major | плотная двухколоночная сетка chip-блока на малой ширине | fixed | 160134 -> 161111 |
| ai_studio | action row | `button_clipping` | major | длинный CTA в двухколоночном ряду при high scale | fixed | 160134 -> 161111 |

## Текущее состояние
- Run `20260312_161111`: layout anomalies не обнаружены (`critical=0`, `major=0`, `minor=0`).

## Артефакты
- `runtime/ui_validation/20260312_160134/ui_screenshots_manifest.json`
- `runtime/ui_validation/20260312_161111/ui_screenshots_manifest.json`
- `runtime/ui_compare/latest_run.json` (если сравнение запускалось отдельно)
