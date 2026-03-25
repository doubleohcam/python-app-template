"""Shared fixtures for the generator test suite.

All writes go to pytest's tmp_path (ephemeral, per-test temp directory).
Reads from templates/ are intentional — we test real template content.
"""

import pytest

from generator.config import ProjectConfig
from generator.copier import TemplateCopier

# ─────────────────────────────────────────────────────────────
# ProjectConfig variants — dest_dir always lives in tmp_path
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def dest_dir(tmp_path):
    """Parent directory for generated output — lives in tmp_path."""
    d = tmp_path / "generated"
    d.mkdir()
    return d


@pytest.fixture
def plain_config(dest_dir):
    """ProjectConfig for a plain (non-Django) Python project."""
    return ProjectConfig(
        raw_name="my-cool-app",
        dest_parent=str(dest_dir),
        is_django=False,
    )


@pytest.fixture
def django_config(dest_dir):
    """ProjectConfig for a Django project."""
    return ProjectConfig(
        raw_name="my-cool-app",
        dest_parent=str(dest_dir),
        is_django=True,
    )


@pytest.fixture
def git_config(dest_dir):
    """ProjectConfig with git enabled."""
    return ProjectConfig(
        raw_name="my-cool-app",
        dest_parent=str(dest_dir),
        is_git=True,
        repo_url="https://github.com/user/my-cool-app.git",
        branch="main",
        push_initial_commit=False,
    )


# ─────────────────────────────────────────────────────────────
# TemplateCopier instances — read real templates, write to tmp_path
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def copier(plain_config):
    """TemplateCopier wired to the plain config."""
    return TemplateCopier(plain_config)


@pytest.fixture
def django_copier(django_config):
    """TemplateCopier wired to the Django config."""
    return TemplateCopier(django_config)
