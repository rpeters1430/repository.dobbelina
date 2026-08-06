import types
import pytest
from resources.lib import flaresolverr
from resources.lib.flaresolverr import FlareSolverrManager, _validate_flaresolverr_url


class _FakeResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = "fake_text"

    def json(self):
        return self.json_data

    def raise_for_status(self):
        pass


def test_validate_flaresolverr_url_safe():
    # Localhost should always be safe
    _validate_flaresolverr_url("http://127.0.0.1:8191/v1")
    _validate_flaresolverr_url("http://localhost:8191/v1")


def test_validate_flaresolverr_url_unsafe():
    # Remote host should raise RuntimeError if settings are not mocked (and thus not allowed)
    # and it is not a private IP or local domain.
    with pytest.raises(RuntimeError) as excinfo:
        _validate_flaresolverr_url("http://remote-host.com:8191/v1")
    assert "remote host" in str(excinfo.value)
    assert "enable remote FlareSolverr hosts" in str(excinfo.value)


def test_validate_flaresolverr_url_private_ips():
    # Private IPs (both IPv4 and IPv6) should be automatically allowed
    _validate_flaresolverr_url("http://192.168.1.50:8191/v1")
    _validate_flaresolverr_url("http://10.0.0.5:8191/v1")
    _validate_flaresolverr_url("http://100.64.0.1:8191/v1")  # Tailscale
    _validate_flaresolverr_url("http://[fd00::1]:8191/v1")   # Unique Local IPv6


def test_validate_flaresolverr_url_local_domains():
    # Local/LAN/Tailscale domains should be automatically allowed
    _validate_flaresolverr_url("http://my-flaresolverr.local:8191/v1")
    _validate_flaresolverr_url("http://homeserver.lan:8191/v1")
    _validate_flaresolverr_url("http://node.domain.ts.net:8191/v1")
    _validate_flaresolverr_url("http://node.tailnet:8191/v1")


def test_validate_flaresolverr_url_allows_remote_ip_when_setting_enabled(monkeypatch):
    class _FakeAddon:
        def getSetting(self, key):
            if key == "fs_allow_remote":
                return "true"
            return ""

    monkeypatch.setattr(flaresolverr.xbmcaddon, "Addon", lambda *args, **kwargs: _FakeAddon())

    _validate_flaresolverr_url("http://100.90.80.70:8191/v1")


def _install_stateless_manager_fakes(monkeypatch, remote_calls):
    def fake_post(*args, **kwargs):
        remote_calls.append((args, kwargs))
        raise AssertionError("construction must not call FlareSolverr")

    class _FakeSession:
        def __init__(self):
            self.cookies = []

        def close(self):
            pass

    monkeypatch.setattr(flaresolverr.requests, "post", fake_post)
    monkeypatch.setattr(
        flaresolverr.requests, "session", lambda: _FakeSession(), raising=False
    )


def test_manager_construction_does_not_call_remote_session_commands(monkeypatch):
    remote_calls = []
    _install_stateless_manager_fakes(monkeypatch, remote_calls)

    FlareSolverrManager(
        flaresolverr_url="http://127.0.0.1:8191/v1",
        session_id="legacy-caller-session",
    )

    assert remote_calls == []


def test_request_retries_on_timeout(monkeypatch):
    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append((url, json, timeout))
        if json["cmd"] == "request.get" and not hasattr(fake_post, "failed"):
            setattr(fake_post, "failed", True)
            raise TimeoutError("timeout")

        return _FakeResponse({"status": "ok", "solution": {"response": "ok"}})

    class _FakeSession:
        def __init__(self):
            self.cookies = []
        def close(self):
            pass

    monkeypatch.setattr(flaresolverr.requests, "post", fake_post)
    monkeypatch.setattr(
        flaresolverr.requests, "session", lambda: _FakeSession(), raising=False
    )
    monkeypatch.setattr(
        flaresolverr.requests,
        "exceptions",
        types.SimpleNamespace(
            Timeout=TimeoutError, 
            ConnectionError=ConnectionError,
            RequestException=Exception
        ),
        raising=False,
    )
    monkeypatch.setattr(flaresolverr.time, "sleep", lambda *a, **k: None)

    manager = FlareSolverrManager(
        flaresolverr_url="http://127.0.0.1:8191/v1", session_id="cumination_session_new"
    )
    response = manager.request("http://example.com", tries=2, max_timeout=1000)

    assert response.status_code == 200
    req_calls = [c for c in calls if c[1].get("cmd") == "request.get"]
    assert len(req_calls) == 2


def test_close_does_not_call_remote_session_commands(monkeypatch):
    remote_calls = []
    _install_stateless_manager_fakes(monkeypatch, remote_calls)

    manager = FlareSolverrManager("http://127.0.0.1:8191/v1")
    manager.close(destroy_session=True)

    assert remote_calls == []


@pytest.mark.parametrize("version_fields", [{}, {"version": "2.0.0"}])
def test_request_uses_stateless_payload_for_v1_and_v2(monkeypatch, version_fields):
    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append((url, json, timeout))
        payload = {
            "status": "ok",
            "solution": {
                "response": "<html>ok</html>",
                "status": 200,
                "url": "https://spankbang.party/new_videos/1/?o=new",
                "headers": {"content-type": "text/html"},
                "cookies": [],
            },
        }
        payload.update(version_fields)
        return _FakeResponse(payload)

    class _FakeSession:
        def __init__(self):
            self.cookies = []
        def close(self):
            pass

    monkeypatch.setattr(flaresolverr.requests, "post", fake_post)
    monkeypatch.setattr(
        flaresolverr.requests, "session", lambda: _FakeSession(), raising=False
    )

    manager = FlareSolverrManager("http://127.0.0.1:8191/v1")
    response = manager.request("https://spankbang.party/new_videos/1/?o=new")

    assert response.status_code == 200
    assert response.text == "<html>ok</html>"
    assert len(calls) == 1
    assert calls[0][1]["cmd"] == "request.get"
    assert "session" not in calls[0][1]


def test_request_retries_status_error_without_session(monkeypatch):
    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append(json)
        if len(calls) == 1:
            return _FakeResponse({"status": "error", "message": "temporary solve failure"})
        return _FakeResponse({
            "status": "ok",
            "solution": {"response": "ok", "status": 200, "cookies": []},
        })

    class _FakeSession:
        def __init__(self):
            self.cookies = []

        def close(self):
            pass

    monkeypatch.setattr(flaresolverr.requests, "post", fake_post)
    monkeypatch.setattr(
        flaresolverr.requests, "session", lambda: _FakeSession(), raising=False
    )
    monkeypatch.setattr(flaresolverr.time, "sleep", lambda *_: None)
    monkeypatch.setattr(
        flaresolverr.requests,
        "exceptions",
        types.SimpleNamespace(RequestException=Exception),
        raising=False,
    )

    manager = FlareSolverrManager("http://127.0.0.1:8191/v1")
    response = manager.request("http://example.test", tries=2, max_timeout=1000)

    assert response.status_code == 200
    assert len(calls) == 2
    assert all("session" not in call for call in calls)
