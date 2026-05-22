"""Builder module for parsing YAML into Pydantic models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models.compose import DockerComposeFile


class ComposeBuilder:
    """Build Pydantic DockerComposeFile models from YAML sources."""

    @staticmethod
    def from_file(path: str | Path) -> DockerComposeFile:
        """Load a Compose file from a filesystem path.

        Args:
            path: Path to the YAML file.

        Returns:
            Parsed DockerComposeFile model.
        """
        path = Path(path)
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if data is None:
            data = {}
        return ComposeBuilder.from_dict(data)

    @staticmethod
    def from_string(yaml_str: str) -> DockerComposeFile:
        """Parse a Compose file from a YAML string.

        Args:
            yaml_str: YAML content as a string.

        Returns:
            Parsed DockerComposeFile model.
        """
        data = yaml.safe_load(yaml_str)
        if data is None:
            data = {}
        return ComposeBuilder.from_dict(data)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> DockerComposeFile:
        """Build a DockerComposeFile model from a plain dictionary.

        Args:
            data: Dictionary representing the compose file structure.

        Returns:
            Parsed DockerComposeFile model.
        """
        return DockerComposeFile.model_validate(data)
