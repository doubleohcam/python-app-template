# CLAUDE.md

You are a senior software developer. Use best practices for code, patterns, and infrastructure. Be concise. Don't over-engineer.

## What This Repo Is

A project generator that scaffolds new Python applications (plain or Django) with opinionated tooling, Docker infrastructure, CI, and scripts — all configured to a personal standard. This is not a library; it is a template repo. The code here is copied into new projects.

Run `script/setup_new_app` to generate a new project.

## Key Concepts

**Two modes:** The generator asks if this is a Django app. If yes, it includes Django files, scripts, docker services (runtime, nginx), and CI workflows. If no, it includes only the Python/Docker/CI essentials.

**Template variables:** Three placeholders are replaced throughout all generated files (content and filenames):
- `{app_name}` — snake_case (e.g. `dynamic_journal`)
- `{app_name_pretty}` — Title Case (e.g. `Dynamic Journal`)
- `{app_name_config}` — PascalCase + Config (e.g. `DynamicJournalConfig`)

All three are derived from a single user input like "dynamic-journal".

**Single source of truth for bootstrap:** `script/bootstrap` is called everywhere — Docker entrypoints, CI workflows, local setup. Never duplicate its logic.

**Single `.env`:** One `.env` file at project root, one `.env.template` as reference. No `.env.example`, no per-service env files. Docker Compose loads `.env` natively.

## Repo Structure

```
generator/                  # Python generator (the tool itself)
  config.py                 # ProjectConfig dataclass + user prompts
  copier.py                 # TemplateCopier — file copy with var replacement
  project_files.py          # Common files, scripts, pyproject.toml setup
  docker_setup.py           # Docker file copying
  github_setup.py           # .github files, dependabot, workflows
  django_setup.py           # Django app files + .env setup
  git_setup.py              # Git init, remote, initial commit
  setup.py                  # Entry point — wires classes together

templates/                  # Everything that gets copied into new projects
  django_files/             # Django app skeleton (copied into {app_name}/)
    __init__.py
    apps.py                 # AppConfig using {app_name_config}
    logging.py              # LoggingConfig class (standard + production)
    manage.py               # Placed at project root during generation
    urls.py                 # Includes /health/ endpoint
    wsgi.py
    models/
      __init__.py           # Imports BaseModel
      base_model.py         # Abstract base: DirtyFieldsMixin + auto_prefetch
    migrations/__init__.py
    settings/
      __init__.py
      base.py               # Shared settings, uses django-environ
      dev.py                # DEBUG=True
      prod.py               # Loki logging, security headers
      test.py               # SQLite in-memory, no env vars needed
  script/                   # Shared scripts (copied to all projects)
    bootstrap               # Single source of truth for env setup
    bootstrap_python        # Poetry install
    lint, pre-commit, test  # Dev tooling
    django/                 # Django-only scripts (flattened into script/ during generation)
      runserver             # Checks migrations, starts gunicorn or dev server
      migrate, makemigrations, check_migrations, check_migrate_needed, collectstatic
  docker-compose.yml        # At project root. Profiles: dev, db, runtime, logging
  docker-setup/             # Build contexts only (Dockerfiles, nginx.conf, loki config)
    base/Dockerfile         # Base Python image (compose build-only service)
    claude-dev/             # Dev container with Claude CLI, Poetry, gh
    django-runtime/         # Multi-stage production Django image
    nginx/                  # Reverse proxy + static files
    logging/                # Loki + Grafana config
  .github/                  # CI workflows + dependabot (copied to new projects)
  .env.template             # Reference for all env vars
  .pre-commit-config.yaml   # Pre-commit hooks config
  .gitignore                # Standard Python gitignore
  pyproject.toml            # Base pyproject.toml (Django deps added during generation)
  wordlist.txt              # Custom spellcheck dictionary

script/setup_new_app        # Entry point — runs the generator (stays at repo root)
preferences.md              # Design decisions and coding standards
todos.md                    # Current task tracking
```

## Code Style

- `from __future__ import annotations` in all Python files
- `ClassVar` for class-level type hints
- Verbose docstrings on classes and Meta classes
- Ruff for linting and formatting (see `pyproject.toml` for rule config)
- Poetry for dependency management, virtualenvs in-project
- All scripts use `poetry run python` — Poetry is always available, including in Docker runtime

## Django Conventions

- Settings are a module (`settings/base.py`, `dev.py`, `prod.py`, `test.py`), not a single file
- Models directory instead of `models.py` — every model imported in `__init__.py`
- All models inherit from `BaseModel` (auto_prefetch + DirtyFieldsMixin, created_at/updated_at)
- `manage.py` at project root, not nested
- Logging config lives in `{app_name}/logging.py` as a `LoggingConfig` class with `standard` and `production` classproperties. Settings import it.
- `/health/` endpoint is required (Docker healthchecks depend on it)

## Docker

- No wrapper scripts. Native `docker compose` commands only.
- `docker compose --profile dev run --rm claude-dev` for dev
- `docker compose --profile runtime up -d` for production-like stack
- Security hardened: drop all caps, no-new-privileges, read-only root, resource limits
- All project-specific values from `.env` via `${COMPOSE_PROJECT_NAME}` interpolation
- `script/bootstrap` is called by both the claude-dev entrypoint and django-runtime CMD

## Important Files

- `preferences.md` — Design decisions. Read this before making architectural choices.
- `todos.md` — Current state of work. Check before starting new tasks.
- `generator/config.py` — `ProjectConfig` dataclass. All template variables derived here.
- `generator/copier.py` — `TemplateCopier`. All file copying goes through this.
- `templates/django_files/settings/base.py` — The base Django settings template. Most config lives here.
- `templates/django_files/logging.py` — `LoggingConfig` with shared formatters and logger definitions.
- `script/bootstrap` — Called everywhere. Never bypass or duplicate.
