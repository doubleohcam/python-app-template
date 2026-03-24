# Docker Setup

Build contexts and configuration files for the project's Docker infrastructure.

`docker-compose.yml` lives at the project root and loads `.env` natively.

## Directory Structure

```
docker-setup/
├── base/
│   └── Dockerfile              # Base Python image (shared by all containers)
├── claude-dev/
│   ├── Dockerfile              # Claude Code development environment
│   └── entrypoint.sh           # Git config, poetry install, home dir init
├── django-runtime/
│   └── Dockerfile              # Production Django image (multi-stage build)
├── nginx/
│   ├── Dockerfile              # Nginx reverse proxy
│   └── nginx.conf              # Nginx configuration
├── logging/
│   ├── loki-config.yml         # Loki log aggregation config
│   ├── grafana-datasources.yml # Grafana datasource provisioning
│   └── django_logging_config.py # Django logging config reference
└── README.md
```

## Commands

All orchestration uses native `docker compose` from the project root.

| Action | Command |
|--------|---------|
| Build base image | `docker compose build base` |
| Build all images | `docker compose build base && docker compose build` |
| Claude Code dev shell | `docker compose --profile dev run --rm claude-dev` |
| Bash in dev container | `docker compose --profile dev run --rm claude-dev /bin/bash` |
| Start Claude Code CLI | `docker compose --profile dev run --rm claude-dev claude` |
| Start PostgreSQL | `docker compose --profile db up -d` |
| Start runtime stack | `docker compose --profile runtime up -d` |
| Start logging stack | `docker compose --profile logging up -d` |
| Stop all services | `docker compose --profile dev --profile db --profile runtime --profile logging down` |
| Clean everything | `docker compose down -v --remove-orphans && docker image prune -f` |

## Profiles

| Profile | Services | Purpose |
|---------|----------|---------|
| `build` | base | Build-only base Python image |
| `dev` | claude-dev | Interactive dev environment with Claude CLI, Poetry, gh |
| `db` | postgres | PostgreSQL for local development |
| `runtime` | django-runtime, nginx | Production-like Django + Gunicorn behind Nginx |
| `logging` | loki, grafana | Log aggregation and search (http://localhost:3000) |

## Architecture

```
Browser :80
    │
    ▼
┌─────────────────┐
│     Nginx       │
│     (:80)       │
└────────┬────────┘
         │
    ┌────┴────┬─────────────┐
    │         │             │
    ▼         ▼             ▼
/static/   /media/     /* (everything else)
    │         │             │
    ▼         ▼             ▼
static-   media-      ┌─────────────────┐
files     files       │  Django/Gunicorn│
volume    volume      │     (:8000)     │
                      └────────┬────────┘
                               │
                      ┌────────┴────────┐
                      │                 │
                      ▼                 ▼
                  PostgreSQL         Loki
                   (:5432)          (:3100)
```

## Environment

All configuration is in `.env` at the project root. See `.env.template` for required variables.

## Security

| Feature | Description |
|---------|-------------|
| Non-root user | All containers run as `devuser` (UID 1000) |
| Read-only filesystem | Container root is immutable |
| Dropped capabilities | Minimal Linux capabilities |
| No privilege escalation | `no-new-privileges` enabled |
| Resource limits | CPU and memory limits on dev container |
| Network isolation | Containers communicate on isolated Docker network |
