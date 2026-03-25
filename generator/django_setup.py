"""Copies Django app files and writes environment configuration."""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from generator.copier import TEMPLATE_DIR

if TYPE_CHECKING:
    from generator.config import ProjectConfig
    from generator.copier import TemplateCopier


class DjangoSetup:
    """Copies django_files/ template and configures .env with django values."""

    def __init__(self, config: ProjectConfig, copier: TemplateCopier) -> None:
        """Initialize with config and copier."""
        self.config = config
        self.copier = copier

    def run(self) -> None:
        """Copy Django app skeleton into {app_name}/."""
        print("Copying Django app files...")  # noqa: T201
        django_src = TEMPLATE_DIR / "django_files"
        django_dest = self.config.dest_dir / self.config.app_name
        self.copier.copy_tree(django_src, django_dest)


class EnvSetup:
    """Writes .env and .env.template for the new project."""

    def __init__(self, config: ProjectConfig, copier: TemplateCopier) -> None:
        """Initialize with config and copier."""
        self.config = config
        self.copier = copier

    def run(self) -> None:
        """Create .env.template (clean reference) and .env (with populated values)."""
        print("Writing .env and .env.template...")  # noqa: T201
        src = TEMPLATE_DIR / ".env.template"
        template_content = self.copier.replace_vars(src.read_text())

        (self.config.dest_dir / ".env.template").write_text(template_content)

        env_content = template_content
        if self.config.is_django:
            env_content = env_content.replace(
                "DJANGO_SECRET_KEY=",
                f"DJANGO_SECRET_KEY={secrets.token_urlsafe(50)}",
            )
            env_content = env_content.replace(
                "GUNICORN_WSGI_MODULE=",
                f"GUNICORN_WSGI_MODULE={self.config.app_name}.wsgi:application",
            )
            env_content = env_content.replace(
                "DJANGO_SETTINGS_MODULE=",
                f"DJANGO_SETTINGS_MODULE={self.config.app_name}.settings.dev",
            )

        (self.config.dest_dir / ".env").write_text(env_content)
