# Voice Pipeline (Preparation Layer)

## Scope
Voice layer is a practical preparation pipeline for future dubbing iterations.
It is not final production dubbing.

## Added Core Modules
- `app/voice/voice_sample_bank.py`
- `app/voice/speaker_grouping.py`
- `app/voice/duration_planner.py`
- `app/voice/attempt_history.py`
- `app/voice/preview_player.py`

## What Works
- Voice linking diagnostics:
  - speaker-aware linking
  - scene-aware metadata
  - broken link validation
  - link confidence score
- Speaker groups persisted (`speaker_groups`).
- Voice sample bank persisted (`voice_sample_bank`).
- Duration planning and alignment hints per attempt.
- Mock synthesis with stable speaker/style/emotion variation.
- Voice attempt history persisted (`voice_attempt_history`).
- Preview path resolver for source/generated audio availability.

## UI Coverage
In `Voice` tab:
- Speaker Groups section
- Voice Attempt History section
- Voice Preview panel
- Duration Plan widget
- Voice Quality/Confidence widget

In reporting UI:
- `Reports` tab: voice attempt counts, alignment/quality summary, synthesis mode usage
- `Diagnostics` tab: quality snapshot history (including voice-related metrics)

## Honest Status
- Active synthesis mode: `mock_demo_tts_stub`.
- Explicitly demo/mock preparation behavior.
- Not implemented in this sprint:
  - real speech cloning
  - final production dubbing
  - lip sync
  - full phoneme forced alignment
  - universal multi-engine reinjection

## Why It Is Useful
This layer already provides durable preparation data:
- per-speaker sample structure
- link quality diagnostics
- duration planning baseline
- attempt history for iterative tuning
