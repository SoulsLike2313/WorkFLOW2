from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .contracts import BaseDeviceProvider
from .errors import NotFoundError, ProviderError
from .models import DeviceProviderType, DeviceSession, DeviceStatus


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class _MockDevice:
    id: str
    label: str
    status: DeviceStatus


class _BaseMockDeviceProvider(BaseDeviceProvider):
    provider_name: str
    provider_type: DeviceProviderType

    def __init__(self, provider_name: str, provider_type: DeviceProviderType, devices: list[_MockDevice]) -> None:
        self.provider_name = provider_name
        self.provider_type = provider_type
        self._devices: dict[str, _MockDevice] = {device.id: device for device in devices}

    def list_devices(self) -> list[DeviceSession]:
        return [self._as_session(device) for device in self._devices.values()]

    def connect_device(self, device_id: str) -> DeviceSession:
        device = self._devices.get(device_id)
        if device is None:
            raise NotFoundError("device", device_id)
        device.status = DeviceStatus.ONLINE
        return self._as_session(device)

    def disconnect_device(self, device_id: str) -> bool:
        device = self._devices.get(device_id)
        if device is None:
            raise NotFoundError("device", device_id)
        device.status = DeviceStatus.OFFLINE
        return True

    def get_stream_descriptor(self, device_id: str) -> dict[str, Any]:
        self._require_device(device_id)
        return {"video": True, "audio": False, "fps": 30, "resolution": "1080x1920"}

    def get_input_capabilities(self, device_id: str) -> list[str]:
        self._require_device(device_id)
        return ["tap", "swipe", "text_input"]

    def health_check(self, device_id: str | None = None) -> dict[str, Any]:
        if device_id:
            device = self._require_device(device_id)
            return {"status": "ok", "device_id": device.id, "device_status": device.status.value}
        online = sum(1 for item in self._devices.values() if item.status == DeviceStatus.ONLINE)
        return {"status": "ok", "provider": self.provider_name, "online_devices": online, "total_devices": len(self._devices)}

    def capture_frame(self, device_id: str) -> dict[str, Any]:
        device = self._require_device(device_id)
        return {
            "device_id": device.id,
            "provider": self.provider_name,
            "captured_at": _now().isoformat(),
            "frame_ref": f"mock://{self.provider_name}/{device.id}/frame/{int(_now().timestamp())}",
        }

    def get_device_state(self, device_id: str) -> dict[str, Any]:
        device = self._require_device(device_id)
        return {"device_id": device.id, "status": device.status.value, "provider": self.provider_name}

    def _as_session(self, device: _MockDevice) -> DeviceSession:
        return DeviceSession(
            id=device.id,
            provider_type=self.provider_type,
            provider_name=self.provider_name,
            device_label=device.label,
            device_status=device.status,
            stream_capabilities=["video_stream"],
            input_capabilities=["tap", "swipe", "text_input"],
            last_seen_at=_now(),
        )

    def _require_device(self, device_id: str) -> _MockDevice:
        device = self._devices.get(device_id)
        if device is None:
            raise NotFoundError("device", device_id)
        return device


class LocalAndroidProvider(_BaseMockDeviceProvider):
    def __init__(self) -> None:
        super().__init__(
            provider_name="local_android_bridge",
            provider_type=DeviceProviderType.LOCAL_ANDROID,
            devices=[
                _MockDevice(id="local-android-01", label="Pixel Local", status=DeviceStatus.ONLINE),
            ],
        )


class EmulatorProvider(_BaseMockDeviceProvider):
    def __init__(self) -> None:
        super().__init__(
            provider_name="emulator_bridge",
            provider_type=DeviceProviderType.EMULATOR,
            devices=[
                _MockDevice(id="emu-01", label="Android Emulator A", status=DeviceStatus.OFFLINE),
            ],
        )


class RemoteDeviceProvider(_BaseMockDeviceProvider):
    def __init__(self) -> None:
        super().__init__(
            provider_name="remote_device_bridge",
            provider_type=DeviceProviderType.REMOTE_DEVICE,
            devices=[
                _MockDevice(id="remote-01", label="Remote Device Node", status=DeviceStatus.UNKNOWN),
            ],
        )


class DeviceProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[DeviceProviderType, BaseDeviceProvider] = {
            DeviceProviderType.LOCAL_ANDROID: LocalAndroidProvider(),
            DeviceProviderType.EMULATOR: EmulatorProvider(),
            DeviceProviderType.REMOTE_DEVICE: RemoteDeviceProvider(),
        }

    def get(self, provider_type: DeviceProviderType) -> BaseDeviceProvider:
        provider = self._providers.get(provider_type)
        if provider is None:
            raise ProviderError("device_registry", f"Unsupported provider type: {provider_type}")
        return provider

    def list_all_devices(self) -> list[DeviceSession]:
        sessions: list[DeviceSession] = []
        for provider in self._providers.values():
            sessions.extend(provider.list_devices())
        return sessions
