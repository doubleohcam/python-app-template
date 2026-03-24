"""Tests for generator.docker_setup — DockerSetup conditional file copying.

All copier calls are mocked — this tests the branching logic only.
"""

from unittest.mock import MagicMock

from generator.docker_setup import DOCKER_COMMON, DOCKER_DJANGO, DockerSetup


class TestDockerSetup:
    """Verify Docker files are copied with correct conditional logic."""

    def test_always_copies_common_files(self, plain_config):
        """Verify DockerSetup always copies DOCKER_COMMON files regardless of project type."""
        mock_copier = MagicMock()
        DockerSetup(plain_config, mock_copier).run()
        mock_copier.copy_file_list.assert_any_call(DOCKER_COMMON)

    def test_plain_project_skips_django_files(self, plain_config):
        """Verify a plain project copies only DOCKER_COMMON and skips DOCKER_DJANGO files."""
        mock_copier = MagicMock()
        DockerSetup(plain_config, mock_copier).run()
        mock_copier.copy_file_list.assert_called_once_with(DOCKER_COMMON)

    def test_django_project_copies_both_file_lists(self, django_config):
        """Verify a Django project copies both DOCKER_COMMON and DOCKER_DJANGO file lists."""
        mock_copier = MagicMock()
        DockerSetup(django_config, mock_copier).run()

        assert mock_copier.copy_file_list.call_count == 2
        mock_copier.copy_file_list.assert_any_call(DOCKER_COMMON)
        mock_copier.copy_file_list.assert_any_call(DOCKER_DJANGO)


class TestDockerFileLists:
    """Verify the file list constants contain expected entries."""

    def test_common_includes_compose(self):
        """Verify DOCKER_COMMON includes docker-compose.yml."""
        assert "docker-compose.yml" in DOCKER_COMMON

    def test_common_includes_base_dockerfile(self):
        """Verify DOCKER_COMMON includes the base Dockerfile."""
        assert "docker-setup/base/Dockerfile" in DOCKER_COMMON

    def test_common_includes_claude_dev(self):
        """Verify DOCKER_COMMON includes the claude-dev container files."""
        assert any("claude-dev" in f for f in DOCKER_COMMON)

    def test_django_includes_runtime_dockerfile(self):
        """Verify DOCKER_DJANGO includes the django-runtime Dockerfile."""
        assert "docker-setup/django-runtime/Dockerfile" in DOCKER_DJANGO

    def test_django_includes_nginx(self):
        """Verify DOCKER_DJANGO includes nginx configuration files."""
        assert any("nginx" in f for f in DOCKER_DJANGO)

    def test_django_includes_logging(self):
        """Verify DOCKER_DJANGO includes logging (Loki/Grafana) configuration files."""
        assert any("logging" in f for f in DOCKER_DJANGO)
