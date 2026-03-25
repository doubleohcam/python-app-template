"""Tests for generator.setup — the generate() orchestration function.

All setup classes and subprocess are mocked. The only real filesystem
operation is config.dest_dir.mkdir() which writes to tmp_path.
"""

from unittest.mock import DEFAULT, patch

from generator.config import ProjectConfig
from generator.setup import generate


class TestGenerate:
    """Verify generate() calls the right setup classes conditionally."""

    def _run_generate(self, config):
        """Run generate() with all setup classes mocked, return the mocks."""
        with patch.multiple(
            "generator.setup",
            GitSetup=DEFAULT,
            ProjectFilesSetup=DEFAULT,
            DockerSetup=DEFAULT,
            GitHubSetup=DEFAULT,
            EnvSetup=DEFAULT,
            DjangoSetup=DEFAULT,
            subprocess=DEFAULT,
        ) as mocks:
            generate(config)
            return mocks

    def test_creates_dest_dir(self, plain_config):
        """Verify generate() creates the destination directory before running setup classes."""
        self._run_generate(plain_config)
        assert plain_config.dest_dir.exists()

    def test_always_runs_core_setup_classes(self, plain_config):
        """Verify generate() always calls run() on all four core setup classes."""
        mocks = self._run_generate(plain_config)
        mocks["ProjectFilesSetup"].return_value.run.assert_called_once()
        mocks["DockerSetup"].return_value.run.assert_called_once()
        mocks["GitHubSetup"].return_value.run.assert_called_once()
        mocks["EnvSetup"].return_value.run.assert_called_once()

    def test_plain_skips_django_setup(self, plain_config):
        """Verify generate() does not call DjangoSetup.run() for a plain project."""
        mocks = self._run_generate(plain_config)
        mocks["DjangoSetup"].return_value.run.assert_not_called()

    def test_django_runs_django_setup(self, django_config):
        """Verify generate() calls DjangoSetup.run() for a Django project."""
        mocks = self._run_generate(django_config)
        mocks["DjangoSetup"].return_value.run.assert_called_once()

    def test_no_git_skips_git_init(self, plain_config):
        """Verify generate() does not call GitSetup.init() when is_git is False."""
        mocks = self._run_generate(plain_config)
        mocks["GitSetup"].return_value.init.assert_not_called()

    def test_git_enabled_runs_git_init(self, git_config):
        """Verify generate() calls GitSetup.init() when is_git is True."""
        mocks = self._run_generate(git_config)
        mocks["GitSetup"].return_value.init.assert_called_once()

    def test_git_push_when_enabled(self, dest_dir):
        """Verify generate() calls push_initial_commit() when push is enabled."""
        config = ProjectConfig(
            raw_name="test",
            dest_parent=str(dest_dir),
            is_git=True,
            repo_url="https://github.com/user/test.git",
            push_initial_commit=True,
        )
        mocks = self._run_generate(config)
        mocks["GitSetup"].return_value.push_initial_commit.assert_called_once()

    def test_no_push_when_disabled(self, git_config):
        """Verify generate() skips push_initial_commit() when push is disabled."""
        mocks = self._run_generate(git_config)
        mocks["GitSetup"].return_value.push_initial_commit.assert_not_called()

    def test_bootstrap_runs_by_default(self, plain_config):
        """Verify generate() runs script/bootstrap via subprocess when run_bootstrap is True."""
        mocks = self._run_generate(plain_config)
        mocks["subprocess"].run.assert_called_once()

    def test_bootstrap_skipped_when_disabled(self, dest_dir):
        """Verify generate() skips the bootstrap subprocess call when run_bootstrap is False."""
        config = ProjectConfig(
            raw_name="test",
            dest_parent=str(dest_dir),
            run_bootstrap=False,
        )
        mocks = self._run_generate(config)
        mocks["subprocess"].run.assert_not_called()
