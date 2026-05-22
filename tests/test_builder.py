"""Tests for the ComposeBuilder."""

from __future__ import annotations

from dockercomposefile import ComposeBuilder
from dockercomposefile.models import (
    DockerComposeFile,
    PortConfig,
    VolumeMount,
)


class TestFromString:
    """Tests for ComposeBuilder.from_string()."""

    def test_minimal_compose(self):
        yaml_str = """
services:
  web:
    image: nginx
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert isinstance(compose, DockerComposeFile)
        assert "web" in compose.services
        assert compose.services["web"].image == "nginx"

    def test_empty_string(self):
        compose = ComposeBuilder.from_string("")
        assert isinstance(compose, DockerComposeFile)
        assert compose.services is None or compose.services == {}

    def test_ports_short_syntax(self):
        yaml_str = """
services:
  web:
    image: nginx
    ports:
      - "80:80"
      - "127.0.0.1:8000:8000"
      - "[::1]:6000:6000"
      - "6060/udp"
"""
        compose = ComposeBuilder.from_string(yaml_str)
        ports = compose.services["web"].ports
        assert len(ports) == 4
        assert ports[0] == PortConfig(target=80, published="80")
        assert ports[1] == PortConfig(target=8000, published="8000", host_ip="127.0.0.1")
        assert ports[2] == PortConfig(target=6000, published="6000", host_ip="::1")
        assert ports[3] == PortConfig(target=6060, protocol="udp")

    def test_ports_long_syntax(self):
        yaml_str = """
services:
  web:
    image: nginx
    ports:
      - target: 80
        published: "8080"
        protocol: tcp
        mode: host
"""
        compose = ComposeBuilder.from_string(yaml_str)
        ports = compose.services["web"].ports
        assert len(ports) == 1
        assert ports[0] == PortConfig(
            target=80, published="8080", protocol="tcp", mode="host"
        )

    def test_environment_dict(self):
        yaml_str = """
services:
  web:
    image: nginx
    environment:
      DEBUG: "true"
      PORT: "8080"
"""
        compose = ComposeBuilder.from_string(yaml_str)
        env = compose.services["web"].environment
        assert env == {"DEBUG": "true", "PORT": "8080"}

    def test_environment_list(self):
        yaml_str = """
services:
  web:
    image: nginx
    environment:
      - DEBUG=true
      - PORT=8080
"""
        compose = ComposeBuilder.from_string(yaml_str)
        env = compose.services["web"].environment
        assert env == {"DEBUG": "true", "PORT": "8080"}

    def test_volumes_short_syntax(self):
        yaml_str = """
services:
  web:
    image: nginx
    volumes:
      - ./html:/usr/share/nginx/html:ro
      - db-data:/data
"""
        compose = ComposeBuilder.from_string(yaml_str)
        vols = compose.services["web"].volumes
        assert len(vols) == 2
        assert vols[0] == VolumeMount(
            type="bind", source="./html", target="/usr/share/nginx/html", read_only=True
        )
        assert vols[1] == VolumeMount(
            type="volume", source="db-data", target="/data"
        )

    def test_volumes_long_syntax(self):
        yaml_str = """
services:
  web:
    image: nginx
    volumes:
      - type: bind
        source: ./html
        target: /usr/share/nginx/html
        read_only: true
"""
        compose = ComposeBuilder.from_string(yaml_str)
        vols = compose.services["web"].volumes
        assert len(vols) == 1
        assert vols[0] == VolumeMount(
            type="bind", source="./html", target="/usr/share/nginx/html", read_only=True
        )

    def test_build_short_syntax(self):
        yaml_str = """
services:
  web:
    image: nginx
    build: .
"""
        compose = ComposeBuilder.from_string(yaml_str)
        build = compose.services["web"].build
        assert build == "."

    def test_build_long_syntax(self):
        yaml_str = """
services:
  web:
    image: nginx
    build:
      context: .
      dockerfile: Dockerfile
      target: prod
"""
        compose = ComposeBuilder.from_string(yaml_str)
        build = compose.services["web"].build
        assert build.context == "."
        assert build.dockerfile == "Dockerfile"
        assert build.target == "prod"

    def test_healthcheck(self):
        yaml_str = """
services:
  db:
    image: postgres
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5
      disable: false
"""
        compose = ComposeBuilder.from_string(yaml_str)
        hc = compose.services["db"].healthcheck
        assert hc.test == ["CMD", "pg_isready"]
        assert hc.interval == "10s"
        assert hc.timeout == "5s"
        assert hc.retries == 5

    def test_depends_on_short(self):
        yaml_str = """
services:
  web:
    image: nginx
    depends_on:
      - db
      - cache
  db:
    image: postgres
  cache:
    image: redis
"""
        compose = ComposeBuilder.from_string(yaml_str)
        deps = compose.services["web"].depends_on
        assert deps == ["db", "cache"]

    def test_depends_on_long(self):
        yaml_str = """
services:
  web:
    image: nginx
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
        required: false
"""
        compose = ComposeBuilder.from_string(yaml_str)
        deps = compose.services["web"].depends_on
        assert deps["db"].condition == "service_healthy"
        assert deps["cache"].condition == "service_started"
        assert deps["cache"].required is False

    def test_extra_hosts_dict(self):
        yaml_str = """
services:
  web:
    image: nginx
    extra_hosts:
      somehost: "162.242.195.82"
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert compose.services["web"].extra_hosts == {"somehost": "162.242.195.82"}

    def test_extra_hosts_list(self):
        yaml_str = """
services:
  web:
    image: nginx
    extra_hosts:
      - "somehost=162.242.195.82"
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert compose.services["web"].extra_hosts == {"somehost": "162.242.195.82"}

    def test_networks(self):
        yaml_str = """
services:
  web:
    image: nginx
    networks:
      - frontend
      - backend
"""
        compose = ComposeBuilder.from_string(yaml_str)
        nets = compose.services["web"].networks
        assert nets == ["frontend", "backend"]

    def test_networks_long(self):
        yaml_str = """
services:
  web:
    image: nginx
    networks:
      frontend:
        aliases:
          - alias1
        ipv4_address: 172.16.238.10
"""
        compose = ComposeBuilder.from_string(yaml_str)
        nets = compose.services["web"].networks
        assert "frontend" in nets
        assert nets["frontend"].aliases == ["alias1"]
        assert nets["frontend"].ipv4_address == "172.16.238.10"

    def test_top_level_networks(self):
        yaml_str = """
networks:
  frontend:
    driver: bridge
  backend:
    external: true
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert compose.networks["frontend"].driver == "bridge"
        assert compose.networks["backend"].external is True

    def test_top_level_volumes(self):
        yaml_str = """
volumes:
  db-data:
    driver: local
  shared:
    external:
      name: actual-name
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert compose.volumes["db-data"].driver == "local"
        assert compose.volumes["shared"].external == {"name": "actual-name"}

    def test_top_level_configs(self):
        yaml_str = """
configs:
  http_config:
    file: ./httpd.conf
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert compose.configs["http_config"].file == "./httpd.conf"

    def test_top_level_secrets(self):
        yaml_str = """
secrets:
  token:
    environment: "OAUTH_TOKEN"
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert compose.secrets["token"].environment == "OAUTH_TOKEN"

    def test_command_string(self):
        yaml_str = """
services:
  web:
    image: nginx
    command: nginx -g 'daemon off;'
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert compose.services["web"].command == "nginx -g 'daemon off;'"

    def test_command_list(self):
        yaml_str = """
services:
  web:
    image: nginx
    command: ["nginx", "-g", "daemon off;"]
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert compose.services["web"].command == ["nginx", "-g", "daemon off;"]

    def test_labels_dict(self):
        yaml_str = """
services:
  web:
    image: nginx
    labels:
      com.example.description: "Web server"
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert compose.services["web"].labels == {"com.example.description": "Web server"}

    def test_labels_list(self):
        yaml_str = """
services:
  web:
    image: nginx
    labels:
      - "com.example.description=Web server"
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert compose.services["web"].labels == {"com.example.description": "Web server"}

    def test_extensions_preserved(self):
        yaml_str = """
x-custom:
  foo: bar

services:
  web:
    image: nginx
    x-foo: bar
"""
        compose = ComposeBuilder.from_string(yaml_str)
        # Top-level x-* keys are preserved via extra="allow"
        assert "x-custom" in compose.model_extra
        assert compose.model_extra["x-custom"] == {"foo": "bar"}
        # Service-level x-* keys are preserved
        assert compose.services["web"].model_extra.get("x-foo") == "bar"
        assert compose.services["web"].image == "nginx"


    def test_empty_volume(self):
        yaml_str = """
volumes:
  frontend_build:
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert "frontend_build" in compose.volumes
        assert compose.volumes["frontend_build"].driver is None

    def test_empty_network(self):
        yaml_str = """
networks:
  frontend:
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert "frontend" in compose.networks
        assert compose.networks["frontend"].driver is None

    def test_empty_config(self):
        yaml_str = """
configs:
  my_config:
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert "my_config" in compose.configs
        assert compose.configs["my_config"].file is None

    def test_empty_secret(self):
        yaml_str = """
secrets:
  my_secret:
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert "my_secret" in compose.secrets
        assert compose.secrets["my_secret"].file is None

    def test_service_volume_references_empty_volume(self):
        yaml_str = """
services:
  web:
    image: nginx
    volumes:
      - frontend_build:/pwahub/frontend/build

volumes:
  frontend_build:
"""
        compose = ComposeBuilder.from_string(yaml_str)
        assert "frontend_build" in compose.volumes
        vol = compose.services["web"].volumes[0]
        assert vol.source == "frontend_build"
        assert vol.target == "/pwahub/frontend/build"


class TestFromFile:
    """Tests for ComposeBuilder.from_file()."""

    def test_from_file(self, tmp_path):
        compose_path = tmp_path / "docker-compose.yml"
        compose_path.write_text("""
services:
  web:
    image: nginx
""")
        compose = ComposeBuilder.from_file(compose_path)
        assert compose.services["web"].image == "nginx"


class TestFromDict:
    """Tests for ComposeBuilder.from_dict()."""

    def test_from_dict(self):
        data = {
            "services": {
                "web": {"image": "nginx"},
            },
        }
        compose = ComposeBuilder.from_dict(data)
        assert compose.services["web"].image == "nginx"
