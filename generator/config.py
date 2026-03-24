"""Project configuration derived from user input."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProjectConfig:
    """All user-provided parameters and derived template variables."""

    raw_name: str
    dest_parent: str
    is_django: bool = False
    run_bootstrap: bool = True
    is_git: bool = False
    repo_url: str = ""
    branch: str = "main"
    push_initial_commit: bool = False

    # Derived
    app_name: str = field(init=False)
    app_name_pretty: str = field(init=False)
    app_name_config: str = field(init=False)
    dest_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        """Derive template variables from raw_name."""
        self.app_name = re.sub(r"[-\s]+", "_", self.raw_name.strip()).lower()
        self.app_name_pretty = " ".join(word.capitalize() for word in self.app_name.split("_"))
        self.app_name_config = self.app_name_pretty.replace(" ", "") + "Config"
        self.dest_dir = Path(self.dest_parent).resolve() / self.app_name

    @property
    def template_vars(self) -> dict[str, str]:
        """Mapping of placeholder strings to their replacements."""
        return {
            "{app_name}": self.app_name,
            "{app_name_pretty}": self.app_name_pretty,
            "{app_name_config}": self.app_name_config,
        }

    def summary(self) -> str:
        """Human-readable summary of the configuration."""
        lines = [
            f"  App name:    {self.app_name}",
            f"  Pretty name: {self.app_name_pretty}",
            f"  Destination: {self.dest_dir}",
            f"  Django:      {self.is_django}",
            f"  Git:         {self.is_git}",
        ]
        return "\n".join(lines)


def collect_config() -> ProjectConfig:
    """Prompt the user and return a fully populated ProjectConfig."""
    print("Welcome to the setup script!\n")  # noqa: T201

    dest_parent = _prompt("Path for the new app directory (eg. 'path/to/dir')")
    raw_name = _prompt("Name of the new app (eg. 'my-app')")
    is_django = _prompt_yn("Is this a Django app?")
    run_bootstrap = _prompt_yn("Run bootstrap after setup?", default=True)

    is_git = _prompt_yn("Should this be a git repository?")
    repo_url = ""
    branch = "main"
    push = False
    if is_git:
        repo_url = _prompt("Git repository URL")
        branch = _prompt("Main branch name", default="main")
        push = _prompt_yn("Push an initial commit?")

    return ProjectConfig(
        raw_name=raw_name,
        dest_parent=dest_parent,
        is_django=is_django,
        run_bootstrap=run_bootstrap,
        is_git=is_git,
        repo_url=repo_url,
        branch=branch,
        push_initial_commit=push,
    )


def _prompt(message: str, default: str = "") -> str:
    suffix = f" (default: {default})" if default else ""
    result = input(f"> {message}{suffix}: ").strip()
    return result if result else default


def _prompt_yn(message: str, *, default: bool = False) -> bool:
    hint = "Y/n" if default else "y/N"
    result = input(f"> {message} ({hint}): ").strip().lower()
    if not result:
        return default
    return result == "y"
