from __future__ import annotations


class WorkspaceError(Exception):
    """Base class for workspace domain errors."""


class NotFoundError(WorkspaceError):
    def __init__(self, entity: str, entity_id: str) -> None:
        super().__init__(f"{entity} '{entity_id}' not found")
        self.entity = entity
        self.entity_id = entity_id


class LimitExceededError(WorkspaceError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ValidationError(WorkspaceError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class PolicyDeniedError(WorkspaceError):
    def __init__(self, action_type: str, mode: str, reason: str) -> None:
        super().__init__(f"Action '{action_type}' denied for mode '{mode}': {reason}")
        self.action_type = action_type
        self.mode = mode
        self.reason = reason


class ConnectorError(WorkspaceError):
    def __init__(self, connector_type: str, message: str) -> None:
        super().__init__(f"{connector_type} connector error: {message}")
        self.connector_type = connector_type


class ProviderError(WorkspaceError):
    def __init__(self, provider_name: str, message: str) -> None:
        super().__init__(f"{provider_name} provider error: {message}")
        self.provider_name = provider_name
