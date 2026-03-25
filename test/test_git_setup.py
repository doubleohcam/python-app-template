"""Tests for generator.git_setup — git init and push operations.

All subprocess calls are mocked — no real git operations.
"""

from unittest.mock import patch

from generator.git_setup import GitSetup


class TestGitInit:
    """Verify git init calls the right commands."""

    @patch("generator.git_setup.subprocess.run")
    def test_runs_expected_commands(self, mock_run, git_config):
        """Verify init() runs git init, remote add, and pull commands."""
        git_config.dest_dir.mkdir(parents=True, exist_ok=True)
        GitSetup(git_config).init()

        commands = [c.args[0] for c in mock_run.call_args_list]
        assert ("git", "init") in commands
        assert ("git", "remote", "add", "origin", git_config.repo_url) in commands
        assert ("git", "pull", "origin", git_config.branch) in commands

    @patch("generator.git_setup.subprocess.run")
    def test_runs_in_dest_dir(self, mock_run, git_config):
        """Verify all init() commands are run with cwd set to dest_dir."""
        git_config.dest_dir.mkdir(parents=True, exist_ok=True)
        GitSetup(git_config).init()

        for c in mock_run.call_args_list:
            assert c.kwargs["cwd"] == git_config.dest_dir

    @patch("generator.git_setup.subprocess.run")
    def test_uses_check_true(self, mock_run, git_config):
        """Verify all init() subprocess calls use check=True to raise on failure."""
        git_config.dest_dir.mkdir(parents=True, exist_ok=True)
        GitSetup(git_config).init()

        for c in mock_run.call_args_list:
            assert c.kwargs["check"] is True


class TestPushInitialCommit:
    """Verify initial commit and push logic."""

    @patch("generator.git_setup.subprocess.run")
    def test_runs_expected_commands(self, mock_run, git_config):
        """Verify push_initial_commit() runs checkout, add, commit, and push commands."""
        git_config.dest_dir.mkdir(parents=True, exist_ok=True)
        GitSetup(git_config).push_initial_commit()

        commands = [c.args[0] for c in mock_run.call_args_list]
        assert ("git", "checkout", "-b", "initial-setup") in commands
        assert ("git", "add", ".") in commands
        assert ("git", "commit", "-m", "[automated] Initial setup") in commands
        assert ("git", "push", "--set-upstream", "origin", "initial-setup") in commands

    @patch("generator.git_setup.subprocess.run")
    def test_commands_run_in_correct_order(self, mock_run, git_config):
        """Verify push_initial_commit() runs commands in checkout → add → commit → push order."""
        git_config.dest_dir.mkdir(parents=True, exist_ok=True)
        GitSetup(git_config).push_initial_commit()

        commands = [c.args[0] for c in mock_run.call_args_list]
        checkout_idx = next(i for i, c in enumerate(commands) if "checkout" in c)
        add_idx = next(i for i, c in enumerate(commands) if c == ("git", "add", "."))
        commit_idx = next(i for i, c in enumerate(commands) if "commit" in c)
        push_idx = next(i for i, c in enumerate(commands) if "push" in c)

        assert checkout_idx < add_idx < commit_idx < push_idx
