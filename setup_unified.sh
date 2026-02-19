#!/usr/bin/env bash
#
# setup_unified.sh
#
# Unified environment setup for this repository (Kodi addon + tooling).
#
# Goals:
# - Work across many Linux distros by detecting the package manager (capability > branding).
# - Install common system dependencies used for Kodi addon development/repo packaging.
# - Create a Python virtualenv and install Python requirements (defaults to requirements*.txt when present).
# - Optional: install Playwright runtime deps + browsers (only if you use Playwright in this repo).
#
# Usage:
#   ./setup_unified.sh
#
# Optional env vars:
#   VENV_DIR=...                         (default: ./.venv)
#   REQUIREMENTS_FILE=...                (default auto-detect; see below)
#   INSTALL_KODI=0|1                     (default: 0) Install Kodi app package too
#   INSTALL_PLAYWRIGHT_DEPS=0|1          (default: 0) Install system deps for Playwright browsers
#   INSTALL_PLAYWRIGHT_BROWSERS=0|1      (default: 0) Download Playwright browser binaries in venv
#   PLAYWRIGHT_BROWSER=chromium|firefox|webkit|all  (default: chromium)
#
# Requirements file auto-detect order:
#   1) REQUIREMENTS_FILE env var (if set)
#   2) requirements.txt
#   3) requirements-dev.txt
#   4) requirements-test.txt
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${VENV_DIR:-$REPO_ROOT/.venv}"
INSTALL_KODI="${INSTALL_KODI:-0}"
INSTALL_PLAYWRIGHT_DEPS="${INSTALL_PLAYWRIGHT_DEPS:-0}"
INSTALL_PLAYWRIGHT_BROWSERS="${INSTALL_PLAYWRIGHT_BROWSERS:-0}"
PLAYWRIGHT_BROWSER="${PLAYWRIGHT_BROWSER:-chromium}"

command_exists() { command -v "$1" >/dev/null 2>&1; }

require_sudo() {
  if [[ $(id -u) -ne 0 ]]; then
    if command_exists sudo; then
      SUDO="sudo"
    else
      echo "This script needs admin privileges but 'sudo' was not found." >&2
      exit 1
    fi
  else
    SUDO=""
  fi
}

detect_pm() {
  # Order matters: prefer native distro PMs over "universal" ones.
  if command_exists apt-get; then echo "apt"; return; fi
  if command_exists dnf; then echo "dnf"; return; fi
  if command_exists pacman; then echo "pacman"; return; fi
  if command_exists zypper; then echo "zypper"; return; fi
  if command_exists apk; then echo "apk"; return; fi
  if command_exists xbps-install; then echo "xbps"; return; fi
  echo ""
}

pick_requirements_file() {
  if [[ -n "${REQUIREMENTS_FILE:-}" ]]; then
    if [[ -f "$REPO_ROOT/$REQUIREMENTS_FILE" ]]; then
      echo "$REPO_ROOT/$REQUIREMENTS_FILE"
      return
    fi
    echo "REQUIREMENTS_FILE was set but not found: $REPO_ROOT/$REQUIREMENTS_FILE" >&2
    exit 1
  fi

  for f in requirements.txt requirements-dev.txt requirements-test.txt; do
    if [[ -f "$REPO_ROOT/$f" ]]; then
      echo "$REPO_ROOT/$f"
      return
    fi
  done

  # No requirements file is not fatal for a Kodi addon repo (sometimes pure zip/XML).
  echo ""
}

install_deps_apt() {
  require_sudo
  echo "Using apt (Debian/Ubuntu/Kubuntu/Pop!_OS/Linux Mint/etc.)"

  $SUDO apt-get update

  # Core dev + packaging tooling
  $SUDO apt-get install -y \
    git curl wget rsync jq zip unzip \
    python3 python3-venv python3-pip \
    build-essential cmake pkg-config \
    imagemagick pngquant \
    xmlstarlet

  if [[ "$INSTALL_KODI" == "1" ]]; then
    $SUDO apt-get install -y kodi || true
  fi

  if [[ "$INSTALL_PLAYWRIGHT_DEPS" == "1" ]]; then
    # Based on Playwright Linux deps (Debian/Ubuntu family). This is optional & somewhat heavy.
    $SUDO apt-get install -y \
      libnss3 libnspr4 libatk-bridge2.0-0 libatk1.0-0 libcups2 \
      libdrm2 libdbus-1-3 libxkbcommon0 libx11-6 libxcomposite1 \
      libxdamage1 libxext6 libxfixes3 libxrandr2 libgbm1 \
      libpango-1.0-0 libcairo2 libasound2 xvfb
  fi
}

install_deps_dnf() {
  require_sudo
  echo "Using dnf (Fedora/Nobara/RHEL-family derivatives)"

  $SUDO dnf -y install \
    git curl wget rsync jq zip unzip \
    python3 python3-pip \
    gcc gcc-c++ make cmake pkgconf-pkg-config \
    ImageMagick pngquant \
    xmlstarlet

  # Fedora splits venv support into python3 (already) but ensure venv module exists
  $SUDO dnf -y install python3-virtualenv || true

  if [[ "$INSTALL_KODI" == "1" ]]; then
    $SUDO dnf -y install kodi || true
  fi

  if [[ "$INSTALL_PLAYWRIGHT_DEPS" == "1" ]]; then
    $SUDO dnf -y install \
      nss nspr atk at-spi2-atk cups-libs \
      libdrm dbus-libs libxkbcommon libX11 libXcomposite libXdamage \
      libXext libXfixes libXrandr mesa-libgbm \
      pango cairo alsa-lib xorg-x11-server-Xvfb
  fi
}

install_deps_pacman() {
  require_sudo
  echo "Using pacman (Arch/CachyOS/Manjaro/EndeavourOS/etc.)"

  $SUDO pacman -Syu --noconfirm
  $SUDO pacman -S --needed --noconfirm \
    git curl wget rsync jq zip unzip \
    python python-pip \
    base-devel cmake pkgconf \
    imagemagick pngquant \
    xmlstarlet

  if [[ "$INSTALL_KODI" == "1" ]]; then
    $SUDO pacman -S --needed --noconfirm kodi || true
  fi

  if [[ "$INSTALL_PLAYWRIGHT_DEPS" == "1" ]]; then
    $SUDO pacman -S --needed --noconfirm \
      nss nspr at-spi2-core libcups libdrm dbus libxcb libxkbcommon \
      libx11 libxcomposite libxdamage libxext libxfixes libxrandr \
      mesa pango cairo alsa-lib xorg-server-xvfb
  fi
}

install_deps_zypper() {
  require_sudo
  echo "Using zypper (openSUSE Leap/Tumbleweed)"

  $SUDO zypper --non-interactive refresh
  $SUDO zypper --non-interactive install \
    git curl wget rsync jq zip unzip \
    python3 python3-pip python3-virtualenv \
    gcc gcc-c++ make cmake pkg-config \
    ImageMagick pngquant \
    xmlstarlet

  if [[ "$INSTALL_KODI" == "1" ]]; then
    $SUDO zypper --non-interactive install kodi || true
  fi

  if [[ "$INSTALL_PLAYWRIGHT_DEPS" == "1" ]]; then
    # Package names vary a bit by SUSE version; this is a best-effort set.
    $SUDO zypper --non-interactive install \
      libnss3 libnspr4 at-spi2-atk cups-libs \
      libdrm2 dbus-1 libxkbcommon0 libX11-6 libXcomposite1 libXdamage1 \
      libXext6 libXfixes3 libXrandr2 Mesa-libgbm1 \
      pango cairo alsa-lib xvfb-run || true
  fi
}

install_deps_apk() {
  require_sudo
  echo "Using apk (Alpine Linux)"

  $SUDO apk update
  $SUDO apk add \
    git curl wget rsync jq zip unzip \
    python3 py3-pip py3-virtualenv \
    build-base cmake pkgconf \
    imagemagick pngquant \
    xmlstarlet

  if [[ "$INSTALL_KODI" == "1" ]]; then
    $SUDO apk add kodi || true
  fi

  if [[ "$INSTALL_PLAYWRIGHT_DEPS" == "1" ]]; then
    echo "Playwright deps on Alpine can be tricky (musl); consider using Playwright's container images."
  fi
}

install_deps_xbps() {
  require_sudo
  echo "Using xbps (Void Linux)"

  $SUDO xbps-install -Suy
  $SUDO xbps-install -Sy \
    git curl wget rsync jq zip unzip \
    python3 python3-pip python3-virtualenv \
    base-devel cmake pkg-config \
    ImageMagick pngquant \
    xmlstarlet

  if [[ "$INSTALL_KODI" == "1" ]]; then
    $SUDO xbps-install -Sy kodi || true
  fi

  if [[ "$INSTALL_PLAYWRIGHT_DEPS" == "1" ]]; then
    echo "Playwright deps on Void vary; use 'npx playwright install-deps' guidance if needed."
  fi
}

create_venv_and_install() {
  local req_file
  req_file="$(pick_requirements_file)"

  # Pick python
  local PY="python3"
  if ! command_exists python3 && command_exists python; then
    PY="python"
  fi
  if ! command_exists "$PY"; then
    echo "Python not found (python3/python). Install it first." >&2
    exit 1
  fi

  # Recreate broken venv
  if [[ -d "$VENV_DIR" && ! -f "$VENV_DIR/bin/activate" ]]; then
    echo "Found existing venv dir but it's incomplete: $VENV_DIR"
    echo "Removing and recreating..."
    rm -rf "$VENV_DIR"
  fi

  if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating Python virtual environment at $VENV_DIR (using $PY)"
    "$PY" -m venv "$VENV_DIR" 2>/dev/null || {
      # Some distros require virtualenv package
      echo "python -m venv failed; trying virtualenv..."
      "$PY" -m pip install --user --upgrade virtualenv
      "$PY" -m virtualenv "$VENV_DIR"
    }
  fi

  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"

  python -m pip install --upgrade pip wheel setuptools

  if [[ -n "$req_file" ]]; then
    echo "Installing Python deps from: $req_file"
    python -m pip install -r "$req_file"
  else
    echo "No requirements*.txt found. Skipping pip installs (this can be normal for Kodi addon repos)."
  fi

  # Optional: Playwright browser download
  if python -c "import playwright" >/dev/null 2>&1; then
    if [[ "$INSTALL_PLAYWRIGHT_BROWSERS" == "1" ]]; then
      echo "Installing Playwright browser binaries ($PLAYWRIGHT_BROWSER)..."
      if [[ "$PLAYWRIGHT_BROWSER" == "all" ]]; then
        python -m playwright install
      else
        python -m playwright install "$PLAYWRIGHT_BROWSER"
      fi
    else
      echo "Playwright detected, but browser download is disabled (INSTALL_PLAYWRIGHT_BROWSERS=0)."
    fi
  fi

  echo
  echo "Environment ready."
  echo "Activate with: source \"$VENV_DIR/bin/activate\""
}

main() {
  # Windows hint (if run under MSYS/MINGW)
  case "${OS:-$(uname -s)}" in
    *[Ww]indows*|MSYS*|MINGW*|CYGWIN*)
      echo "Windows detected. Use the Windows setup script (if present) from PowerShell."
      exit 0
      ;;
    *)
      ;;
  esac

  local pm
  pm="$(detect_pm)"
  if [[ -z "$pm" ]]; then
    echo "Unsupported distribution: couldn't find a known package manager (apt/dnf/pacman/zypper/apk/xbps)." >&2
    exit 1
  fi

  echo "Repo root: $REPO_ROOT"
  echo "Venv dir : $VENV_DIR"
  echo "PM       : $pm"
  echo

  case "$pm" in
    apt) install_deps_apt ;;
    dnf) install_deps_dnf ;;
    pacman) install_deps_pacman ;;
    zypper) install_deps_zypper ;;
    apk) install_deps_apk ;;
    xbps) install_deps_xbps ;;
    *) echo "Internal error: unknown pm '$pm'." >&2; exit 1 ;;
  esac

  create_venv_and_install

  echo
  echo "Setup complete."
}

main "$@"
