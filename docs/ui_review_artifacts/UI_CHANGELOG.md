# UI Changelog

## 2026-03-12 — UI-QA normalization + corrective pass

### 1) Artifact system
- `ui_snapshot_runner`: screenshot entries расширены (`screen_name`, `state_name`, `screenshot_path`, `timestamp`, `notes`, `tags`, `severity_reference`, `issue_reference`).
- `ui_doctor`: добавлены `latest_run.txt` и `latest_run.json`.
- `ui_validate`: consolidated summary приведён к repo-relative paths, добавлен `manual_testing_allowed`, ужесточён gate.
- Все новые run-артефакты пишутся без абсолютных `E:\...` путей.

### 2) Corrective UI changes
- `UserWorkspaceWindow`: скорректирован баланс splitter и ширины context panel.
- `Dashboard`: quick-actions переведены в устойчивую grid-схему (2 колонки).
- `Profiles/Analytics/AI Studio`: metric area приведена к grid (2x2) для high-scale устойчивости.
- `Sessions`: chip-компоновка переведена в вертикальный стек, preview стал более информативным.
- `AI Studio`: CTA-row переведён в вертикальную схему, длинный CTA сокращён.

### 3) Machine runs
- `ui_snapshot_runner`: `20260312_160910` -> `PASS`
- `ui_validate`: `20260312_160707` -> `PASS`
- `ui_doctor`: `20260312_161111` -> `PASS`

### 4) Regression evidence
- До фиксов: `20260312_160134` -> `PASS_WITH_WARNINGS` (12 major)
- После фиксов: `20260312_161111` -> `PASS` (0 issues)
