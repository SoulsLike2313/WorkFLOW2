# Architecture

## Layers
- `app/bootstrap.py`: central application orchestration and end-to-end pipeline entrypoints.
- `app/storage/`: SQLite schema and repositories.
- `app/scanner/`: file scan + manifest.
- `app/extractors/`: format-specific text extractors (`txt/json/xml/csv/ini/yaml`).
- `app/language/`: heuristic language detection.
- `app/translator/`: backend routing, glossary injection, TM lookup, postprocess, quality score.
- `app/voice/`: speaker profile metadata, mock synthesis, alignment and quality scoring.
- `app/learning/`: feedback loop, correction tracking, adaptation history.
- `app/qa/`: quality checks and finding persistence.
- `app/patcher/`: patch export manifest + diff report.
- `app/ui/`: PySide6 tabs bound to real services.

## Data Flow
1. Scan files -> save to `scanned_files`.
2. Extract entries -> save to `extracted_entries` + `voice_links`.
3. Detect language -> save to `language_detections`.
4. Translate -> save to `translations`; remember in `translation_memory`.
5. Voice attempts -> save to `voice_attempts`.
6. Feedback corrections -> `correction_history` + adaptation events + TM/glossary updates.
7. QA -> `qa_findings`.
8. Export -> `export_jobs` + files on disk.

## Learning Model (MVP)
Learning is transparent rule adaptation, not model retraining:
- glossary terms,
- translation memory reuse,
- user corrections,
- style presets,
- speaker profile updates,
- quality scoring,
- adaptation event logs.
