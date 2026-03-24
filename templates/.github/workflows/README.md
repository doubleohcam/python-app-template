# GitHub Actions Workflows

This directory contains CI/CD workflows that run on push and pull requests to the `main` branch.

## Workflows Overview

| Workflow | File | Purpose |
|----------|------|---------|
| Tests | `test.yml` | Run the test suite with coverage |
| Lint | `lint.yml` | Check code quality and formatting |
| Migrations | `migrations.yml` | Verify database migrations |
| Dependabot | `../dependabot.yml` | Automated dependency updates |

## Workflow Details

### Tests (`test.yml`)

Runs the full test suite using pytest.

**Triggers:** Push/PR to `main`

**What it does:**
- Sets up Python 3.12 and Poetry
- Installs dependencies via `script/bootstrap`
- Runs `script/test --ci --coverage`
- Generates coverage reports (HTML and XML)
- Uploads test results and coverage as artifacts

**What it catches:**
- Failing tests
- Code that doesn't meet coverage thresholds
- Regressions in functionality

### Lint (`lint.yml`)

Checks code quality and formatting standards.

**Triggers:** Push/PR to `main`

**What it does:**
- Runs `ruff check` with GitHub-formatted output
- Runs `ruff format --check` to verify formatting

**What it catches:**
- Linting violations (style, complexity, potential bugs)
- Code formatting inconsistencies
- Import ordering issues

### Migrations (`migrations.yml`)

Verifies database migrations are complete and valid.

**Triggers:** Push/PR to `main`

**Jobs:**

#### 1. `check-migrations-created`
Ensures all model changes have corresponding migration files.

- Uses SQLite (no database service needed)
- Runs `script/check_migrations`
- Fails if `makemigrations` would generate new files

**What it catches:**
- Model changes without migrations
- Forgotten migration files

#### 2. `apply-migrations`
Verifies migrations can be applied to a fresh PostgreSQL database.

- Spins up PostgreSQL 16 service container
- Runs `script/migrate` against a clean database
- Fails if any migration errors occur

**What it catches:**
- Migration syntax errors
- Migration conflicts
- PostgreSQL-specific issues (that SQLite might miss)
- Data migration bugs

## Local Equivalents

These workflows mirror the pre-commit hooks. To run the same checks locally:

| Workflow | Local Command |
|----------|---------------|
| Tests | `script/test` |
| Lint | `script/lint` or `poetry run ruff check .` |
| Migration check | `script/check_migrations` |
| Migration apply | `script/migrate` |

### Dependabot (`../dependabot.yml`)

Automated dependency updates via GitHub's Dependabot.

**Schedule:** Weekly on Mondays at 9:00 AM ET

**What it monitors:**

| Ecosystem | Directory | Labels |
|-----------|-----------|--------|
| Python (pip/Poetry) | `/` | `dependencies`, `python` |
| GitHub Actions | `/` | `dependencies`, `github-actions` |
| Docker | `/docker-setup/base` | `dependencies`, `docker` |
| Docker | `/docker-setup/django-runtime` | `dependencies`, `docker` |

**Features:**
- Groups minor and patch Python updates to reduce PR noise
- Adds appropriate labels for filtering
- Auto-assigns reviewers
- Commit message prefixes: `deps:`, `ci:`, `docker:`

**What it catches:**
- Outdated dependencies with known vulnerabilities
- New versions of packages
- Security updates

## Adding New Workflows

When adding new workflows:

1. Create a new `.yml` file in this directory
2. Follow the existing patterns for setup (Python, Poetry, caching)
3. Use `script/bootstrap` for dependency installation
4. Update this README with the new workflow details
