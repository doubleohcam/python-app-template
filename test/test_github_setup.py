"""Tests for generator.github_setup — GitHub files, dependabot, workflows.

Dependabot tests read real templates/.github/dependabot.yml and write to tmp_path.
Workflow template tests read real templates and write to tmp_path.
Run() dispatch tests use a mocked copier.
"""

from unittest.mock import MagicMock, patch

from generator.github_setup import GITHUB_COMMON, GITHUB_DJANGO, GitHubSetup


class TestGitHubSetupRun:
    """Verify run() dispatches to the right copier calls."""

    def test_always_copies_common_files(self, plain_config):
        """Verify run() always copies GITHUB_COMMON files regardless of project type."""
        mock_copier = MagicMock()
        setup = GitHubSetup(plain_config, mock_copier)

        with patch.object(setup, "write_dependabot"):
            setup.run()

        mock_copier.copy_file_list.assert_any_call(GITHUB_COMMON)

    def test_plain_project_skips_django_workflows(self, plain_config):
        """Verify a plain project copies only GITHUB_COMMON and skips GITHUB_DJANGO workflows."""
        mock_copier = MagicMock()
        setup = GitHubSetup(plain_config, mock_copier)

        with patch.object(setup, "write_dependabot"):
            setup.run()

        mock_copier.copy_file_list.assert_called_once_with(GITHUB_COMMON)

    def test_django_project_copies_django_workflows(self, django_config):
        """Verify a Django project also copies GITHUB_DJANGO workflow files."""
        mock_copier = MagicMock()
        setup = GitHubSetup(django_config, mock_copier)

        with patch.object(setup, "write_dependabot"):
            setup.run()

        mock_copier.copy_file_list.assert_any_call(GITHUB_DJANGO)


class TestDependabot:
    """Verify dependabot.yml generation from real template."""

    def test_django_keeps_django_runtime_entry(self, django_config, django_copier):
        """Verify write_dependabot() keeps the django-runtime entry for Django projects."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        GitHubSetup(django_config, django_copier).write_dependabot()

        content = (django_config.dest_dir / ".github" / "dependabot.yml").read_text()
        assert "django-runtime" in content

    def test_plain_removes_django_runtime_entry(self, plain_config, copier):
        """Verify write_dependabot() removes the django-runtime entry for plain projects."""
        plain_config.dest_dir.mkdir(parents=True, exist_ok=True)
        GitHubSetup(plain_config, copier).write_dependabot()

        content = (plain_config.dest_dir / ".github" / "dependabot.yml").read_text()
        assert "django-runtime" not in content

    def test_preserves_non_django_entries(self, plain_config, copier):
        """Verify write_dependabot() keeps pip and base docker entries for plain projects."""
        plain_config.dest_dir.mkdir(parents=True, exist_ok=True)
        GitHubSetup(plain_config, copier).write_dependabot()

        content = (plain_config.dest_dir / ".github" / "dependabot.yml").read_text()
        # pip and base docker entries should survive
        assert "pip" in content
        assert "docker-setup/base" in content

    def test_no_unreplaced_template_vars(self, plain_config, copier):
        """Verify write_dependabot() leaves no {app_name*} placeholders in the output file."""
        plain_config.dest_dir.mkdir(parents=True, exist_ok=True)
        GitHubSetup(plain_config, copier).write_dependabot()

        content = (plain_config.dest_dir / ".github" / "dependabot.yml").read_text()
        assert "{app_name}" not in content


class TestMigrationsWorkflowTemplate:
    """Verify migrations.yml uses {app_name} template vars, not hardcoded names.

    Reads real template, writes to tmp_path. No _replace_workflow_vars involved.
    """

    def test_no_dynamic_journal_after_copy(self, django_config, django_copier):
        """Verify 'dynamic_journal' is not present in migrations.yml after copying."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        django_copier.copy_file_list([".github/workflows/migrations.yml"])

        content = (django_config.dest_dir / ".github" / "workflows" / "migrations.yml").read_text()
        assert "dynamic_journal" not in content

    def test_app_name_present_after_copy(self, django_config, django_copier):
        """Verify the app name is present in migrations.yml after copying."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        django_copier.copy_file_list([".github/workflows/migrations.yml"])

        content = (django_config.dest_dir / ".github" / "workflows" / "migrations.yml").read_text()
        assert django_config.app_name in content


class TestGitHubFileLists:
    """Verify file list constants contain expected entries."""

    def test_common_includes_pr_template(self):
        """Verify GITHUB_COMMON includes the pull request template."""
        assert ".github/PULL_REQUEST_TEMPLATE.md" in GITHUB_COMMON

    def test_common_includes_lint_workflow(self):
        """Verify GITHUB_COMMON includes the lint workflow."""
        assert ".github/workflows/lint.yml" in GITHUB_COMMON

    def test_common_includes_test_workflow(self):
        """Verify GITHUB_COMMON includes the test workflow."""
        assert ".github/workflows/test.yml" in GITHUB_COMMON

    def test_django_includes_migrations_workflow(self):
        """Verify GITHUB_DJANGO includes the migrations workflow."""
        assert ".github/workflows/migrations.yml" in GITHUB_DJANGO
