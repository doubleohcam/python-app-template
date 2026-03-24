"""Production settings for {app_name} project.

Use with: DJANGO_SETTINGS_MODULE={app_name}.settings.prod.
"""

from .base import *  # noqa: F403
from .base import env

from {app_name}.logging import LoggingConfig

# set explicitly for prod
DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost"])

LOGGING = LoggingConfig.production

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
