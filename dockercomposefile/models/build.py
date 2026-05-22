"""Build configuration models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from .common import (
    ComposeBaseModel,
    _parse_additional_contexts,
    _parse_list_or_dict,
    validate_byte_value,
)


class BuildSecret(BaseModel):
    """Secret reference for build."""

    source: str
    target: str | None = None
    uid: str | None = None
    gid: str | None = None
    mode: str | None = None


class BuildConfig(ComposeBaseModel):
    """Build configuration for a service."""

    context: str | None = None
    dockerfile: str | None = None
    dockerfile_inline: str | None = None
    args: dict[str, str | None] | list[str] | None = Field(
        default=None, validate_default=True
    )
    ssh: str | list[str] | None = Field(default=None, validate_default=True)
    labels: dict[str, str] | list[str] | None = Field(
        default=None, validate_default=True
    )
    cache_from: list[str] | None = None
    cache_to: list[str] | None = None
    entitlements: list[str] | None = None
    additional_contexts: dict[str, str] | list[str] | None = Field(
        default=None, validate_default=True
    )
    isolation: str | None = None
    network: str | None = None
    shm_size: str | int | None = Field(default=None, validate_default=True)
    target: str | None = None
    platforms: list[str] | None = None
    tags: list[str] | None = None
    pull: bool | None = None
    no_cache: bool | None = None
    privileged: bool | None = None
    secrets: list[str | BuildSecret] | None = Field(
        default=None, validate_default=True
    )
    provenance: bool | str | None = None
    sbom: bool | str | None = None
    ulimits: dict[str, Any] | None = None
    extra_hosts: dict[str, str] | list[str] | None = Field(
        default=None, validate_default=True
    )

    @classmethod
    def model_validate(cls, obj: Any) -> "BuildConfig":
        if isinstance(obj, str):
            obj = {"context": obj}
        return super().model_validate(obj)

    # -- validators ----------------------------------------------------------

    @field_validator("args", mode="before")
    @staticmethod
    def _args(v: Any) -> dict[str, str | None] | list[str] | None:
        return _parse_list_or_dict(v) if v is not None else None

    @field_validator("ssh", mode="before")
    @staticmethod
    def _ssh(v: Any) -> str | list[str] | None:
        return v if isinstance(v, (str, list)) or v is None else None

    @field_validator("labels", mode="before")
    @staticmethod
    def _labels(v: Any) -> dict[str, str] | list[str] | None:
        return _parse_list_or_dict(v) if v is not None else None

    @field_validator("additional_contexts", mode="before")
    @staticmethod
    def _additional_contexts(v: Any) -> dict[str, str] | list[str] | None:
        return _parse_additional_contexts(v) if v is not None else None

    @field_validator("shm_size", mode="before")
    @staticmethod
    def _shm_size(v: Any) -> str | int | None:
        return validate_byte_value(v)

    @field_validator("secrets", mode="before")
    @staticmethod
    def _secrets(v: Any) -> list[str | BuildSecret] | None:
        if v is None:
            return None
        if isinstance(v, list):
            result: list[str | BuildSecret] = []
            for item in v:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    result.append(BuildSecret.model_validate(item))
            return result
        return None

    @field_validator("extra_hosts", mode="before")
    @staticmethod
    def _extra_hosts(v: Any) -> dict[str, str] | list[str] | None:
        if v is None:
            return None
        if isinstance(v, dict):
            return {str(k): str(val) for k, val in v.items()}
        if isinstance(v, list):
            return [str(item) for item in v]
        return None

