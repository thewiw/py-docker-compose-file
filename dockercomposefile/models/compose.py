"""Top-level DockerComposeFile model."""

from __future__ import annotations

from typing import Any

from pydantic import model_validator

from .common import ComposeBaseModel
from .config import Config
from .model import Model
from .network import Network
from .secret import Secret
from .service import Service
from .volume import Volume


class Include(ComposeBaseModel):
    """Include configuration for composing multiple files."""

    path: list[str] | str | None = None
    project_directory: str | None = None
    env_file: list[str] | str | None = None


class DockerComposeFile(ComposeBaseModel):
    """Top-level Docker Compose file model."""

    version: str | None = None
    name: str | None = None
    include: list[Include] | None = None
    services: dict[str, Service] | None = None
    networks: dict[str, Network] | None = None
    volumes: dict[str, Volume] | None = None
    configs: dict[str, Config] | None = None
    secrets: dict[str, Secret] | None = None
    models: dict[str, Model] | None = None

    @model_validator(mode="before")
    @staticmethod
    def _normalize_none_values(data: Any) -> Any:
        """Replace None values in resource dicts with empty dicts.

        Docker Compose allows declaring resources with no attributes
        (e.g. ``volumes:\n  frontend_build:``), which YAML parses as
        ``None``. Convert these to empty dicts for Pydantic validation.
        """
        if not isinstance(data, dict):
            return data
        for key in ("networks", "volumes", "configs", "secrets"):
            if key not in data or data[key] is None:
                continue
            resource = data[key]
            if isinstance(resource, dict):
                for name, value in list(resource.items()):
                    if value is None:
                        resource[name] = {}
        return data
