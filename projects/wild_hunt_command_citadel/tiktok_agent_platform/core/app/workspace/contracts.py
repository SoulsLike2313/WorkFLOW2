from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .models import (
    ConnectionStatus,
    ContentItem,
    DeviceProviderType,
    DeviceSession,
    MetricsSourceType,
    Profile,
    ProfileConnection,
    VideoGenerationBrief,
)


class BaseProfileConnector(ABC):
    connector_type: str

    @abstractmethod
    def connect(self, profile: Profile, connection: ProfileConnection) -> ProfileConnection:
        raise NotImplementedError

    @abstractmethod
    def disconnect(self, profile: Profile, connection: ProfileConnection) -> ProfileConnection:
        raise NotImplementedError

    @abstractmethod
    def health_check(self, profile: Profile, connection: ProfileConnection) -> tuple[ConnectionStatus, dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_runtime_info(self, profile: Profile, connection: ProfileConnection) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def validate_configuration(self, connection: ProfileConnection) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_capabilities(self) -> dict[str, Any]:
        raise NotImplementedError


class BaseDeviceProvider(ABC):
    provider_type: DeviceProviderType

    @abstractmethod
    def list_devices(self) -> list[DeviceSession]:
        raise NotImplementedError

    @abstractmethod
    def connect_device(self, device_id: str) -> DeviceSession:
        raise NotImplementedError

    @abstractmethod
    def disconnect_device(self, device_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_stream_descriptor(self, device_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_input_capabilities(self, device_id: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def health_check(self, device_id: str | None = None) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def capture_frame(self, device_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_device_state(self, device_id: str) -> dict[str, Any]:
        raise NotImplementedError


class BaseMetricsProvider(ABC):
    source_type: MetricsSourceType

    @abstractmethod
    def fetch_profile_metrics(self, profile: Profile) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def fetch_content_metrics(self, profile: Profile, content_ids: list[str]) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def fetch_recent_content(self, profile: Profile, limit: int = 20) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def fetch_engagement_events(self, profile: Profile, limit: int = 100) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_capabilities(self) -> dict[str, Any]:
        raise NotImplementedError


class BaseVideoGeneratorAdapter(ABC):
    adapter_name: str

    @abstractmethod
    def submit_generation_brief(self, brief: VideoGenerationBrief) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def check_generation_status(self, external_job_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def fetch_generated_assets(self, external_job_id: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def validate_output(self, content_item: ContentItem) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_capabilities(self) -> dict[str, Any]:
        raise NotImplementedError


class OptionalAIAdapter(ABC):
    @abstractmethod
    def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
