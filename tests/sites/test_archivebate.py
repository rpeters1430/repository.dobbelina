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
