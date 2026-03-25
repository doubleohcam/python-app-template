"""Copies Docker files into the new project."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from generator.config import ProjectConfig
    from generator.copier import TemplateCopier

DOCKER_COMMON = [
    "docker-compose.yml",
    "docker-setup/base/Dockerfile",
    "docker-setup/claude-dev/Dockerfile",
    "docker-setup/claude-dev/entrypoint.sh",
    "docker-setup/README.md",
]

DOCKER_DJANGO = [
    "docker-setup/django-runtime/Dockerfile",
    "docker-setup/nginx/Dockerfile",
    "docker-setup/nginx/nginx.conf",
    "docker-setup/logging/loki-config.yml",
    "docker-setup/logging/grafana-datasources.yml",
    "docker-setup/logging/README.md",
]


class DockerSetup:
    """Copies Docker configuration files."""

    def __init__(self, config: ProjectConfig, copier: TemplateCopier) -> None:
        """Initialize with config and copier."""
        self.config = config
        self.copier = copier

    def run(self) -> None:
        """Copy Docker files, including django-specific ones if applicable."""
        print("Copying Docker files...")  # noqa: T201
        self.copier.copy_file_list(DOCKER_COMMON)

        if self.config.is_django:
            self.copier.copy_file_list(DOCKER_DJANGO)
