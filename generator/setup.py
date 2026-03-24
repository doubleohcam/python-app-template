"""Entry point for the project generator."""

from __future__ import annotations

import subprocess

from generator.config import ProjectConfig, collect_config
from generator.copier import TemplateCopier
from generator.django_setup import DjangoSetup, EnvSetup
from generator.docker_setup import DockerSetup
from generator.git_setup import GitSetup
from generator.github_setup import GitHubSetup
from generator.project_files import ProjectFilesSetup


def generate(config: ProjectConfig) -> None:
    """Run the full generation pipeline from a config."""
    print(f"\nSetting up: {config.app_name_pretty}")  # noqa: T201
    print(config.summary())  # noqa: T201
    print()  # noqa: T201

    config.dest_dir.mkdir(parents=True, exist_ok=True)

    copier = TemplateCopier(config)

    if config.is_git:
        GitSetup(config).init()

    ProjectFilesSetup(config, copier).run()
    DockerSetup(config, copier).run()
    GitHubSetup(config, copier).run()
    EnvSetup(config, copier).run()

    if config.is_django:
        DjangoSetup(config, copier).run()

    if config.run_bootstrap:
        print("Running bootstrap...")  # noqa: T201
        subprocess.run(["./script/bootstrap"], cwd=config.dest_dir, check=True)

    if config.is_git and config.push_initial_commit:
        GitSetup(config).push_initial_commit()

    print(f"\nSetup complete! New app at: {config.dest_dir}")  # noqa: T201


def main() -> None:
    """Collect user input and run the generator."""
    config = collect_config()
    generate(config)


if __name__ == "__main__":
    main()
