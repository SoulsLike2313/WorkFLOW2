from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any


def build_translation_report(entries: list[dict[str, Any]], translations: list[dict[str, Any]]) -> dict[str, Any]:
    total_entries = len(entries)
    translated_count = len([row for row in translations if (row.get("translated_text") or "").strip()])
    untranslated_count = max(0, total_entries - translated_count)

    glossary_hits = len([row for row in translations if row.get("glossary_hits_json")])
    tm_hits = len(
        [
            row
            for row in translations
            if row.get("tm_hits_json") or str(row.get("backend") or "") == "translation_memory"
        ]
    )
    low_quality_count = len([row for row in translations if float(row.get("quality_score") or 0.0) < 0.6])
    uncertain_translation_count = len([row for row in translations if float(row.get("uncertainty") or 0.0) >= 0.28])

    language_distribution = Counter(str(row.get("detected_lang") or "unknown") for row in entries)
    uncertain_language_count = len(
        [
            row
            for row in entries
            if str(row.get("detected_lang") or "unknown") in {"unknown", "mixed"}
            or float(row.get("language_confidence") or 0.0) < 0.75
        ]
    )

    backend_usage = Counter(str(row.get("backend") or "unknown") for row in translations)
    latencies = [int(row.get("latency_ms") or 0) for row in translations]
    latency_stats = _latency_stats(latencies)

    denominator = max(1, translated_count)
    return {
        "entries_total": total_entries,
        "translated_count": translated_count,
        "untranslated_count": untranslated_count,
        "translation_coverage_rate": round(translated_count / max(1, total_entries), 4),
        "backend_usage": dict(sorted(backend_usage.items())),
        "latency_stats": latency_stats,
        "glossary_hit_count": glossary_hits,
        "glossary_hit_rate": round(glossary_hits / denominator, 4),
        "tm_hit_count": tm_hits,
        "tm_hit_rate": round(tm_hits / denominator, 4),
        "uncertain_language_count": uncertain_language_count,
        "uncertain_language_rate": round(uncertain_language_count / max(1, total_entries), 4),
        "low_quality_count": low_quality_count,
        "low_quality_rate": round(low_quality_count / denominator, 4),
        "uncertain_translation_count": uncertain_translation_count,
        "language_distribution": dict(sorted(language_distribution.items())),
    }


def _latency_stats(latencies: list[int]) -> dict[str, float]:
    if not latencies:
        return {"avg_ms": 0.0, "min_ms": 0.0, "max_ms": 0.0, "p95_ms": 0.0}
    sorted_lat = sorted(latencies)
    p95_idx = max(0, min(len(sorted_lat) - 1, int(len(sorted_lat) * 0.95) - 1))
    return {
        "avg_ms": round(float(mean(sorted_lat)), 3),
        "min_ms": float(sorted_lat[0]),
        "max_ms": float(sorted_lat[-1]),
        "p95_ms": float(sorted_lat[p95_idx]),
    }

