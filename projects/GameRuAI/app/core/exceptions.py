class GameRuAIError(Exception):
    """Base exception for the app."""


class ConfigurationError(GameRuAIError):
    """Raised when config cannot be loaded."""


class StorageError(GameRuAIError):
    """Raised for database/storage failures."""


class PipelineError(GameRuAIError):
    """Raised for pipeline execution failures."""
