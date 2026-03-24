"""Copies .github files, configures dependabot and workflows."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from generator.copier import TEMPLATE_DIR

if TYPE_CHECKING:
    from generator.config import ProjectConfig
    from generator.copier import TemplateCopier

GITHUB_COMMON = [
    ".github/ISSUE_TEMPLATE/batch.md",
    ".github/ISSUE_TEMPLATE/epic.md",
    ".github/ISSUE_TEMPLATE/initiative.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/README.md",
    ".github/workflows/lint.yml",
    ".github/workflows/test.yml",
]

GITHUB_DJANGO = [
    ".github/workflows/migrations.yml",
]


class GitHubSetup:
    """Copies GitHub config files with conditional django support."""

    def __init__(self, config: ProjectConfig, copier: TemplateCopier) -> None:
        """Initialize with config and copier."""
        self.config = config
        self.copier = copier

    def run(self) -> None:
        """Copy GitHub files, write dependabot, and replace workflow variables."""
        print("Copying GitHub files...")  # noqa: T201
        self.copier.copy_file_list(GITHUB_COMMON)

        if self.config.is_django:
            self.copier.copy_file_list(GITHUB_DJANGO)

        self.write_dependabot()

    def write_dependabot(self) -> None:
        """Write dependabot.yml, removing django-runtime entry for non-django projects."""
        src = TEMPLATE_DIR / ".github" / "dependabot.yml"
        content = src.read_text()

        if not self.config.is_django:
            pattern = (
                r"\n  - package-ecosystem: \"docker\""
                r"\n    directory: \"/docker-setup/django-runtime\""
                r".*?(?=\n  - |\Z)"
            )
            content = re.sub(pattern, "", content, flags=re.DOTALL)

        dest = self.config.dest_dir / ".github" / "dependabot.yml"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(self.copier.replace_vars(content))
