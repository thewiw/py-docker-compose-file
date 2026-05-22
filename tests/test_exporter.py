"""Tests for the ComposeExporter."""

from __future__ import annotations

import yaml

from dockercomposefile import ComposeBuilder, ComposeExporter
from dockercomposefile.models import DockerComposeFile, Service


class TestToString:
    """Tests for ComposeExporter.to_string()."""

    def test_basic_export(self):
        compose = DockerComposeFile(
            services={"web": Service(image="nginx")},
        )
        yaml_str = ComposeExporter.to_string(compose)
        data = yaml.safe_load(yaml_str)
        assert data["services"]["web"]["image"] == "nginx"

    def test_omits_none_fields(self):
        compose = DockerComposeFile(
            services={"web": Service(image="nginx")},
        )
        yaml_str = ComposeExporter.to_string(compose)
        data = yaml.safe_load(yaml_str)
        assert "build" not in data["services"]["web"]
        assert "command" not in data["services"]["web"]

    def test_preserves_environment(self):
        compose = DockerComposeFile(
            services={
                "web": Service(
                    image="nginx",
                    environment={"DEBUG": "true"},
                ),
            },
        )
        yaml_str = ComposeExporter.to_string(compose)
        data = yaml.safe_load(yaml_str)
        assert data["services"]["web"]["environment"]["DEBUG"] == "true"

    def test_preserves_ports(self):
        compose = DockerComposeFile(
            services={
                "web": Service(
                    image="nginx",
                    ports=[{"target": 80, "published": "8080"}],
                ),
            },
        )
        yaml_str = ComposeExporter.to_string(compose)
        data = yaml.safe_load(yaml_str)
        assert data["services"]["web"]["ports"][0]["target"] == 80
        assert data["services"]["web"]["ports"][0]["published"] == "8080"

    def test_roundtrip_ports(self):
        yaml_str = """
services:
  web:
    image: nginx
    ports:
      - "80:80"
      - "127.0.0.1:8000:8000"
"""
        compose1 = ComposeBuilder.from_string(yaml_str)
        exported = ComposeExporter.to_string(compose1)
        compose2 = ComposeBuilder.from_string(exported)
        ports = compose2.services["web"].ports
        assert len(ports) == 2
        assert ports[0].target == 80
        assert ports[0].published == "80"
        assert ports[1].target == 8000
        assert ports[1].published == "8000"
        assert ports[1].host_ip == "127.0.0.1"


class TestToFile:
    """Tests for ComposeExporter.to_file()."""

    def test_to_file(self, tmp_path):
        compose = DockerComposeFile(
            services={"web": Service(image="nginx")},
        )
        path = tmp_path / "docker-compose.yml"
        ComposeExporter.to_file(compose, path)
        data = yaml.safe_load(path.read_text())
        assert data["services"]["web"]["image"] == "nginx"


class TestToDict:
    """Tests for ComposeExporter.to_dict()."""

    def test_to_dict(self):
        compose = DockerComposeFile(
            services={"web": Service(image="nginx")},
        )
        data = ComposeExporter.to_dict(compose)
        assert data["services"]["web"]["image"] == "nginx"
        assert "build" not in data["services"]["web"]
