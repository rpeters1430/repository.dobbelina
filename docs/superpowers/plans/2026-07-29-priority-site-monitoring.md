# Priority Site Monitoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add trusted daily monitoring that detects incorrect listings and unusable playback for the 17 priority sites and opens actionable issues on the first failure.

**Architecture:** Extend the existing live runner to expose bounded listing samples, then pass those samples through focused listing and media validators. Keep strict results and history separate from broad smoke results, add stable issue lifecycle automation, and use a small Kodi JSON-RPC probe as an independent runtime signal.

**Tech Stack:** Python 3.11, pytest, requests, GitHub Actions, FlareSolverr, Kodi JSON-RPC v12, headless Kodi under Xvfb.

## Global Constraints

- Strict monitoring covers exactly: `anybunny`, `ask4porn`, `cam4`, `camsoda`, `chaturbate`, `luxuretv`, `missav`, `porndig`, `pornhub`, `pornkai`, `spankbang`, `streamate`, `thothub`, `xnxx`, `xvideos`, `youporn`, and `yourlesbians`.
- The broad smoke scan remains separate and cannot contribute to the trusted healthy count.
- Required strict stages may not turn `SKIP` into `HEALTHY`.
- A first `BROKEN` or `BLOCKED` result opens or updates an issue immediately.
- Only successful strict runs update healthy metric baselines.
- Close a site issue only after two consecutive complete strict passes.
- Redact cookies, authorization values, and sensitive query values before persistence.
- Never persist downloaded media.

---

## File Map

- `scripts/site_health_types.py`: strict health enums, validation records, failure signatures, and redaction.
- `scripts/listing_validator.py`: deterministic listing contract and baseline checks.
- `scripts/media_validator.py`: bounded direct-media, HLS, and DASH verification.
- `scripts/live_smoke_test.py`: expose bounded listing samples captured from the existing addon dispatcher.
- `scripts/strict_site_monitor.py`: compose capture, listing validation, media validation, and report rendering.
- `scripts/strict_health_history.py`: merge isolated strict reports and maintain bounded recovery/baseline history.
- `scripts/generate_strict_triage_requests.py`: convert strict state/history into stable issue actions.
- `scripts/automate_triage.py`: execute create, update, reopen, and close actions.
- `scripts/kodi_jsonrpc.py`: transport-only Kodi JSON-RPC client.
- `scripts/kodi_site_probe.py`: directory and playback checks against a running Kodi instance.
- `config/site_profiles.json`: strict contracts and adjusted Tier 1 membership.
- `.github/workflows/site-health.yml`: strict matrix, Kodi job, merge, triage, artifacts, and persistence.

### Task 1: Strict Types, Redaction, Profiles, and Matrix

**Files:**
- Create: `scripts/site_health_types.py`
- Modify: `config/site_profiles.json`
- Modify: `scripts/generate_smoke_matrix.py`
- Modify: `tests/test_generate_smoke_matrix.py`
- Create: `tests/test_site_health_types.py`
- Modify: `tests/test_site_profiles.py`

**Interfaces:**
- Produces: `HealthState`, `ValidationResult`, `redact_url(url: str) -> str`, `failure_signature(result: dict) -> str`.
- Produces: `strict_contract` profile object and `build_strict_matrix(profiles: dict) -> dict`.

- [ ] **Step 1: Write failing type and redaction tests**

```python
def test_redact_url_removes_sensitive_values():
    value = redact_url("https://cdn.test/a.m3u8?token=secret&quality=720")
    assert value == "https://cdn.test/a.m3u8?token=REDACTED&quality=720"

def test_failure_signature_ignores_volatile_urls():
    left = {"state": "BROKEN", "failed_stage": "media", "classification": "PLAYBACK"}
    right = {**left, "sample_url": "https://cdn.test/expiring?token=x"}
    assert failure_signature(left) == failure_signature(right)
```

- [ ] **Step 2: Run the focused tests and verify they fail**

Run: `.venv\Scripts\python.exe -m pytest tests/test_site_health_types.py tests/test_generate_smoke_matrix.py tests/test_site_profiles.py -q`

Expected: FAIL because the strict types, contract, and matrix do not exist.

- [ ] **Step 3: Add the strict types and pure helpers**

```python
class HealthState(str, Enum):
    HEALTHY = "HEALTHY"
    BROKEN = "BROKEN"
    BLOCKED = "BLOCKED"
    HARNESS_ERROR = "HARNESS_ERROR"
    NOT_TESTED = "NOT_TESTED"

@dataclass
class ValidationResult:
    passed: bool
    classification: str
    message: str
    metrics: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
```

Redact query keys matching `token`, `auth`, `authorization`, `cookie`, `key`,
`signature`, `sig`, `expires`, and `hdntl`. Build failure signatures only from
state, failed stage, classification, and normalized message.

- [ ] **Step 4: Add and validate strict profiles**

Add `strict_contract` under the default profile with `min_video_items: 5`,
`min_unique_title_ratio: 0.8`, `min_unique_url_ratio: 0.8`,
`sample_count: 1`, empty allowed-host lists, required listing/playback/media
stages, and advisory thumbnail/description fields. Remove Tier 1 from
`stripchat`; add `thothub` as Tier 1. Add explicit host lists and any necessary
threshold overrides for all 17 sites by inspecting their `AdultSite.url` and
known playback hosts. Profile validation must reject a Tier 1 site with a
missing or empty strict contract.

- [ ] **Step 5: Add the isolated strict matrix**

```python
def build_strict_matrix(profiles):
    names = sorted(
        name for name, profile in profiles["sites"].items()
        if profile.get("tier") == 1
    )
    return {"include": [{"site": name} for name in names]}
```

Expose `python scripts/generate_smoke_matrix.py --strict` while preserving the
existing four-chunk default output.

- [ ] **Step 6: Run tests and commit**

Run: `.venv\Scripts\python.exe -m pytest tests/test_site_health_types.py tests/test_generate_smoke_matrix.py tests/test_site_profiles.py -q`

Expected: PASS.

Commit: `git commit -m "Add strict site health contracts"`

### Task 2: Listing Contract Validator

**Files:**
- Create: `scripts/listing_validator.py`
- Create: `tests/test_listing_validator.py`

**Interfaces:**
- Consumes: `ValidationResult`.
- Produces: `validate_listing(items: list[dict], contract: dict, baseline: dict | None = None) -> ValidationResult`.

- [ ] **Step 1: Write failing listing tests**

Cover a healthy five-item listing, zero items, duplicate URL ratio below 0.8,
blank titles, non-HTTP URLs, disallowed hosts, category/login modes emitted as
videos, challenge-page evidence, a 70% count drop from baseline, and advisory
thumbnail degradation.

```python
def test_duplicate_flood_is_broken():
    items = [video("A", "https://example.test/watch/1") for _ in range(5)]
    result = validate_listing(items, contract())
    assert result.passed is False
    assert result.classification == "PARSER"
```

- [ ] **Step 2: Verify failures**

Run: `.venv\Scripts\python.exe -m pytest tests/test_listing_validator.py -q`

Expected: FAIL because `listing_validator` does not exist.

- [ ] **Step 3: Implement deterministic validation**

Normalize Kodi color markup out of titles; calculate item count, unique-title
ratio, unique-URL ratio, thumbnail coverage, description coverage, mode set,
and host distribution. Reject mode names containing `category`, `categories`,
`login`, `logout`, `search`, or `genre` unless explicitly allowed. Treat an
item-count drop greater than `contract["max_count_drop_ratio"]` as broken only
when a successful baseline exists. Return all metrics and bounded redacted
evidence.

- [ ] **Step 4: Run tests and commit**

Run: `.venv\Scripts\python.exe -m pytest tests/test_listing_validator.py -q`

Expected: PASS.

Commit: `git commit -m "Add strict listing validation"`

### Task 3: Media Validator

**Files:**
- Create: `scripts/media_validator.py`
- Create: `tests/test_media_validator.py`

**Interfaces:**
- Consumes: `ValidationResult`.
- Produces: `validate_media(url: str, allowed_hosts: list[str], timeout: float = 15, session: requests.Session | None = None) -> ValidationResult`.

- [ ] **Step 1: Write failing HTTP-backed tests**

Use a local threaded HTTP server for direct MP4 bytes, byte ranges, HLS master
to media playlist to segment, DASH MPD to segment, redirects, redirect loops,
expired links, HTML returned with 200, malformed manifests, missing segments,
a disallowed host, and a Kodi URL with pipe-suffixed request headers.

```python
def test_hls_requires_a_media_segment(http_server):
    result = validate_media(http_server.url("/master.m3u8"), ["127.0.0.1"])
    assert result.passed is True
    assert result.metrics["media_kind"] == "hls"
    assert result.metrics["segment_bytes"] > 0
```

- [ ] **Step 2: Verify failures**

Run: `.venv\Scripts\python.exe -m pytest tests/test_media_validator.py -q`

Expected: FAIL because `media_validator` does not exist.

- [ ] **Step 3: Implement bounded probing**

Use one `requests.Session`, at most five redirects, a 64 KiB maximum response
read, and `Range: bytes=0-65535` for direct media. Split Kodi media values of
the form `URL|Header=Value&Referer=...`, URL-decode the header values, apply
them only to requests for that sample, and redact them from evidence. Parse HLS
using URI lines and
`#EXT-X-STREAM-INF`; parse DASH XML using `BaseURL` plus the first resolvable
segment template or initialization URL. Reject HTML signatures and challenge,
login, removal, or error text even on HTTP 200. Return only redacted URLs,
status, content type, redirect count, media kind, and byte count.

- [ ] **Step 4: Run tests and commit**

Run: `.venv\Scripts\python.exe -m pytest tests/test_media_validator.py -q`

Expected: PASS.

Commit: `git commit -m "Verify manifests and media bytes"`

### Task 4: Strict Runner and Report

**Files:**
- Modify: `scripts/live_smoke_test.py`
- Create: `scripts/strict_site_monitor.py`
- Modify: `tests/test_live_smoke_test.py`
- Create: `tests/test_strict_site_monitor.py`

**Interfaces:**
- Produces from live runner: top-level `listing_samples: list[dict]`, bounded by profile `sample_count`.
- Produces from live runner: `run_site_child(..., strict: bool = False) -> dict`.
- Produces: `evaluate_record(record: dict, profile: dict, baseline: dict | None = None) -> dict`.
- CLI: `python scripts/strict_site_monitor.py --site SITE --out DIR [--baseline FILE]`.

- [ ] **Step 1: Write failing capture and precedence tests**

Assert captured samples from `main`, `list`, or `search` retain only `name`,
`url`, `mode`, `icon`, and `desc`;
strict mode still invokes playback for a priority cam whose legacy profile has
`supports.play: false`;
one failing required stage yields `BROKEN`; a positive challenge classification
yields `BLOCKED`; exceptions before a trustworthy result yield
`HARNESS_ERROR`; and no result yields `NOT_TESTED`.

- [ ] **Step 2: Verify failures**

Run: `.venv\Scripts\python.exe -m pytest tests/test_live_smoke_test.py tests/test_strict_site_monitor.py -q`

Expected: FAIL on missing samples and strict evaluator.

- [ ] **Step 3: Expose bounded samples**

Add a defaulted `strict=False` argument. When `step_main`, `step_list`, or
`step_search` captures videos, copy the configured number into a separate
`listing_samples` list before later steps clear the capture buffer. In strict
mode, use `strict_contract.required_stages` instead of legacy harness skip flags
for listing/playback requirements. A cam may satisfy listing dispatch from
`main` without exposing a separate `List` function, but it must still invoke
the captured item's playback mode and produce a media URL. Preserve current
broad behavior when `strict` is false.

- [ ] **Step 4: Compose strict validation**

Load and validate the Tier 1 profile, call `run_site_child`, validate listing
samples, take the captured `steps.play.play_url`, validate its media, and apply
state precedence:

```python
if infrastructure_error:
    state = HealthState.HARNESS_ERROR
elif blocked_stage:
    state = HealthState.BLOCKED
elif any_required_stage_failed_or_skipped:
    state = HealthState.BROKEN
else:
    state = HealthState.HEALTHY
```

Write `strict_site_<site>.json` and `.md`; exit 0 only for `HEALTHY`, 1 for
site failures, and 2 for harness errors.

- [ ] **Step 5: Run tests and commit**

Run: `.venv\Scripts\python.exe -m pytest tests/test_live_smoke_test.py tests/test_strict_site_monitor.py -q`

Expected: PASS.

Commit: `git commit -m "Add strict priority site runner"`

### Task 5: Strict History and Recovery State

**Files:**
- Create: `scripts/strict_health_history.py`
- Create: `tests/test_strict_health_history.py`

**Interfaces:**
- Produces: `merge_reports(paths: list[Path], previous: dict | None) -> tuple[dict, dict]`.
- CLI outputs: `strict_health_latest.json`, `strict_health_latest.md`, and `strict_history.json`.

- [ ] **Step 1: Write failing history tests**

Test isolated report merging, missing-site `NOT_TESTED`, healthy-only baseline
updates, failure retention, bounded 14-run history, first recovery pass count
of one, second recovery pass count of two, and broad smoke data being ignored.

- [ ] **Step 2: Verify failures**

Run: `.venv\Scripts\python.exe -m pytest tests/test_strict_health_history.py -q`

Expected: FAIL because the history module does not exist.

- [ ] **Step 3: Implement merge and bounded history**

Store for each site `runs`, `consecutive_healthy`, `healthy_baseline`,
`open_failure_signature`, and `last_state`. Update `healthy_baseline` only on
`HEALTHY`; retain the newest 14 runs; render strict results before a clearly
separated “Basic coverage” section.

- [ ] **Step 4: Run tests and commit**

Run: `.venv\Scripts\python.exe -m pytest tests/test_strict_health_history.py -q`

Expected: PASS.

Commit: `git commit -m "Track strict site health history"`

### Task 6: Stable Issue Lifecycle

**Files:**
- Create: `scripts/generate_strict_triage_requests.py`
- Modify: `scripts/automate_triage.py`
- Modify: `scripts/ensure_labels.py`
- Create: `tests/test_generate_strict_triage_requests.py`
- Create: `tests/test_automate_triage.py`

**Interfaces:**
- Produces request actions: `CREATE_OR_REOPEN`, `UPDATE`, `CLOSE`, or `NONE`.
- Stable marker: `<!-- strict-site-health:SITE -->`.

- [ ] **Step 1: Write failing lifecycle tests**

Cover first `BROKEN`, first `BLOCKED`, unchanged signature, changed signature,
`HARNESS_ERROR`, one recovery pass, two recovery passes, and regression after a
closed issue. Mock `run_gh` and assert exact `gh issue` arguments.

- [ ] **Step 2: Verify failures**

Run: `.venv\Scripts\python.exe -m pytest tests/test_generate_strict_triage_requests.py tests/test_automate_triage.py -q`

Expected: FAIL on missing strict request generation and actions.

- [ ] **Step 3: Generate stable actions**

Use title `[Site Monitor] {site} is broken`, include the stable marker, failed
stage, classification, metrics, redacted evidence, reproduction command, and
artifact URL. Emit `UPDATE` only when the failure signature changes. Emit
`CLOSE` only at `consecutive_healthy == 2`. Route `HARNESS_ERROR` to
`[Site Monitor] Monitoring infrastructure failure`.

- [ ] **Step 4: Execute actions safely**

Search issues with `--state all` and the stable title; reopen closed issues with
`gh issue reopen`; use `tempfile.NamedTemporaryFile` for bodies/comments; close
with a recovery comment. Add labels `site-monitor`, `failure/blocked`, and
`failure/harness`.

- [ ] **Step 5: Run tests and commit**

Run: `.venv\Scripts\python.exe -m pytest tests/test_generate_strict_triage_requests.py tests/test_automate_triage.py -q`

Expected: PASS.

Commit: `git commit -m "Add strict site issue lifecycle"`

### Task 7: Kodi JSON-RPC Probe

**Files:**
- Create: `scripts/kodi_jsonrpc.py`
- Create: `scripts/kodi_site_probe.py`
- Create: `tests/test_kodi_jsonrpc.py`
- Create: `tests/test_kodi_site_probe.py`

**Interfaces:**
- Produces: `KodiClient.call(method: str, params: dict | None = None) -> Any`.
- Produces: `probe_site(client: KodiClient, site: str, strict_record: dict, timeout: float) -> dict`.

- [ ] **Step 1: Write failing client and probe tests**

Mock HTTP JSON-RPC responses for readiness, `Files.GetDirectory`,
`Player.Open`, `Player.GetActivePlayers`, `Player.GetItem`, JSON-RPC errors,
timeouts, incorrect item types, count mismatches, and playback never starting.

- [ ] **Step 2: Verify failures**

Run: `.venv\Scripts\python.exe -m pytest tests/test_kodi_jsonrpc.py tests/test_kodi_site_probe.py -q`

Expected: FAIL because the Kodi modules do not exist.

- [ ] **Step 3: Implement the transport**

POST JSON with `Content-Type: application/json` to `/jsonrpc`, increment request
IDs, raise a typed error for JSON-RPC `error`, and poll `JSONRPC.Ping` until the
configured timeout.

- [ ] **Step 4: Implement the site probe**

Call `Files.GetDirectory` with the plugin URL for the site's registered default
mode and request `file`, `filetype`, `label`, `thumbnail`, and `plot`. Compare
video count and URL hosts with the strict record. Call `Player.Open` for the
sampled plugin item, poll `Player.GetActivePlayers`, then confirm the active
item with `Player.GetItem`. Always stop playback after evidence capture.

- [ ] **Step 5: Run tests and commit**

Run: `.venv\Scripts\python.exe -m pytest tests/test_kodi_jsonrpc.py tests/test_kodi_site_probe.py -q`

Expected: PASS.

Commit: `git commit -m "Add Kodi runtime site probe"`

### Task 8: Daily Workflow Integration

**Files:**
- Modify: `.github/workflows/site-health.yml`
- Create: `scripts/merge_kodi_results.py`
- Create: `tests/test_merge_kodi_results.py`
- Modify: `docs/testing/LIVE_SMOKE_TESTING.md`
- Modify: `docs/testing/SITE_HEALTH_PROFILES.md`

**Interfaces:**
- Consumes all earlier CLI outputs.
- Produces the final strict summary, history, triage requests, and persisted artifacts.

- [ ] **Step 1: Write failing Kodi merge tests**

Verify a Kodi mismatch overrides `HEALTHY`, a Kodi infrastructure failure
becomes `HARNESS_ERROR`, a matching Kodi result preserves `HEALTHY`, and broad
results cannot override strict state.

- [ ] **Step 2: Verify failures**

Run: `.venv\Scripts\python.exe -m pytest tests/test_merge_kodi_results.py -q`

Expected: FAIL because the merge module does not exist.

- [ ] **Step 3: Add strict matrix jobs**

Generate `strict_matrix` in setup. Run one strict site per job with
FlareSolverr, always upload its JSON, and continue to report merging for exit
code 1 while failing immediately on exit code 2.

- [ ] **Step 4: Add packaged Kodi job**

Build the addon with `python build_repo_addons.py --out build/addons`, create a
clean Kodi profile with the web server enabled only on loopback, install the
addon and required repository dependencies, launch Kodi under Xvfb, wait for
`JSONRPC.Ping`, and run `kodi_site_probe.py` for the strict matrix. Pin the Kodi
major version used by CI and record it in every result. Kodi requires an X
window manager even in standalone mode; use the distribution package plus
`xvfb` and a minimal window manager rather than treating Kodi as a console-only
process.

- [ ] **Step 5: Merge, triage, and persist**

Merge Kodi results into strict results, update strict history, generate strict
triage actions, execute them, publish strict results first, and persist
`strict_health_latest.*` plus `strict_history.json` on `site-health`. Keep the
existing broad files unchanged and separately labeled.

- [ ] **Step 6: Update operator documentation**

Document strict states, profile fields, local listing/media commands, Kodi
requirements, artifact names, issue recovery rules, and the distinction
between basic coverage and trusted health.

- [ ] **Step 7: Run focused and full verification**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_site_health_types.py tests/test_listing_validator.py tests/test_media_validator.py tests/test_strict_site_monitor.py tests/test_strict_health_history.py tests/test_generate_strict_triage_requests.py tests/test_automate_triage.py tests/test_kodi_jsonrpc.py tests/test_kodi_site_probe.py tests/test_merge_kodi_results.py -q
.venv\Scripts\python.exe -m pytest -q
```

Expected: both commands PASS.

- [ ] **Step 8: Run a manual no-write production probe**

Run one video site, one cam site, and `thothub` without issue automation:

```powershell
.venv\Scripts\python.exe scripts/strict_site_monitor.py --site pornhub --out results/strict-manual
.venv\Scripts\python.exe scripts/strict_site_monitor.py --site chaturbate --out results/strict-manual
.venv\Scripts\python.exe scripts/strict_site_monitor.py --site thothub --out results/strict-manual
```

Expected: each command writes sanitized JSON/Markdown and any failure identifies
listing, playback resolution, media, blocking, or harness infrastructure
without persisting media.

- [ ] **Step 9: Commit workflow integration**

Commit: `git commit -m "Run trusted priority site monitoring daily"`

## Final Verification

- [ ] Run `git diff --check`.
- [ ] Run `.venv\Scripts\python.exe -m pytest -q`.
- [ ] Run `python scripts/generate_smoke_matrix.py --strict` and confirm the
  exact 17-site set with `thothub` present and `stripchat` absent.
- [ ] Inspect generated reports and confirm all sensitive query values are
  redacted.
- [ ] Trigger `site-health.yml` manually with issue automation disabled for the
  first calibration run.
- [ ] Confirm every priority site has a strict result and every missing result
  is `NOT_TESTED`, never `HEALTHY`.
- [ ] Enable issue automation and the daily schedule after calibration.

## Primary References

- Approved design: `docs/superpowers/specs/2026-07-29-priority-site-monitoring-design.md`
- Kodi JSON-RPC transport: `https://kodi.wiki/view/JSON-RPC_API`
- Kodi v12 `Files.GetDirectory`, `Player.Open`, and player methods:
  `https://kodi.wiki/view/JSON-RPC_API/v12`
- Kodi Linux startup requirements:
  `https://kodi.wiki/view/HOW-TO%3AAutostart_Kodi_for_Linux`
