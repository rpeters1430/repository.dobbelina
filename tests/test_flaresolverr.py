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
    with pytest.raises(RuntimeError) as excinfo:
        _validate_flaresolverr_url("http://remote-host:8191/v1")
    assert "remote host" in str(excinfo.value)


def test_init_clears_old_sessions(monkeypatch):
    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append((url, json, timeout))
        cmd = (json or {}).get("cmd")
        if cmd == "sessions.list":
            return _FakeResponse(
                {"sessions": ["cumination_session_old", "other_session"]}
            )
        if cmd == "sessions.destroy":
            return _FakeResponse({"status": "ok"})
        if cmd == "sessions.create":
            return _FakeResponse({"status": "ok", "session": "cumination_session_new"})
        return _FakeResponse({})

    class _FakeSession:
        def __init__(self):
            self.cookies = []
        def post(self, *args, **kwargs):
            return _FakeResponse({"status": "ok"})
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

    manager = FlareSolverrManager(
        flaresolverr_url="http://127.0.0.1:8191/v1", session_id="cumination_session_new"
    )

    assert manager.flaresolverr_session == "cumination_session_new"
    # Verify we listed and destroyed old session
    assert any(c[1].get("cmd") == "sessions.list" for c in calls)
    assert any(
        c[1].get("cmd") == "sessions.destroy"
        and c[1].get("session") == "cumination_session_old"
        for c in calls
    )


def test_request_retries_on_timeout(monkeypatch):
    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append((url, json, timeout))
        cmd = (json or {}).get("cmd")
        if cmd == "sessions.list":
            return _FakeResponse({"sessions": []})
        if cmd == "sessions.create":
            return _FakeResponse({"status": "ok", "session": "cumination_session_new"})
        if cmd == "sessions.destroy":
            return _FakeResponse({"status": "ok"})
        
        # Simulate timeout on first request.get/post
        if cmd in ("request.get", "request.post") and not hasattr(fake_post, "failed"):
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
    # 1 list + 1 create + 2 request attempts = 4
    # But we check for self.flaresolverr_url specifically
    req_calls = [c for c in calls if c[0] == "http://127.0.0.1:8191/v1" and c[1].get("cmd") == "request.get"]
    assert len(req_calls) == 2


def test_close_can_destroy_session_once(monkeypatch):
    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append((url, json, timeout))
        if json and json.get("cmd") == "sessions.list":
            return _FakeResponse({"sessions": []})
        if json and json.get("cmd") == "sessions.create":
            return _FakeResponse({"status": "ok", "session": "cumination_session_new"})
        if json and json.get("cmd") == "sessions.destroy":
            return _FakeResponse({"status": "ok"})
        return _FakeResponse({"status": "ok", "solution": {"response": "ok"}})

    class _FakeSession:
        def __init__(self):
            self.cookies = []
        def close(self):
            calls.append(("session.close", None, None))

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

    manager = FlareSolverrManager(
        flaresolverr_url="http://127.0.0.1:8191/v1", session_id="cumination_session_new"
    )
    manager.close(destroy_session=True)
    manager.close(destroy_session=True)

    destroy_calls = [
        c for c in calls if isinstance(c[1], dict) and c[1].get("cmd") == "sessions.destroy"
    ]
    assert len(destroy_calls) == 1


def test_request_recreates_session_on_invalid_session_id(monkeypatch):
    fs_calls = []

    def fake_post(url, json=None, timeout=None):
        fs_calls.append((url, json, timeout))
        cmd = (json or {}).get("cmd")
        if cmd == "sessions.list":
            return _FakeResponse({"sessions": []})
        if cmd == "sessions.create":
            return _FakeResponse({"status": "ok", "session": "cumination_session_new"})
        if cmd == "sessions.destroy":
            return _FakeResponse({"status": "ok"})
        
        # Simulate invalid session id on first request
        if cmd in ("request.get", "request.post") and not hasattr(fake_post, "failed"):
            setattr(fake_post, "failed", True)
            return _FakeResponse(
                {"status": "error", "message": "Error solving the challenge. Message: invalid session id"}
            )
            
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
    create_calls = [c for c in fs_calls if isinstance(c[1], dict) and c[1].get("cmd") == "sessions.create"]
    assert len(create_calls) >= 2
