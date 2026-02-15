#!/usr/bin/env bash
#
# Unified environment setup
# - Supports Ubuntu/Debian, Fedora, and Arch-based distros (CachyOS).
# - Installs system deps + creates a Python venv + installs requirements-test.txt.
# - Includes Playwright runtime deps and optional browser download.
#
# Usage:
#   ./setup.sh
#
# Optional env vars:
#   VENV_DIR=...                     (default: ./.venv)
#   INSTALL_PLAYWRIGHT_BROWSERS=1    (default: 1)  Set 0 to skip browser download
#   PLAYWRIGHT_BROWSER=chromium      (default: chromium)  Or: firefox, webkit, all
#   PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1   (set to 1 to silence host checks)
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${VENV_DIR:-$REPO_ROOT/.venv}"
INSTALL_PLAYWRIGHT_BROWSERS="${INSTALL_PLAYWRIGHT_BROWSERS:-1}"
PLAYWRIGHT_BROWSER="${PLAYWRIGHT_BROWSER:-chromium}"

command_exists() { command -v "$1" >/dev/null 2>&1; }

# Prefer python3 if present, otherwise fall back to python (common on Arch/CachyOS)
python_bin() {
  if command_exists python3; then
    echo "python3"
  elif command_exists python; then
    echo "python"
  else
    echo ""
  fi
}

require_sudo() {
  if [[ $(id -u) -ne 0 ]]; then
    if command_exists sudo; then
      SUDO="sudo"
    else
      echo "This script requires administrative privileges but sudo was not found." >&2
      exit 1
    fi
  else
    SUDO=""
  fi
}

install_ubuntu() {
  echo "Detected Ubuntu/Debian. Installing dependencies..."
  require_sudo
  $SUDO apt-get update
  $SUDO apt-get install -y python3 python3-venv python3-pip imagemagick pngquant git
}

install_fedora() {
  echo "Detected Fedora. Installing dependencies..."
  require_sudo
  $SUDO dnf install -y python3 python3-pip ImageMagick pngquant git
}

install_arch() {
  echo "Detected Arch-based distro (e.g., CachyOS). Installing dependencies..."
  require_sudo

  # Core tools
  $SUDO pacman -S --needed --noconfirm     python python-pip imagemagick pngquant git

  # Playwright runtime deps (needed to run browsers on Arch-based systems)
  $SUDO pacman -S --needed --noconfirm     nss nspr at-spi2-core libcups libdrm dbus libxcb libxkbcommon     libx11 libxcomposite libxdamage libxext libxfixes libxrandr     mesa pango cairo alsa-lib xorg-server-xvfb
}

create_venv_and_install() {
  local PY
  PY="$(python_bin)"
  if [[ -z "$PY" ]]; then
    echo "Python is required but was not found (python3/python)." >&2
    exit 1
  fi

  # If venv exists but is broken/missing activate script, recreate it.
  if [[ -d "$VENV_DIR" && ! -f "$VENV_DIR/bin/activate" ]]; then
    echo "Found existing venv dir but it's incomplete: $VENV_DIR"
    echo "Removing and recreating..."
    rm -rf "$VENV_DIR"
  fi

  if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating Python virtual environment at $VENV_DIR (using $PY)"
    "$PY" -m venv "$VENV_DIR"
  fi

  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"

  python -m pip install --upgrade pip

  if [[ ! -f "$REPO_ROOT/requirements-test.txt" ]]; then
    echo "requirements-test.txt not found in repo root: $REPO_ROOT" >&2
    exit 1
  fi

  python -m pip install -r "$REPO_ROOT/requirements-test.txt"

  if command_exists playwright; then
    if [[ "$INSTALL_PLAYWRIGHT_BROWSERS" == "1" ]]; then
      echo "Installing Playwright browser binaries ($PLAYWRIGHT_BROWSER)..."
      if [[ "$PLAYWRIGHT_BROWSER" == "all" ]]; then
        python -m playwright install
      else
        python -m playwright install "$PLAYWRIGHT_BROWSER"
      fi
    else
      echo "Skipping Playwright browser download (INSTALL_PLAYWRIGHT_BROWSERS=0)."
    fi
  else
    echo "Playwright not found in venv (not in requirements-test.txt?). Skipping browser install."
  fi

  echo "Environment ready. Activate with: source "$VENV_DIR/bin/activate""
}

# Windows hint
case "${OS:-$(uname -s)}" in
  *[Ww]indows*|MSYS*|MINGW*|CYGWIN*)
    echo "Windows environment detected. Run setup_windows.ps1 from PowerShell as Administrator:"
    echo "  powershell -ExecutionPolicy Bypass -File "$REPO_ROOT/setup_windows.ps1""
    exit 0
    ;;
  *)
    ;;
esac

# OS detection
if [[ -f /etc/os-release ]]; then
  # shellcheck disable=SC1091
  . /etc/os-release
  case "${ID:-}" in
    ubuntu|debian) install_ubuntu ;;
    fedora) install_fedora ;;
    arch|cachyos|manjaro|endeavouros|garuda) install_arch ;;
    *)
      echo "Unsupported Linux distribution: ${ID:-unknown}" >&2
      echo "If you're on an Arch-based distro, ensure /etc/os-release has ID=arch (or cachyos, etc.)." >&2
      exit 1
      ;;
  esac
else
  echo "/etc/os-release not found. Unable to determine OS." >&2
  exit 1
fi

create_venv_and_install

echo "Setup complete. Run tests with: source "$VENV_DIR/bin/activate" && pytest"
