"""Git initialization and initial commit."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from generator.config import ProjectConfig


class GitSetup:
    """Handles git init, remote configuration, and initial commit."""

    def __init__(self, config: ProjectConfig) -> None:
        """Initialize with project config."""
        self.config = config

    def init(self) -> None:
        """Initialize repo and connect to remote."""
        print("Setting up git...")  # noqa: T201
        self._run("git", "init")
        self._run("git", "remote", "add", "origin", self.config.repo_url)
        self._run("git", "pull", "origin", self.config.branch)

    def push_initial_commit(self) -> None:
        """Create and push an initial commit on a setup branch."""
        print("Pushing initial commit...")  # noqa: T201
        self._run("git", "checkout", "-b", "initial-setup")
        self._run("git", "add", ".")
        self._run("git", "commit", "-m", "[automated] Initial setup")
        self._run("git", "push", "--set-upstream", "origin", "initial-setup")

    def _run(self, *args: str) -> None:
        subprocess.run(args, cwd=self.config.dest_dir, check=True)  # noqa: S603
