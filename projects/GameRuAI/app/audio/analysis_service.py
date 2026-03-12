from __future__ import annotations

from pathlib import Path
from typing import Any

from app.audio.speech_segments import build_speech_segments
from app.audio.transcript_linker import link_transcript_to_segments
from app.audio.waveform_summary import summarize_waveform


class AudioAnalysisService:
    def analyze(self, path: Path, *, line_id: str = "", transcript_text: str = "") -> dict[str, Any]:
        summary = summarize_waveform(path)
        segments = build_speech_segments(int(summary.get("duration_ms") or 0))
        transcript_links = link_transcript_to_segments(
            line_id=line_id,
            segments=segments,
            transcript_text=transcript_text,
        )
        return {
            "path": str(path),
            "summary": summary,
            "segments": segments,
            "transcript_links": transcript_links,
            "analysis_status": "ok" if summary.get("status") == "ok" else "partial",
        }

