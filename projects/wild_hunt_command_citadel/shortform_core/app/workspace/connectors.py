from __future__ import annotations

import socket
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from .contracts import BaseProfileConnector
from .device_providers import DeviceProviderRegistry
from .errors import ConnectorError
from .models import ConnectionStatus, ConnectionType, Profile, ProfileConnection


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CdpProfileConnector(BaseProfileConnector):
    connector_type = ConnectionType.CDP.value

    def connect(self, profile: Profile, connection: ProfileConnection) -> ProfileConnection:
        issues = self.validate_configuration(connection)
        if issues:
            raise ConnectorError(self.connector_type, "; ".join(issues))

        status, metadata = self.health_check(profile, connection)
        updated = connection.model_copy(
            update={
                "connection_status": status,
                "runtime_metadata": metadata,
                "last_connected_at": datetime.now(timezone.utc) if status == ConnectionStatus.CONNECTED else None,
                "error_message": None if status == ConnectionStatus.CONNECTED else "CDP endpoint unavailable",
            }
        )
        return updated

    def disconnect(self, profile: Profile, connection: ProfileConnection) -> ProfileConnection:
        return connection.model_copy(update={"connection_status": ConnectionStatus.DISCONNECTED})

    def health_check(self, profile: Profile, connection: ProfileConnection) -> tuple[ConnectionStatus, dict[str, Any]]:
        if not connection.cdp_url:
            return ConnectionStatus.ERROR, {"error": "Missing cdp_url"}

        parsed = urlparse(connection.cdp_url)
        host = parsed.hostname
        port = parsed.port
        if not host or not port:
            return ConnectionStatus.ERROR, {"error": "Invalid CDP URL"}

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        try:
            sock.connect((host, port))
            return ConnectionStatus.CONNECTED, {"host": host, "port": port, "checked_at": _utc_iso()}
        except OSError as error:
            return ConnectionStatus.ERROR, {"error": str(error), "host": host, "port": port}
        finally:
            sock.close()

    def get_runtime_info(self, profile: Profile, connection: ProfileConnection) -> dict[str, Any]:
        return {
            "connector": self.connector_type,
            "profile_id": profile.id,
            "connection_status": connection.connection_status.value,
            "metadata": connection.runtime_metadata,
        }

    def validate_configuration(self, connection: ProfileConnection) -> list[str]:
        issues: list[str] = []
        if not connection.cdp_url:
            issues.append("cdp_url is required")
            return issues

        parsed = urlparse(connection.cdp_url)
        if parsed.scheme not in {"http", "https", "ws", "wss"}:
            issues.append("cdp_url scheme must be http/https/ws/wss")
        if parsed.hostname is None:
            issues.append("cdp_url hostname is missing")
        if parsed.port is None:
            issues.append("cdp_url port is missing")
        return issues

    def get_capabilities(self) -> dict[str, Any]:
        return {
            "connect": True,
            "disconnect": True,
            "health_check": True,
            "runtime_info": True,
            "safe_mode": True,
        }


class OfficialAuthConnector(BaseProfileConnector):
    connector_type = ConnectionType.OFFICIAL_AUTH.value

    def connect(self, profile: Profile, connection: ProfileConnection) -> ProfileConnection:
        return connection.model_copy(
            update={
                "connection_status": ConnectionStatus.NOT_IMPLEMENTED,
                "error_message": "Official auth flow is not implemented yet. Use provider contract integration.",
                "runtime_metadata": {"mode": "stub"},
            }
        )

    def disconnect(self, profile: Profile, connection: ProfileConnection) -> ProfileConnection:
        return connection.model_copy(update={"connection_status": ConnectionStatus.DISCONNECTED, "error_message": None})

    def health_check(self, profile: Profile, connection: ProfileConnection) -> tuple[ConnectionStatus, dict[str, Any]]:
        return ConnectionStatus.NOT_IMPLEMENTED, {"message": "Official auth connector is a contract stub."}

    def get_runtime_info(self, profile: Profile, connection: ProfileConnection) -> dict[str, Any]:
        return {"connector": self.connector_type, "status": connection.connection_status.value, "stub": True}

    def validate_configuration(self, connection: ProfileConnection) -> list[str]:
        if not connection.auth_provider:
            return ["auth_provider is required for official_auth connector"]
        return []

    def get_capabilities(self) -> dict[str, Any]:
        return {"auth_flow": "contract_stub", "supports_password_login": False}


class DeviceProfileConnector(BaseProfileConnector):
    connector_type = ConnectionType.DEVICE.value

    def __init__(self, registry: DeviceProviderRegistry) -> None:
        self.registry = registry

    def connect(self, profile: Profile, connection: ProfileConnection) -> ProfileConnection:
        issues = self.validate_configuration(connection)
        if issues:
            raise ConnectorError(self.connector_type, "; ".join(issues))

        provider = self._provider_from_connection(connection)
        session = provider.connect_device(connection.device_id or "")
        return connection.model_copy(
            update={
                "connection_status": ConnectionStatus.CONNECTED,
                "last_connected_at": datetime.now(timezone.utc),
                "runtime_metadata": {
                    "provider_name": session.provider_name,
                    "device_label": session.device_label,
                    "provider_type": session.provider_type.value,
                },
                "error_message": None,
            }
        )

    def disconnect(self, profile: Profile, connection: ProfileConnection) -> ProfileConnection:
        provider = self._provider_from_connection(connection)
        if connection.device_id:
            provider.disconnect_device(connection.device_id)
        return connection.model_copy(update={"connection_status": ConnectionStatus.DISCONNECTED})

    def health_check(self, profile: Profile, connection: ProfileConnection) -> tuple[ConnectionStatus, dict[str, Any]]:
        provider = self._provider_from_connection(connection)
        payload = provider.health_check(connection.device_id)
        return ConnectionStatus.CONNECTED, payload

    def get_runtime_info(self, profile: Profile, connection: ProfileConnection) -> dict[str, Any]:
        provider = self._provider_from_connection(connection)
        payload = provider.get_device_state(connection.device_id or "")
        payload["connector"] = self.connector_type
        return payload

    def validate_configuration(self, connection: ProfileConnection) -> list[str]:
        issues: list[str] = []
        if not connection.device_id:
            issues.append("device_id is required")
        if not connection.remote_provider:
            issues.append("remote_provider is required (local_android / emulator / remote_device)")
        else:
            normalized = connection.remote_provider.lower()
            if normalized not in {"local_android", "emulator", "remote_device"}:
                issues.append("remote_provider must be local_android | emulator | remote_device")
        return issues

    def get_capabilities(self) -> dict[str, Any]:
        return {"connect": True, "streaming": True, "capture_frame": True, "input_bridge": True}

    def _provider_from_connection(self, connection: ProfileConnection):
        if not connection.remote_provider:
            raise ConnectorError(self.connector_type, "remote_provider is required")

        normalized = connection.remote_provider.lower()
        mapping = {
            "local_android": "LOCAL_ANDROID",
            "emulator": "EMULATOR",
            "remote_device": "REMOTE_DEVICE",
        }
        enum_name = mapping.get(normalized)
        if not enum_name:
            raise ConnectorError(self.connector_type, f"Unsupported remote_provider '{normalized}'")
        from .models import DeviceProviderType

        provider_type = DeviceProviderType[enum_name]
        return self.registry.get(provider_type)


class ConnectorRegistry:
    def __init__(self, device_registry: DeviceProviderRegistry) -> None:
        self._connectors: dict[ConnectionType, BaseProfileConnector] = {
            ConnectionType.CDP: CdpProfileConnector(),
            ConnectionType.OFFICIAL_AUTH: OfficialAuthConnector(),
            ConnectionType.DEVICE: DeviceProfileConnector(device_registry),
        }

    def get(self, connection_type: ConnectionType) -> BaseProfileConnector:
        connector = self._connectors.get(connection_type)
        if connector is None:
            raise ConnectorError("registry", f"Unsupported connector type: {connection_type.value}")
        return connector
