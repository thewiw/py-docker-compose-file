"""Secret models."""

from __future__ import annotations

from pydantic import Field, field_validator

from .common import ComposeBaseModel, _parse_external, _parse_list_or_dict


class Secret(ComposeBaseModel):
    """Top-level secret definition."""

    file: str | None = None
    environment: str | None = None
    external: bool | dict[str, str] | None = Field(
        default=None, validate_default=True
    )
    name: str | None = None
    labels: dict[str, str] | list[str] | None = Field(
        default=None, validate_default=True
    )
    template_driver: str | None = None

    @field_validator("labels", mode="before")
    @staticmethod
    def _labels(v):
        return _parse_list_or_dict(v) if v is not None else None

    @field_validator("external", mode="before")
    @staticmethod
    def _external(v):
        return _parse_external(v) if v is not None else None


class ServiceSecret(ComposeBaseModel):
    """Service-level secret reference."""

    source: str
    target: str | None = None
    uid: str | None = None
    gid: str | None = None
    mode: str | None = None
