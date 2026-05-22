# dockercomposefile

Pydantic2 models for Docker Compose files with YAML builder and exporter.

## Installation

```bash
pip install dockercomposefile
```

## Usage

### Parse a Compose file

```python
from dockercomposefile import ComposeBuilder

# From a YAML string
compose = ComposeBuilder.from_string("""
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
""")

# From a file
compose = ComposeBuilder.from_file("docker-compose.yml")

# From a dictionary
compose = ComposeBuilder.from_dict({"services": {"web": {"image": "nginx"}}})
```

### Access model data

```python
# Access services
web = compose.services["web"]
print(web.image)  # nginx:latest

# Access ports (normalized to long form)
for port in web.ports:
    print(f"{port.target} -> {port.published}")

# Access networks
for name, network in compose.networks.items():
    print(f"Network: {name}, driver: {network.driver}")
```

### Export to YAML

```python
from dockercomposefile import ComposeExporter

# To a string
yaml_str = ComposeExporter.to_string(compose)

# To a file
ComposeExporter.to_file(compose, "docker-compose.yml")

# To a dictionary
data = ComposeExporter.to_dict(compose)
```

### Create programmatically

```python
from dockercomposefile.models import DockerComposeFile, Service

compose = DockerComposeFile(
    services={
        "web": Service(
            image="nginx:latest",
            ports=[{"target": 80, "published": "8080"}],
        ),
    },
)
```

## Supported Compose Specification

The library models the full Docker Compose specification, including:

- **Services**: image, build, command, entrypoint, environment, ports, volumes,
  networks, depends_on, healthcheck, logging, deploy, develop, and more
- **Networks**: driver, driver_opts, ipam, external, labels
- **Volumes**: driver, driver_opts, external, labels
- **Configs/Secrets**: file, environment, content, external
- **Models** (AI): model, context_size, runtime_flags
- **Build**: context, dockerfile, args, cache_from, secrets, ssh, platforms
- **Deploy**: replicas, resources, placement, restart_policy, update_config
- **Develop**: watch rules for file syncing and rebuilds

Short syntax (e.g., `ports: ["80:80"]`) is automatically normalized to long
form (structured objects) on parse. On export, the long form is emitted.

`x-*` extension fields are preserved on both parse and export.

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=dockercomposefile --cov-report=term-missing
```

## License

MIT
