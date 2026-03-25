"""Tests for generator.copier — TemplateCopier file operations.

Tests that exercise copy_file, copy_tree, and replace_vars use tmp_path
for both source and destination. Tests for copy_file_list read from the
real templates/ directory and write to tmp_path.
"""

from generator.copier import TEMPLATE_DIR


class TestTemplateDir:
    """Verify TEMPLATE_DIR points to the right place."""

    def test_exists(self):
        """Verify TEMPLATE_DIR exists on disk."""
        assert TEMPLATE_DIR.exists()

    def test_is_absolute(self):
        """Verify TEMPLATE_DIR is an absolute path."""
        assert TEMPLATE_DIR.is_absolute()

    def test_is_named_templates(self):
        """Verify TEMPLATE_DIR is named 'templates'."""
        assert TEMPLATE_DIR.name == "templates"


class TestReplaceVars:
    """Verify template variable replacement in strings."""

    def test_replaces_app_name(self, copier, plain_config):
        """Verify {app_name} placeholder is replaced with the derived app name."""
        assert copier.replace_vars("{app_name}") == plain_config.app_name

    def test_replaces_app_name_pretty(self, copier, plain_config):
        """Verify {app_name_pretty} placeholder is replaced with the pretty app name."""
        assert copier.replace_vars("{app_name_pretty}") == plain_config.app_name_pretty

    def test_replaces_app_name_config(self, copier, plain_config):
        """Verify {app_name_config} placeholder is replaced with the PascalCase config name."""
        assert copier.replace_vars("{app_name_config}") == plain_config.app_name_config

    def test_replaces_multiple_vars_in_one_string(self, copier, plain_config):
        """Verify multiple distinct placeholders in one string are all replaced."""
        result = copier.replace_vars("{app_name} and {app_name_pretty}")
        assert plain_config.app_name in result
        assert plain_config.app_name_pretty in result

    def test_leaves_unrelated_content_alone(self, copier):
        """Verify strings with no placeholders are returned unchanged."""
        assert copier.replace_vars("no placeholders here") == "no placeholders here"

    def test_handles_empty_string(self, copier):
        """Verify replace_vars handles an empty string without error."""
        assert copier.replace_vars("") == ""


class TestCopyFile:
    """Verify single file copy with variable replacement.

    Source and destination both live in tmp_path.
    """

    def test_copies_text_file_with_replacement(self, copier, plain_config, tmp_path):
        """Verify copy_file copies a text file and replaces template variables in its content."""
        src = tmp_path / "src" / "test.txt"
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text("name={app_name}")

        dest = tmp_path / "dest" / "test.txt"
        copier.copy_file(src, dest)

        assert dest.exists()
        assert dest.read_text() == f"name={plain_config.app_name}"

    def test_creates_parent_directories(self, copier, tmp_path):
        """Verify copy_file creates any missing parent directories for the destination."""
        src = tmp_path / "src.txt"
        src.write_text("content")

        dest = tmp_path / "a" / "b" / "c" / "dest.txt"
        copier.copy_file(src, dest)

        assert dest.exists()

    def test_copies_binary_file_without_replacement(self, copier, tmp_path):
        """Verify copy_file copies binary files byte-for-byte without attempting replacement."""
        src = tmp_path / "image.bin"
        binary_content = bytes(range(256))
        src.write_bytes(binary_content)

        dest = tmp_path / "out" / "image.bin"
        copier.copy_file(src, dest)

        assert dest.read_bytes() == binary_content


class TestCopyFileList:
    """Verify batch file copying from the real templates/ directory.

    Reads real template files, writes to tmp_path.
    """

    def test_skips_missing_files_with_warning(self, copier, capsys):
        """Verify copy_file_list prints a WARNING and continues for missing files."""
        copier.copy_file_list(["nonexistent/file.txt"])
        captured = capsys.readouterr()
        assert "WARNING" in captured.out

    def test_copies_existing_template_file(self, copier, plain_config):
        """Verify copy_file_list copies an existing template file to the destination."""
        plain_config.dest_dir.mkdir(parents=True, exist_ok=True)
        copier.copy_file_list([".pre-commit-config.yaml"])
        dest = plain_config.dest_dir / ".pre-commit-config.yaml"
        assert dest.exists()
        assert len(dest.read_text()) > 0

    def test_applies_prefix_remapping(self, copier, plain_config):
        """script/django/runserver → script/runserver via prefix swap."""
        plain_config.dest_dir.mkdir(parents=True, exist_ok=True)
        copier.copy_file_list(
            ["script/django/runserver"],
            src_prefix="script/django/",
            dest_prefix="script/",
        )
        assert (plain_config.dest_dir / "script" / "runserver").exists()

    def test_replaces_vars_in_copied_files(self, copier, plain_config):
        """Template variables in .pre-commit-config.yaml should be replaced."""
        plain_config.dest_dir.mkdir(parents=True, exist_ok=True)
        copier.copy_file_list(["pyproject.toml"])
        content = (plain_config.dest_dir / "pyproject.toml").read_text()
        # The template pyproject.toml uses {app_name} — should be replaced
        assert "{app_name}" not in content


class TestCopyTree:
    """Verify recursive directory copying.

    Source and destination both live in tmp_path.
    """

    def test_copies_all_files_recursively(self, copier, tmp_path):
        """Verify copy_tree copies all files from nested subdirectories to the destination."""
        src = tmp_path / "tree"
        (src / "a").mkdir(parents=True)
        (src / "a" / "one.txt").write_text("file one")
        (src / "b").mkdir(parents=True)
        (src / "b" / "two.txt").write_text("file two")

        dest = tmp_path / "out"
        copier.copy_tree(src, dest)

        assert (dest / "a" / "one.txt").exists()
        assert (dest / "b" / "two.txt").exists()

    def test_replaces_vars_in_copied_files(self, copier, plain_config, tmp_path):
        """Verify copy_tree replaces template variables in all copied files."""
        src = tmp_path / "tree"
        src.mkdir()
        (src / "config.txt").write_text("app={app_name}")

        dest = tmp_path / "out"
        copier.copy_tree(src, dest)

        assert (dest / "config.txt").read_text() == f"app={plain_config.app_name}"

    def test_preserves_directory_structure(self, copier, tmp_path):
        """Verify copy_tree recreates the full directory hierarchy at the destination."""
        src = tmp_path / "tree"
        (src / "sub" / "deep").mkdir(parents=True)
        (src / "sub" / "deep" / "file.txt").write_text("content")

        dest = tmp_path / "out"
        copier.copy_tree(src, dest)

        assert (dest / "sub" / "deep").is_dir()
        assert (dest / "sub" / "deep" / "file.txt").exists()
