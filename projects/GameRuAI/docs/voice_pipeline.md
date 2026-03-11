# Voice Pipeline (Preparation Layer)

## Sprint Scope
This sprint improves the voice layer as a practical preparation pipeline.
It does not claim final production-grade Russian dubbing.

## Added Modules
- `app/voice/voice_sample_bank.py`
- `app/voice/speaker_grouping.py`
- `app/voice/duration_planner.py`
- `app/voice/attempt_history.py`
- `app/voice/preview_player.py`

## What Works
- Voice-linked entries are analyzed with:
  - speaker-aware linking
  - scene-aware metadata
  - broken link validation
  - link confidence scoring
- Speaker groups are built and persisted.
- Voice sample bank is built and persisted (source file, duration, scene, speaker).
- Duration planning produces alignment/action/confidence hints.
- Mock synthesis uses stable speaker parameters + style/emotion variation.
- Voice attempt history is persisted and visible in UI.
- Preview path resolver reports source/generated file availability for UI.

## Database Tables
- `speaker_groups`
- `voice_sample_bank`
- `voice_attempt_history`

## UI Coverage
In `Voice` tab:
- Speaker Groups section
- Voice Attempt History section
- Voice Preview panel
- Duration Plan widget
- Voice Quality/Confidence widget

## Honest Status (Important)
- Active synthesis mode: `mock_demo_tts_stub`.
- This is explicitly a demo/mock preparation layer.
- Not implemented in this sprint:
  - real speech cloning
  - final production dubbing
  - lip sync
  - full phoneme forced alignment
  - universal multi-engine reinjection

## Why This Is Useful
Even with mock synthesis, the layer now gives reusable structure for future RU dubbing:
- speaker/sample organization
- link quality diagnostics
- duration planning for alignment
- attempt history for iterative tuning
