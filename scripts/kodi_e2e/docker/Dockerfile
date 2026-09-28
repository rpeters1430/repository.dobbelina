# Headless Kodi + the e2e harness. The repository is mounted at /repo, so the
# container always tests your current working tree.
#
#   docker compose -f scripts/kodi_e2e/docker/compose.yml run --rm kodi-e2e
#
# Debian 13 (trixie) ships Kodi 21 "Omega" in its own repositories. For Kodi
# 20 "Nexus" instead, build with BASE_IMAGE=ubuntu:24.04.
ARG BASE_IMAGE=debian:trixie
FROM ${BASE_IMAGE}

ARG KODI_CHANNEL=distro
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

COPY scripts/kodi_e2e/install_kodi.sh /tmp/install_kodi.sh
RUN apt-get update -q \
 && apt-get install -y -q --no-install-recommends python3 curl \
 && bash /tmp/install_kodi.sh "${KODI_CHANNEL}" \
 && rm -rf /var/lib/apt/lists/*

# The mounted repo belongs to your user; let git read it.
RUN git config --global --add safe.directory '*'

WORKDIR /repo
ENTRYPOINT ["python3", "-m", "scripts.kodi_e2e"]
CMD ["crawl", "--workers", "3"]
