"""Tests for generator.project_files — common files, scripts, pyproject.toml.

Run() dispatch tests use a mocked copier.
update_pyproject tests create fixture data in tmp_path.
"""

from unittest.mock import MagicMock, patch

from generator.project_files import (
    COMMON_FILES,
    COMMON_SCRIPTS,
    DJANGO_SCRIPTS,
    ProjectFilesSetup,
)


class TestProjectFilesSetupRun:
    """Verify run() dispatches to the right copier calls."""

    def test_copies_common_files(self, plain_config):
        """Verify run() copies COMMON_FILES for all project types."""
        mock_copier = MagicMock()
        setup = ProjectFilesSetup(plain_config, mock_copier)
        with patch.object(setup, "update_pyproject"):
            setup.run()
        mock_copier.copy_file_list.assert_any_call(COMMON_FILES)

    def test_copies_common_scripts(self, plain_config):
        """Verify run() copies COMMON_SCRIPTS for all project types."""
        mock_copier = MagicMock()
        setup = ProjectFilesSetup(plain_config, mock_copier)
        with patch.object(setup, "update_pyproject"):
            setup.run()
        mock_copier.copy_file_list.assert_any_call(COMMON_SCRIPTS)

    def test_plain_project_skips_django_scripts(self, plain_config):
        """Verify a plain project skips Django scripts (exactly two copy_file_list calls)."""
        mock_copier = MagicMock()
        setup = ProjectFilesSetup(plain_config, mock_copier)
        with patch.object(setup, "update_pyproject"):
            setup.run()
        assert mock_copier.copy_file_list.call_count == 2

    def test_django_project_copies_django_scripts_with_flattening(self, django_config):
        """Verify Django scripts are copied with the script/django/ → script/ prefix remapping."""
        mock_copier = MagicMock()
        setup = ProjectFilesSetup(django_config, mock_copier)
        with patch.object(setup, "update_pyproject"):
            setup.run()
        mock_copier.copy_file_list.assert_any_call(
            DJANGO_SCRIPTS,
            src_prefix="script/django/",
            dest_prefix="script/",
        )


class TestUpdatePyproject:
    """Verify pyproject.toml modifications — writes to tmp_path only."""

    def _write_pyproject(self, config, content):
        config.dest_dir.mkdir(parents=True, exist_ok=True)
        (config.dest_dir / "pyproject.toml").write_text(content)

    def test_replaces_project_name(self, plain_config, copier):
        """Verify update_pyproject() replaces the template project name with app_name."""
        self._write_pyproject(
            plain_config,
            '[tool.poetry]\nname = "python_app_template"\n',
        )
        ProjectFilesSetup(plain_config, copier).update_pyproject()

        result = (plain_config.dest_dir / "pyproject.toml").read_text()
        assert f'name = "{plain_config.app_name}"' in result
        assert "python_app_template" not in result

    def test_django_adds_dependencies(self, django_config, django_copier):
        """Verify update_pyproject() injects Django, gunicorn, and psycopg2 dependencies."""
        self._write_pyproject(
            django_config,
            '[tool.poetry]\nname = "python_app_template"\n\n'
            '[tool.poetry.group.dev.dependencies]\nruff = "*"\n',
        )
        ProjectFilesSetup(django_config, django_copier).update_pyproject()

        result = (django_config.dest_dir / "pyproject.toml").read_text()
        assert "django" in result.lower()
        assert "gunicorn" in result.lower()
        assert "psycopg2" in result.lower()

    def test_plain_project_no_django_deps(self, plain_config, copier):
        """Verify update_pyproject() does not add Django dependencies for plain projects."""
        self._write_pyproject(
            plain_config,
            '[tool.poetry]\nname = "python_app_template"\n\n'
            '[tool.poetry.group.dev.dependencies]\nruff = "*"\n',
        )
        ProjectFilesSetup(plain_config, copier).update_pyproject()

        result = (plain_config.dest_dir / "pyproject.toml").read_text()
        # "django" should not appear as a dependency
        lines = [line.strip() for line in result.splitlines()]
        assert not any(line.startswith("django") for line in lines)

    def test_template_vars_replaced(self, plain_config, copier):
        """Verify update_pyproject() replaces {app_name} placeholders in the file content."""
        self._write_pyproject(
            plain_config,
            'name = "python_app_template"\napp = "{app_name}"\n',
        )
        ProjectFilesSetup(plain_config, copier).update_pyproject()

        result = (plain_config.dest_dir / "pyproject.toml").read_text()
        assert "{app_name}" not in result
        assert plain_config.app_name in result


class TestFileLists:
    """Verify file list constants contain expected entries."""

    def test_common_files_includes_gitignore(self):
        """Verify COMMON_FILES includes .gitignore."""
        assert ".gitignore" in COMMON_FILES

    def test_common_files_includes_pyproject(self):
        """Verify COMMON_FILES includes pyproject.toml."""
        assert "pyproject.toml" in COMMON_FILES

    def test_common_scripts_includes_bootstrap(self):
        """Verify COMMON_SCRIPTS includes script/bootstrap."""
        assert "script/bootstrap" in COMMON_SCRIPTS

    def test_common_scripts_includes_test(self):
        """Verify COMMON_SCRIPTS includes script/test."""
        assert "script/test" in COMMON_SCRIPTS

    def test_django_scripts_includes_runserver(self):
        """Verify DJANGO_SCRIPTS includes script/django/runserver."""
        assert "script/django/runserver" in DJANGO_SCRIPTS

    def test_django_scripts_includes_migrate(self):
        """Verify DJANGO_SCRIPTS includes script/django/migrate."""
        assert "script/django/migrate" in DJANGO_SCRIPTS

    def test_django_scripts_all_under_script_django(self):
        """Verify every entry in DJANGO_SCRIPTS starts with the script/django/ prefix."""
        for path in DJANGO_SCRIPTS:
            assert path.startswith("script/django/")
