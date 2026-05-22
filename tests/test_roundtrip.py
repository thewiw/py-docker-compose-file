"""Round-trip tests: parse YAML -> export YAML -> parse again."""

from __future__ import annotations

from dockercomposefile import ComposeBuilder, ComposeExporter


FULL_COMPOSE = """
name: my-app

services:
  frontend:
    image: nginx:alpine
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: prod
    command: ["nginx", "-g", "daemon off;"]
    environment:
      NODE_ENV: production
      API_URL: http://api:8080
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./frontend/html:/usr/share/nginx/html:ro
    depends_on:
      api:
        condition: service_started
    networks:
      - frontend
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    labels:
      com.example.service: frontend
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.50'
          memory: 128M

  api:
    image: myapp/api:latest
    environment:
      - DB_HOST=db
      - DB_PORT=5432
    ports:
      - target: 8080
        published: "8080"
        protocol: tcp
    depends_on:
      db:
        condition: service_healthy
    networks:
      backend:
        aliases:
          - api-service
    secrets:
      - db_password
    configs:
      - source: app_config
        target: /app/config.yml
    healthcheck:
      test: curl -f http://localhost:8080/health || exit 1
      interval: 10s
      timeout: 5s
      retries: 5
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - type: volume
        source: db-data
        target: /var/lib/postgresql/data
    networks:
      - backend
    secrets:
      - db_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true

volumes:
  db-data:
    driver: local

secrets:
  db_password:
    file: ./secrets/db_password.txt

configs:
  app_config:
    file: ./config/app.yml
"""


class TestRoundtrip:
    """End-to-end round-trip tests."""

    def test_full_compose_roundtrip(self):
        compose1 = ComposeBuilder.from_string(FULL_COMPOSE)

        # Export
        exported = ComposeExporter.to_string(compose1)

        # Re-parse
        compose2 = ComposeBuilder.from_string(exported)

        # Verify services
        assert set(compose2.services.keys()) == {"frontend", "api", "db"}

        # Frontend
        fe = compose2.services["frontend"]
        assert fe.image == "nginx:alpine"
        assert fe.build.context == "./frontend"
        assert fe.build.dockerfile == "Dockerfile"
        assert fe.build.target == "prod"
        assert fe.command == ["nginx", "-g", "daemon off;"]
        assert fe.environment == {
            "NODE_ENV": "production",
            "API_URL": "http://api:8080",
        }
        assert len(fe.ports) == 2
        assert fe.ports[0].target == 80
        assert fe.ports[0].published == "80"
        assert fe.ports[1].target == 443
        assert fe.ports[1].published == "443"
        assert len(fe.volumes) == 1
        assert fe.volumes[0].type == "bind"
        assert fe.volumes[0].source == "./frontend/html"
        assert fe.volumes[0].target == "/usr/share/nginx/html"
        assert fe.volumes[0].read_only is True
        assert fe.depends_on["api"].condition == "service_started"
        assert fe.healthcheck.test == ["CMD", "curl", "-f", "http://localhost"]
        assert fe.healthcheck.interval == "30s"
        assert fe.healthcheck.timeout == "10s"
        assert fe.healthcheck.retries == 3
        assert fe.restart == "unless-stopped"
        assert fe.labels == {"com.example.service": "frontend"}
        assert fe.deploy.replicas == 2
        assert fe.deploy.resources.limits.cpus == "0.50"
        assert fe.deploy.resources.limits.memory == "128M"

        # API
        api = compose2.services["api"]
        assert api.image == "myapp/api:latest"
        assert api.environment == {"DB_HOST": "db", "DB_PORT": "5432"}
        assert api.ports[0].target == 8080
        assert api.ports[0].published == "8080"
        assert api.ports[0].protocol == "tcp"
        assert api.depends_on["db"].condition == "service_healthy"
        assert api.networks["backend"].aliases == ["api-service"]
        assert api.secrets == ["db_password"]
        assert api.configs[0].source == "app_config"
        assert api.configs[0].target == "/app/config.yml"
        assert api.healthcheck.test == "curl -f http://localhost:8080/health || exit 1"
        assert api.logging.driver == "json-file"
        assert api.logging.options == {"max-size": "10m", "max-file": "3"}

        # DB
        db = compose2.services["db"]
        assert db.image == "postgres:15"
        assert db.environment["POSTGRES_DB"] == "myapp"
        assert db.environment["POSTGRES_USER"] == "appuser"
        assert db.volumes[0].type == "volume"
        assert db.volumes[0].source == "db-data"
        assert db.volumes[0].target == "/var/lib/postgresql/data"
        assert db.secrets == ["db_password"]
        assert db.healthcheck.test == ["CMD-SHELL", "pg_isready -U appuser -d myapp"]
        assert db.healthcheck.start_period == "30s"

        # Networks
        assert compose2.networks["frontend"].driver == "bridge"
        assert compose2.networks["backend"].driver == "bridge"
        assert compose2.networks["backend"].internal is True

        # Volumes
        assert compose2.volumes["db-data"].driver == "local"

        # Secrets
        assert compose2.secrets["db_password"].file == "./secrets/db_password.txt"

        # Configs
        assert compose2.configs["app_config"].file == "./config/app.yml"

    def test_empty_compose(self):
        compose1 = ComposeBuilder.from_string("")
        exported = ComposeExporter.to_string(compose1)
        compose2 = ComposeBuilder.from_string(exported)
        assert compose2.services is None or compose2.services == {}
