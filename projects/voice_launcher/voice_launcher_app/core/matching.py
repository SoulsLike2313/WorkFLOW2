from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple


def normalize_phrase(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def consonant_skeleton(text: str) -> str:
    vowels = set("аеёиоуыэюяьъ ")
    return "".join(ch for ch in text if ch not in vowels)


def command_match_score(candidate: str, key: str) -> float:
    candidate = normalize_phrase(candidate)
    key = normalize_phrase(key)
    if not candidate or not key:
        return 0.0
    if candidate == key:
        return 1.0

    score = difflib.SequenceMatcher(None, candidate, key).ratio()
    min_len = min(len(candidate), len(key))
    max_len = max(len(candidate), len(key))
    overlap = min_len / max(1, max_len)

    if key.startswith(candidate):
        score = max(score, 0.72 + 0.28 * overlap)
    if candidate.startswith(key):
        score = max(score, 0.74 + 0.26 * overlap)
    if candidate in key or key in candidate:
        score = max(score, 0.60 + 0.34 * overlap)

    if len(candidate) <= 2 and key.startswith(candidate):
        score = max(score, 0.78)
    elif len(candidate) <= 2 and candidate in key:
        score = max(score, 0.66)

    c_skel = consonant_skeleton(candidate)
    k_skel = consonant_skeleton(key)
    if c_skel and k_skel:
        skel_ratio = difflib.SequenceMatcher(None, c_skel, k_skel).ratio()
        score = max(score, 0.55 + 0.30 * skel_ratio)
        if len(c_skel) <= 2 and k_skel.startswith(c_skel):
            score = max(score, 0.74)

    if len(candidate) <= 2 and candidate and key and candidate[0] != key[0]:
        score *= 0.62

    return min(1.0, score)


@dataclass
class MatchResult:
    phrase: Optional[str]
    entry: Optional[dict]
    score: float
    heard: str
    margin: float


def find_best_command(
    candidates: Iterable[str],
    commands: Dict[str, dict],
    base_threshold: float = 0.72,
) -> MatchResult:
    candidates = [normalize_phrase(c) for c in candidates if normalize_phrase(c)]
    if not candidates or not commands:
        return MatchResult(None, None, 0.0, "", 0.0)

    for candidate in candidates:
        if candidate in commands:
            return MatchResult(candidate, commands[candidate], 1.0, candidate, 1.0)

    keys = list(commands.keys())
    best_phrase = None
    best_candidate = ""
    best_score = 0.0
    second_score = 0.0

    for candidate in candidates:
        for key in keys:
            score = command_match_score(candidate, key)
            if score > best_score:
                second_score = best_score
                best_score = score
                best_phrase = key
                best_candidate = candidate
            elif score > second_score:
                second_score = score

    if not best_phrase:
        return MatchResult(None, None, best_score, best_candidate, 0.0)

    margin = best_score - second_score
    adaptive_threshold = base_threshold
    if len(best_candidate) <= 2:
        adaptive_threshold = max(0.66, base_threshold - 0.14)
        required_margin = 0.18
    elif len(best_candidate) <= 4:
        adaptive_threshold = max(0.70, base_threshold - 0.10)
        required_margin = 0.11
    else:
        required_margin = 0.05

    if len(best_candidate) <= 2 and best_candidate and best_phrase:
        if best_candidate[0] != best_phrase[0]:
            return MatchResult(None, None, best_score, best_candidate, margin)

    if best_score >= adaptive_threshold and margin >= required_margin:
        return MatchResult(best_phrase, commands[best_phrase], best_score, best_candidate, margin)
    return MatchResult(None, None, best_score, best_candidate, margin)

