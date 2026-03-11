from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..connectors import ConnectorRegistry
from ..diagnostics import diag_log
from ..errors import LimitExceededError, NotFoundError
from ..models import (
    ActionResult,
    ActorType,
    ConnectionStatus,
    ConnectionType,
    HealthState,
    ManagementMode,
    Platform,
    Profile,
    ProfileConnection,
    ProfileStatus,
)
from ..policy import PolicyGuard
from ..repository import WorkspaceRepository
from .audit_service import AuditService


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProfileService:
    def __init__(
        self,
        *,
        repository: WorkspaceRepository,
        connector_registry: ConnectorRegistry,
        policy_guard: PolicyGuard,
        audit_service: AuditService,
        max_profiles: int = 10,
    ) -> None:
        self.repository = repository
        self.connector_registry = connector_registry
        self.policy_guard = policy_guard
        self.audit_service = audit_service
        self.max_profiles = max_profiles

    def create_profile(
        self,
        *,
        display_name: str,
        platform: Platform,
        connection_type: ConnectionType,
        management_mode: ManagementMode,
        notes: str = "",
        tags: list[str] | None = None,
    ) -> Profile:
        if self.repository.count_profiles() >= self.max_profiles:
            message = f"Profile limit reached ({self.max_profiles}). Increase MAX_PROFILES in configuration."
            diag_log(
                "runtime_logs",
                "profile_limit_reached",
                level="WARNING",
                payload={"display_name": display_name, "max_profiles": self.max_profiles},
            )
            self.audit_service.log_action(
                action_type="create_profile",
                actor_type=ActorType.SYSTEM,
                result=ActionResult.DENIED,
                action_payload={"display_name": display_name, "limit": self.max_profiles},
                error_text=message,
            )
            raise LimitExceededError(message)

        profile = Profile(
            display_name=display_name,
            platform=platform,
            connection_type=connection_type,
            management_mode=management_mode,
            notes=notes,
            tags=tags or [],
            status=ProfileStatus.DISCONNECTED,
            health_state=HealthState.UNKNOWN,
        )
        connection = ProfileConnection(
            profile_id=profile.id,
            connection_type=connection_type,
            connection_status=ConnectionStatus.DISCONNECTED,
        )

        self.repository.save_profile(profile)
        self.repository.save_connection(connection)
        diag_log(
            "runtime_logs",
            "profile_created",
            payload={
                "profile_id": profile.id,
                "display_name": display_name,
                "connection_type": connection_type.value,
                "management_mode": management_mode.value,
            },
        )
        self.audit_service.log_action(
            action_type="create_profile",
            profile_id=profile.id,
            action_payload={
                "connection_type": connection_type.value,
                "management_mode": management_mode.value,
            },
            result=ActionResult.SUCCESS,
        )
        return profile

    def list_profiles(self) -> list[Profile]:
        return self.repository.list_profiles()

    def get_profile(self, profile_id: str) -> Profile:
        profile = self.repository.get_profile(profile_id)
        if profile is None:
            raise NotFoundError("profile", profile_id)
        return profile

    def get_connection(self, profile_id: str) -> ProfileConnection:
        connection = self.repository.get_connection(profile_id)
        if connection is None:
            raise NotFoundError("profile_connection", profile_id)
        return connection

    def set_management_mode(self, profile_id: str, management_mode: ManagementMode) -> Profile:
        profile = self.get_profile(profile_id)
        updated = profile.model_copy(update={"management_mode": management_mode, "updated_at": _utc_now()})
        self.repository.save_profile(updated)
        diag_log(
            "runtime_logs",
            "profile_management_mode_updated",
            payload={"profile_id": profile_id, "management_mode": management_mode.value},
        )
        self.audit_service.log_action(
            action_type="set_management_mode",
            profile_id=profile_id,
            action_payload={"management_mode": management_mode.value},
            result=ActionResult.SUCCESS,
        )
        return updated

    def connect_profile(
        self,
        profile_id: str,
        *,
        cdp_url: str | None = None,
        auth_provider: str | None = None,
        device_id: str | None = None,
        remote_provider: str | None = None,
        confirmed: bool = False,
    ) -> ProfileConnection:
        profile = self.get_profile(profile_id)
        self.policy_guard.enforce(profile.management_mode, "connect_profile", confirmed=confirmed)

        connection = self.repository.get_connection(profile_id)
        if connection is None:
            connection = ProfileConnection(profile_id=profile_id, connection_type=profile.connection_type)

        updated_connection = connection.model_copy(
            update={
                "cdp_url": cdp_url if cdp_url is not None else connection.cdp_url,
                "auth_provider": auth_provider if auth_provider is not None else connection.auth_provider,
                "device_id": device_id if device_id is not None else connection.device_id,
                "remote_provider": remote_provider if remote_provider is not None else connection.remote_provider,
            }
        )

        connector = self.connector_registry.get(profile.connection_type)
        connected = connector.connect(profile, updated_connection)
        status, health = self._profile_status_from_connection(connected.connection_status)
        diag_log(
            "runtime_logs",
            "profile_connected",
            payload={
                "profile_id": profile_id,
                "connection_type": profile.connection_type.value,
                "connection_status": connected.connection_status.value,
            },
        )

        self.repository.save_connection(connected)
        self.repository.save_profile(
            profile.model_copy(
                update={"status": status, "health_state": health, "updated_at": _utc_now()},
            )
        )
        self.audit_service.log_action(
            action_type="connect_profile",
            profile_id=profile_id,
            action_payload={
                "connection_type": profile.connection_type.value,
                "connection_status": connected.connection_status.value,
            },
            result=ActionResult.SUCCESS if connected.connection_status != ConnectionStatus.ERROR else ActionResult.FAILURE,
            error_text=connected.error_message,
        )
        return connected

    def disconnect_profile(self, profile_id: str, *, confirmed: bool = False) -> ProfileConnection:
        profile = self.get_profile(profile_id)
        self.policy_guard.enforce(profile.management_mode, "disconnect_profile", confirmed=confirmed)
        connection = self.get_connection(profile_id)

        connector = self.connector_registry.get(profile.connection_type)
        disconnected = connector.disconnect(profile, connection)
        diag_log(
            "runtime_logs",
            "profile_disconnected",
            payload={"profile_id": profile_id, "connection_type": profile.connection_type.value},
        )

        self.repository.save_connection(disconnected)
        self.repository.save_profile(
            profile.model_copy(
                update={
                    "status": ProfileStatus.DISCONNECTED,
                    "health_state": HealthState.UNKNOWN,
                    "updated_at": _utc_now(),
                }
            )
        )
        self.audit_service.log_action(
            action_type="disconnect_profile",
            profile_id=profile_id,
            action_payload={"connection_type": profile.connection_type.value},
            result=ActionResult.SUCCESS,
        )
        return disconnected

    def health_check(self, profile_id: str) -> dict[str, Any]:
        profile = self.get_profile(profile_id)
        connection = self.get_connection(profile_id)
        connector = self.connector_registry.get(profile.connection_type)
        status, metadata = connector.health_check(profile, connection)
        diag_log(
            "runtime_logs",
            "profile_health_check",
            payload={"profile_id": profile_id, "status": status.value, "metadata": metadata},
        )
        self.audit_service.log_action(
            action_type="profile_health_check",
            profile_id=profile_id,
            action_payload={"status": status.value},
            result=ActionResult.INFO,
        )
        return {
            "profile_id": profile_id,
            "connection_type": profile.connection_type.value,
            "connection_status": status.value,
            "metadata": metadata,
        }

    def get_runtime_info(self, profile_id: str) -> dict[str, Any]:
        profile = self.get_profile(profile_id)
        connection = self.get_connection(profile_id)
        connector = self.connector_registry.get(profile.connection_type)
        return connector.get_runtime_info(profile, connection)

    @staticmethod
    def _profile_status_from_connection(connection_status: ConnectionStatus) -> tuple[ProfileStatus, HealthState]:
        if connection_status == ConnectionStatus.CONNECTED:
            return ProfileStatus.ACTIVE, HealthState.HEALTHY
        if connection_status == ConnectionStatus.NOT_IMPLEMENTED:
            return ProfileStatus.WARNING, HealthState.UNKNOWN
        if connection_status == ConnectionStatus.ERROR:
            return ProfileStatus.WARNING, HealthState.DEGRADED
        if connection_status == ConnectionStatus.PENDING:
            return ProfileStatus.DISCONNECTED, HealthState.UNKNOWN
        return ProfileStatus.DISCONNECTED, HealthState.UNKNOWN
