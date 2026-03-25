# Base Python image with security hardening
# This serves as the foundation for all project-specific images

ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

# Security: Don't run as root
# Create a non-root user early
RUN groupadd --gid 1000 devuser \
    && useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home devuser

# Security: Minimize attack surface
# - No cache for apt (reduces image size and stale package risk)
# - Remove unnecessary packages after install
# - Clear apt lists
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        curl \
        ca-certificates \
        gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Security: Set restrictive umask
ENV UMASK=027

# Poetry configuration (installed in derived images if needed)
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR="/tmp/poetry_cache"

# Pip configuration
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Security: Read-only root filesystem preparation
# Create necessary writable directories
RUN mkdir -p /workspace /home/devuser/.cache /home/devuser/.local \
    && chown -R devuser:devuser /workspace /home/devuser

WORKDIR /workspace

# Default to non-root user
USER devuser

# Health check placeholder (override in derived images)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD echo "healthy" || exit 1
