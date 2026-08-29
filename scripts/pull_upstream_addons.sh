#!/usr/bin/env bash
set -e

# Pull updated code from upstream addon repositories
PYTHON_CMD="python"
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

"$PYTHON_CMD" "$REPO_ROOT/scripts/pull_upstream_addons.py" "$@"
