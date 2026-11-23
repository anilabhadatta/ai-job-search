#!/usr/bin/env bash
# ==============================================================================
# AI Job Search - Linux Setup & Server Launcher
# Automatically checks dependencies, creates virtualenv, skips setup if already
# configured, and starts the web application.
#
# Usage:
#   ./start_linux.sh                    # Start on default port 5000 with /ai-job-search
#   ./start_linux.sh --port 8080        # Custom port
#   ./start_linux.sh --prod             # Production WSGI server (Waitress)
#   ./start_linux.sh --url-context /    # Root URL context
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$SCRIPT_DIR"

echo "================================================================="
echo "  🚀 AI Job Search - Linux Launcher"
echo "  Target: Indian Software Hubs & Global Remote"
echo "================================================================="

VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"
SETUP_MARKER="$VENV_DIR/.setup_complete"

# ------------------------------------------------------------------------------
# 1. Check if Setup is Already Completed
# ------------------------------------------------------------------------------
is_setup_done() {
    if [ -d "$VENV_DIR" ] && [ -x "$VENV_PYTHON" ]; then
        # Check if core modules can be imported
        if "$VENV_PYTHON" -c "import flask, fitz, requests, waitress, bs4" >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

if is_setup_done; then
    echo "[✔] Existing virtual environment detected with required dependencies."
    echo "[✔] Setup is already completed. Skipping setup..."
else
    echo "[*] Setting up environment..."

    # Check for Python 3
    if ! command -v python3 >/dev/null 2>&1; then
        echo "[!] Error: python3 is not installed or not in PATH."
        echo "    Install with: sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
        exit 1
    fi

    PY_VERSION="$(python3 --version 2>&1)"
    echo "[*] Found: $PY_VERSION"

    # Verify python3-venv module availability
    if ! python3 -m venv --help >/dev/null 2>&1; then
        echo "[!] Error: python3-venv is missing."
        echo "    Install with: sudo apt install -y python3-venv"
        exit 1
    fi

    # Create virtual environment if missing
    if [ ! -d "$VENV_DIR" ] || [ ! -x "$VENV_PYTHON" ]; then
        echo "[*] Creating Python virtual environment in .venv..."
        python3 -m venv "$VENV_DIR"
    fi

    # Upgrade pip and install requirements
    echo "[*] Upgrading pip..."
    "$VENV_PYTHON" -m pip install --quiet --upgrade pip

    if [ -f "requirements-web.txt" ]; then
        echo "[*] Installing dependencies from requirements-web.txt..."
        "$VENV_PIP" install --quiet -r requirements-web.txt
    elif [ -f "requirements.txt" ]; then
        echo "[*] Installing dependencies from requirements.txt..."
        "$VENV_PIP" install --quiet -r requirements.txt
    fi

    # Verify installation
    if "$VENV_PYTHON" -c "import flask, fitz, requests, waitress, bs4" >/dev/null 2>&1; then
        touch "$SETUP_MARKER"
        echo "[✔] Environment setup completed successfully!"
    else
        echo "[!] Warning: Some packages could not be verified, but continuing..."
    fi
fi

# ------------------------------------------------------------------------------
# 2. Check Optional AI Agent CLIs
# ------------------------------------------------------------------------------
echo "-----------------------------------------------------------------"
if command -v codex >/dev/null 2>&1; then
    CODEX_VER="$(codex --version 2>/dev/null || echo 'installed')"
    echo "[✔] OpenAI Codex CLI detected ($CODEX_VER) - Live AI web search enabled."
else
    echo "[-] OpenAI Codex CLI not found (optional - install via: npm install -g @openai/codex)"
fi

if command -v claude >/dev/null 2>&1; then
    CLAUDE_VER="$(claude --version 2>/dev/null || echo 'installed')"
    echo "[✔] Claude Code CLI detected ($CLAUDE_VER)."
else
    echo "[-] Claude Code CLI not found (optional - install via: npm install -g @anthropic-ai/claude-code)"
fi
echo "-----------------------------------------------------------------"

# ------------------------------------------------------------------------------
# 3. Start the Web Server
# ------------------------------------------------------------------------------
PORT="${PORT:-5000}"
URL_PREFIX="${URL_PREFIX:-/ai-job-search}"

echo "[*] Launching AI Job Search server on port $PORT..."
echo "    Local URL: http://localhost:${PORT}${URL_PREFIX}"
echo "    Press Ctrl+C to stop."
echo "================================================================="

exec "$VENV_PYTHON" run_web.py "$@"
