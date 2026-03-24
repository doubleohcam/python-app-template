"""Development settings for {app_name_pretty}.

Use with: DJANGO_SETTINGS_MODULE={app_name}.settings.dev.
"""

from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
