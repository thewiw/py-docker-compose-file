"""Volume models."""

from __future__ import annotations

from pydantic import Field, field_validator

from .common import ComposeBaseModel, _parse_external, _parse_list_or_dict


class Volume(ComposeBaseModel):
    """Top-level volume definition."""

    driver: str | None = None
    driver_opts: dict[str, str | int] | None = None
    external: bool | dict[str, str] | None = Field(
        default=None, validate_default=True
    )
    labels: dict[str, str] | list[str] | None = Field(
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


class BindConfig(ComposeBaseModel):
    """Bind mount options."""

    propagation: str | None = None
    create_host_path: bool | None = None
    selinux: str | None = None


class VolumeOptions(ComposeBaseModel):
    """Named volume options."""

    nocopy: bool | None = None
    subpath: str | None = None


class TmpfsConfig(ComposeBaseModel):
    """Tmpfs mount options."""

    size: str | int | None = None
    mode: int | None = None


class ImageMountConfig(ComposeBaseModel):
    """Image mount options."""

    subpath: str | None = None


class VolumeMount(ComposeBaseModel):
    """Service-level volume mount."""

    type: str = "volume"
    source: str | None = None
    target: str
    read_only: bool | None = None
    bind: BindConfig | None = None
    volume: VolumeOptions | None = None
    tmpfs: TmpfsConfig | None = None
    image: ImageMountConfig | None = None
    consistency: str | None = None
