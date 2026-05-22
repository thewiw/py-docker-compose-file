"""AI model models."""

from __future__ import annotations

from .common import ComposeBaseModel


class Model(ComposeBaseModel):
    """Top-level AI model definition."""

    model: str
    context_size: int | None = None
    runtime_flags: list[str] | None = None


class ServiceModelConfig(ComposeBaseModel):
    """Service-level model reference (long syntax)."""

    endpoint_var: str | None = None
    model_var: str | None = None
