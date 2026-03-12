from __future__ import annotations

from difflib import SequenceMatcher


def _norm(text: str) -> str:
    return " ".join((text or "").lower().strip().split())


def compare_with_references(candidate: str, references: list[str]) -> list[dict]:
    candidate_norm = _norm(candidate)
    out: list[dict] = []
    for idx, ref in enumerate(references):
        ref_norm = _norm(ref)
        similarity = SequenceMatcher(None, candidate_norm, ref_norm).ratio()
        out.append(
            {
                "reference_id": idx + 1,
                "reference_text": ref,
                "similarity": round(float(similarity), 4),
                "verdict": "close" if similarity >= 0.78 else "divergent",
            }
        )
    return out

