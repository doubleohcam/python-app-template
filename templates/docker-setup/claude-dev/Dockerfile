# Claude Code Development Environment
# Extends base image with Claude Code CLI and development tools

ARG BASE_IMAGE=python-base:latest
FROM ${BASE_IMAGE} AS claude-dev

# Switch to root for installation
USER root

# Install Node.js (required for Claude Code CLI)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Development tools (optional, comment out what you don't need)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        vim \
        less \
        jq \
        make \
        build-essential \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create directory for Claude Code configuration
RUN mkdir -p /home/devuser/.claude \
    && chown -R devuser:devuser /home/devuser/.claude

# Copy entrypoint script
COPY --chown=root:root entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

# Security: npm global packages go to user directory
ENV NPM_CONFIG_PREFIX=/home/devuser/.npm-global \
    PATH="/home/devuser/.npm-global/bin:${PATH}"

# Switch back to non-root user
USER devuser

# Ensure npm global directory exists
RUN mkdir -p /home/devuser/.npm-global

# Set up default shell configuration (copied to volume on first run by entrypoint)
RUN echo 'export PATH="/home/devuser/.npm-global/bin:$PATH"' >> /home/devuser/.bashrc \
    && echo 'export PATH="/workspace/.venv/bin:$PATH"' >> /home/devuser/.bashrc

# Default entrypoint initializes home dir and runs bootstrap
ENTRYPOINT ["/opt/entrypoint.sh"]

# Default command opens a shell
CMD ["/bin/bash"]
