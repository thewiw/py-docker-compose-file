"""Deploy configuration models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from .common import ComposeBaseModel, validate_byte_value, validate_duration


class PlacementPreference(BaseModel):
    """Placement preference."""

    spread: str | None = None


class Placement(ComposeBaseModel):
    """Placement constraints and preferences."""

    constraints: list[str] | None = None
    preferences: list[PlacementPreference] | None = None
    max_replicas_per_node: int | None = None


class ResourceLimits(ComposeBaseModel):
    """Resource limits."""

    cpus: str | None = None
    memory: str | None = Field(default=None, validate_default=True)
    pids: int | None = None

    @field_validator("memory", mode="before")
    @staticmethod
    def _memory(v: Any) -> str | None:
        return validate_byte_value(v)


class ResourceReservations(ComposeBaseModel):
    """Resource reservations."""

    cpus: str | None = None
    memory: str | None = Field(default=None, validate_default=True)
    pids: int | None = None
    devices: list[dict[str, Any]] | None = None

    @field_validator("memory", mode="before")
    @staticmethod
    def _memory(v: Any) -> str | None:
        return validate_byte_value(v)


class Resources(ComposeBaseModel):
    """Resource configuration."""

    limits: ResourceLimits | None = None
    reservations: ResourceReservations | None = None


class RestartPolicy(ComposeBaseModel):
    """Restart policy for deploy."""

    condition: str | None = None
    delay: str | None = Field(default=None, validate_default=True)
    max_attempts: int | None = None
    window: str | None = Field(default=None, validate_default=True)

    @field_validator("delay", "window", mode="before")
    @staticmethod
    def _duration(v: Any) -> str | None:
        return validate_duration(v)


class UpdateConfig(ComposeBaseModel):
    """Update configuration."""

    parallelism: int | None = None
    delay: str | None = Field(default=None, validate_default=True)
    failure_action: str | None = None
    monitor: str | None = Field(default=None, validate_default=True)
    max_failure_ratio: float | None = None
    order: str | None = None

    @field_validator("delay", "monitor", mode="before")
    @staticmethod
    def _duration(v: Any) -> str | None:
        return validate_duration(v)


class RollbackConfig(ComposeBaseModel):
    """Rollback configuration."""

    parallelism: int | None = None
    delay: str | None = Field(default=None, validate_default=True)
    failure_action: str | None = None
    monitor: str | None = Field(default=None, validate_default=True)
    max_failure_ratio: float | None = None
    order: str | None = None

    @field_validator("delay", "monitor", mode="before")
    @staticmethod
    def _duration(v: Any) -> str | None:
        return validate_duration(v)


class DeployConfig(ComposeBaseModel):
    """Deploy configuration for a service."""

    endpoint_mode: str | None = None
    labels: dict[str, str] | list[str] | None = None
    mode: str | None = None
    replicas: int | None = None
    resources: Resources | None = None
    placement: Placement | None = None
    restart_policy: RestartPolicy | None = None
    rollback_config: RollbackConfig | None = None
    update_config: UpdateConfig | None = None
