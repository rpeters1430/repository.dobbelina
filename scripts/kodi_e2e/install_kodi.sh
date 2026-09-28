#!/usr/bin/env bash
# Install Kodi + what the e2e harness needs on Ubuntu/Debian.
#   install_kodi.sh ppa     -> latest stable Kodi from ppa:team-xbmc/ppa (Omega/21+)
#   install_kodi.sh distro  -> the distribution's Kodi (Ubuntu 24.04: 20.5 Nexus)
set -euo pipefail

channel="${1:-ppa}"
SUDO=""
if [ "$(id -u)" -ne 0 ]; then SUDO="sudo"; fi
export DEBIAN_FRONTEND=noninteractive

$SUDO apt-get update -q
if [ "$channel" = "ppa" ]; then
  $SUDO apt-get install -y -q --no-install-recommends software-properties-common gpg-agent
  if ! $SUDO add-apt-repository -y ppa:team-xbmc/ppa; then
    echo "::warning::team-xbmc PPA unavailable; falling back to the distribution's Kodi"
  fi
  $SUDO apt-get update -q
fi

$SUDO apt-get install -y -q --no-install-recommends \
  kodi xvfb xauth ffmpeg ca-certificates fonts-dejavu-core git python3-pil
# Binary addon for HLS/DASH; the harness warns if it is missing.
$SUDO apt-get install -y -q --no-install-recommends kodi-inputstream-adaptive \
  || echo "::warning::kodi-inputstream-adaptive not installed; adaptive streams will use Kodi's ffmpeg"

kodi --version 2>/dev/null | head -1 || true
