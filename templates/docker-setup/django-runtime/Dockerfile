# Django Runtime Image
# Optimized for production deployment, minimal footprint

ARG BASE_IMAGE=python-base:latest
FROM ${BASE_IMAGE} AS builder

USER root

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER devuser

# Ensure .local/bin is in PATH for pip-installed tools like poetry
ENV PATH="/home/devuser/.local/bin:${PATH}"

# Copy application code
WORKDIR /workspace
COPY --chown=devuser:devuser . .

# Run bootstrap script to install dependencies
RUN chmod +x script/bootstrap && script/bootstrap

# ─────────────────────────────────────────────────────────────
# Production stage - minimal image
# ─────────────────────────────────────────────────────────────
FROM ${BASE_IMAGE} AS runtime

USER root

# Only runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER devuser

# Ensure .local/bin is in PATH for poetry
ENV PATH="/home/devuser/.local/bin:${PATH}"

# Copy Poetry from builder
COPY --from=builder --chown=devuser:devuser /home/devuser/.local /home/devuser/.local

WORKDIR /workspace

# Copy everything from builder (including installed dependencies)
COPY --from=builder --chown=devuser:devuser /workspace /workspace

# Ensure venv is in PATH
ENV PATH="/workspace/.venv/bin:${PATH}" \
    VIRTUAL_ENV="/workspace/.venv"

# Defaults that can be overridden by environment variables
# DJANGO_SETTINGS_MODULE and GUNICORN_WSGI_MODULE must be provided via .env
ENV DJANGO_DEBUG=False

# Ensure startup script is executable
RUN chmod +x script/runserver

# Note: collectstatic and migrations run at container startup (in script/runserver)
# because static files go to a shared volume only available at runtime

EXPOSE 8000

# Health check for Django
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

CMD ["sh", "-c", "script/bootstrap && script/runserver"]