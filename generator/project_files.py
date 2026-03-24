"""Copies common project files, scripts, and updates pyproject.toml."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from generator.config import ProjectConfig
    from generator.copier import TemplateCopier

COMMON_FILES = [
    ".gitignore",
    ".pre-commit-config.yaml",
    "pyproject.toml",
    "wordlist.txt",
]

COMMON_SCRIPTS = [
    "script/bootstrap",
    "script/bootstrap_python",
    "script/claude",
    "script/lint",
    "script/pre-commit",
    "script/add_to_wordlist",
    "script/sort_wordlist",
    "script/update_all_the_things",
    "script/test",
]

DJANGO_SCRIPTS = [
    "script/django/runserver",
    "script/django/migrate",
    "script/django/check_migrations",
    "script/django/check_migrate_needed",
    "script/django/collectstatic",
    "script/django/makemigrations",
]


class ProjectFilesSetup:
    """Copies common files, scripts, and configures pyproject.toml."""

    def __init__(self, config: ProjectConfig, copier: TemplateCopier) -> None:
        """Initialize with config and copier."""
        self.config = config
        self.copier = copier

    def run(self) -> None:
        """Copy common files and scripts, then update pyproject.toml."""
        print("Copying common files...")  # noqa: T201
        self.copier.copy_file_list(COMMON_FILES)

        print("Copying scripts...")  # noqa: T201
        self.copier.copy_file_list(COMMON_SCRIPTS)

        if self.config.is_django:
            print("Copying Django scripts...")  # noqa: T201
            self.copier.copy_file_list(
                DJANGO_SCRIPTS,
                src_prefix="script/django/",
                dest_prefix="script/",
            )

        self.update_pyproject()

    def update_pyproject(self) -> None:
        """Update pyproject.toml with project name and django deps if needed."""
        print("Updating pyproject.toml...")  # noqa: T201
        pyproject = self.config.dest_dir / "pyproject.toml"
        content = pyproject.read_text()

        content = content.replace(
            'name = "python_app_template"',
            f'name = "{self.config.app_name}"',
        )

        if self.config.is_django:
            django_deps = (
                "\n"
                "# Django\n"
                'django = "*"\n'
                'django-environ = "*"\n'
                'django-extensions = "*"\n'
                'django-pghistory = "*"\n'
                'gunicorn = "*"\n'
                'psycopg2-binary = "*"\n'
                "# Django utilities\n"
                'auto-prefetch = "*"\n'
                'django-dirtyfields = "*"\n'
                "# Logging\n"
                'python-json-logger = "*"\n'
                'python-logging-loki = "*"\n'
            )
            content = content.replace(
                "[tool.poetry.group.dev.dependencies]",
                f"{django_deps}\n[tool.poetry.group.dev.dependencies]",
            )

            content = content.replace(
                'addopts = "--cov=$project',
                f'addopts = "--cov={self.config.app_name}',
            )

        content = self.copier.replace_vars(content)
        pyproject.write_text(content)
