# FlareSolverr v1/v2 Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Cumination use the stateless FlareSolverr request API that works with both v1 and v2.0.0.

**Architecture:** `FlareSolverrManager` will retain its public constructor and local `requests.Session`, but will stop managing remote browser sessions. Each solve sends `request.get` or `request.post` without a `session` field, then preserves the existing retry, cookie, response-wrapper, and error behavior.

**Tech Stack:** Python, Requests, pytest, Kodi Python compatibility stubs, FlareSolverr HTTP API.

## Global Constraints

- FlareSolverr v1 and v2.0.0 must use the same automatic stateless request path.
- Do not send `sessions.create`, `sessions.list`, or `sessions.destroy` during normal manager use.
- Do not send a `session` field in `request.get` or `request.post` payloads.
- Keep accepting the public `session_id` constructor argument for source compatibility.
- Preserve URL validation, retry count, timeouts, cookie handling, response wrapping, and genuine solve-error propagation.
- Do not change SpankBang parsing, add proxies, add CAPTCHA services, or add another browser stack.
- Preserve the user's unrelated `.claude/settings.local.json` modification and the repository-root diagnostic `kodi.log`.

---

### Task 1: Replace one-request remote sessions with stateless FlareSolverr calls

**Files:**
- Modify: `plugin.video.cumination/resources/lib/flaresolverr.py:1-300`
- Modify: `tests/test_flaresolverr.py:1-280`

**Interfaces:**
- Consumes: `FlareSolverrManager(flaresolverr_url: str | None = None, session_id: str | None = None)` and `request(url: str, method: str = "get", post_data: Any = None, tries: int = 3, max_timeout: int = 60000)`.
- Produces: the existing response-like object with `text`, `status_code`, `url`, `headers`, `raw_json`, `json()`, and `close()`, using a payload with `cmd`, `url`, `maxTimeout`, optional `postData`, and optional `cookies`, but no remote `session` field.

- [ ] **Step 1: Replace session-lifecycle expectations with failing stateless-construction and close tests**

Replace `test_init_clears_old_sessions` and `test_close_can_destroy_session_once` with tests shaped as follows:

```python
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
    monkeypatch.setattr(flaresolverr.requests, "session", lambda: _FakeSession())


def test_manager_construction_does_not_call_remote_session_commands(monkeypatch):
    remote_calls = []
    _install_stateless_manager_fakes(monkeypatch, remote_calls)

    FlareSolverrManager(
        flaresolverr_url="http://127.0.0.1:8191/v1",
        session_id="legacy-caller-session",
    )

    assert remote_calls == []


def test_close_does_not_call_remote_session_commands(monkeypatch):
    remote_calls = []
    _install_stateless_manager_fakes(monkeypatch, remote_calls)

    manager = FlareSolverrManager("http://127.0.0.1:8191/v1")
    manager.close(destroy_session=True)

    assert remote_calls == []
```

- [ ] **Step 2: Run the construction test and verify RED**

Run:

```powershell
C:\Users\rpete\repository.dobbelina\.venv\Scripts\python.exe -m pytest tests\test_flaresolverr.py -k "remote_session_commands" -q
```

Expected: both tests FAIL because construction sends `sessions.list`/`sessions.create`; after construction is repaired, the close test continues to catch `sessions.destroy`.

- [ ] **Step 3: Add failing v1/v2 stateless request coverage**

Add a parameterized test using one response without a `version` field (v1-shaped) and one with `"version": "2.0.0"` (observed v2-shaped):

```python
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
    monkeypatch.setattr(flaresolverr.requests, "session", lambda: _FakeSession())

    manager = FlareSolverrManager("http://127.0.0.1:8191/v1")
    response = manager.request("https://spankbang.party/new_videos/1/?o=new")

    assert response.status_code == 200
    assert response.text == "<html>ok</html>"
    assert len(calls) == 1
    assert calls[0][1]["cmd"] == "request.get"
    assert "session" not in calls[0][1]
```

- [ ] **Step 4: Run the stateless request test and verify RED**

Run:

```powershell
C:\Users\rpete\repository.dobbelina\.venv\Scripts\python.exe -m pytest tests\test_flaresolverr.py::test_request_uses_stateless_payload_for_v1_and_v2 -q
```

Expected: FAIL because construction currently makes session calls and request payloads contain `session`.

- [ ] **Step 5: Implement the minimal stateless manager lifecycle**

In `FlareSolverrManager.__init__`, retain URL validation, the local Requests session, the caller-supplied `session_id`, and `_destroyed`, but remove remote session listing/creation:

```python
def __init__(self, flaresolverr_url=None, session_id=None):
    self.session = requests.session()
    self.flaresolverr_url = flaresolverr_url or "http://127.0.0.1:8191/v1"
    _validate_flaresolverr_url(self.flaresolverr_url)
    self.session_id = session_id
    self.flaresolverr_session = None
    self._destroyed = False
```

Delete `_build_session_id`, `_reset_session`, `_create_session`, and `clear_old_sessions`, then remove their now-unused `os` and `uuid` imports. Build request payloads without `session`:

```python
flaresolverr_request = {
    "cmd": "request.get" if method.lower() == "get" else "request.post",
    "url": url,
    "maxTimeout": max_timeout,
}
```

Remove both invalid-session reset branches. Keep other transport retries and `status=error` handling intact. Change diagnostic logging to describe `session=stateless` without indexing a removed payload field.

In `close`, ignore the legacy `destroy_session` flag for remote calls and close only the local HTTP session:

```python
def close(self, destroy_session=False):
    if self._destroyed:
        return
    self.session.close()
    self._destroyed = True
```

- [ ] **Step 6: Update retry tests without weakening their assertions**

Update `test_request_retries_on_timeout` so its fake server handles only `request.get`, and keep the assertion that exactly two request attempts occur. Replace `test_request_recreates_session_on_invalid_session_id` with a genuine server-error retry test:

```python
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
    monkeypatch.setattr(flaresolverr.requests, "session", lambda: _FakeSession())
    monkeypatch.setattr(flaresolverr.time, "sleep", lambda *_: None)

    manager = FlareSolverrManager("http://127.0.0.1:8191/v1")
    response = manager.request("http://example.test", tries=2, max_timeout=1000)

    assert response.status_code == 200
    assert len(calls) == 2
    assert all("session" not in call for call in calls)
```

Keep the existing retry semantics: a `status=error` response raises `ValueError`, the existing retry loop retries it until `tries` is exhausted, and every attempt remains stateless.

- [ ] **Step 7: Run focused FlareSolverr tests and verify GREEN**

Run:

```powershell
C:\Users\rpete\repository.dobbelina\.venv\Scripts\python.exe -m pytest tests\test_flaresolverr.py -q
```

Expected: all FlareSolverr tests pass, no session lifecycle command is observed, and all request attempts omit `session`.

- [ ] **Step 8: Run SpankBang and shared HTTP regression tests**

Run:

```powershell
C:\Users\rpete\repository.dobbelina\.venv\Scripts\python.exe -m pytest tests\sites\test_spankbang.py tests\test_utils_gethtml.py tests\test_utils_http_fetch.py -q
```

Expected: all selected tests pass.

- [ ] **Step 9: Verify against the live v2.0.0 service**

Run a one-request diagnostic through the production manager with Kodi stubs available and `http://192.168.50.163:8191/v1`. Request `https://spankbang.party/new_videos/1/?o=new`, then verify:

- response status is 200;
- response body contains SpankBang listing HTML;
- the logged/request payload is `request.get` without `session`;
- no `sessions.create` or `sessions.destroy` request occurs.

Do not persist returned cookie values or response HTML in the repository.

- [ ] **Step 10: Run patch hygiene and the full suite**

Run:

```powershell
git diff --check
C:\Users\rpete\repository.dobbelina\.venv\Scripts\python.exe -m pytest -q
git status --short
git diff -- .claude\settings.local.json kodi.log
```

Expected: no whitespace errors; compatibility tests pass; any unrelated baseline failures are reported by exact test name; `.claude/settings.local.json` and `kodi.log` remain untouched.

- [ ] **Step 11: Commit the compatibility fix**

```powershell
git add plugin.video.cumination\resources\lib\flaresolverr.py tests\test_flaresolverr.py
git commit -m "Support stateless FlareSolverr v1 and v2"
```
