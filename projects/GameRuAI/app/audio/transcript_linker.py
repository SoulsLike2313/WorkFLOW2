from __future__ import annotations


def link_transcript_to_segments(*, line_id: str, segments: list[dict], transcript_text: str) -> list[dict]:
    if not segments:
        return []
    words = len((transcript_text or "").split())
    share = max(1, words // max(1, len(segments)))
    out = []
    for segment in segments:
        out.append(
            {
                "line_id": line_id,
                "segment_id": int(segment.get("segment_id") or 0),
                "start_ms": int(segment.get("start_ms") or 0),
                "end_ms": int(segment.get("end_ms") or 0),
                "token_estimate": share,
                "link_confidence": 0.58,
            }
        )
    return out

