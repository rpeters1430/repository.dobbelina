#!/usr/bin/env bash
# Install Kodi + what the e2e harness needs on Debian/Ubuntu.
#   install_kodi.sh distro  -> the distribution's Kodi (default)
#                              Debian 13 trixie: Kodi 21 Omega; Ubuntu 24.04: Kodi 20.5 Nexus
#   install_kodi.sh ppa     -> try ppa:team-xbmc/ppa (Ubuntu only); if the PPA has no build
#                              for this release, it is removed again and the distro Kodi is used
set -euo pipefail

channel="${1:-distro}"
SUDO=""
if [ "$(id -u)" -ne 0 ]; then SUDO="sudo"; fi
export DEBIAN_FRONTEND=noninteractive

warn() { echo "::warning::$*"; }

$SUDO apt-get update -q

if [ "$channel" = "ppa" ]; then
  if ! grep -qi ubuntu /etc/os-release; then
    warn "the team-xbmc PPA is Ubuntu-only; using this distribution's Kodi"
  else
    $SUDO apt-get install -y -q --no-install-recommends software-properties-common gpg-agent
    if $SUDO add-apt-repository -y ppa:team-xbmc/ppa && $SUDO apt-get update -q; then
      echo "using ppa:team-xbmc/ppa"
    else
      # e.g. no build for this Ubuntu release (404 on the Release file)
      warn "team-xbmc PPA unavailable for this release; falling back to the distribution's Kodi"
      $SUDO add-apt-repository -y --remove ppa:team-xbmc/ppa || true
      $SUDO rm -f /etc/apt/sources.list.d/team-xbmc-*
      $SUDO apt-get update -q
    fi
  fi
fi

$SUDO apt-get install -y -q --no-install-recommends \
  kodi xvfb xauth ffmpeg ca-certificates fonts-dejavu-core git python3 python3-pil
# Binary addon for HLS/DASH; the harness warns if it is missing.
$SUDO apt-get install -y -q --no-install-recommends kodi-inputstream-adaptive \
  || warn "kodi-inputstream-adaptive not installed; adaptive streams will use Kodi's ffmpeg"

kodi --version 2>/dev/null | head -1 || true
