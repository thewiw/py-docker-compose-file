"""Common types and validators shared across all compose models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic_core import PydanticCustomError


def _parse_list_or_dict(value: Any) -> dict[str, str | None]:
    """Parse a value that can be either a dict or a list of KEY=VALUE strings."""
    if value is None:
        return {}
    if isinstance(value, dict):
        return {str(k): str(v) if v is not None else None for k, v in value.items()}
    if isinstance(value, list):
        result: dict[str, str | None] = {}
        for item in value:
            if isinstance(item, str):
                if "=" in item:
                    k, v = item.split("=", 1)
                    result[k] = v
                else:
                    result[item] = None
        return result
    raise PydanticCustomError("list_or_dict", "Value must be a dict or list of strings")


def _parse_string_or_list(value: Any) -> list[str]:
    """Parse a value that can be either a string or a list of strings."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    raise PydanticCustomError("string_or_list", "Value must be a string or list of strings")


def _parse_command(value: Any) -> str | list[str] | None:
    """Parse a command that can be a string, a list of strings, or None."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return [str(item) for item in value]
    raise PydanticCustomError("command", "Command must be a string or list of strings")


def validate_duration(value: Any) -> str | None:
    """Validate a duration string.

    Accepts formats like ``10s``, ``1m30s``, ``1h5m30s20ms``,
    or plain integers (microseconds).
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise PydanticCustomError("duration", "Duration must be a string")
    # Plain integers are treated as microseconds
    if value.isdigit():
        return value

    import re

    _DURATION_RE = re.compile(r"^(\d+(?:\.\d+)?)(us|ms|s|m|h)$")
    remaining = value
    while remaining:
        m = _DURATION_RE.match(remaining)
        if not m:
            raise PydanticCustomError(
                "duration",
                f"Invalid duration format: {value!r}",
            )
        remaining = remaining[m.end() :]
    return value


def validate_byte_value(value: Any) -> str | int | None:
    """Validate a byte value string or integer.

    Accepts formats like ``1gb``, ``300m``, ``1024kb``,
    or plain integers (bytes).
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if value.isdigit():
            return int(value)
        import re

        _BYTE_VALUE_RE = re.compile(
            r"^(\d+(?:\.\d+)?)\s*([kmgt]?b)$", re.IGNORECASE
        )
        _BYTE_VALUE_RE_2 = re.compile(r"^(\d+(?:\.\d+)?)\s*([kmgt])$", re.IGNORECASE)
        m = _BYTE_VALUE_RE.match(value)
        if not m:
            m = _BYTE_VALUE_RE_2.match(value)
        if not m:
            raise PydanticCustomError(
                "byte_value",
                f"Invalid byte value format: {value!r}",
            )
        return value
    raise PydanticCustomError("byte_value", "Byte value must be a string or integer")


def _parse_port(value: Any) -> dict[str, Any]:
    """Parse a port specification from short or long form."""
    if isinstance(value, dict):
        return dict(value)
    if not isinstance(value, str):
        raise PydanticCustomError("port", "Port must be a string or dict")

    s = value.strip()

    # Extract protocol
    protocol: str | None = None
    if "/" in s:
        s, protocol = s.split("/", 1)

    # Handle bracketed IPv6: [::1]:6000:6000
    if s.startswith("["):
        bracket_end = s.find("]")
        if bracket_end == -1:
            raise PydanticCustomError("port", f"Invalid port format: {value!r}")
        host_ip = s[1:bracket_end]
        rest = s[bracket_end + 1 :]
        if rest.startswith(":"):
            rest = rest[1:]
        parts = rest.split(":")
        if len(parts) == 2 and parts[0] and parts[1]:
            return {
                "host_ip": host_ip,
                "published": parts[0],
                "target": int(parts[1]),
                **({"protocol": protocol} if protocol else {}),
            }
        if len(parts) == 1 and parts[0]:
            return {
                "host_ip": host_ip,
                "target": int(parts[0]),
                **({"protocol": protocol} if protocol else {}),
            }
        raise PydanticCustomError("port", f"Invalid port format: {value!r}")

    parts = s.split(":")

    if len(parts) == 1:
        # Just container port
        return {
            "target": int(parts[0]),
            **({"protocol": protocol} if protocol else {}),
        }

    if len(parts) == 2:
        # HOST:CONTAINER  or  IP:CONTAINER
        first, second = parts[0], parts[1]
        if "." in first:
            # IPv4 address without host port
            return {
                "host_ip": first,
                "target": int(second),
                **({"protocol": protocol} if protocol else {}),
            }
        return {
            "published": first,
            "target": int(second),
            **({"protocol": protocol} if protocol else {}),
        }

    if len(parts) == 3:
        # IP:HOST:CONTAINER
        return {
            "host_ip": parts[0],
            "published": parts[1],
            "target": int(parts[2]),
            **({"protocol": protocol} if protocol else {}),
        }

    raise PydanticCustomError("port", f"Invalid port format: {value!r}")


# Volume mount parsing (short syntax)
_VOLUME_MOUNT_RE = __import__("re").compile(
    r"^(?P<source>[^:]+):(?P<target>[^:]+)(?::(?P<mode>[^:]*))?$"
)


def _parse_service_volume(value: Any) -> dict[str, Any]:
    """Parse a service volume mount from short or long form."""
    if isinstance(value, dict):
        return dict(value)
    if not isinstance(value, str):
        raise PydanticCustomError("volume", "Volume mount must be a string or dict")
    m = _VOLUME_MOUNT_RE.match(value)
    if not m:
        # Could be a named volume without source (just target)
        return {"type": "volume", "target": value}
    source = m.group("source")
    target = m.group("target")
    mode = m.group("mode")
    result: dict[str, Any] = {"target": target}
    if source.startswith(".") or source.startswith("/") or source.startswith("~"):
        result["type"] = "bind"
        result["source"] = source
    elif source.startswith("\\"):
        result["type"] = "npipe"
        result["source"] = source
    else:
        result["type"] = "volume"
        result["source"] = source
    if mode:
        modes = mode.split(",")
        if "ro" in modes:
            result["read_only"] = True
        if "z" in modes:
            result.setdefault("bind", {})
            result["bind"]["selinux"] = "z"
        if "Z" in modes:
            result.setdefault("bind", {})
            result["bind"]["selinux"] = "Z"
    return result


def _parse_env_file(value: Any) -> list[dict[str, Any]] | None:
    """Parse env_file which can be a string, list of strings, or list of objects."""
    if value is None:
        return None
    if isinstance(value, str):
        return [{"path": value, "required": True}]
    if isinstance(value, list):
        result: list[dict[str, Any]] = []
        for item in value:
            if isinstance(item, str):
                result.append({"path": item, "required": True})
            elif isinstance(item, dict):
                result.append(dict(item))
        return result
    raise PydanticCustomError("env_file", "env_file must be a string or list")


def _parse_external(value: Any) -> dict[str, Any] | bool:
    """Parse external which can be a boolean or a dict with a name."""
    if isinstance(value, bool):
        return value
    if isinstance(value, dict):
        return dict(value)
    raise PydanticCustomError("external", "external must be a boolean or dict")


def _parse_extra_hosts(value: Any) -> dict[str, str] | None:
    """Parse extra_hosts which can be a dict or list of HOST=IP strings."""
    if value is None:
        return None
    if isinstance(value, dict):
        return {str(k): str(v) for k, v in value.items()}
    if isinstance(value, list):
        result: dict[str, str] = {}
        for item in value:
            if isinstance(item, str):
                sep = "=" if "=" in item else ":"
                parts = item.split(sep, 1)
                if len(parts) == 2:
                    result[parts[0]] = parts[1]
        return result
    raise PydanticCustomError("extra_hosts", "extra_hosts must be a dict or list")


def _parse_ulimits(value: Any) -> dict[str, Any] | None:
    """Parse ulimits which can be a dict of int or dict with soft/hard."""
    if value is None:
        return None
    if isinstance(value, dict):
        return dict(value)
    raise PydanticCustomError("ulimits", "ulimits must be a dict")


def _parse_blkio_config(value: Any) -> dict[str, Any] | None:
    """Parse blkio_config from input."""
    if value is None:
        return None
    if isinstance(value, dict):
        return dict(value)
    raise PydanticCustomError("blkio_config", "blkio_config must be a dict")


def _parse_depends_on(value: Any) -> dict[str, Any] | list[str] | None:
    """Parse depends_on which can be a list of strings or a dict."""
    if value is None:
        return None
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, dict):
        return dict(value)
    raise PydanticCustomError("depends_on", "depends_on must be a list or dict")


def _parse_tmpfs(value: Any) -> list[str] | None:
    """Parse tmpfs which can be a string or list of strings."""
    if value is None:
        return None
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    raise PydanticCustomError("tmpfs", "tmpfs must be a string or list")


def _parse_volumes_from(value: Any) -> list[str] | None:
    """Parse volumes_from which is a list of strings."""
    if value is None:
        return None
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    raise PydanticCustomError("volumes_from", "volumes_from must be a string or list")


def _parse_annotations(value: Any) -> dict[str, str] | None:
    """Parse annotations which can be a dict or list of KEY=VALUE strings."""
    if value is None:
        return None
    return _parse_list_or_dict(value)


def _parse_labels(value: Any) -> dict[str, str] | None:
    """Parse labels which can be a dict or list of KEY=VALUE strings."""
    if value is None:
        return None
    return _parse_list_or_dict(value)


def _parse_environment(value: Any) -> dict[str, str | None] | None:
    """Parse environment which can be a dict or list of KEY=VALUE strings."""
    if value is None:
        return None
    return _parse_list_or_dict(value)


def _parse_devices(value: Any) -> list[str] | None:
    """Parse devices which is a list of strings."""
    if value is None:
        return None
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    raise PydanticCustomError("devices", "devices must be a string or list")


def _parse_dns(value: Any) -> str | list[str] | None:
    """Parse dns which can be a string or list of strings."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return [str(item) for item in value]
    raise PydanticCustomError("dns", "dns must be a string or list")


def _parse_configs_or_secrets(value: Any) -> list[dict[str, Any]] | list[str] | None:
    """Parse configs/secrets which can be a list of strings or list of dicts."""
    if value is None:
        return None
    if isinstance(value, list):
        result: list[dict[str, Any] | str] = []
        for item in value:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                result.append(dict(item))
        return result
    raise PydanticCustomError("configs_secrets", "Must be a list")


def _parse_additional_contexts(value: Any) -> dict[str, str] | list[str] | None:
    """Parse additional_contexts which can be a dict or list of NAME=VALUE strings."""
    if value is None:
        return None
    if isinstance(value, dict):
        return {str(k): str(v) for k, v in value.items()}
    if isinstance(value, list):
        result: dict[str, str] = {}
        for item in value:
            if isinstance(item, str) and "=" in item:
                k, v = item.split("=", 1)
                result[k] = v
        return result
    raise PydanticCustomError("additional_contexts", "Must be a dict or list")


# ---------------------------------------------------------------------------
# Model base class shared by all compose models
# ---------------------------------------------------------------------------

class ComposeBaseModel(BaseModel):
    """Base model for all compose file models.

    Allows extra fields for ``x-*`` extensions and unknown fields.
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
