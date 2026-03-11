# Asset Research Mode

## Scope
Asset Research Mode is a lightweight, safe exploration layer for project resources.
It does not attempt heavy runtime capture or 3D reconstruction.

Implemented modules:
- `app/assets/explorer_service.py`
- `app/assets/preview_models.py`
- `app/assets/texture_preview.py`
- `app/assets/audio_preview.py`
- `app/assets/archive_report.py`
- `app/assets/type_classifier.py`

## What Is Indexed
For each scanned file, the index stores:
- `asset_type`
- `preview_type`
- `preview_status`
- `metadata_json`
- `suspected_container`
- `relevance_score`

Database tables:
- `asset_index`
- `asset_previews`
- `archive_reports`

## Preview Support
Working previews:
- texture/image preview for supported image formats
- audio preview metadata for WAV files

Metadata-only fallback:
- unsupported audio formats (e.g. mp3/ogg in current MVP)
- unknown/binary formats
- unsupported image codecs

When fallback is used, UI explicitly shows metadata-only status.

## Archive/Container Heuristics
The archive report flags probable containers using lightweight signals:
- known archive/container extensions
- archive-like filenames
- large opaque binary files

This is heuristic-only research data, not a definitive unpacking result.

## UI
Asset Explorer tab includes:
- resource tree
- metadata panel
- texture preview widget
- audio preview widget
- archive/container report table

## Not Implemented In This Sprint
- universal 3D viewer
- mesh editor
- scene reconstruction
- runtime scene capture
- memory inspection
