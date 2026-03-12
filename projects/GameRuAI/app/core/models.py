from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .enums import QaSeverity, TranslationStatus, VoiceAttemptStatus


@dataclass(slots=True)
class Project:
    id: int
    name: str
    game_path: str


@dataclass(slots=True)
class ScannedFile:
    project_id: int
    file_path: str
    file_type: str
    file_ext: str
    size_bytes: int
    sha1: str
    manifest_group: str


@dataclass(slots=True)
class ExtractionRecord:
    project_id: int
    line_id: str
    file_path: str
    source_text: str
    speaker_id: str | None = None
    context_type: str = "unknown"
    tags: list[str] = field(default_factory=list)
    placeholders: list[str] = field(default_factory=list)
    voice_link: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LanguageDetection:
    entry_id: int
    detected_lang: str
    confidence: float
    heuristics: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TranslationDecision:
    entry_id: int
    source_lang: str
    translated_text: str
    status: TranslationStatus
    glossary_hits: list[dict[str, Any]] = field(default_factory=list)
    tm_hits: list[dict[str, Any]] = field(default_factory=list)
    quality_score: float = 0.0
    latency_ms: int = 0
    backend: str = "dummy"
    fallback_backend: str | None = None
    context_used: bool = False
    context_summary: dict[str, Any] = field(default_factory=dict)
    uncertainty: float = 0.0
    decision_log: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TranslationCandidate:
    text: str
    backend: str
    score: float
    note: str = ""


@dataclass(slots=True)
class TranslationPackage:
    entry_id: int
    source_text: str
    source_lang: str
    context_summary: dict[str, Any]
    chosen_backend: str
    fallback_used: bool
    glossary_hits: list[dict[str, Any]] = field(default_factory=list)
    tm_hits: list[dict[str, Any]] = field(default_factory=list)
    alternatives: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    quality_score: float = 0.0
    warnings: list[str] = field(default_factory=list)
    final_translation: str = ""
    reference_checks: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class VoiceAttempt:
    entry_id: int
    speaker_id: str
    source_voice_path: str
    output_voice_path: str
    status: VoiceAttemptStatus
    quality_score: float
    duration_source_ms: int
    duration_output_ms: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class QaFinding:
    project_id: int
    check_name: str
    severity: QaSeverity
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    entry_id: int | None = None


@dataclass(slots=True)
class ExportResult:
    output_dir: Path
    manifest_path: Path
    diff_report_path: Path
    translated_entries: int
    voiced_entries: int
