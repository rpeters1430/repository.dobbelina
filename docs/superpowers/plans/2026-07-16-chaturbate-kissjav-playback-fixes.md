# Chaturbate and KissJav Playback Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore Chaturbate public-room playback through its AJAX HLS endpoint and correct KissJav direct-media referrers.

**Architecture:** Preserve the fork's dossier-driven Chaturbate proxy behavior and add an AJAX HLS fallback only when the dossier is unavailable. Keep KissJav's existing decoder and change only the request referer.

**Tech Stack:** Python, pytest, Kodi site modules.

## Global Constraints

- Preserve existing Chaturbate proxy and non-public-room behavior.
- Do not import upstream legacy implementations over the fork's BeautifulSoup modules.
- Add focused regression tests before production changes.

---

### Task 1: Add regression tests

**Files:**
- Modify: `tests/sites/test_chaturbate.py`
- Modify: `tests/sites/test_kissjav.py`

**Interfaces:**
- Consumes: `chaturbate.Playvid(url, name)` and `kissjav.Playvid(url, name, download=None)`.
- Produces: tests that assert AJAX HLS fallback and root-site KissJav referer behavior.

- [ ] **Step 1: Write failing tests**

```python
def test_playvid_falls_back_to_ajax_hls_when_dossier_is_missing(monkeypatch):
    # Mock an empty room page and a public get_edge_hls_url_ajax response.
    # Assert the resolved stream contains the returned HLS URL.

def test_playvid_uses_site_url_as_media_referer(monkeypatch):
    # Mock a KissJav page with video_url and assert the direct link ends in site.url.
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv\\Scripts\\python.exe -m pytest tests\\sites\\test_chaturbate.py tests\\sites\\test_kissjav.py -q`

Expected: the new assertions fail before the production changes.

### Task 2: Add minimal playback fallbacks

**Files:**
- Modify: `plugin.video.cumination/resources/lib/sites/chaturbate.py:434`
- Modify: `plugin.video.cumination/resources/lib/sites/kissjav.py:296`

**Interfaces:**
- Consumes: `utils.get_html_with_cloudflare_retry`, `utils._getHtml`, and `HTTP_HEADERS_IPAD`.
- Produces: a public-room HLS URL when `initialRoomDossier` is absent, and a KissJav root-site referer.

- [ ] **Step 1: Implement the Chaturbate fallback**

```python
slug = url.rstrip('/').rsplit('/', 1)[-1]
headers = HTTP_HEADERS_IPAD.copy()
headers.update({'X-Requested-With': 'XMLHttpRequest', 'Referer': url})
response = json.loads(utils._getHtml(bu + 'get_edge_hls_url_ajax/', headers=headers,
                                    data={'room_slug': slug, 'bandwidth': 'high'}))
```

Use `response['url']` only when `room_status == 'public'`, preserving dossier values when present.

- [ ] **Step 2: Implement the KissJav referer correction**

```python
vp.play_from_direct_link(surl + '|referer=' + site.url)
```

- [ ] **Step 3: Run focused tests**

Run: `.venv\\Scripts\\python.exe -m pytest tests\\sites\\test_chaturbate.py tests\\sites\\test_kissjav.py -q`

Expected: PASS.

### Task 3: Verify live behavior and update tracking

**Files:**
- Modify: `docs/development/UPSTREAM_SYNC.md`

- [ ] **Step 1: Run live smoke checks**

Run: `$env:PYTHONIOENCODING='utf-8'; .venv\\Scripts\\python.exe scripts\\live_smoke_test.py --site chaturbate kissjav --steps main,list,play --site-timeout 90 --timeout 25`

Expected: both sites pass supported checks.

- [ ] **Step 2: Record source commits and validation in the upstream ledger**

Add one 2026-07-16 session entry for `99c93d13`, `665842a7`, and `8acaa5fc` with the focused-test and smoke-test result.
