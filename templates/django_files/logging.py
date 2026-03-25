"""Logging configuration for {app_name}.

JSON-formatted output with extra fields support.

Usage in settings:
    from {app_name}.logging import LoggingConfig

    LOGGING = LoggingConfig.standard    # dev, test
    LOGGING = LoggingConfig.production  # prod — adds Loki handler

Usage in application code:
    import logging

    logger = logging.getLogger("app")

    logger.info("User logged in", extra={"user_id": 123, "ip": "192.168.1.1"})
    logger.error("Payment failed", extra={"amount": 99.99, "error_code": "DECLINED"})

Requires: python-json-logger, python-logging-loki (prod only)
"""

from __future__ import annotations

import os
from typing import ClassVar


class classproperty:  # noqa: N801
    """Descriptor for class-level properties."""

    def __init__(self, func: classmethod) -> None:
        self.fget = func

    def __get__(self, obj: object, owner: type) -> object:
        """Return the result of calling the wrapped function with the owner class."""
        return self.fget(owner)


class LoggingConfig:
    """Centralized logging configuration."""

    _formatter: ClassVar[dict] = {
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(message)s %(levelname)s %(asctime)s %(name)s %(module)s",
            "rename_fields": {
                "asctime": "timestamp",
                "levelname": "level",
            },
        },
    }

    _loggers: ClassVar[dict] = {
        "django": {
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "level": "WARNING",
            "propagate": False,
        },
        "app": {
            "level": "DEBUG",
            "propagate": False,
        },
    }

    @staticmethod
    def _build(handlers: dict, loggers: dict) -> dict:
        """Build a LOGGING dict with the given handlers wired to all loggers."""
        handler_names = list(handlers.keys())

        wired_loggers = {}
        for name, config in loggers.items():
            wired_loggers[name] = {**config, "handlers": list(handler_names)}

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": LoggingConfig._formatter,
            "handlers": handlers,
            "root": {
                "handlers": list(handler_names),
                "level": "INFO",
            },
            "loggers": wired_loggers,
        }

    @classproperty
    def standard(cls) -> dict:
        """JSON-formatted console output. For dev and test environments."""
        return cls._build(
            handlers={
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                },
            },
            loggers=cls._loggers,
        )

    @classproperty
    def production(cls) -> dict:
        """Console + Loki. For production environments."""
        return cls._build(
            handlers={
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                },
                "loki": {
                    "class": "logging_loki.LokiHandler",
                    "url": os.environ.get("LOKI_URL", "http://loki:3100/loki/api/v1/push"),
                    "tags": {
                        "app": os.environ.get("COMPOSE_PROJECT_NAME", "django"),
                        "environment": os.environ.get("ENVIRONMENT", "prod"),
                    },
                    "version": "1",
                },
            },
            loggers=cls._loggers,
        )
