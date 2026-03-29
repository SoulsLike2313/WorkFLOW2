# CHAT_TRANSFER_CAPSULE_V1

## 1. Роли
- **Codex** получает промты и исполняет работу в repo.
- **GPT** не является исполнителем шага; GPT читает bundle, держит канон, формирует промты для Codex и проверяет честность/направление.
- Цель промтов для Codex: **максимально коротко, максимально жёстко, но без слома истины**.

## 2. Базовый режим
- source of truth = **локальный canonical repo**
- safe mirror = **не default**, не sovereign source
- bundle-first / repo-law-first / delta-only
- one primary truth bundle per active step
- chat = управление
- bundle = содержание
- для Codex short-first / ultra-short response discipline активна

## 3. Что уже закреплено в каноне
- foundation vs mutable split уже создан
- system entrypoint уже создан
- single artifact entrypoint response law уже создан
- response contract уже усилен до формы:
  - `CURRENT PRIMARY TRUTH` = имя главного bundle
  - `ARTIFACT PATH` = один путь к нему
- режим vNext активен как основной рабочий режим для Codex
- ultra-compact prompt compression почти дошёл до безопасного нижнего предела, но окончательная фиксация как жёсткой нормы ждёт ещё bundle-visible подтверждения на следующих шагах

## 4. Текущее понимание системы
Это уже не просто проект, а **система / организм / маленькая империя с заделом на масштаб**.

### Фундамент
Меняется только по owner / Emperor decision:
- суверенность локального repo
- governance / authority / command model
- doctrine / spirit / canon
- foundation reading order
- immutable rules

### Живой слой
Меняется постоянно:
- active primary bundles
- tranche / delta steps
- experiments
- visual evolution
- product state
- ongoing contradictions / gaps / tests

## 5. Текущие большие направления работы
Работа идёт одновременно по нескольким линиям, а не по одной:

1. **TikTok-агент**
   - training-ground, не весь мир системы
   - продуктовая линия, seams, reliability, diagnostics, prompt-lineage, runtime observability

2. **Имперский dashboard / visual layer**
   - должен стать главным читаемым окном всей системы
   - не только продукт, но и:
     - constitution
     - canon / control brain
     - memory / chronology
     - production line
     - active limits
     - trust / warning / contradiction
     - owner-decision triggers
   - local-first imperial surface
   - future-ready для multi-project / multi-node / emperor-view
   - worker-node visibility = ограниченная, owner/emperor = полная

3. **Semantic state layer**
   - dashboard должен читать реальные semantic surfaces
   - visual не придумывает смысл
   - exact / derived / gap / stale / unknown-reason должны быть честно различимы

4. **Codex prompt compression**
   - с каждым bundle промты для Codex ужимаются
   - нижняя безопасная граница уже почти достигнута
   - дальше нельзя жать ценой истины
   - следующее доказательство нужно для фиксации ultra-compact режима как жёсткой нормы

5. **Repository sovereignty / portability**
   - local-only sovereign repo doctrine
   - future portable emperor machine bootstrap
   - future two-disk storage doctrine
   - future N-backup expansion
   - future disaster recovery to last canonical step
   - tests реального переноса на 2 диска пока **не делаются**, сейчас закрепляется doctrine и архитектурный вектор

## 6. Что уже решено по суверенности и будущему
- safe mirror и GitHub больше не должны быть default canonical surfaces
- внешняя safe/export surface допустима только вручную, по owner / sovereign decision
- system dashboard в будущем должен видеть всю империю, но сам, скорее всего, будет подниматься локально и открывать туннель наружу только когда это нужно и только в нужном объёме

## 7. Что важно про 2 диска и восстановление
Это пока **будущий контур**, но его надо держать в памяти:

- Disk 1 = live system / primary runtime surface
- Disk 2 = logs / history / backups / recovery support
- в будущем возможна N-disk backup expansion
- цель восстановления:
  - не “примерно на старую дату”
  - а **до последнего канонического рабочего шага**
- система должна уметь показать:
  - где была последняя нормальная точка
  - где произошла авария
  - как поднять новый пустой M.2 до последнего рабочего состояния и продолжить в каноне

## 8. Что уже видно по dashboard
### Хорошо
- появилась многослойность
- age axis сильная и ценная ось
- history / chronology уже разгружают память owner'а
- prompt-lineage показывается честно, без выдуманного полного prompt text

### Нужно продолжать
- owner-readable русский слой
- truth parity
- semantic execution hardening
- убрать raw/debug inspector из main aquarium
- различать причины UNKNOWN
- не показывать static/hardcoded summary как live truth

## 9. Последовательность ближайших visual шагов
После уже выполненных шагов логика такая:

1. **SEMANTIC_EXECUTION_HARDENING_DELTA**
   - убрать secondary inspector из main aquarium
   - усилить truth integrity
   - развести UNKNOWN по причинам
   - дотянуть semantic surfaces до owner-ready уровня

2. **IMPERIAL_DASHBOARD_LANGUAGE_TRUTH_PARITY_HARDENING_DELTA**
   - сделать язык owner-facing интерфейса заметно более понятным по-русски
   - сохранить техничку вторым слоем
   - усилить truth parity каждой крупной visual zone

3. **ULTRA_COMPACT_PROMPT_SMOKE_TRANCHE**
   - не новый abstract law, а практическая проверка
   - подтвердить, что сверхкороткая форма для Codex безопасна на реальных bounded tasks

## 10. Как читать систему в новом чате
Минимальный вход:
1. `SYSTEM_ENTRYPOINT_V1`
2. `FOUNDATION_VS_MUTABLE_READING_GUIDE_V1`
3. `FOUNDATION_INDEX_V1`
4. `LIVE_SYSTEM_INDEX_V1`
5. current active primary bundle path

Не начинать с хаотичной bundle-археологии, если входные surfaces доступны.

## 11. Что GPT должен делать в новом чате
- сначала восстановить truth по entrypoint + foundation/live split + active primary bundle
- помнить, что Codex = исполнитель, GPT = проектировщик/контролёр/интерпретатор
- если возникает сомнение в зоне фундаментального канона:
  - не угадывать
  - поднимать owner-decision question
- работать только по канону

## 12. Что Codex должен делать
- отвечать ultra-short
- наружу давать один artifact path
- внутри шага работать bundle-first
- не пересказывать канон, если он уже закреплён в repo
- не раздувать reply в чат
- не скрывать gaps
- не выходить за scope

## 13. Что важно не забыть
- визуал должен подниматься ко всему
- и всё должно подтягиваться к визуалу
- цель: чтобы owner **видел систему глазами**, а не держал её состояние в голове
- TikTok не равен всей системе; это training-ground для общего паттерна
- при следующих bundle нужно искать честное доказательство, что ultra-compact prompts для Codex можно закрепить как жёсткую норму
- GPT промты не исполняет; GPT их формирует по системе

## 14. Краткая формула текущего состояния
- система уже стала заметно более самописуемой и самочитаемой
- dashboard уже начал превращаться в центральную поверхность чтения
- Codex уже почти дожат до безопасного пола
- следующий выигрыш идёт через visual clarity + semantic truth + practical ultra-compact smoke validation

## 15. Что просить в следующем чате
Сразу сказать:
- работаем по канону
- Codex получает короткие жёсткие промты
- GPT формирует их и проверяет bundle
- чтение начинать от entrypoint + foundation/live split + current primary bundle
- текущий рабочий фронт:
  1. semantic execution hardening
  2. imperial dashboard language/truth parity hardening
  3. ultra-compact prompt smoke tranche
