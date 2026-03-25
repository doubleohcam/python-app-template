#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Claude Code Dev Container Entrypoint
#
# Handles first-run home dir init, git credential config,
# poetry install, then hands off to CMD.
# ─────────────────────────────────────────────────────────────
set -e

# ─────────────────────────────────────────────────────────────
# First-run: initialize home directory (volume is empty)
# ─────────────────────────────────────────────────────────────
if [[ ! -f /home/devuser/.bashrc ]]; then
    echo "Initializing home directory..."

    mkdir -p /home/devuser/.npm-global
    mkdir -p /home/devuser/.claude
    mkdir -p /home/devuser/.cache
    mkdir -p /home/devuser/.local

    cat > /home/devuser/.bashrc << 'BASHRC'
export PATH="/home/devuser/.npm-global/bin:$PATH"
export PATH="/workspace/.venv/bin:$PATH"
BASHRC
fi

# ─────────────────────────────────────────────────────────────
# Git credential configuration
# ─────────────────────────────────────────────────────────────
setup_git() {
    local configured=true

    if [[ -n "${GIT_USER_NAME:-}" ]]; then
        git config --global user.name "${GIT_USER_NAME}"
    elif [[ -z "$(git config --global user.name 2>/dev/null)" ]]; then
        echo "GIT_USER_NAME not set in .env"
        configured=false
    fi

    if [[ -n "${GIT_USER_EMAIL:-}" ]]; then
        git config --global user.email "${GIT_USER_EMAIL}"
    elif [[ -z "$(git config --global user.email 2>/dev/null)" ]]; then
        echo "GIT_USER_EMAIL not set in .env"
        configured=false
    fi

    if [[ -n "${GITHUB_TOKEN:-}" ]]; then
        git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
    else
        echo "GITHUB_TOKEN not set in .env - git push will require manual auth"
        configured=false
    fi

    if [[ "$configured" == true ]]; then
        echo "Git configured as: $(git config --global user.name) <$(git config --global user.email)>"
    fi
}

# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
setup_git

if [[ -f "/workspace/script/bootstrap" ]]; then
    cd /workspace
    script/bootstrap
fi

echo ""
echo "Ready. Project is at /workspace"

exec "$@"
