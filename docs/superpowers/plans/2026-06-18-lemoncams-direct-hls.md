# LemonCams Direct HLS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Play standard LemonCams HLS streams directly with LemonCams request headers instead of passing them through Stripchat's manifest proxy.

**Architecture:** `lemoncams.Playvid` will resolve a cached or refreshed LemonCams stream URL, construct the Kodi URL-header suffix, and hand it directly to `utils.VideoPlayer` configured for inputstream.adaptive. Stripchat playback remains unchanged and is no longer a LemonCams dependency.

**Tech Stack:** Python, pytest, Kodi `VideoPlayer`, inputstream.adaptive URL headers

## Global Constraints

- Use LemonCams as the `Referer` and `Origin`.
- Include `manifest_headers=1` for child playlists and media segments.
- Refresh through `_find_model_stream(provider, username)` only when no cached URL is supplied.
- Preserve existing invalid-model, unsupported-provider, and offline notifications.
- Do not modify Stripchat playback or proxy behavior.

---

### Task 1: Direct LemonCams HLS Playback

**Files:**
- Modify: `tests/sites/test_lemoncams.py`
- Modify: `plugin.video.cumination/resources/lib/sites/lemoncams.py`

**Interfaces:**
- Consumes: `_parse_model_identifier(value) -> (provider, username, stream_url)`
- Consumes: `_find_model_stream(provider, username) -> str`
- Produces: `Playvid(url, name)` direct HLS playback through `utils.VideoPlayer`

- [ ] **Step 1: Replace delegation tests with failing direct-playback tests**

Update `tests/sites/test_lemoncams.py` so cached playback asserts:

```python
def test_playvid_plays_cached_hls_directly_with_lemoncams_headers(monkeypatch):
    played = []

    class FakeVideoPlayer:
        def __init__(self, name, IA_check=None):
            assert name == "model1"
            assert IA_check == "IA"

        def play_from_direct_link(self, url):
            played.append(url)

    monkeypatch.setattr(lemoncams.utils, "VideoPlayer", FakeVideoPlayer)

    lemoncams.Playvid(
        "https://www.lemoncams.com/stripchat/model1|"
        "https://edge.example/master.m3u8",
        "Model 1",
    )

    assert len(played) == 1
    assert played[0].startswith("https://edge.example/master.m3u8|")
    assert "User-Agent=" in played[0]
    assert "Referer=https%3A//www.lemoncams.com/" in played[0]
    assert "Origin=https%3A//www.lemoncams.com/" in played[0]
    assert "manifest_headers=1" in played[0]
```

Add an uncached refresh test:

```python
def test_playvid_refreshes_missing_stream_before_direct_playback(monkeypatch):
    played = []
    searches = []

    class FakeVideoPlayer:
        def __init__(self, name, IA_check=None):
            assert name == "model1"
            assert IA_check == "IA"

        def play_from_direct_link(self, url):
            played.append(url)

    monkeypatch.setattr(lemoncams.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(
        lemoncams,
        "_find_model_stream",
        lambda provider, username: (
            searches.append((provider, username))
            or "https://edge.example/refreshed.m3u8"
        ),
    )

    lemoncams.Playvid("https://www.lemoncams.com/stripchat/model1", "Model 1")

    assert searches == [("stripchat", "model1")]
    assert played[0].startswith("https://edge.example/refreshed.m3u8|")
```

Add an unavailable-stream test:

```python
def test_playvid_notifies_when_refreshed_stream_is_missing(monkeypatch):
    notifications = []

    monkeypatch.setattr(lemoncams, "_find_model_stream", lambda *args: "")
    monkeypatch.setattr(
        lemoncams.utils,
        "notify",
        lambda heading, message, *args, **kwargs: notifications.append(
            (heading, message)
        ),
    )

    lemoncams.Playvid("https://www.lemoncams.com/stripchat/model1", "Model 1")

    assert notifications == [
        ("LemonCams", "Model offline or no stream found")
    ]
```

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests\sites\test_lemoncams.py -q
```

Expected: the new direct-playback tests fail because `Playvid` still delegates to `stripchat_playvid`.

- [ ] **Step 3: Implement the minimal direct-HLS path**

In `plugin.video.cumination/resources/lib/sites/lemoncams.py`:

1. Remove:

```python
from resources.lib.sites.stripchat import Playvid as stripchat_playvid
```

2. Replace the final Stripchat delegation in `Playvid` with:

```python
    playable_url = stream_url or _find_model_stream(provider, username)
    if not playable_url:
        utils.notify("LemonCams", "Model offline or no stream found")
        return

    headers = {
        "User-Agent": utils.USER_AGENT,
        "Referer": site.url,
        "Origin": site.url,
    }
    header_string = (
        "User-Agent={0}&Referer={1}&Origin={2}&manifest_headers=1"
    ).format(
        urllib_parse.quote(headers["User-Agent"], safe=""),
        urllib_parse.quote(headers["Referer"], safe="/"),
        urllib_parse.quote(headers["Origin"], safe="/"),
    )

    player = utils.VideoPlayer(username, IA_check="IA")
    player.play_from_direct_link("{}|{}".format(playable_url, header_string))
```

- [ ] **Step 4: Run focused LemonCams tests and verify GREEN**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests\sites\test_lemoncams.py -q
```

Expected: all LemonCams tests pass.

- [ ] **Step 5: Run related Stripchat regression tests**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests\sites\test_lemoncams.py tests\sites\test_stripchat.py -q
```

Expected: LemonCams tests pass and existing environment-dependent Stripchat tests either pass or retain their existing skips.

- [ ] **Step 6: Run a live read-only LemonCams smoke test**

Run:

```powershell
$env:PYTHONIOENCODING='utf-8'
.venv\Scripts\python.exe scripts\live_smoke_test.py --site lemoncams --steps main,list,play --timeout 45 --site-timeout 180
```

Expected: listing and playback extraction complete without routing through the Stripchat proxy. If the harness cannot emulate Kodi playback, document the limitation and retain the earlier HTTP 200 manifest/segment evidence.

- [ ] **Step 7: Commit the implementation**

```powershell
git add tests\sites\test_lemoncams.py plugin.video.cumination\resources\lib\sites\lemoncams.py
git commit -m "Fix LemonCams direct HLS playback"
```
