"""Service model and sub-models."""

from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator

from .build import BuildConfig
from .config import ServiceConfig
from .common import (
    ComposeBaseModel,
    _parse_annotations,
    _parse_command,
    _parse_devices,
    _parse_dns,
    _parse_environment,
    _parse_extra_hosts,
    _parse_labels,
    _parse_port,
    _parse_service_volume,
    _parse_tmpfs,
    _parse_ulimits,
    _parse_volumes_from,
    validate_byte_value,
    validate_duration,
)
from .deploy import DeployConfig
from .develop import DevelopConfig
from .model import ServiceModelConfig
from .network import ServiceNetworkConfig
from .secret import ServiceSecret
from .volume import VolumeMount


class BlkioLimit(ComposeBaseModel):
    """Block IO limit for a specific device."""

    path: str
    rate: str | int


class BlkioWeight(ComposeBaseModel):
    """Block IO weight for a specific device."""

    path: str
    weight: int


class BlkioConfig(ComposeBaseModel):
    """Block IO configuration."""

    weight: int | None = None
    weight_device: list[BlkioWeight] | None = None
    device_read_bps: list[BlkioLimit] | None = None
    device_read_iops: list[BlkioLimit] | None = None
    device_write_bps: list[BlkioLimit] | None = None
    device_write_iops: list[BlkioLimit] | None = None


class Healthcheck(ComposeBaseModel):
    """Healthcheck configuration."""

    test: str | list[str] | None = None
    interval: str | None = Field(default=None, validate_default=True)
    timeout: str | None = Field(default=None, validate_default=True)
    retries: int | None = None
    start_period: str | None = Field(default=None, validate_default=True)
    start_interval: str | None = Field(default=None, validate_default=True)
    disable: bool | None = None

    @field_validator("interval", "timeout", "start_period", "start_interval", mode="before")
    @staticmethod
    def _validate_duration(v: Any) -> str | None:
        return validate_duration(v) if v is not None else None


class Logging(ComposeBaseModel):
    """Logging configuration."""

    driver: str | None = None
    options: dict[str, str] | None = None


class PortConfig(ComposeBaseModel):
    """Port configuration (long syntax)."""

    target: int
    published: str | None = None
    host_ip: str | None = None
    protocol: str | None = None
    app_protocol: str | None = None
    mode: str | None = None
    name: str | None = None


class Ulimit(ComposeBaseModel):
    """Ulimit configuration."""

    soft: int
    hard: int


class CredentialSpec(ComposeBaseModel):
    """Credential specification for Windows containers."""

    file: str | None = None
    registry: str | None = None
    config: str | None = None


class DependsOnConfig(ComposeBaseModel):
    """Long-form depends_on entry."""

    condition: str | None = None
    restart: bool | None = None
    required: bool | None = None


class ExtendsConfig(ComposeBaseModel):
    """Extends configuration."""

    service: str
    file: str | None = None


class EnvFileEntry(ComposeBaseModel):
    """Environment file entry with options."""

    path: str
    required: bool = True
    format: str | None = None


class PostStartHook(ComposeBaseModel):
    """Post-start lifecycle hook."""

    command: str | list[str]
    user: str | None = None
    privileged: bool | None = None
    working_dir: str | None = None
    environment: dict[str, str] | list[str] | None = None


class ProviderConfig(ComposeBaseModel):
    """Provider configuration for delegated services."""

    type: str
    options: dict[str, Any] | None = None


class GpuConfig(ComposeBaseModel):
    """GPU configuration."""

    driver: str | None = None
    count: int | str | None = None
    device_ids: list[str] | None = None
    capabilities: list[str] | None = None
    options: dict[str, Any] | None = None


class Service(ComposeBaseModel):
    """Service definition in a Compose file."""

    # Core & Image
    image: str | None = None
    build: "BuildConfig | str | None" = Field(default=None, validate_default=True)
    command: str | list[str] | None = Field(default=None, validate_default=True)
    entrypoint: str | list[str] | None = Field(default=None, validate_default=True)

    # Environment
    environment: dict[str, str | None] | None = Field(
        default=None, validate_default=True
    )
    env_file: list[EnvFileEntry] | list[str] | str | None = Field(
        default=None, validate_default=True
    )

    # Networking
    ports: list[PortConfig] | list[str] | None = Field(
        default=None, validate_default=True
    )
    expose: list[str] | None = None
    networks: dict[str, "ServiceNetworkConfig"] | list[str] | None = None
    network_mode: str | None = None
    hostname: str | None = None
    domainname: str | None = None
    mac_address: str | None = None
    extra_hosts: dict[str, str] | list[str] | None = Field(
        default=None, validate_default=True
    )
    dns: str | list[str] | None = Field(default=None, validate_default=True)
    dns_search: str | list[str] | None = Field(default=None, validate_default=True)
    dns_opt: list[str] | None = None
    external_links: list[str] | None = None
    links: list[str] | None = None

    # Storage
    volumes: list["VolumeMount"] | list[str] | None = Field(
        default=None, validate_default=True
    )
    volumes_from: list[str] | None = Field(default=None, validate_default=True)
    tmpfs: list[str] | None = Field(default=None, validate_default=True)
    working_dir: str | None = None

    # Runtime
    user: str | None = None
    privileged: bool | None = None
    read_only: bool | None = None
    stdin_open: bool | None = None
    tty: bool | None = None
    init: bool | None = None
    restart: str | None = None
    stop_grace_period: str | None = Field(default=None, validate_default=True)
    stop_signal: str | None = None
    runtime: str | None = None
    platform: str | None = None
    ipc: str | None = None
    pid: str | None = None
    uts: str | None = None
    cgroup: str | None = None
    cgroup_parent: str | None = None
    isolation: str | None = None
    userns_mode: str | None = None
    oom_kill_disable: bool | None = None
    oom_score_adj: int | None = None
    pids_limit: int | None = None

    # Resources
    cpu_count: int | None = None
    cpu_percent: int | None = None
    cpu_shares: int | None = None
    cpu_period: int | None = None
    cpu_quota: int | None = None
    cpu_rt_runtime: str | int | None = None
    cpu_rt_period: str | int | None = None
    cpus: float | None = None
    cpuset: str | None = None
    mem_limit: str | int | None = Field(default=None, validate_default=True)
    mem_reservation: str | int | None = Field(default=None, validate_default=True)
    mem_swappiness: int | None = None
    memswap_limit: str | int | None = Field(default=None, validate_default=True)
    shm_size: str | int | None = Field(default=None, validate_default=True)
    storage_opt: dict[str, str] | None = None
    ulimits: dict[str, int | dict[str, int]] | None = Field(
        default=None, validate_default=True
    )
    sysctls: dict[str, str | int] | list[str] | None = Field(
        default=None, validate_default=True
    )
    blkio_config: BlkioConfig | None = Field(default=None, validate_default=True)

    # Capabilities & Security
    cap_add: list[str] | None = None
    cap_drop: list[str] | None = None
    security_opt: list[str] | None = None
    device_cgroup_rules: list[str] | None = None
    devices: list[str] | None = Field(default=None, validate_default=True)
    group_add: list[str] | None = None

    # Health & Logging
    healthcheck: Healthcheck | None = None
    logging: Logging | None = None

    # Dependencies
    depends_on: dict[str, DependsOnConfig] | list[str] | None = Field(
        default=None, validate_default=True
    )
    links: list[str] | None = None
    external_links: list[str] | None = None

    # Configs & Secrets
    configs: list["ServiceConfig"] | list[str] | None = Field(
        default=None, validate_default=True
    )
    secrets: list["ServiceSecret"] | list[str] | None = Field(
        default=None, validate_default=True
    )

    # Metadata
    container_name: str | None = None
    labels: dict[str, str] | list[str] | None = Field(
        default=None, validate_default=True
    )
    annotations: dict[str, str] | list[str] | None = Field(
        default=None, validate_default=True
    )
    label_file: str | list[str] | None = Field(default=None, validate_default=True)

    # Profiles & Scaling
    profiles: list[str] | None = None
    scale: int | None = None

    # Build & Deploy
    deploy: "DeployConfig | None" = None
    develop: "DevelopConfig | None" = None

    # Pull policy
    pull_policy: str | None = None

    # Credentials
    credential_spec: CredentialSpec | None = None

    # Extends
    extends: ExtendsConfig | None = None

    # Lifecycle hooks
    post_start: list[PostStartHook] | None = None
    pre_stop: list[PostStartHook] | None = None

    # GPU
    gpus: list[GpuConfig] | str | None = None

    # Models
    models: list[str] | dict[str, "ServiceModelConfig"] | None = None

    # Provider
    provider: ProviderConfig | None = None

    # API socket
    use_api_socket: bool | None = None

    # Attach
    attach: bool | None = None

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("build", mode="before")
    @staticmethod
    def _build(v: Any) -> dict[str, Any] | str | None:
        if v is None or isinstance(v, (str, dict)):
            return v
        return None

    @field_validator("command", mode="before")
    @staticmethod
    def _command(v: Any) -> str | list[str] | None:
        return _parse_command(v)

    @field_validator("entrypoint", mode="before")
    @staticmethod
    def _entrypoint(v: Any) -> str | list[str] | None:
        return _parse_command(v)

    @field_validator("environment", mode="before")
    @staticmethod
    def _environment(v: Any) -> dict[str, str | None] | None:
        return _parse_environment(v)

    @field_validator("env_file", mode="before")
    @staticmethod
    def _env_file(v: Any) -> list[EnvFileEntry] | list[str] | str | None:
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            result: list[EnvFileEntry | str] = []
            for item in v:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    result.append(EnvFileEntry.model_validate(item))
            return result
        return None

    @field_validator("ports", mode="before")
    @staticmethod
    def _ports(v: Any) -> list[PortConfig] | list[str] | None:
        if v is None:
            return None
        if isinstance(v, list):
            result: list[PortConfig | str] = []
            for item in v:
                if isinstance(item, str):
                    result.append(PortConfig.model_validate(_parse_port(item)))
                elif isinstance(item, dict):
                    result.append(PortConfig.model_validate(item))
                elif isinstance(item, int):
                    result.append(PortConfig.model_validate({"target": item}))
            return result
        return None

    @field_validator("extra_hosts", mode="before")
    @staticmethod
    def _extra_hosts(v: Any) -> dict[str, str] | list[str] | None:
        return _parse_extra_hosts(v)

    @field_validator("dns", mode="before")
    @staticmethod
    def _dns(v: Any) -> str | list[str] | None:
        return _parse_dns(v)

    @field_validator("dns_search", mode="before")
    @staticmethod
    def _dns_search(v: Any) -> str | list[str] | None:
        return _parse_dns(v)

    @field_validator("volumes", mode="before")
    @staticmethod
    def _volumes(v: Any) -> list[VolumeMount] | list[str] | None:
        if v is None:
            return None
        if isinstance(v, list):
            from .volume import VolumeMount
            result: list[VolumeMount | str] = []
            for item in v:
                if isinstance(item, str):
                    result.append(VolumeMount.model_validate(_parse_service_volume(item)))
                elif isinstance(item, dict):
                    result.append(VolumeMount.model_validate(item))
            return result
        return None

    @field_validator("volumes_from", mode="before")
    @staticmethod
    def _volumes_from(v: Any) -> list[str] | None:
        return _parse_volumes_from(v)

    @field_validator("tmpfs", mode="before")
    @staticmethod
    def _tmpfs(v: Any) -> list[str] | None:
        return _parse_tmpfs(v)

    @field_validator("stop_grace_period", mode="before")
    @staticmethod
    def _stop_grace_period(v: Any) -> str | None:
        return validate_duration(v) if v is not None else None

    @field_validator("mem_limit", mode="before")
    @staticmethod
    def _mem_limit(v: Any) -> str | int | None:
        return validate_byte_value(v)

    @field_validator("mem_reservation", mode="before")
    @staticmethod
    def _mem_reservation(v: Any) -> str | int | None:
        return validate_byte_value(v)

    @field_validator("memswap_limit", mode="before")
    @staticmethod
    def _memswap_limit(v: Any) -> str | int | None:
        return validate_byte_value(v)

    @field_validator("shm_size", mode="before")
    @staticmethod
    def _shm_size(v: Any) -> str | int | None:
        return validate_byte_value(v)

    @field_validator("ulimits", mode="before")
    @staticmethod
    def _ulimits(v: Any) -> dict[str, int | dict[str, int]] | None:
        return _parse_ulimits(v)

    @field_validator("sysctls", mode="before")
    @staticmethod
    def _sysctls(v: Any) -> dict[str, str | int] | list[str] | None:
        if v is None:
            return None
        if isinstance(v, dict):
            return {str(k): v for k, v in v.items()}
        if isinstance(v, list):
            return [str(item) for item in v]
        return None

    @field_validator("blkio_config", mode="before")
    @staticmethod
    def _blkio_config(v: Any) -> BlkioConfig | None:
        if v is None:
            return None
        if isinstance(v, dict):
            return BlkioConfig.model_validate(v)
        return None

    @field_validator("devices", mode="before")
    @staticmethod
    def _devices(v: Any) -> list[str] | None:
        return _parse_devices(v)

    @field_validator("depends_on", mode="before")
    @staticmethod
    def _depends_on(v: Any) -> dict[str, DependsOnConfig] | list[str] | None:
        if v is None:
            return None
        if isinstance(v, list):
            return [str(item) for item in v]
        if isinstance(v, dict):
            result: dict[str, DependsOnConfig] = {}
            for k, val in v.items():
                if isinstance(val, str):
                    result[str(k)] = DependsOnConfig(condition=val)
                elif isinstance(val, dict):
                    result[str(k)] = DependsOnConfig.model_validate(val)
                elif isinstance(val, bool):
                    result[str(k)] = DependsOnConfig()
            return result
        return None

    @field_validator("configs", mode="before")
    @staticmethod
    def _configs(v: Any) -> list[ServiceConfig] | list[str] | None:
        if v is None:
            return None
        from .config import ServiceConfig
        if isinstance(v, list):
            result: list[ServiceConfig | str] = []
            for item in v:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    result.append(ServiceConfig.model_validate(item))
            return result
        return None

    @field_validator("secrets", mode="before")
    @staticmethod
    def _secrets(v: Any) -> list[ServiceSecret] | list[str] | None:
        if v is None:
            return None
        from .secret import ServiceSecret
        if isinstance(v, list):
            result: list[ServiceSecret | str] = []
            for item in v:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    result.append(ServiceSecret.model_validate(item))
            return result
        return None

    @field_validator("labels", mode="before")
    @staticmethod
    def _labels(v: Any) -> dict[str, str] | list[str] | None:
        return _parse_labels(v)

    @field_validator("annotations", mode="before")
    @staticmethod
    def _annotations(v: Any) -> dict[str, str] | list[str] | None:
        return _parse_annotations(v)

    @field_validator("label_file", mode="before")
    @staticmethod
    def _label_file(v: Any) -> str | list[str] | None:
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            return [str(item) for item in v]
        return None

    @field_validator("networks", mode="before")
    @staticmethod
    def _networks(v: Any) -> dict[str, "ServiceNetworkConfig"] | list[str] | None:
        if v is None:
            return None
        from .network import ServiceNetworkConfig
        if isinstance(v, list):
            return [str(item) for item in v]
        if isinstance(v, dict):
            result: dict[str, ServiceNetworkConfig] = {}
            for k, val in v.items():
                if val is None or val == {}:
                    result[str(k)] = ServiceNetworkConfig()
                elif isinstance(val, dict):
                    result[str(k)] = ServiceNetworkConfig.model_validate(val)
            return result
        return None

    @field_validator("gpus", mode="before")
    @staticmethod
    def _gpus(v: Any) -> list[GpuConfig] | str | None:
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, list):
            result: list[GpuConfig] = []
            for item in v:
                if isinstance(item, dict):
                    result.append(GpuConfig.model_validate(item))
            return result
        return None

    @field_validator("models", mode="before")
    @staticmethod
    def _models(v: Any) -> list[str] | dict[str, "ServiceModelConfig"] | None:
        if v is None:
            return None
        if isinstance(v, list):
            return [str(item) for item in v]
        if isinstance(v, dict):
            from .model import ServiceModelConfig
            return {str(k): ServiceModelConfig.model_validate(val) if isinstance(val, dict) else ServiceModelConfig() for k, val in v.items()}
        return None

