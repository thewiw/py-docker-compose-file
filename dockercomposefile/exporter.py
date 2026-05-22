"""Exporter module for serializing Pydantic models to YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models.compose import DockerComposeFile


class _CustomRepresenter(yaml.SafeDumper):
    """Custom YAML representer that preserves empty dicts and ordering."""

    def represent_none(self, data):
        return self.represent_scalar("tag:yaml.org,2002:null", "")

    def represent_empty_dict(self, data):
        return self.represent_mapping("tag:yaml.org,2002:map", {})


_CustomRepresenter.add_representer(type(None), _CustomRepresenter.represent_none)


def _custom_dump(data: Any, stream: Any = None, **kwargs: Any) -> Any:
    """Dump data to YAML with custom formatting."""
    return yaml.dump(
        data,
        stream,
        Dumper=_CustomRepresenter,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=float("inf"),
        **kwargs,
    )


class ComposeExporter:
    """Export Pydantic DockerComposeFile models to YAML."""

    @staticmethod
    def to_file(compose: DockerComposeFile, path: str | Path) -> None:
        """Serialize a DockerComposeFile to a YAML file.

        Args:
            compose: The DockerComposeFile model to export.
            path: Destination file path.
        """
        path = Path(path)
        yaml_str = ComposeExporter.to_string(compose)
        with path.open("w", encoding="utf-8") as fh:
            fh.write(yaml_str)

    @staticmethod
    def to_string(compose: DockerComposeFile) -> str:
        """Serialize a DockerComposeFile to a YAML string.

        Args:
            compose: The DockerComposeFile model to export.

        Returns:
            YAML string representation.
        """
        data = ComposeExporter.to_dict(compose)
        return _custom_dump(data)

    @staticmethod
    def to_dict(compose: DockerComposeFile) -> dict[str, Any]:
        """Serialize a DockerComposeFile to a plain dictionary.

        Args:
            compose: The DockerComposeFile model to export.

        Returns:
            Dictionary representation suitable for YAML serialization.
        """
        return compose.model_dump(
            mode="json",
            exclude_none=True,
            by_alias=True,
        )
