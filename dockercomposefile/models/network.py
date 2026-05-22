"""Network models."""

from __future__ import annotations

from pydantic import Field, field_validator

from .common import ComposeBaseModel, _parse_external, _parse_list_or_dict


class IPAMConfig(ComposeBaseModel):
    """IPAM configuration entry."""

    subnet: str | None = None
    ip_range: str | None = None
    gateway: str | None = None
    aux_addresses: dict[str, str] | None = None


class IPAM(ComposeBaseModel):
    """IP Address Management configuration."""

    driver: str | None = None
    config: list[IPAMConfig] | None = None
    options: dict[str, str] | None = None


class Network(ComposeBaseModel):
    """Top-level network definition."""

    driver: str | None = None
    driver_opts: dict[str, str | int] | None = None
    attachable: bool | None = None
    enable_ipv4: bool | None = None
    enable_ipv6: bool | None = None
    ipam: IPAM | None = None
    internal: bool | None = None
    labels: dict[str, str] | list[str] | None = Field(
        default=None, validate_default=True
    )
    external: bool | dict[str, str] | None = Field(
        default=None, validate_default=True
    )
    name: str | None = None

    @field_validator("labels", mode="before")
    @staticmethod
    def _labels(v):
        return _parse_list_or_dict(v) if v is not None else None

    @field_validator("external", mode="before")
    @staticmethod
    def _external(v):
        return _parse_external(v) if v is not None else None


class ServiceNetworkConfig(ComposeBaseModel):
    """Service-level network attachment configuration."""

    aliases: list[str] | None = None
    ipv4_address: str | None = None
    ipv6_address: str | None = None
    link_local_ips: list[str] | None = None
    mac_address: str | None = None
    driver_opts: dict[str, str | int] | None = None
    priority: int | None = None
    gw_priority: int | None = None
    interface_name: str | None = None
