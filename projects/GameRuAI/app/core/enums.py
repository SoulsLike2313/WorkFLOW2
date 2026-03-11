from __future__ import annotations

from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class TranslationStatus(str, Enum):
    PENDING = "pending"
    TRANSLATED = "translated"
    CORRECTED = "corrected"
    SKIPPED = "skipped"


class VoiceAttemptStatus(str, Enum):
    PENDING = "pending"
    GENERATED = "generated"
    FAILED = "failed"
    SKIPPED = "skipped"


class QaSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class EntryType(str, Enum):
    UI = "ui"
    DIALOGUE = "dialogue"
    COMBAT = "combat"
    RADIO = "radio"
    TUTORIAL = "tutorial"
    QUEST = "quest"
    CODEX = "codex"
    SHOP = "shop"
    SYSTEM = "system"
    UNKNOWN = "unknown"
