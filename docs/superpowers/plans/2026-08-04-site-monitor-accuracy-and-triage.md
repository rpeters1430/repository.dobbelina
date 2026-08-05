# Site Monitor Accuracy and Triage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct strict site-health stage classification and media handling, reuse stable GitHub issues, and close the confirmed false-positive issues with accurate diagnostics.

**Architecture:** Keep collection, evaluation, hosted-page resolution, and GitHub triage as separate units. The live harness will capture only video entries for listing validation and expose a small hosted-source resolver; the strict evaluator will apply access/listing/playback/media precedence; the workflow will feed existing issue state into the already-tested triage generator.

**Tech Stack:** Python 3.11, pytest, GitHub Actions YAML, GitHub CLI

## Global Constraints

- Do not add `tap4porn.cc`; both tested domains return HTTP 403 after FlareSolverr processing.
- Do not add proxies, CAPTCHA services, or a new browser stack.
- Do not weaken strict listing, playback, or media requirements.
- Treat website HTTP 403 through a functioning FlareSolverr as `BLOCKED` and FlareSolverr connectivity failure as `HARNESS_ERROR`.
- Keep Ask4Porn #279 open until two complete healthy runs.
- Preserve the user's unrelated `.claude/settings.local.json` modification.

---

### Task 1: Correct strict state precedence and FlareSolverr classification

**Files:**
- Modify: `scripts/strict_site_monitor.py:22-140`
- Test: `tests/test_strict_site_monitor.py`

**Interfaces:**
- Consumes: execution records returned by `run_site_child()`.
- Produces: `classify_flaresolverr_failure(record: dict[str, Any]) -> tuple[str, str] | None` and corrected `evaluate_record()` reports.

- [ ] **Step 1: Add failing strict-evaluator tests**

Append tests that prove a skipped playback sample URL is not treated as media, a functioning FlareSolverr website 403 is blocked at listing, and a FlareSolverr connection failure is infrastructure failure:

```python
def test_skipped_playback_does_not_probe_sample_page_as_media(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("media validator must not receive a detail page")

    monkeypatch.setattr("scripts.strict_site_monitor.validate_media", fail_if_called)
    record = {
        "site": "xnxx",
        "status": "PASS",
        "listing_samples": [sample_video(i) for i in range(1, 6)],
        "steps": {
            "list": {"status": "PASS"},
            "play": {
                "status": "SKIP",
                "sample_url": "https://example.test/watch/deleted",
                "play_url": "",
            },
        },
    }

    report = evaluate_record(record, sample_profile())

    assert report["state"] == HealthState.BROKEN
    assert report["failed_stage"] == "playback"
    assert report["classification"] == "PLAYBACK_FAILED"


def test_flaresolverr_website_403_is_listing_block():
    record = {
        "site": "ask4porn",
        "status": "PASS",
        "listing_samples": [],
        "steps": {
            "list": {"status": "SKIP", "message": "FlareSolverr required but unavailable in harness"},
            "play": {"status": "SKIP"},
        },
        "notifications": [
            "FlareSolverr Failed: FlareSolverr solved challenge but got HTTP 403 from website"
        ],
    }

    report = evaluate_record(record, sample_profile())

    assert report["state"] == HealthState.BLOCKED
    assert report["failed_stage"] == "listing"
    assert report["classification"] == "BLOCKED"


def test_flaresolverr_connection_failure_is_harness_error():
    record = {
        "site": "ask4porn",
        "status": "PASS",
        "listing_samples": [],
        "steps": {"list": {"status": "SKIP"}, "play": {"status": "SKIP"}},
        "notifications": [
            "FlareSolverr Failed: Failed to connect to FlareSolverr: connection refused"
        ],
    }

    report = evaluate_record(record, sample_profile())

    assert report["state"] == HealthState.HARNESS_ERROR
    assert report["failed_stage"] == "harness"
    assert report["exit_code"] == 2
```

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_strict_site_monitor.py -q
```

Expected: the sample-page test calls `validate_media`, and the two FlareSolverr tests return incorrect states.

- [ ] **Step 3: Implement minimal classification and precedence changes**

Add a focused classifier and use only a real `play_url` for media validation:

```python
def classify_flaresolverr_failure(record: dict[str, Any]) -> tuple[str, str] | None:
    messages = [str(message) for message in record.get("notifications", [])]
    messages.extend(
        str(step.get("message", ""))
        for step in record.get("steps", {}).values()
        if isinstance(step, dict)
    )
    for message in messages:
        normalized = message.lower()
        if "flaresolverr" not in normalized:
            continue
        if "http 403 from website" in normalized or "challenge was not solved" in normalized:
            return HealthState.BLOCKED, message
        if any(token in normalized for token in ("failed to connect", "connection refused", "not available")):
            return HealthState.HARNESS_ERROR, message
    return None
```

In `evaluate_record()`:

```python
fs_failure = classify_flaresolverr_failure(record)
if fs_failure:
    state, message = fs_failure
    failed_stage = "listing" if state == HealthState.BLOCKED else "harness"
    classification = "BLOCKED" if state == HealthState.BLOCKED else "HARNESS_ERROR"
    return {
        "site": site_name,
        "state": state,
        "exit_code": 1 if state == HealthState.BLOCKED else 2,
        "failed_stage": failed_stage,
        "classification": classification,
        "message": message,
        "failure_signature": failure_signature({
            "state": state,
            "failed_stage": failed_stage,
            "classification": classification,
            "message": message,
        }),
        "record": record,
    }
```

Replace the media input fallback:

```python
play_url = play_step.get("play_url", "")
```

Evaluate failed listing first, then required playback status, then `media_res`.

- [ ] **Step 4: Run strict-evaluator tests and verify GREEN**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_strict_site_monitor.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit the strict evaluator repair**

```powershell
git add scripts\strict_site_monitor.py tests\test_strict_site_monitor.py
git commit -m "Fix strict monitor failure classification"
```

### Task 2: Capture video listing samples only

**Files:**
- Modify: `scripts/live_smoke_test.py:672-738`
- Test: `tests/test_live_smoke_test.py`

**Interfaces:**
- Consumes: callbacks from `addDir` and `addDownLink`.
- Produces: `record_listing_sample(samples: list[dict[str, Any]], *, is_video: bool, name: Any, url: Any, mode: Any, icon: Any = "", desc: Any = "") -> None`.

- [ ] **Step 1: Add failing video-only capture tests**

```python
def test_record_listing_sample_ignores_navigation_directories():
    samples = []

    live_smoke_test.record_listing_sample(
        samples,
        is_video=False,
        name="Categories",
        url="https://example.test/categories",
        mode="example.Categories",
    )

    assert samples == []


def test_record_listing_sample_captures_unique_video_entries():
    samples = []
    kwargs = {
        "is_video": True,
        "name": "Video",
        "url": "https://example.test/watch/1",
        "mode": "example.Playvid",
        "icon": "https://example.test/thumb.jpg",
        "desc": "Description",
    }

    live_smoke_test.record_listing_sample(samples, **kwargs)
    live_smoke_test.record_listing_sample(samples, **kwargs)

    assert samples == [{
        "name": "Video",
        "url": "https://example.test/watch/1",
        "mode": "example.Playvid",
        "icon": "https://example.test/thumb.jpg",
        "desc": "Description",
    }]
```

- [ ] **Step 2: Run capture tests and verify RED**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_live_smoke_test.py -q
```

Expected: failure because `record_listing_sample` does not exist.

- [ ] **Step 3: Add the helper and wire only download callbacks to it**

```python
def record_listing_sample(samples, *, is_video, name, url, mode, icon="", desc=""):
    if not is_video:
        return
    name_str = str(name or "")
    url_str = str(url or "")
    if not name_str or not url_str or any(sample["url"] == url_str for sample in samples):
        return
    samples.append({
        "name": name_str,
        "url": url_str,
        "mode": str(mode or ""),
        "icon": str(icon or ""),
        "desc": str(desc or ""),
    })
```

Remove the nested `record_sample`. Do not record `fake_add_dir` output. Call
`record_listing_sample(..., is_video=True, ...)` from `fake_add_down`.

- [ ] **Step 4: Run live-smoke and strict-monitor tests and verify GREEN**

```powershell
.venv\Scripts\python.exe -m pytest tests\test_live_smoke_test.py tests\test_strict_site_monitor.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit video-only listing capture**

```powershell
git add scripts\live_smoke_test.py tests\test_live_smoke_test.py
git commit -m "Validate video listing entries only"
```

### Task 3: Resolve hosted pages without treating HTML as media

**Files:**
- Modify: `scripts/live_smoke_test.py:500-520,764-807`
- Test: `tests/test_live_smoke_test.py`

**Interfaces:**
- Consumes: a ResolveURL source or HTTP(S) hosted-page string and an HTML fetch callable.
- Produces: `extract_direct_media_url(html: str) -> str` and `resolve_harness_hosted_source(source: Any, fetch_html: Callable[[str], str]) -> str`.

- [ ] **Step 1: Add failing hosted-source tests**

```python
def test_extract_direct_media_url_finds_hls():
    html = "html5player.setVideoHLS('https://cdn.example.test/master.m3u8')"
    assert live_smoke_test.extract_direct_media_url(html) == "https://cdn.example.test/master.m3u8"


def test_resolve_harness_hosted_source_fetches_embed_page():
    fetched = []

    def fetch_html(url):
        fetched.append(url)
        return '<script>player("https://cdn.example.test/video.mp4")</script>'

    result = live_smoke_test.resolve_harness_hosted_source(
        "https://host.example.test/embed/42", fetch_html
    )

    assert result == "https://cdn.example.test/video.mp4"
    assert fetched == ["https://host.example.test/embed/42"]


def test_resolve_harness_hosted_source_rejects_html_page_without_media():
    result = live_smoke_test.resolve_harness_hosted_source(
        "https://host.example.test/embed/42", lambda url: "<html>No media</html>"
    )
    assert result == ""
```

- [ ] **Step 2: Run hosted-source tests and verify RED**

```powershell
.venv\Scripts\python.exe -m pytest tests\test_live_smoke_test.py -q
```

Expected: the two helper functions are missing.

- [ ] **Step 3: Implement bounded generic hosted-page extraction**

```python
def extract_direct_media_url(html: str) -> str:
    for pattern in (
        r"html5player\.setVideoHLS\(['\"]([^'\"]+)",
        r"(https?://[^\s\"'\\,\]]+\.mp4(?:[^\s\"'\\,\]]*)?)",
        r"(https?://[^\s\"'\\,\]]+\.m3u8(?:[^\s\"'\\,\]]*)?)",
    ):
        match = re.search(pattern, html or "", re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def resolve_harness_hosted_source(source, fetch_html):
    resolved = source
    if hasattr(source, "resolve"):
        try:
            resolved = source.resolve()
        except Exception:
            return ""
    resolved = str(resolved or "")
    if not resolved.startswith(("http://", "https://")):
        return ""
    if any(extension in resolved.lower() for extension in (".mp4", ".m3u8")):
        return resolved
    return extract_direct_media_url(fetch_html(resolved))
```

Reuse `extract_direct_media_url` in `FakeVideoPlayer.play_from_html`. In
`play_from_link_to_resolve`, append only the URL returned by
`resolve_harness_hosted_source(source, lambda url: utils.getHtml(url, ""))`.

- [ ] **Step 4: Run live-smoke tests and verify GREEN**

```powershell
.venv\Scripts\python.exe -m pytest tests\test_live_smoke_test.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit hosted-page harness resolution**

```powershell
git add scripts\live_smoke_test.py tests\test_live_smoke_test.py
git commit -m "Resolve hosted media in smoke harness"
```

### Task 4: Feed existing issues into strict triage

**Files:**
- Modify: `.github/workflows/site-health.yml:156-162`
- Test: `tests/test_site_health_workflow.py`
- Test: `tests/test_generate_strict_triage_requests.py`

**Interfaces:**
- Consumes: GitHub issue JSON fields `number`, `title`, `body`, and `state`.
- Produces: `results/existing_site_monitor_issues.json` passed through `--existing-issues`.

- [ ] **Step 1: Add failing workflow and reopen tests**

Create `tests/test_site_health_workflow.py`:

```python
from pathlib import Path


WORKFLOW = Path(".github/workflows/site-health.yml")


def test_site_health_workflow_passes_existing_issues_to_triage_generator():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "gh issue list --state all" in workflow
    assert "--json number,title,body,state" in workflow
    assert "> results/existing_site_monitor_issues.json" in workflow
    assert "--existing-issues results/existing_site_monitor_issues.json" in workflow
```

Append to `tests/test_generate_strict_triage_requests.py`:

```python
def test_closed_existing_issue_is_reopened_instead_of_duplicated():
    latest, history = sample_latest_and_history(state=HealthState.BROKEN, sig="sig100")
    existing = [{
        "number": 42,
        "title": "[Site Monitor] pornhub is broken",
        "body": "<!-- strict-site-health:pornhub -->",
        "state": "CLOSED",
    }]

    requests = generate_strict_triage_requests(latest, history, existing_issues=existing)

    assert requests[0]["action"] == "CREATE_OR_REOPEN"
    assert requests[0]["issue_number"] == 42
```

- [ ] **Step 2: Run workflow and triage tests and verify RED**

```powershell
.venv\Scripts\python.exe -m pytest tests\test_site_health_workflow.py tests\test_generate_strict_triage_requests.py -q
```

Expected: the workflow-content test fails because existing issues are not fetched or passed. The reopen test should pass, confirming the generator already supports the intended behavior.

- [ ] **Step 3: Fetch and pass existing issues in the report job**

Replace the generator step with:

```yaml
      - name: Generate strict triage requests
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh issue list --state all --limit 1000 \
            --json number,title,body,state \
            > results/existing_site_monitor_issues.json
          python scripts/generate_strict_triage_requests.py \
            --latest results/strict_health_latest.json \
            --history results/strict_history.json \
            --existing-issues results/existing_site_monitor_issues.json \
            --out results/strict_triage_requests.json
```

- [ ] **Step 4: Run workflow and triage tests and verify GREEN**

```powershell
.venv\Scripts\python.exe -m pytest tests\test_site_health_workflow.py tests\test_generate_strict_triage_requests.py tests\test_automate_triage.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit issue reuse wiring**

```powershell
git add .github\workflows\site-health.yml tests\test_site_health_workflow.py tests\test_generate_strict_triage_requests.py
git commit -m "Reuse existing site monitor issues"
```

### Task 5: Verify the complete repair

**Files:**
- Verify only: all files changed in Tasks 1-4

**Interfaces:**
- Consumes: completed implementation and test suite.
- Produces: fresh verification evidence for local correctness and repository cleanliness.

- [ ] **Step 1: Run the focused regression suite**

```powershell
.venv\Scripts\python.exe -m pytest tests\test_strict_site_monitor.py tests\test_live_smoke_test.py tests\test_generate_strict_triage_requests.py tests\test_automate_triage.py tests\test_site_health_workflow.py -q
```

Expected: all focused tests pass with zero failures.

- [ ] **Step 2: Run the complete Python test suite**

```powershell
.venv\Scripts\python.exe -m pytest -q
```

Expected: all tests pass, or any unrelated pre-existing failures are documented with exact names and output.

- [ ] **Step 3: Check patch hygiene and user-change isolation**

```powershell
git diff --check
git status --short
git diff -- .claude\settings.local.json
```

Expected: no whitespace errors; `.claude/settings.local.json` remains the user's untouched modification.

### Task 6: Close confirmed false-positive GitHub issues

**Files:**
- No repository files.

**Interfaces:**
- Consumes: verified implementation results and issue targets authorized by the user.
- Produces: diagnostic comments and closed state for #276, #280, #281, and #282; leaves #279 open.

- [ ] **Step 1: Reconfirm exact issue targets and current states**

```powershell
gh issue view 276 --repo rpeters1430/repository.dobbelina --json number,title,state,url
gh issue view 280 --repo rpeters1430/repository.dobbelina --json number,title,state,url
gh issue view 281 --repo rpeters1430/repository.dobbelina --json number,title,state,url
gh issue view 282 --repo rpeters1430/repository.dobbelina --json number,title,state,url
gh issue view 279 --repo rpeters1430/repository.dobbelina --json number,title,state,url
```

Expected: #279 remains the Ask4Porn issue; only #276, #280, #281, and #282 are closure targets.

- [ ] **Step 2: Comment and close PornKai issues**

Use this comment on #276 and #280:

```text
Closing as a strict-monitor false positive. The harness treated an unresolved third-party embed page as media and classified its HTML response as blocked. Local strict reproduction resolved and verified real media. The monitor now distinguishes hosted-page resolution from media verification and the workflow reuses the stable site issue.
```

Run `gh issue comment` followed by `gh issue close --reason "not planned"` for each issue.

- [ ] **Step 3: Comment and close XNXX #281**

```text
Closing as a transient sample plus monitor-classification false positive. The selected detail page did not resolve playback, after which the monitor incorrectly probed that HTML page as media. XNXX passed the full strict contract locally; media probing now requires an actual resolved playback URL.
```

Run `gh issue comment 281` and `gh issue close 281 --reason "not planned"`.

- [ ] **Step 4: Comment and close YouPorn #282**

```text
Closing as a runner-dependent listing failure that was mislabeled as playback. Navigation/category entries were counted as video samples even though no videos were emitted. Strict listing validation now considers downloadable video entries only, so a recurrence will produce the correct listing-stage issue.
```

Run `gh issue comment 282` and `gh issue close 282 --reason "not planned"`.

- [ ] **Step 5: Verify final GitHub state**

```powershell
gh issue list --repo rpeters1430/repository.dobbelina --state open --limit 20 --json number,title,url
```

Expected: #279 remains open; #276, #280, #281, and #282 are closed.

