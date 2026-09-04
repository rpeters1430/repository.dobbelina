"""Optional integration test for FlareSolverrManager against a real solverr container.

Runs only when Docker is available on the machine: pulls (if missing) and starts
https://github.com/rpeters1430/solverr (a FlareSolverr-compatible drop-in) as a
throwaway container, exercises FlareSolverrManager against it for real, then tears
the container down. When Docker isn't installed/running, the test skips instead of
failing so `run_tests.py` stays green on machines without Docker.
"""

import shutil
import subprocess
import sys
import time
import uuid

import pytest

DOCKER_IMAGE = "ghcr.io/rpeters1430/solverr:latest"
CONTAINER_PORT = 8191
HOST_PORT = 18191
TARGET_URL = "https://example.com/"
PULL_TIMEOUT = 300
HEALTH_TIMEOUT = 90


def _docker_available():
    if shutil.which("docker") is None:
        return False
    try:
        subprocess.run(["docker", "info"], capture_output=True, timeout=10, check=True)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return False
    return True


def _load_real_requests():
    """Return the real ``requests`` package, bypassing conftest's no-op stub.

    tests/conftest.py replaces sys.modules["requests"] with a fake, always-200,
    empty-body stub so site-parsing tests never hit the network (see
    _ensure_kodi_stubs). This test is the one place that deliberately wants real
    HTTP, so it borrows the genuine module without disturbing the stub other
    tests rely on.
    """
    stub = sys.modules.pop("requests", None)
    try:
        import requests as real_requests
    finally:
        if stub is not None:
            sys.modules["requests"] = stub
    return real_requests


@pytest.fixture(scope="module")
def solverr_url():
    if not _docker_available():
        pytest.skip("Docker is not available; skipping solverr integration test")

    real_requests = _load_real_requests()

    have_image = subprocess.run(
        ["docker", "image", "inspect", DOCKER_IMAGE], capture_output=True
    ).returncode == 0
    if not have_image:
        try:
            pull = subprocess.run(
                ["docker", "pull", DOCKER_IMAGE],
                capture_output=True,
                text=True,
                timeout=PULL_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            pytest.skip("Timed out pulling {}".format(DOCKER_IMAGE))
        if pull.returncode != 0:
            pytest.skip("Could not pull {}: {}".format(DOCKER_IMAGE, pull.stderr.strip()))

    container_name = "cumination-solverr-test-{}".format(uuid.uuid4().hex[:8])
    run = subprocess.run(
        [
            "docker", "run", "-d", "--rm",
            "--name", container_name,
            "-p", "{}:{}".format(HOST_PORT, CONTAINER_PORT),
            DOCKER_IMAGE,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if run.returncode != 0:
        pytest.skip("Could not start solverr container: {}".format(run.stderr.strip()))

    base_url = "http://127.0.0.1:{}".format(HOST_PORT)

    try:
        deadline = time.time() + HEALTH_TIMEOUT
        healthy = False
        while time.time() < deadline:
            try:
                resp = real_requests.get(base_url + "/health", timeout=5)
                if resp.status_code == 200:
                    healthy = True
                    break
            except real_requests.exceptions.RequestException:
                pass
            time.sleep(2)

        if not healthy:
            pytest.skip("solverr container did not become healthy in time")

        yield base_url
    finally:
        subprocess.run(
            ["docker", "stop", container_name], capture_output=True, timeout=30
        )


def test_flaresolverr_manager_resolves_via_solverr_container(monkeypatch, solverr_url):
    from resources.lib import flaresolverr

    monkeypatch.setattr(flaresolverr, "requests", _load_real_requests())

    manager = flaresolverr.FlareSolverrManager(flaresolverr_url=solverr_url + "/v1")
    try:
        response = manager.request(TARGET_URL, max_timeout=60000)
    finally:
        manager.close()

    assert response.status_code == 200
    assert "Example Domain" in response.text
