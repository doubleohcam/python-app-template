"""Tests for generator.config — ProjectConfig derivation and user prompts."""

import pytest

from generator.config import ProjectConfig, _prompt, _prompt_yn, collect_config


class TestProjectConfigDerivation:
    """Verify that derived fields are computed correctly from raw_name."""

    @pytest.mark.parametrize(
        ("raw_name", "expected_app_name", "expected_pretty", "expected_config"),
        [
            ("my-cool-app", "my_cool_app", "My Cool App", "MyCoolAppConfig"),
            ("dynamic journal", "dynamic_journal", "Dynamic Journal", "DynamicJournalConfig"),
            ("single", "single", "Single", "SingleConfig"),
            ("UPPER-CASE", "upper_case", "Upper Case", "UpperCaseConfig"),
            ("  spaced-out  ", "spaced_out", "Spaced Out", "SpacedOutConfig"),
        ],
    )
    def test_name_derivation(self, raw_name, expected_app_name, expected_pretty, expected_config):
        """Verify app_name, app_name_pretty, and app_name_config are all derived correctly."""
        config = ProjectConfig(raw_name=raw_name, dest_parent="/tmp")  # noqa: S108
        assert config.app_name == expected_app_name
        assert config.app_name_pretty == expected_pretty
        assert config.app_name_config == expected_config

    def test_dest_dir_is_absolute(self):
        """Verify dest_dir is an absolute path."""
        config = ProjectConfig(raw_name="test-app", dest_parent="/tmp")  # noqa: S108
        assert config.dest_dir.is_absolute()

    def test_dest_dir_includes_app_name(self):
        """Verify dest_dir name matches app_name and is nested under dest_parent."""
        config = ProjectConfig(raw_name="test-app", dest_parent="/tmp")  # noqa: S108
        assert config.dest_dir.name == "test_app"
        assert str(config.dest_dir.parent) == "/tmp"  # noqa: S108

    def test_defaults(self):
        """Verify default values for optional fields are set correctly."""
        config = ProjectConfig(raw_name="x", dest_parent="/tmp")  # noqa: S108
        assert config.is_django is False
        assert config.run_bootstrap is True
        assert config.is_git is False
        assert config.repo_url == ""
        assert config.branch == "main"
        assert config.push_initial_commit is False


class TestTemplateVars:
    """Verify the template_vars property returns the correct mapping."""

    def test_has_exactly_three_keys(self, plain_config):
        """Verify template_vars contains exactly the three expected placeholder keys."""
        assert set(plain_config.template_vars.keys()) == {
            "{app_name}",
            "{app_name_pretty}",
            "{app_name_config}",
        }

    def test_values_match_derived_fields(self, plain_config):
        """Verify template_vars values match the corresponding derived config fields."""
        v = plain_config.template_vars
        assert v["{app_name}"] == plain_config.app_name
        assert v["{app_name_pretty}"] == plain_config.app_name_pretty
        assert v["{app_name_config}"] == plain_config.app_name_config


class TestSummary:
    """Verify the summary() method for generate() output."""

    def test_summary_contains_key_fields(self, plain_config):
        """Verify summary() output includes app_name, app_name_pretty, and dest_dir."""
        s = plain_config.summary()
        assert plain_config.app_name in s
        assert plain_config.app_name_pretty in s
        assert str(plain_config.dest_dir) in s


class TestPromptHelpers:
    """Unit tests for the _prompt and _prompt_yn input helpers."""

    def test_prompt_returns_input(self, monkeypatch):
        """Verify _prompt returns the user's input string."""
        monkeypatch.setattr("builtins.input", lambda _: "hello")
        assert _prompt("msg") == "hello"

    def test_prompt_strips_whitespace(self, monkeypatch):
        """Verify _prompt strips leading and trailing whitespace from input."""
        monkeypatch.setattr("builtins.input", lambda _: "  hello  ")
        assert _prompt("msg") == "hello"

    def test_prompt_returns_default_on_empty(self, monkeypatch):
        """Verify _prompt returns the default value when input is empty."""
        monkeypatch.setattr("builtins.input", lambda _: "")
        assert _prompt("msg", default="fallback") == "fallback"

    def test_prompt_yn_yes(self, monkeypatch):
        """Verify _prompt_yn returns True when user enters 'y'."""
        monkeypatch.setattr("builtins.input", lambda _: "y")
        assert _prompt_yn("msg") is True

    def test_prompt_yn_no(self, monkeypatch):
        """Verify _prompt_yn returns False when user enters 'n'."""
        monkeypatch.setattr("builtins.input", lambda _: "n")
        assert _prompt_yn("msg") is False

    def test_prompt_yn_default_false(self, monkeypatch):
        """Verify _prompt_yn returns False when input is empty and default is False."""
        monkeypatch.setattr("builtins.input", lambda _: "")
        assert _prompt_yn("msg", default=False) is False

    def test_prompt_yn_default_true(self, monkeypatch):
        """Verify _prompt_yn returns True when input is empty and default is True."""
        monkeypatch.setattr("builtins.input", lambda _: "")
        assert _prompt_yn("msg", default=True) is True


class TestCollectConfig:
    """Integration test for the interactive config collection."""

    def test_collect_plain_project(self, monkeypatch, tmp_path):
        """Verify collect_config builds a plain (non-Django, non-git) ProjectConfig."""
        responses = iter(
            [
                str(tmp_path),  # dest_parent
                "my-app",  # raw_name
                "n",  # is_django
                "y",  # run_bootstrap
                "n",  # is_git
            ]
        )
        monkeypatch.setattr("builtins.input", lambda _: next(responses))

        config = collect_config()
        assert config.app_name == "my_app"
        assert config.is_django is False
        assert config.is_git is False

    def test_collect_django_git_project(self, monkeypatch, tmp_path):
        """Verify collect_config builds a Django + git ProjectConfig with push enabled."""
        responses = iter(
            [
                str(tmp_path),  # dest_parent
                "web-app",  # raw_name
                "y",  # is_django
                "y",  # run_bootstrap
                "y",  # is_git
                "https://github.com/user/web-app.git",  # repo_url
                "main",  # branch
                "y",  # push_initial_commit
            ]
        )
        monkeypatch.setattr("builtins.input", lambda _: next(responses))

        config = collect_config()
        assert config.is_django is True
        assert config.is_git is True
        assert config.push_initial_commit is True
        assert "web-app" in config.repo_url
