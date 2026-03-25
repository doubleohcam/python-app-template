# python-app-template

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A project generator that scaffolds new Python and Django applications with opinionated tooling, Docker infrastructure, CI, and scripts.

## Quick Start

### Generate a new project

```bash
script/setup_new_app
```

This will prompt you for a project name and configuration, then generate a new app with:

- Python project structure with Poetry, Ruff, pytest, pre-commit
- Docker Compose setup (dev container, optional PostgreSQL, runtime, logging)
- GitHub Actions CI (lint, test, optional migration checks)
- `.env` / `.env.template` configuration
- **Django mode** (optional): app skeleton, settings module, models directory, scripts, Gunicorn/Nginx runtime

### Development with Claude Code (Docker)

```bash
script/claude
```

This builds images on first run and starts the dev container with Claude Code CLI, Poetry, GitHub CLI, and all dev tools. The workspace is mounted at `/workspace`.

To force rebuild after Dockerfile changes:

```bash
docker compose build base && docker compose build --no-cache claude-dev
```

### Local development (no Docker)

```bash
script/bootstrap
```

### Run tests

```bash
script/test
```

### Lint

```bash
script/lint
```

## Configuration

Claude Code settings live in `.claude/settings.json`:

- **Model**: set to `"opus"` (always latest Opus)
- **Planning mode**: enabled by default
- **Plugins**: declared in `enabledPlugins`

Personal overrides go in `.claude/settings.local.json` (gitignored).

## Repo Structure

```
generator/          Python generator (the tool itself)
templates/          Everything that gets copied into new projects
script/             Dev scripts for this repo
docker-setup/       Docker build contexts (base image, claude-dev)
.claude/            Claude Code project settings
```

See `CLAUDE.md` for detailed documentation, `preferences.md` for design decisions.
