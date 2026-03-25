## Docker

- [x] move `docker-compose.yml` to project root (native `.env` loading, no wrapper script needed)
- [x] restructure `docker-setup/` into build contexts only (Dockerfiles, nginx.conf, loki config, etc.)
- [x] delete `dev.sh` — all orchestration via native `docker compose` commands
- [x] merge `entrypoint.sh` and `bootstrap.sh` into a single entrypoint
- [x] add base image as a build-only service in `docker-compose.yml` (no manual `docker build` step)
- [x] remove hardcoded "dynamic_journal" from django-runtime Dockerfile
- [x] replace all `{app-name}` references with env var interpolation (`${COMPOSE_PROJECT_NAME}`)
- [x] single `.env` at project root (loaded natively by compose), `.env.template` as the reference
- [x] document native compose commands in README (replaces dev.sh help text)

## Django App Template

- [x] create django app template directory (the skeleton files that get copied during generation)
  - [x] `{app_name}/settings/base.py`, `dev.py`, `prod.py`, `test.py`, `__init__.py`
  - [x] `{app_name}/urls.py` with `/health/` endpoint pre-wired
  - [x] `{app_name}/wsgi.py` wired to `{app_name}.wsgi:application`
  - [x] `{app_name}/models/` directory with `__init__.py` and `base_model.py`
  - [x] `{app_name}/apps.py` with `{app_name_config}` AppConfig
  - [x] `{app_name}/logging.py` with `LoggingConfig` (standard + production)
  - [x] `{app_name}/__init__.py`
  - [x] `{app_name}/migrations/__init__.py`
  - [x] `manage.py` at project root
  - [x] `script/django/*` (runserver, migrate, check_migrations, check_migrate_needed, collectstatic, makemigrations)
  - [x] `.env.template` with required keys
  - [x] delete old template files (`django-settings/`, `base_model.py` at root, `docker_logging_config.py`)

## Generator

- [x] python-based generator in `generator/` package
  - [x] `ProjectConfig` dataclass with derived template variables
  - [x] `TemplateCopier` for file copy with variable replacement
  - [x] `ProjectFilesSetup` — common files, scripts, pyproject.toml
  - [x] `DockerSetup` — Docker files, conditional django-runtime/nginx
  - [x] `GitHubSetup` — .github files, dependabot, workflow variable replacement
  - [x] `DjangoSetup` — Django app skeleton into `{app_name}/`
  - [x] `EnvSetup` — .env and .env.template, DJANGO_SECRET_KEY generation
  - [x] `GitSetup` — git init, remote, initial commit/push
  - [x] `setup.py` entry point wiring all classes together
  - [x] `setup_new_app` reduced to one-liner calling Python generator

## Repo Organization

- [x] move all template files into `/templates/` (clean separation of generator vs template)
- [x] update generator code to reference `templates/` directory
- [x] update CLAUDE.md to reflect new structure
- [ ] docker-compose.yml: strip django-specific services for non-django projects (low priority — profiles already isolate them)
