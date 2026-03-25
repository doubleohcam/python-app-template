"""Low-level file copying with template variable replacement."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from generator.config import ProjectConfig

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


class TemplateCopier:
    """Copies files from the template repo to a destination, replacing template variables."""

    def __init__(self, config: ProjectConfig) -> None:
        """Initialize with a ProjectConfig supplying template variables and destination."""
        self.config = config

    def copy_file(self, src: Path, dest: Path) -> None:
        """Copy a single file, replacing template variables in text files."""
        dest.parent.mkdir(parents=True, exist_ok=True)

        try:
            content = src.read_text()
        except UnicodeDecodeError:
            shutil.copy2(src, dest)
            return

        dest.write_text(self.replace_vars(content))

    def copy_file_list(
        self,
        file_list: list[str],
        *,
        src_prefix: str = "",
        dest_prefix: str = "",
    ) -> None:
        """Copy a list of repo-relative paths to the destination directory."""
        for rel_path in file_list:
            src = TEMPLATE_DIR / rel_path

            if not src.exists():
                print(f"  WARNING: {rel_path} not found, skipping")  # noqa: T201
                continue

            if dest_prefix and src_prefix:
                out_path = rel_path.replace(src_prefix, dest_prefix, 1)
            else:
                out_path = rel_path

            self.copy_file(src, self.config.dest_dir / out_path)

    def copy_tree(self, src_dir: Path, dest_dir: Path) -> None:
        """Recursively copy a directory, replacing template variables in all text files."""
        for src_path in src_dir.rglob("*"):
            if src_path.is_dir():
                continue
            rel = src_path.relative_to(src_dir)
            self.copy_file(src_path, dest_dir / rel)

    def replace_vars(self, content: str) -> str:
        """Replace all template variables in a string."""
        for placeholder, value in self.config.template_vars.items():
            content = content.replace(placeholder, value)
        return content
