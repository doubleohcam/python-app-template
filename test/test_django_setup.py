"""Tests for generator.django_setup — DjangoSetup and EnvSetup.

DjangoSetup reads real templates/django_files/ and writes to tmp_path.
EnvSetup reads real templates/.env.template and writes to tmp_path.
"""

from generator.django_setup import DjangoSetup, EnvSetup


class TestDjangoSetup:
    """Verify Django app skeleton is copied into {app_name}/ correctly."""

    def test_creates_app_directory(self, django_config, django_copier):
        """Verify DjangoSetup creates the {app_name}/ directory in dest_dir."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        DjangoSetup(django_config, django_copier).run()

        app_dir = django_config.dest_dir / django_config.app_name
        assert app_dir.is_dir()

    def test_copies_init_file(self, django_config, django_copier):
        """Verify __init__.py is copied into the app directory."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        DjangoSetup(django_config, django_copier).run()

        assert (django_config.dest_dir / django_config.app_name / "__init__.py").exists()

    def test_copies_apps_py(self, django_config, django_copier):
        """Verify apps.py is copied into the app directory."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        DjangoSetup(django_config, django_copier).run()

        assert (django_config.dest_dir / django_config.app_name / "apps.py").exists()

    def test_replaces_app_name_config_in_apps_py(self, django_config, django_copier):
        """Verify {app_name_config} is replaced with the real config class name in apps.py."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        DjangoSetup(django_config, django_copier).run()

        content = (django_config.dest_dir / django_config.app_name / "apps.py").read_text()
        assert django_config.app_name_config in content
        assert "{app_name_config}" not in content

    def test_no_unreplaced_template_vars(self, django_config, django_copier):
        """Verify no {app_name*} placeholders remain in any copied Django app file."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        DjangoSetup(django_config, django_copier).run()

        app_dir = django_config.dest_dir / django_config.app_name
        for path in app_dir.rglob("*"):
            if path.is_file():
                try:
                    content = path.read_text()
                except UnicodeDecodeError:
                    continue
                assert "{app_name}" not in content, f"Unreplaced var in {path.name}"
                assert "{app_name_pretty}" not in content, f"Unreplaced var in {path.name}"
                assert "{app_name_config}" not in content, f"Unreplaced var in {path.name}"

    def test_copies_settings_module(self, django_config, django_copier):
        """Verify all four settings files (base/dev/prod/test) are copied into the app directory."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        DjangoSetup(django_config, django_copier).run()

        settings = django_config.dest_dir / django_config.app_name / "settings"
        assert settings.is_dir()
        assert (settings / "base.py").exists()
        assert (settings / "dev.py").exists()
        assert (settings / "prod.py").exists()
        assert (settings / "test.py").exists()

    def test_copies_models_directory(self, django_config, django_copier):
        """Verify the models/ directory with __init__.py and base_model.py is copied."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        DjangoSetup(django_config, django_copier).run()

        models = django_config.dest_dir / django_config.app_name / "models"
        assert models.is_dir()
        assert (models / "__init__.py").exists()
        assert (models / "base_model.py").exists()


class TestEnvSetup:
    """Verify .env and .env.template generation."""

    def test_creates_both_env_files(self, django_config, django_copier):
        """Verify EnvSetup creates both .env and .env.template in dest_dir."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        EnvSetup(django_config, django_copier).run()

        assert (django_config.dest_dir / ".env").exists()
        assert (django_config.dest_dir / ".env.template").exists()

    def test_env_template_has_empty_django_secret_key(self, django_config, django_copier):
        """Verify .env.template contains DJANGO_SECRET_KEY with an empty value."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        EnvSetup(django_config, django_copier).run()

        template = (django_config.dest_dir / ".env.template").read_text()
        assert "DJANGO_SECRET_KEY=\n" in template

    def test_django_env_has_populated_secret_key(self, django_config, django_copier):
        """Verify .env contains a non-empty DJANGO_SECRET_KEY value of sufficient length."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        EnvSetup(django_config, django_copier).run()

        env = (django_config.dest_dir / ".env").read_text()
        for line in env.splitlines():
            if line.startswith("DJANGO_SECRET_KEY="):
                value = line.split("=", 1)[1]
                assert len(value) > 20, "Secret key should be a long token"
                return
        msg = "DJANGO_SECRET_KEY line not found in .env"
        raise AssertionError(msg)

    def test_django_env_has_wsgi_module(self, django_config, django_copier):
        """Verify .env sets GUNICORN_WSGI_MODULE to the correct wsgi application path."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        EnvSetup(django_config, django_copier).run()

        env = (django_config.dest_dir / ".env").read_text()
        assert f"GUNICORN_WSGI_MODULE={django_config.app_name}.wsgi:application" in env

    def test_django_env_has_settings_module(self, django_config, django_copier):
        """Verify .env contains DJANGO_SETTINGS_MODULE pointing to the app's dev settings."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        EnvSetup(django_config, django_copier).run()

        env = (django_config.dest_dir / ".env").read_text()
        assert f"DJANGO_SETTINGS_MODULE={django_config.app_name}.settings.dev" in env

    def test_plain_env_leaves_django_fields_empty(self, plain_config, copier):
        """Verify a plain (non-Django) .env has empty values for Django-specific fields."""
        plain_config.dest_dir.mkdir(parents=True, exist_ok=True)
        EnvSetup(plain_config, copier).run()

        env = (plain_config.dest_dir / ".env").read_text()
        assert "DJANGO_SECRET_KEY=\n" in env
        assert "GUNICORN_WSGI_MODULE=\n" in env
        assert "DJANGO_SETTINGS_MODULE=\n" in env

    def test_secret_keys_differ_across_runs(self, django_config, django_copier):
        """Verify each run of EnvSetup generates a unique DJANGO_SECRET_KEY."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        setup = EnvSetup(django_config, django_copier)

        def extract_key(text):
            for line in text.splitlines():
                if line.startswith("DJANGO_SECRET_KEY="):
                    return line.split("=", 1)[1]
            return None

        setup.run()
        key1 = extract_key((django_config.dest_dir / ".env").read_text())

        setup.run()
        key2 = extract_key((django_config.dest_dir / ".env").read_text())

        assert key1 != key2

    def test_template_vars_replaced_in_env(self, django_config, django_copier):
        """Verify no {app_name*} placeholders remain in either generated env file."""
        django_config.dest_dir.mkdir(parents=True, exist_ok=True)
        EnvSetup(django_config, django_copier).run()

        for name in (".env", ".env.template"):
            content = (django_config.dest_dir / name).read_text()
            assert "{app_name}" not in content
            assert "{app_name_pretty}" not in content
