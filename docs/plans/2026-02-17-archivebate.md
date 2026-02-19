# Archivebate Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add Archivebate (cam-archive site) as a new Cumination site plugin that lists
videos via a Livewire two-step fetch and plays them through MixDrop/ResolveURL.

**Architecture:** `requests.Session` handles the GET→CSRF→POST Livewire fetch inside a
private `_livewire_list()` helper. `Playvid` uses `utils.getHtml()` since the watch page
is fully server-rendered. No pagination in v1.

**Tech Stack:** Python, BeautifulSoup4, requests, Kodi AdultSite framework, ResolveURL (MixDrop)

**Reference docs:**
- `docs/sites/ARCHIVEBATE_ANALYSIS.md` — confirmed selectors and Livewire payload structure
- `docs/plans/2026-02-17-archivebate-design.md` — approved design

---

## Task 1: Create HTML fixtures

**Files:**
- Create: `tests/fixtures/sites/archivebate_list.html`
- Create: `tests/fixtures/sites/archivebate_video.html`

These are synthetic fixture files that replicate what the real site returns. They do NOT
need to be fetched live — write them by hand based on the confirmed selectors in the
analysis doc.

**Step 1: Create the listing fixture (Livewire fragment)**

This is the HTML that comes back in `lw_data['effects']['html']` from the Livewire POST.
It contains `<section class="video_item">` elements.

Create `tests/fixtures/sites/archivebate_list.html`:

```html
<div>
  <section class="video_item">
    <a href="https://archivebate.com/watch/111111">
      <video class="video-splash-mov" poster="https://cdn.archivebate.com/thumb1.jpg"></video>
    </a>
    <a href="https://archivebate.com/profile/performer_one">performer_one</a>
    <div class="duration"><span>14:01</span></div>
  </section>
  <section class="video_item">
    <a href="https://archivebate.com/watch/222222">
      <video class="video-splash-mov" poster="https://cdn.archivebate.com/thumb2.jpg"></video>
    </a>
    <a href="https://archivebate.com/profile/performer_two">performer_two</a>
    <div class="duration"><span>1:48:44</span></div>
  </section>
  <section class="video_item">
    <a href="https://archivebate.com/watch/333333">
      <video class="video-splash-mov" poster="https://cdn.archivebate.com/thumb3.jpg"></video>
    </a>
    <a href="https://archivebate.com/profile/performer_three">performer_three</a>
    <div class="duration"><span>45:22</span></div>
  </section>
</div>
```

**Step 2: Create the video page fixture**

This is a static `/watch/NNNNNN` page. The MixDrop iframe src is in the HTML.

Create `tests/fixtures/sites/archivebate_video.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <title>performer_one Chaturbate webcam recordings, Archivebate</title>
  <meta property="og:image" content="https://cdn.archivebate.com/thumb1.jpg">
</head>
<body>
  <iframe class="video-frame" src="https://mixdrop.ag/e/1n4gew0pb0ov1x" allowfullscreen></iframe>
</body>
</html>
```

**Step 3: Verify files exist**

```bash
ls tests/fixtures/sites/archivebate_list.html tests/fixtures/sites/archivebate_video.html
```

Expected: both files listed with no errors.

---

## Task 2: Write the failing tests

**Files:**
- Create: `tests/sites/test_archivebate.py`

**Step 1: Write the test file**

The key challenge is mocking `requests.Session`. We patch it at the module level once
the archivebate module is imported. The `_livewire_list` function calls:
1. `session.get(url)` — needs to return a mock response with `.text` containing csrf meta + wire:initial-data
2. `session.post(...)` — needs to return a mock response with `.json()` returning `{'effects': {'html': fragment}, 'serverMemo': {}}`

Create `tests/sites/test_archivebate.py`:

```python
"""Tests for archivebate site implementation."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from resources.lib.sites import archivebate

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites"


def load_fixture(name):
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def make_session_mock(fragment_html):
    """Build a mock requests.Session that returns Livewire data."""
    # Minimal page HTML with csrf token and wire:initial-data
    page_html = (
        '<meta name="csrf-token" content="test-csrf-token">'
        ' <div wire:initial-data="{&quot;fingerprint&quot;:{&quot;id&quot;:&quot;abc123&quot;,'
        '&quot;name&quot;:&quot;home-videos&quot;},&quot;serverMemo&quot;:{&quot;data&quot;:{}}}"'
        ' wire:init="loadVideos"></div>'
    )

    get_response = MagicMock()
    get_response.text = page_html

    post_response = MagicMock()
    post_response.json.return_value = {
        "effects": {"html": fragment_html},
        "serverMemo": {"data": {}},
    }

    session_instance = MagicMock()
    session_instance.get.return_value = get_response
    session_instance.post.return_value = post_response

    session_class = MagicMock(return_value=session_instance)
    return session_class


# --- List tests ---

def test_list_parses_video_items(monkeypatch):
    """List() correctly extracts url, thumb, and performer name from Livewire fragment."""
    fragment = load_fixture("archivebate_list.html")
    session_mock = make_session_mock(fragment)

    downloads = []

    monkeypatch.setattr(archivebate.requests, "Session", session_mock)
    monkeypatch.setattr(archivebate.site, "add_download_link",
                        lambda name, url, mode, icon, **kw: downloads.append(
                            {"name": name, "url": url, "icon": icon}
                        ))
    monkeypatch.setattr(archivebate.utils, "eod", lambda: None)

    archivebate.List("https://archivebate.com/")

    assert len(downloads) == 3

    assert downloads[0]["name"] == "performer_one"
    assert downloads[0]["url"] == "https://archivebate.com/watch/111111"
    assert downloads[0]["icon"] == "https://cdn.archivebate.com/thumb1.jpg"

    assert downloads[1]["name"] == "performer_two"
    assert downloads[1]["url"] == "https://archivebate.com/watch/222222"
    assert downloads[1]["icon"] == "https://cdn.archivebate.com/thumb2.jpg"

    assert downloads[2]["name"] == "performer_three"
    assert downloads[2]["url"] == "https://archivebate.com/watch/333333"
    assert downloads[2]["icon"] == "https://cdn.archivebate.com/thumb3.jpg"


def test_list_handles_empty_fragment(monkeypatch):
    """List() handles an empty Livewire fragment without crashing."""
    session_mock = make_session_mock("<div></div>")

    downloads = []

    monkeypatch.setattr(archivebate.requests, "Session", session_mock)
    monkeypatch.setattr(archivebate.site, "add_download_link",
                        lambda *a, **k: downloads.append(a))
    monkeypatch.setattr(archivebate.utils, "eod", lambda: None)

    archivebate.List("https://archivebate.com/")

    assert len(downloads) == 0


def test_list_skips_items_without_watch_link(monkeypatch):
    """List() skips section elements that have no /watch/ link."""
    bad_fragment = """
    <div>
      <section class="video_item">
        <!-- no watch link -->
        <a href="https://archivebate.com/profile/someone">someone</a>
      </section>
      <section class="video_item">
        <a href="https://archivebate.com/watch/999999">
          <video class="video-splash-mov" poster="https://cdn.archivebate.com/t.jpg"></video>
        </a>
        <a href="https://archivebate.com/profile/good_performer">good_performer</a>
      </section>
    </div>
    """
    session_mock = make_session_mock(bad_fragment)

    downloads = []

    monkeypatch.setattr(archivebate.requests, "Session", session_mock)
    monkeypatch.setattr(archivebate.site, "add_download_link",
                        lambda name, url, mode, icon, **kw: downloads.append(name))
    monkeypatch.setattr(archivebate.utils, "eod", lambda: None)

    archivebate.List("https://archivebate.com/")

    assert len(downloads) == 1
    assert downloads[0] == "good_performer"


# --- Playvid tests ---

def test_playvid_extracts_mixdrop_url(monkeypatch):
    """Playvid() extracts the MixDrop embed URL from iframe.video-frame."""
    html = load_fixture("archivebate_video.html")

    resolved = []

    fake_vp = MagicMock()
    fake_vp.play_from_link_to_resolve.side_effect = lambda url: resolved.append(url)

    monkeypatch.setattr(archivebate.utils, "getHtml", lambda url, referer=None: html)
    monkeypatch.setattr(archivebate.utils, "VideoPlayer", lambda *a, **k: fake_vp)

    archivebate.Playvid("https://archivebate.com/watch/111111", "performer_one")

    assert len(resolved) == 1
    assert resolved[0] == "https://mixdrop.ag/e/1n4gew0pb0ov1x"


def test_playvid_handles_missing_iframe(monkeypatch):
    """Playvid() does not crash when the iframe is absent."""
    html = "<html><body><p>Video unavailable</p></body></html>"

    fake_vp = MagicMock()

    monkeypatch.setattr(archivebate.utils, "getHtml", lambda url, referer=None: html)
    monkeypatch.setattr(archivebate.utils, "VideoPlayer", lambda *a, **k: fake_vp)

    archivebate.Playvid("https://archivebate.com/watch/000000", "missing")

    fake_vp.play_from_link_to_resolve.assert_not_called()


# --- Main tests ---

def test_main_adds_platform_dirs(monkeypatch):
    """Main() adds Chaturbate and Stripchat platform dirs."""
    dirs = []
    downloads = []

    session_mock = make_session_mock("<div></div>")

    monkeypatch.setattr(archivebate.requests, "Session", session_mock)
    monkeypatch.setattr(archivebate.site, "add_dir",
                        lambda name, url, mode, icon=None, **kw: dirs.append(
                            {"name": name, "url": url}
                        ))
    monkeypatch.setattr(archivebate.site, "add_download_link",
                        lambda *a, **k: downloads.append(a))
    monkeypatch.setattr(archivebate.utils, "eod", lambda: None)

    archivebate.Main()

    names = [d["name"] for d in dirs]
    assert any("Chaturbate" in n for n in names)
    assert any("Stripchat" in n for n in names)
```

**Step 2: Run tests — expect FAIL (module doesn't exist yet)**

```bash
source .venv/bin/activate
pytest tests/sites/test_archivebate.py -v 2>&1 | head -20
```

Expected output contains: `ModuleNotFoundError` or `ImportError` for `archivebate`.

---

## Task 3: Implement the site module

**Files:**
- Create: `plugin.video.cumination/resources/lib/sites/archivebate.py`

**Step 1: Write the site module**

```python
"""
Cumination
Copyright (C) 2023 Team Cumination

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import html as htmlmod
import json
import re

import requests

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "archivebate",
    "[COLOR hotpink]Archivebate[/COLOR]",
    "https://archivebate.com/",
    "archivebate.png",
    "archivebate",
)

_PLATFORMS = [
    ("[COLOR hotpink]Chaturbate[/COLOR]", "https://archivebate.com/platform/Y2hhdHVyYmF0ZQ=="),
    ("[COLOR hotpink]Stripchat[/COLOR]", "https://archivebate.com/platform/c3RyaXBjaGF0"),
]


def _livewire_list(url):
    """Two-step Livewire fetch. Returns the HTML fragment string, or None on failure."""
    session = requests.Session()
    session.headers.update({"User-Agent": utils.USER_AGENT})

    resp = session.get(url)

    csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', resp.text)
    if not csrf_match:
        return None
    csrf = csrf_match.group(1)

    wire_match = re.search(
        r'wire:initial-data="([^"]+)"[^>]*wire:init="loadVideos"', resp.text
    )
    if not wire_match:
        return None
    wire_state = json.loads(htmlmod.unescape(wire_match.group(1)))

    component_name = wire_state["fingerprint"]["name"]
    payload = {
        "fingerprint": wire_state["fingerprint"],
        "serverMemo": wire_state["serverMemo"],
        "updates": [{
            "type": "callMethod",
            "payload": {"id": "lw1", "method": "loadVideos", "params": []},
        }],
    }

    lw_resp = session.post(
        "https://archivebate.com/livewire/message/" + component_name,
        json=payload,
        headers={
            "X-CSRF-TOKEN": csrf,
            "X-Livewire": "true",
            "Accept": "application/json",
            "Referer": url,
        },
    )
    data = lw_resp.json()
    return data.get("effects", {}).get("html")


@site.register(default_mode=True)
def Main():
    for label, platform_url in _PLATFORMS:
        site.add_dir(label, platform_url, "List", site.img_cat)
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    fragment = _livewire_list(url)
    if not fragment:
        utils.eod()
        return

    soup = utils.parse_html(fragment)
    for item in soup.select("section.video_item"):
        link = item.select_one('a[href*="/watch/"]')
        if not link:
            continue

        thumb = item.select_one("video.video-splash-mov")
        performer = item.select_one('a[href*="/profile/"]')

        watch_url = link["href"]
        image = thumb.get("poster", "") if thumb else ""
        name = performer.text.strip() if performer else "Video"

        site.add_download_link(name, watch_url, "Playvid", image)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    soup = utils.parse_html(utils.getHtml(url, site.url))
    iframe = soup.select_one("iframe.video-frame")
    if iframe and iframe.get("src"):
        vp.play_from_link_to_resolve(iframe["src"])
```

**Step 2: Run the failing tests — expect PASS now**

```bash
source .venv/bin/activate
pytest tests/sites/test_archivebate.py -v
```

Expected: all 7 tests PASS.

**Step 3: Run the full test suite to check for regressions**

```bash
python run_tests.py 2>&1 | tail -5
```

Expected: `N passed, M skipped` — no new failures.

**Step 4: Run linter**

```bash
ruff check plugin.video.cumination/resources/lib/sites/archivebate.py
```

Expected: `All checks passed!`

**Step 5: Commit**

```bash
git add plugin.video.cumination/resources/lib/sites/archivebate.py \
        tests/fixtures/sites/archivebate_list.html \
        tests/fixtures/sites/archivebate_video.html \
        tests/sites/test_archivebate.py
git commit -m "feat: add Archivebate site plugin

Livewire two-step fetch for listings, MixDrop via ResolveURL for
playback. No pagination in v1 (tracked as TODO in design doc).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Task 4: Verify site appears in Kodi runtime (smoke check)

The `__init__.py` auto-discovers all `.py` files in the `sites/` directory, so no manual
registration is required. Verify the module is importable cleanly:

**Step 1: Quick import smoke test**

```bash
source .venv/bin/activate
python -c "from resources.lib.sites import archivebate; print('OK:', archivebate.site.name)"
```

Expected output: `OK: archivebate`

**Step 2: Verify it appears in the auto-discovered list**

```bash
python -c "
from resources.lib.sites import __all__
assert 'archivebate' in __all__, 'archivebate not in __all__'
print('archivebate is registered:', 'archivebate' in __all__)
"
```

Expected: `archivebate is registered: True`

---

## Done

The Archivebate site plugin is complete. A follow-up task is needed to:
1. Sniff the `loadMore` XHR (scroll to bottom on live site, capture the Livewire call)
2. Add pagination to `List()` using the updated `serverMemo`
3. Confirm and add Camsoda/OnlyFans/TikTok platform URLs
