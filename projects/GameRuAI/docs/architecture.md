# Architecture

## Product Layers
- `A. Asset Intelligence Core` (`app/assets/asset_intelligence.py`, `asset_manifest.py`, `asset_types.py`, `container_heuristics.py`, `relevance_scoring.py`)
- `B. Content Understanding Core` (`app/understanding/*`)
- `C. Translation Core` (`app/translator/*`, backend adapters + policy + package evidence)
- `D. Speech & Voice Core` (`app/audio/*`, `app/voice/*`)
- `E. Sync & Rebuild Core` (`app/sync/*`)
- `F. Evidence & Learning Core` (`app/learning/evidence_store.py`, `correction_memory.py`, `adaptation_engine.py`, `confidence_tracking.py`, `regression_memory.py`, `external_reference_log.py`)
- `G. Source-of-Truth Manager` (`app/knowledge/*`)
- `H. Product Dashboards / Review Labs` (`app/ui/language_intelligence_panel.py`, `audio_analysis_lab_panel.py`, `evidence_review_panel.py`, `sync_review_panel.py`)

## Storage (Core Additions)
New persistent blocks in `app/storage/schema.sql`:
- `asset_manifest`
- `content_units`
- `scene_groups`
- `transcript_segments`
- `sync_plans`
- `translation_packages`
- `knowledge_sources`
- `external_reference_events`
- `evidence_records`
- `audio_analysis_results`

All tables include project linkage and timestamps; core records include confidence/status/provenance fields.

## Runtime Modes
- `Batch mode` (`app/runtime/batch_pipeline.py`) - working
- `Near-real-time mode` (`app/runtime/realtime_pipeline.py`) - partial/foundation
- `Session-time companion mode` (`app/runtime/session_pipeline.py`) - foundation on top of existing companion flow

## End-to-End Data Flow (Current)
1. Scan -> `scanned_files` + `asset_manifest`
2. Extract -> `extracted_entries`
3. Detect/understand -> `language_detections` + `content_units` + `scene_groups`
4. Translate -> `translations` + `translation_backend_runs` + `translation_packages` + evidence
5. Voice prep -> `voice_attempts` + `voice_sample_bank` + `audio_analysis_results` + `transcript_segments` + `sync_plans`
6. Learning/evidence -> `correction_history`, `adaptation_events`, `evidence_records`, `external_reference_events`
7. Reports/export -> `project_reports`, `quality_snapshots`, `export_jobs`

## Honest Status
- Working:
  - existing MVP pipeline (scan/extract/detect/translate/voice/export)
  - translation package persistence + evidence trail
  - source registry persistence
  - audio/sync prep data persistence
  - new review-lab UI tabs with live data from storage
- Partial:
  - near-real-time architecture layer
  - advanced backend adapters (`argos`, `transformers`, `local_nllb`, `cloud_adapter`) depending on local availability
- Foundation only:
  - plugin-style asset registry
  - transcript and scene orchestration for broader media domains
- Demo/fallback:
  - voice synthesis (`mock_demo_tts_stub`)
- Research-only:
  - image text detection (candidate signals, no full OCR)
  - video semantics (metadata-level only)

