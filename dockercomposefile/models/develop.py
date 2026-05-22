"""Development configuration models."""

from __future__ import annotations

from .common import ComposeBaseModel


class WatchExec(ComposeBaseModel):
    """Exec configuration for watch sync+exec action."""

    command: str | list[str]
    user: str | None = None
    privileged: bool | None = None
    working_dir: str | None = None
    environment: dict[str, str] | list[str] | None = None


class WatchRule(ComposeBaseModel):
    """Watch rule for development."""

    path: str
    action: str
    target: str | None = None
    ignore: list[str] | None = None
    include: list[str] | None = None
    initial_sync: bool | None = None
    exec: WatchExec | None = None


class DevelopConfig(ComposeBaseModel):
    """Development configuration for a service."""

    watch: list[WatchRule] | None = None
