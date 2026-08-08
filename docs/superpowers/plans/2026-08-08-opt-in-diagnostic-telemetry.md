# Opt-In Diagnostic Telemetry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add disabled-by-default, privacy-safe GlitchTip diagnostics for Cumination exceptions, site/resolver failures, and Kodi playback outcomes.

**Architecture:** A `telemetry` facade owns opt-in checks and event creation. Focused modules handle redaction, durable state, Sentry-envelope delivery, and the playback state machine; a Kodi service correlates sanitized attempt files with player callbacks and drains the queue.

**Tech Stack:** Python 3, Kodi `kodi_six`, `requests`, JSON profile storage, GlitchTip Sentry envelopes, pytest.

## Global Constraints

- `telemetry_enabled` defaults to `false`; create no telemetry state before opt-in.
- Disabling removes the queue, rate state, attempt context, and installation ID before any network call.
- Do not add `sentry-sdk`; use the declared `script.module.requests` dependency.
- Never send titles, searches, model/room names, bodies, full URLs, cookies, auth values, credentials, PINs, or frame locals.
- Treat the DSN as public; local throttles prevent accidental floods and GlitchTip quotas handle extracted-key abuse.
- Telemetry must never alter directory output, exception propagation, resolving, playback, or shutdown.
- Ignore playback without an unexpired Cumination attempt.
- Constants: startup timeout 30 s, early-stop window 15 s, stable playback 30 s, attempt TTL 120 s, success sample 10%.

## File Map

- Create `resources/lib/telemetry_privacy.py`, `telemetry_store.py`, `telemetry_transport.py`, `telemetry.py`, and `playback_monitor.py`.
- Create `service.py` and `resources/telemetry.json`.
- Modify `default.py`, `addon.xml`, `resources/settings.xml`, `resources/lib/url_dispatcher.py`, `resources/lib/utils.py`, and `tests/conftest.py`.
- Add `tests/test_telemetry_privacy.py`, `test_telemetry_store.py`, `test_telemetry_transport.py`, `test_telemetry.py`, `test_telemetry_integration.py`, `test_playback_monitor.py`, and `test_telemetry_service.py`.
- Create `docs/diagnostics/GLITCHTIP_SETUP.md`.

---

### Task 1: Privacy Boundary

**Files:**
- Create: `plugin.video.cumination/resources/lib/telemetry_privacy.py`
- Test: `tests/test_telemetry_privacy.py`

**Interfaces:**
- Produces `sanitize_url(str) -> dict`, `sanitize_text(object, addon_root="") -> str`, `sanitize_event(dict, addon_root="") -> dict`, `safe_exception(BaseException, addon_root="") -> dict`.

- [ ] **Step 1: Write failing adversarial tests**

```python
def test_url_keeps_only_origin():
    assert privacy.sanitize_url("https://u:p@example.com/private?q=x#y") == {
        "scheme": "https", "domain": "example.com"
    }

def test_event_removes_secrets_unknowns_and_paths(tmp_path):
    event = {"event_id": "a" * 32, "timestamp": "2026-08-08T12:00:00Z",
             "level": "error", "message": "https://host/private?token=abc",
             "tags": {"site": "xvideos", "password": "bad", "unknown": "drop"},
             "contexts": {"http": {"domain": "host", "cookie": "sid=1"}},
             "extra": {"search": "private words"}}
    text = repr(privacy.sanitize_event(event, str(tmp_path))).lower()
    for forbidden in ("/private", "abc", "password", "cookie", "private words", "unknown"):
        assert forbidden not in text

def test_exception_has_no_locals_or_raw_url(tmp_path):
    try:
        secret = "must-not-leak"
        raise RuntimeError("https://host/path?token=abc")
    except RuntimeError as exc:
        result = privacy.safe_exception(exc, str(tmp_path))
    assert result["type"] == "RuntimeError"
    assert "must-not-leak" not in repr(result)
    assert all("locals" not in frame for frame in result["frames"])
```

- [ ] **Step 2: Run `.venv\Scripts\python.exe -m pytest tests\test_telemetry_privacy.py -q`; expect import failure.**

- [ ] **Step 3: Implement strict allowlisting and safe traces**

```python
MAX_TEXT = 500
TOP_KEYS = {"event_id", "timestamp", "level", "logger", "release", "environment",
            "message", "fingerprint", "tags", "contexts", "exception", "breadcrumbs", "extra"}
SECRET_KEY = re.compile(r"^(authorization|proxy_authorization|cookie|set_cookie|password|token|secret|session|api.?key|pin|username|query|search|media_title|room_name|model_name)$", re.I)

def sanitize_url(value):
    parsed = urllib_parse.urlsplit(str(value).split("|", 1)[0])
    return {"scheme": parsed.scheme.lower(), "domain": (parsed.hostname or "").lower()}

def safe_exception(exc, addon_root=""):
    frames = [{"filename": sanitize_text(f.filename, addon_root),
               "function": f.name, "lineno": f.lineno}
              for f in traceback.extract_tb(exc.__traceback__)]
    return {"type": exc.__class__.__name__,
            "value": sanitize_text(exc, addon_root), "frames": frames[-20:]}
```

`sanitize_text` replaces URLs with origin dictionaries, masks secret assignments, rewrites the add-on root as `<addon>` and `C:\Users\<name>` as `C:\Users\<user>`, then truncates. `sanitize_event` recursively accepts only documented tag/context/exception/breadcrumb keys, rejects `SECRET_KEY`, keeps 30 breadcrumbs/list items and 50 mapping entries, and returns `{}` if core fields are missing.

- [ ] **Step 4: Re-run the focused tests; expect all pass.**

- [ ] **Step 5: Commit:** `git commit -m "Add telemetry privacy sanitizer"` after staging the module and test.

---

### Task 2: Durable Queue, Cooldowns, and Sampling

**Files:**
- Create: `plugin.video.cumination/resources/lib/telemetry_store.py`
- Test: `tests/test_telemetry_store.py`

**Interfaces:**
- Produces `TelemetryStore(profile_dir, now=time.time, random_bytes=os.urandom, max_events=100, max_bytes=524288)`.
- Methods: `installation_id`, `enqueue`, `peek(limit=5)`, `ack`, `retry`, `allow`, `sample_success`, `clear`.

- [ ] **Step 1: Write failing tests** for lazy construction, a 32-hex installation ID, atomic JSON replacement, 100-event/512-KiB caps, success-first eviction, seven-day expiry, eight retries, bounded retry jitter, five-minute failure cooldown with suppressed count, one-hour success cooldown, deterministic 10% sampling, and complete cleanup.

```python
def test_cooldown_reports_suppressed_count(tmp_path):
    clock = Clock(1_700_000_000)
    store = TelemetryStore(str(tmp_path), now=clock)
    assert store.allow("same", "addon_exception") == (True, 0)
    assert store.allow("same", "addon_exception") == (False, 1)
    clock.value += 301
    assert store.allow("same", "addon_exception") == (True, 1)

def test_clear_removes_all_state(tmp_path):
    store = TelemetryStore(str(tmp_path), random_bytes=lambda n: b"a" * n)
    store.installation_id(); store.enqueue({"event_id": "1", "event_type": "addon_exception", "timestamp_epoch": time.time()})
    store.clear()
    assert not (tmp_path / "telemetry").exists()
```

- [ ] **Step 2: Run `.venv\Scripts\python.exe -m pytest tests\test_telemetry_store.py -q`; expect import failure.**

- [ ] **Step 3: Implement storage** under `<profile>/telemetry/{queue.json,rate.json,installation_id}`. Queue entries are `{"event": event, "retries": 0, "next_attempt": 0}`. Write `path.tmp`, flush/fsync, then `os.replace`. Inject `random_value=random.random`; retry delay is `min(3600, 2 ** retries * 5) * (0.8 + 0.4 * random_value())`, giving bounded 20-percent jitter. Sampling uses the first eight SHA-256 hex digits of the attempt ID modulo 100 `< 10`. `clear` removes only `<profile>/telemetry`.

- [ ] **Step 4: Run `pytest tests\test_telemetry_store.py tests\test_basics.py -q`; expect all pass.**

- [ ] **Step 5: Commit:** `git commit -m "Add bounded telemetry event store"`.

---

### Task 3: GlitchTip Envelope Transport

**Files:**
- Create: `plugin.video.cumination/resources/telemetry.json`
- Create: `plugin.video.cumination/resources/lib/telemetry_transport.py`
- Test: `tests/test_telemetry_transport.py`

**Interfaces:**
- Produces `load_dsn`, `parse_dsn -> DsnParts(endpoint, public_key, project_id)`, `build_envelope`, `send_event -> DeliveryResult(ok, retryable, status_code, event_id, message)`.

- [ ] **Step 1: Create supported unconfigured config:** `{"dsn":"","environment":"production"}`. An empty DSN returns a permanent `Telemetry backend is not configured` result.

- [ ] **Step 2: Write failing tests** for `https://public@example.invalid/42` mapping to `https://example.invalid/api/42/envelope/`; envelope header/item/event JSON lines; invalid/non-HTTPS DSNs; 2xx acceptance; 408/425/429/5xx retry; other 4xx drop; request exception retry; and `(2, 3)` timeouts.

```python
def test_envelope_shape():
    event = {"event_id": "a" * 32, "timestamp": "2026-08-08T12:00:00Z", "message": "test"}
    lines = build_envelope(event, DSN).decode().splitlines()
    assert json.loads(lines[0])["dsn"] == DSN
    assert json.loads(lines[1])["type"] == "event"
    assert json.loads(lines[2])["message"] == "test"
```

- [ ] **Step 3: Run the focused test; expect import failure.**

- [ ] **Step 4: Implement `requests.post(endpoint, data=envelope, headers={"Content-Type":"application/x-sentry-envelope"}, timeout=(2,3))`.** Build endpoint from scheme, hostname, optional port/base path, project ID; never log the DSN or response body.

- [ ] **Step 5: Run `pytest tests\test_telemetry_transport.py tests\test_utils_http.py -q`; expect all pass and no live network.**

- [ ] **Step 6: Commit:** `git commit -m "Add GlitchTip envelope transport"`.

---

### Task 4: Reporter Facade and Operation Lifecycle

**Files:**
- Create: `plugin.video.cumination/resources/lib/telemetry.py`
- Test: `tests/test_telemetry.py`

**Interfaces:**
- Produces `TelemetryReporter`, lazy `get_reporter`, `operation_scope`, `breadcrumb`, `note_listing_item`, `http_outcome(url, classification, status=0, elapsed_ms=0, final_url="")`, `resolve_failure`, `start_playback_attempt`, `send_test_report`, `cleanup_if_disabled`.

- [ ] **Step 1: Write failing tests** proving disabled mode creates no files/ID/events; exceptions queue then re-raise; successful zero-item `List` emits `unexpected_empty_listing`; empty `Search` does not; fingerprints ignore volatile message/device data but separate sites/top frames; breadcrumbs cap at 30; 100-KiB payload cap; cooldown suppression; accepted/retryable/permanent drain behavior; opt-out cleanup before transport.

```python
def test_exception_queues_and_reraises(tmp_path):
    reporter = make_reporter(tmp_path, enabled=True)
    with pytest.raises(RuntimeError):
        with reporter.operation_scope("xvideos.List", {}):
            raise RuntimeError("broken")
    assert reporter.store.peek(1)[0]["tags"]["event_type"] == "addon_exception"
```

- [ ] **Step 2: Run the focused test; expect import failure.**

- [ ] **Step 3: Implement the reporter.** `operation_scope` derives site from mode prefix and operation from function name, never stores query values, captures exceptions and re-raises, then detects only successful empty listings. Events contain UUID, UTC timestamp, `logger=cumination.telemetry.v1`, release/environment, runtime/device context, installation ID, sanitized exception, newest breadcrumbs, and fingerprint `event_type|site|operation|stage|classification|exception_type|resolver|top_addon_frame`. Sanitize immediately before queue and again before send.

```python
@contextlib.contextmanager
def operation_scope(self, mode, queries):
    if not self.enabled():
        yield; return
    self.current = {"site": (mode or "main").split(".")[0],
                    "operation": operation_from_mode(mode), "items": 0,
                    "http_success": False, "started": self.now()}
    try:
        yield
    except Exception as exc:
        self.capture_exception(exc)
        raise
    finally:
        self.finish_operation()
        self.current = None
```

Every public method catches internal failures and only writes a scrubbed class name to Kodi log. `drain_once(5)` acknowledges 2xx, retries transient results, and drops permanent rejects.

- [ ] **Step 4: Run all four telemetry unit modules; expect all pass.**

- [ ] **Step 5: Commit:** `git commit -m "Add structured telemetry reporter"`.

---

### Task 5: Shared Failure Instrumentation

**Files:**
- Modify: `plugin.video.cumination/default.py`
- Modify: `plugin.video.cumination/resources/lib/url_dispatcher.py`
- Modify: `plugin.video.cumination/resources/lib/utils.py`
- Create: `tests/test_telemetry_integration.py`
- Modify: `tests/test_default_entrypoint.py`, `tests/test_url_dispatcher.py`

**Interfaces:**
- Consumes Task 4 facade; preserves all existing signatures/returns.

- [ ] **Step 1: Write failing tests** that `default.main` wraps dispatch; `add_download_link` counts an item; `add_dir` counts only nonfolder non-next playable items; HTTP success/error/timeout/TLS/challenge/empty classifications and initial/final redirect domains are recorded; and `VideoPlayer` records `no_direct_source`, `no_supported_source`, `resolver_error`, `resolver_returned_empty` before existing notifications.

```python
def main(argv=None):
    argv = sys.argv if argv is None else argv
    queries = utils.parse_query(argv[2] if len(argv) > 2 else "")
    mode = queries.get("mode")
    with telemetry.operation_scope(mode, queries):
        url_dispatcher.dispatch(mode, queries)
```

- [ ] **Step 2: Run integration/entrypoint/dispatcher tests; expect new assertions fail.**

- [ ] **Step 3: Add local-import hooks.** Time `getHtml`; record `success`, `http_error`, `url_error`, `timeout`, `tls_error`, `cloudflare_challenge`, or `empty_response` before existing returns/raises. For a response, pass `response.geturl()` as `final_url` so the reporter retains only normalized initial/final domains. Never pass headers, referer, cookie jar, body, or exception text. Preserve notifications and resolver returns exactly.

- [ ] **Step 4: Run `pytest tests\test_telemetry_integration.py tests\test_default_entrypoint.py tests\test_url_dispatcher.py tests\test_utils_http.py tests\test_utils_gethtml.py tests\test_utils_video_processing.py -q`; expect all pass.**

- [ ] **Step 5: Commit:** `git commit -m "Instrument addon failure boundaries"`.

---

### Task 6: Playback Context and State Machine

**Files:**
- Modify: `plugin.video.cumination/resources/lib/telemetry.py`
- Create: `plugin.video.cumination/resources/lib/playback_monitor.py`
- Test: `tests/test_playback_monitor.py`, `tests/test_telemetry.py`

**Interfaces:**
- Reporter methods: `start_playback_attempt`, `load_playback_attempt`, `clear_playback_attempt`, `playback_outcome`.
- Produces `PlaybackStateMachine(attempt, now)` methods `av_started`, `playback_error`, `stopped`, `ended`, `tick` returning `None` or `{outcome, elapsed_ms}`.

- [ ] **Step 1: Write failing persistence tests** proving the attempt contains only ID/times/site/operation/domain/scheme/protocol/inputstream; strips path/query/Kodi headers; classifies HLS/DASH/Smooth Streaming/progressive; expires at 121 s; and deletes malformed files.

- [ ] **Step 2: Write a parametrized state table:** no outcome at 29.9 s; startup timeout at 30.0; player error terminal; stop 14.9 s after AV start is probable failure; tick 30.0 s after start is success; stop/end after stability has no failure; all callbacks after terminal are ignored.

- [ ] **Step 3: Run both modules; expect missing APIs.**

- [ ] **Step 4: Persist atomically to `<profile>/telemetry/playback_attempt.json` with TTL 120.** Strip after `|`, retain parsed origin/protocol only. `playback_outcome` maps failure/probable outcomes to `playback_failure`, stable to sampled `playback_success`, queues once, then clears matching ID.

- [ ] **Step 5: Implement constants and idempotent state machine:** `STARTUP_TIMEOUT=30.0`, `EARLY_STOP_WINDOW=15.0`, `STABILITY_THRESHOLD=30.0`; elapsed is nonnegative integer milliseconds.

- [ ] **Step 6: Run both modules; expect all pass.**

- [ ] **Step 7: Commit:** `git commit -m "Add playback telemetry state machine"`.

---

### Task 7: Kodi Service and Playback Handoff

**Files:**
- Create: `plugin.video.cumination/service.py`
- Modify: `plugin.video.cumination/addon.xml`, `resources/lib/utils.py`, `tests/conftest.py`
- Test: `tests/test_telemetry_service.py`, `tests/test_utils_video_processing.py`

**Interfaces:**
- Produces `TelemetryPlayer(xbmc.Player)` and `TelemetryService.run()`.

- [ ] **Step 1: Add deterministic `xbmc.Monitor` stub** with `abortRequested`/`waitForAbort`, and `Player.getPlayingFile()` returning `""`.

- [ ] **Step 2: Write failing tests** for no-attempt isolation, one correlated callback outcome, duplicate callback idempotence, startup tick, stable tick, early/normal stop, expiry, disabled cleanup, 15-second drain cadence, and abort-aware exit. Add a handoff test proving `start_playback_attempt(videourl, IA_check)` occurs immediately before `setResolvedUrl`/`Player.play` while Kodi receives the unchanged URL.

- [ ] **Step 3: Run service/handoff tests; expect missing integration.**

- [ ] **Step 4: Implement callbacks:** `onAVStarted`, `onPlayBackError`, `onPlayBackStopped`, `onPlayBackEnded` delegate to a controller owning one state machine. The run loop calls `waitForAbort(1.0)`, refreshes attempts, advances `tick`, drains five events every 15 s, and when disabled cleans state and skips file/network work. Catch/log internal class names and continue.

- [ ] **Step 5: Register service:**

```xml
<extension point="xbmc.service" library="service.py">
    <provides>executable</provides>
</extension>
```

In `utils.playvid`, after InputStream configuration and before either Kodi handoff, locally import telemetry and call `start_playback_attempt`; isolate its exception without modifying handoff.

- [ ] **Step 6: Run `pytest tests\test_telemetry_service.py tests\test_utils_video_processing.py tests\test_settings_xml.py -q`; expect all pass.**

- [ ] **Step 7: Commit:** `git commit -m "Monitor Kodi playback failures"`.

---

### Task 8: Opt-In UI, Test Report, Runbook, and Verification

**Files:**
- Modify: `plugin.video.cumination/resources/settings.xml`, `default.py`
- Modify: `tests/test_settings_xml.py`, `tests/test_default_entrypoint.py`
- Create: `docs/diagnostics/GLITCHTIP_SETUP.md`

**Interfaces:**
- Produces registered action `main.send_test_report`.

- [ ] **Step 1: Write failing XML/action tests** for boolean default false, disclosure, test action enabled only when the preceding boolean is true, accepted event-ID dialog, unconfigured-backend dialog, HTTP reject dialog, and no DSN/raw exception in UI.

- [ ] **Step 2: Run settings/entrypoint tests; expect failures.**

- [ ] **Step 3: Add this Advanced settings group before FlareSolverr:**

```xml
<setting type="lsep" label="Diagnostic reporting (off by default)" />
<setting id="telemetry_enabled" type="bool" label="Enable privacy-safe diagnostic reporting" default="false" />
<setting type="lsep" label="Sends errors, versions, site/stage, domains, and playback outcomes. Never sends titles, searches, credentials, cookies, or full URLs. The hosted service observes the source IP during delivery." />
<setting id="telemetry_test_report" type="action" label="Send test diagnostic report" enable="eq(-1,true)" option="close" action="RunPlugin(plugin://plugin.video.cumination/?mode=main.send_test_report)" />
```

- [ ] **Step 4: Implement `send_test_report`.** Queue sanitized classification `test_report`, message `Cumination diagnostic test report`, request one immediate drain, show accepted event ID or sanitized unconfigured/HTTP status. Retryable failure remains queued.

- [ ] **Step 5: Write the runbook** covering hosted Python project creation, copying its HTTPS DSN into `resources/telemetry.json`, email alerts for new/regressed issues, ingestion quota and `logger:cumination.telemetry.v1` filtering, test-event lookup, prohibited-field inspection, DSN rotation, opt-out cleanup, and the manual matrix: default-off traffic, stable stream, invalid stream, startup timeout, unavailable site, controlled exception, offline retry, unrelated playback.

- [ ] **Step 6: Run focused and full tests:**

```powershell
.venv\Scripts\python.exe -m pytest tests\test_telemetry_privacy.py tests\test_telemetry_store.py tests\test_telemetry_transport.py tests\test_telemetry.py tests\test_telemetry_integration.py tests\test_playback_monitor.py tests\test_telemetry_service.py tests\test_default_entrypoint.py tests\test_url_dispatcher.py tests\test_utils_http.py tests\test_utils_gethtml.py tests\test_utils_video_processing.py tests\test_settings_xml.py -q
.venv\Scripts\python.exe -m pytest -q
```

Expected: both exit 0 with no failures.

- [ ] **Step 7: Run static verification:**

```powershell
.venv\Scripts\python.exe -m ruff check plugin.video.cumination/resources/lib/telemetry*.py plugin.video.cumination/resources/lib/playback_monitor.py plugin.video.cumination/service.py tests/test_telemetry*.py tests/test_playback_monitor.py
.venv\Scripts\python.exe -m py_compile plugin.video.cumination/resources/lib/telemetry.py plugin.video.cumination/resources/lib/telemetry_privacy.py plugin.video.cumination/resources/lib/telemetry_store.py plugin.video.cumination/resources/lib/telemetry_transport.py plugin.video.cumination/resources/lib/playback_monitor.py plugin.video.cumination/service.py
git diff --check
```

Expected: all exit 0.

- [ ] **Step 8: Commit:** `git commit -m "Add opt-in diagnostic reporting controls"`.

- [ ] **Step 9: Configure the real DSN and perform the runbook's device matrix.** Record event IDs and payload review in PR testing notes; do not claim rollout ready until prohibited fields are absent.
