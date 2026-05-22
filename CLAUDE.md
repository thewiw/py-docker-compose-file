# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`dockercomposefile` is a Python library that provides Pydantic v2 models for Docker Compose files. It can parse YAML Compose files into typed objects, manipulate them programmatically, and export them back to YAML.

- **Python version**: 3.13+
- **Package manager**: `uv` (uv.lock present; also works with pip)

## Commands

### Setup
```bash
uv pip install -e ".[dev]"
# or: pip install -e ".[dev]"
```

### Tests
```bash
pytest                              # Run all tests
pytest tests/test_builder.py       # Run a single test file
pytest -k test_minimal_compose     # Run a single test by name
pytest --cov=dockercomposefile --cov-report=term-missing  # With coverage
```

### Linting and Formatting
```bash
black dockercomposefile/ tests/    # Format code
ruff check dockercomposefile/ tests/  # Lint code
```

## Architecture

### Entry Points

The public API is in `dockercomposefile/__init__.py`:

- **`ComposeBuilder`** (`builder.py`): Static methods `from_file(path)`, `from_string(yaml)`, `from_dict(dict)` that parse input and return a `DockerComposeFile` model.
- **`ComposeExporter`** (`exporter.py`): Static methods `to_file(compose, path)`, `to_string(compose)`, `to_dict(compose)` that serialize a `DockerComposeFile` back out.

### Model Structure

All models live under `dockercomposefile/models/` and inherit from `ComposeBaseModel` (`models/common.py`).

- **`models/compose.py`**: `DockerComposeFile` (top-level model), `Include`.
- **`models/service.py`**: `Service` and its sub-models (`Healthcheck`, `Logging`, `PortConfig`, `BlkioConfig`, etc.).
- **`models/build.py`**: `BuildConfig`, `BuildSecret`.
- **`models/deploy.py`**: `DeployConfig`, `Resources`, `Placement`, `RestartPolicy`, etc.
- **`models/develop.py`**: `DevelopConfig`, `WatchRule`, `WatchExec`.
- **`models/network.py`**: `Network`, `IPAM`, `ServiceNetworkConfig`.
- **`models/volume.py`**: `Volume`, `VolumeMount`, `BindConfig`, `TmpfsConfig`.
- **`models/config.py`**: `Config`, `ServiceConfig`.
- **`models/secret.py`**: `Secret`, `ServiceSecret`.
- **`models/model.py`**: `Model`, `ServiceModelConfig` (AI model support in Compose).
- **`models/common.py`**: `ComposeBaseModel` plus a large collection of validator/parser functions used across models to normalize short syntax.

### Short Syntax Normalization

Docker Compose supports short syntax for many fields (e.g. `ports: ["80:80"]`, `volumes: ["./src:/app"]`). These are **normalized to long-form Pydantic models on parse** by field validators in `models/common.py`:

- `_parse_port` — handles `HOST:CONTAINER`, `IP:HOST:CONTAINER`, `[::1]:6000:6000`, and protocol suffixes.
- `_parse_service_volume` — handles `source:target:mode`, detects bind vs named volume vs npipe.
- `_parse_environment`, `_parse_labels`, `_parse_annotations` — handles dict or `KEY=VALUE` list.
- `_parse_command`, `_parse_env_file`, `_parse_external`, `_parse_extra_hosts`, etc.

On export, the long form is emitted (no round-trip to short syntax).

### Extension Fields (`x-*`)

`ComposeBaseModel` sets `extra="allow"` so unknown fields (including `x-*` extension fields) are preserved through parse and export.

### Custom YAML Export

`exporter.py` uses a custom `yaml.SafeDumper` subclass (`_CustomRepresenter`) that:
- Preserves ordering (`sort_keys=False`).
- Renders `None` values as empty scalars (to support empty dict emission where needed).

### Null Value Normalization

`DockerComposeFile` has a `@model_validator(mode="before")` that converts `None` values inside resource dicts (e.g. `volumes:\n  frontend_build:`) to empty dicts `{}` before Pydantic validation.

## Testing

Tests are in `tests/`:

- `test_builder.py` — parse tests covering short-syntax normalization and edge cases.
- `test_exporter.py` — serialization tests.
- `test_roundtrip.py` — end-to-end parse-then-export tests.
